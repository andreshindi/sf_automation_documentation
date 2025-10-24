from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os
import pandas as pd
import os
import shutil ##using to move folders
import time
from base64 import b64decode
from zipfile import ZipFile
import base64
import zipfile
from ollama import chat
from ollama import ChatResponse


def query_salesforce(query):
    load_dotenv()

    #get credentials from .env
    sf_username = os.getenv("SF_USERNAME")
    sf_password = os.getenv("SF_PASSWORD")
    sf_token = os.getenv("SF_TOKEN")
    
    try:
        sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_token)
        print("*** Connected to Salesforce and Querying Records")
        query_result = sf.query(query)
        print("*** Records retrieved")
        return sf, query_result
    
    except Exception as e:
        print(f"*** Salesfoce Error: {e}")
        quit()

def prepare_dataframe(query_result):
    print("*** Building CSV record with query results")
    df = pd.DataFrame(query_result["records"])
    df = df.drop(columns=["attributes"])
    df["Description"] = df["Description"].str.replace(r'[\r\n]+', ' ', regex=True)
    df['flow_path'] = None
    df['api_response'] = None
    print("*** Dataframe succesfully built")
    return df

def build_unpackage(df):
    """
    this function is building the request that will be sent
    #to SF Metadata API to retrieve the XML of the flows
    """

    flows_list = df['ApiName'].tolist()
    retrieve_request = {
        'Flow': flows_list
    }
    return retrieve_request

def sf_retrieve_flows(sf, df):
    """
    This function receives the sf connection object and the dataframe. 
    The dataframe is used to build the Metadata API call.
    The returns are saved to the /flows folder
    It returns an updated version of the dataframe
    """

    #accessing property to instantiate the metadata class - learn more about lazy instantiation
    mdapi = sf.mdapi

    #get the formatted version of the request
    request = build_unpackage(df)

    print("*** Initiating request to Salesforce")
    retrieve_request = mdapi.retrieve(
            "DUMMY_ID_FOR_INITIATION", #not sure why this is required
            unpackaged=request, 
        )
    
    ##track results - get the ID of the retrieve request and the initial status
    async_id, status = retrieve_request

    #wait for the job to finalize, check status every 5 seconds
    while status not in ['Succeeded', 'Failed']:
        time.sleep(5)
        check_status = mdapi.check_retrieve_status(async_id)
        print(f"*** Current Status: {check_status[0]} ") #this return is a tuple! Is there another way to check the status?
        status = check_status[0]
    
    
    if status == 'Succeeded':
        print(f"*** Request Succeeded - async ID: {async_id} - status: {status}")
        
        # Get the result element - This return is a ZIP file, it will need to be extracted
        result_element = mdapi.retrieve_retrieve_result(async_id, "True")

        #maybe here I can created another function to keep it clean
        # Manipulate the zip element to save it to the /downloads folder
        print("*** Saving flows.zip to /downloads")
        zip_file = result_element.find('mt:zipFile', mdapi._XML_NAMESPACES)
        zip_extraction(zip_file)

        #update dataframe with the link to the flow
        #check all files extracted
        all_flow_files = os.listdir('./flows/')
        #loop each file, split the name api_name.xml to get the API name, match the row in the dataframe and populate the path to the record
        for f in all_flow_files:
            select_row = df.loc[df['ApiName'] == f.split('.')[0], 'flow_path'] = 'flows/'+f
    
        return df
        
    
    else:
            print("*** Request Job Failed")
            print(f"*** Results: {retrieve_result}")

def zip_extraction(zip_file):
    """
    Function used to extract zip file
    Creates the folders flow, extract the files to the folder
    """
    zip_content = zip_file.text
    zip_bytes = base64.b64decode(zip_content)
    
    #create folder if it doesnt exist
    output_folder = "./downloads/"
    output_file = "flows_metadata.zip"
    os.makedirs(output_folder, exist_ok=True)
    zip_path = os.path.join(output_folder, output_file)
    with open(zip_path, "wb") as f:
            f.write(zip_bytes)
    print("*** flows.zip saved with success to /downloads")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)
    print("*** The Flows have been extracted to the /downloads folder ")

    #move extracted flow folder to root
    if os.path.exists("./flows/"):
        shutil.rmtree("./flows/")
    shutil.move("./downloads/flows/", "./flows/")
    print("*** The Flows have been moved to the /flows folder")

    #clear downloads folder
    for filename in os.listdir("./downloads/"):
        file_path = os.path.join("./downloads/", filename)
        if os.path.isfile(file_path):   # only delete files
            os.remove(file_path)
    print("*** Cleaning /downloads folder")

def process_with_ollama(prompt_context, df):
    """
    Let's call the Ollama API with the prompt with the XML of the flows
    Then save the response to the df and save it to /outputs/flow_descriptions.csv
    """

    #removing NaN here so my script can identify only lines populated on flow_path
    df_clean = df.fillna(value='')
    print("*** Preparing dataframe for API calls")

    #iterate each row, checks if the flow_path row has information. 
    for i, r in df_clean.iterrows():
        #only considers rows with information
        if r['flow_path']:
            print(f"*** Processing {r['flow_path']}")
            with open(r['flow_path'], 'r', encoding='utf-8') as file:
                xml_string = file.read()
            #print(xml_string)
            prompt = """give a nickname to this salesforce flow metadata, 
                    do not describe the flow, tell me only the nickname,
                    describe it as you were Mario,
                    your response must contain maximum of two words, 
                    don't ask for more options ---"""+prompt_context


            try:
                response: ChatResponse = chat(model='llama3.1:8b', messages=[{'role': 'user', 'content': prompt,},])
                print(f"**** Saving {r['flow_path']} API response to api_response")
                df.loc[df['flow_path'] == r['flow_path'], 'api_response'] = response.message.content

            except Exception as e:
                print(f"Failure: {e}")
                quit()    

            

    df["api_response"] = df["api_response"].str.replace(r'[\r\n]+', ' ', regex=True)
    df.to_csv('outputs/flow_descriptions.csv', sep=';', index=False)
    print(f"*** Saving dataframe as output/flow_descriptions.csv")




def main():
    #Step 1 - Salesforce connection and query records
    #build the query we want to send to query all the flows
    query="""SELECT id, Label, ApiName, TriggerObjectOrEventLabel, TriggerType, ProcessType, Description 
        FROM FlowDefinitionView
        WHERE isActive = TRUE AND (ProcessType = 'AutoLaunchedFlow' OR ProcessType = 'Flow')"""

    #this function connects to SF and queries SF using the query above: it returns the sf object (connection) that I will
    #use for a metadata call on step 3
    sf, query_result = query_salesforce(query)

    #Step 2 - Build the dataframe that will be used throughout the script and result in a final file
    #Input the results from salesforce query and get a dataframe
    df = prepare_dataframe(query_result)


    #Step 3 - Query Salesforce flow medatada from Salesforce, save files in a flow folder and update the dataframe
    #Input the results from salesforce query and update the dataframe with the flow_path
    df = sf_retrieve_flows(sf, df)

    #Step 4 - Set the context of the prompt and send it for AI processing with ollama. The results will be updated on the dataframe
    prompt_context = """provide a nickname to this salesforce flow metadata, 
                            do not describe the flow, tell me only the nickname,
                            your response must contain maximum of two words, 
                            don't ask for more options ---"""
    
    process_with_ollama(prompt_context, df)



if __name__ == "__main__":
    main()
    
    #print(xml_string)
    
    print("*** END of the code ***")
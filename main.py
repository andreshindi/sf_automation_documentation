from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os
import pandas as pd
import os
import time
from base64 import b64decode
from zipfile import ZipFile
from io import BytesIO
import base64
import zipfile
import shutil ##using to move folders
from ollama import chat
from ollama import ChatResponse








#function to start SF connection
def sf_connection():
    try:
        sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_token)
        print("*** You're connected to Salesforce")
        print("*** ---")
        print("*** Querying records from Salesforce")
        sf_query = """
        """
        query_result = sf.query(sf_query)
        
        #transform result in dataframe and export to CSV (outputs/flow_list.csv)
        #aqui nao preciso salvar nada
        df = build_dataframe(query_result)

        
        #accessing property to instantiate the metadata class - learn more about lazy instantiation
        mdapi = sf.mdapi

    
        
        req = build_unpackage(df) 

        ##logic to start the retrieve job - generates XML files that will be returned as ZIP
        print(req)
        retrieve_result = mdapi.retrieve(
            "DUMMY_ID_FOR_INITIATION",
            unpackaged=req, 
        )

        ##track IDS
        async_id, status = retrieve_result

        #wait for the job to finalize 
        while status not in ['Succeeded', 'Failed']:
            time.sleep(5)
            check_status = mdapi.check_retrieve_status(async_id)
            print(check_status[0])
            status = check_status[0]
        
        
        if status == 'Succeeded':
            print(f"Deu Certo Porra - async ID: {async_id} - status: {status}")
            # Get the result element
            result_element = mdapi.retrieve_retrieve_result(async_id, "True")
            print(result_element)

            ##from this point, another script
            # Extract the result ID (needed to retrieve the zip)
            zip_file = result_element.find('mt:zipFile', mdapi._XML_NAMESPACES)
            #print(f"zip file - result_element.find: {zip_file}")
            zip_content = zip_file.text
            #print(f"zip content - zip_content = zip_file.text: {zip_content}")
            zip_bytes = base64.b64decode(zip_content)
            #create folder if it doesnt exist
            output_folder = "./downloads/"


            os.makedirs(output_folder, exist_ok=True)
            zip_path = os.path.join(output_folder, f"{async_id}.zip")
            with open(zip_path, "wb") as f:
                f.write(zip_bytes)

            #extract zip
            zip_path = f"{output_folder}{async_id}.zip"
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_folder)
            #print(zip_path)

            #move extracted flow folder to root
            if os.path.exists("flows/"):
                shutil.rmtree("flows/")
            shutil.move("downloads/flows/", "flows/")

            #clear downlaods folder
            for filename in os.listdir("downloads/"):
                file_path = os.path.join("downloads/", filename)
                if os.path.isfile(file_path):   # only delete files
                    os.remove(file_path)
            
            link_flows_df(df)

            df = pd.read_csv('outputs/flow_list.csv', sep=';')
            df_clean = df.fillna(value='')

            for i, r in df_clean.iterrows():
                if r['FlowPath']:
                    print(r['FlowPath'])
                    with open(r['FlowPath'], 'r', encoding='utf-8') as file:
                        xml_string = file.read()
                    #print(xml_string)
                    prompt = """give a nickname to this salesforce flow metadata, 
                            do not describe the flow, tell me only the nickname,
                            your response must contain maximum of two words, 
                            don't ask for more options ---"""+xml_string
                    ## from this point, it needs to open the xml data, load into the prompt
                    chat_response = ollama_call(prompt)
                    chat_response = chat_response+r['FlowPath']
                    df.loc[df['FlowPath'] == r['FlowPath'], 'api_response'] = chat_response
                    #flow_df["Description"] = flow_df["Description"].str.replace(r'[\r\n]+', ' ', regex=True)

            df["api_response"] = df["api_response"].str.replace(r'[\r\n]+', ' ', regex=True)
            df.to_csv('outputs/flow_final.csv', sep=';', index=False)

        else:
            print("Deu Errado, porra")
            print(status)
            print(retrieve_result)


    #catch any error here and display        
    except Exception as e:
        print(f"Failure: {e}")

def link_flows_df(df):
    df['FlowPath'] = None
    all_files = os.listdir('./flows/')
    for f in all_files:
        select_row = df.loc[df['ApiName'] == f.split('.')[0], 'FlowPath'] = 'flows/'+f
    os.makedirs('./outputs/', exist_ok=True)
    df.to_csv('./outputs/flow_list.csv', sep=';')
    print('*** Flows saved to outputs/flow_list.csv')
   
    

#function top transform query result in dataframe and export to CSV (outputs/flow_list.csv) - maybe this is another script
def build_dataframe(query_result):
    print("*** ---")
    print("*** Building CSV record with query results")
    flow_df = pd.DataFrame(query_result["records"])
    flow_df = flow_df.drop(columns=["attributes"])
    ##this line below will make sure that long descriptions with multines will stay in the same column when converting to CSV
    flow_df["Description"] = flow_df["Description"].str.replace(r'[\r\n]+', ' ', regex=True)
    #os.makedirs('outputs/', exist_ok=True)
    #flow_df.to_csv('outputs/flow_list.csv',sep=';',index=False)
    #print("*** Flows have been exported to outputs/flow_list.csv")
    return flow_df

#funtion to build the list of flows that will have the metadata retrieved
#goal is to use the output file to build this piece of logic


def ollama_call(prompt):       
    response: ChatResponse = chat(model='llama3.1:8b', messages=[
    {'role': 'user', 'content': prompt,},
    ])
    print(response['message']['content'])
    chat_response = response['message']['content']
    return chat_response

'''New part 
of the code
'''

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

def sf_flows(sf, df):
    """
    This function receives the sf connection object and the dataframe. The dataframe is used to build the Metadata API call.
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
        zip_content = zip_file.text
        zip_bytes = base64.b64decode(zip_content)
        
        #create folder if it doesnt exist
        output_folder = "./downloads/"
        os.makedirs(output_folder, exist_ok=True)
        zip_path = os.path.join(output_folder, "flows_metadata.zip")
        with open(zip_path, "wb") as f:
                f.write(zip_bytes)
        print("*** flows.zip saved with success to /downloads")

    
    else:
            print("*** Request Job Failed")
            print(f"*** Results: {retrieve_result}")


def main():
    '''
    Step 1 - Salesforce connection and query records
    '''
    #build the query we want to send to query all the flows
    query="""SELECT id, Label, ApiName, TriggerObjectOrEventLabel, TriggerType, ProcessType, Description 
        FROM FlowDefinitionView
        WHERE isActive = TRUE AND (ProcessType = 'AutoLaunchedFlow' OR ProcessType = 'Flow')"""

    #this function connects to SF and queries SF using the query above: it returns the sf object (connection) that I will
    #use for a metadata call on step 3
    sf, query_result = query_salesforce(query)


    '''
    Step 2 - Build the dataframe that will be used throughout the script and result in a final file
    '''

    #Input the results from salesforce query and get a dataframe
    df = prepare_dataframe(query_result)

    '''
    Step 3 - Query Salesforce flow medatada from Salesforce, save files in a flow folder and update the dataframe
    '''

    #Input the results from salesforce query and get a dataframe
    sf_flows(sf, df)



if __name__ == "__main__":
    main()
    
    #print(xml_string)
    
    print("*** END ***")
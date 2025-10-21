    from simple_salesforce import Salesforce
    from dotenv import load_dotenv
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


    #load .env file
    load_dotenv()

    #initialize sf credentias
    sf_username = os.getenv('SF_USERNAME')
    sf_password = os.getenv('SF_PASSWORD')
    sf_token = os.getenv('SF_TOKEN')

    #function to start SF connection
    def sf_connection():
        try:
            sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_token)
            print("*** You're connected to Salesforce")
            print("*** ---")
            print("*** Querying records from Salesforce")
            #query_result = sf.query("SELECT id, Label, ApiName, TriggerObjectOrEventLabel, TriggerType, ProcessType, Description FROM FlowDefinitionView WHERE isActive = TRUE")
            
            #transform result in dataframe and export to CSV (outputs/flow_list.csv)
            #build_dataframe(query_result)

            
            #accessing property to instantiate the metadata class - learn more about lazy instantiation
            mdapi = sf.mdapi

        
            
            req = build_unpackage() 

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
                output_folder = "downloads/"


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

            else:
                print("Deu Errado, porra")


        #catch any error here and display        
        except Exception as e:
            print(f"Failure: {e}")

    #function top transform query result in dataframe and export to CSV (outputs/flow_list.csv) - maybe this is another script
    def build_dataframe(query_result):
        print("*** ---")
        print("*** Building CSV record with query results")
        flow_df = pd.DataFrame(query_result["records"])
        flow_df = flow_df.drop(columns=["attributes"])
        ##this line below will make sure that long descriptions with multines will stay in the same column when converting to CSV
        flow_df["Description"] = flow_df["Description"].str.replace(r'[\r\n]+', ' ', regex=True)
        flow_df.to_csv('outputs/flow_list.csv',sep=';',index=False)
        print("*** Flows have been exported to outputs/flow_list.csv")

    #funtion to build the list of flows that will have the metadata retrieved
    #goal is to use the output file to build this piece of logic
    def build_unpackage():
        retrieve_request = {
            'Flow': ['Auto_Refresh_Project_Geographic_Area_List_on_Project'] 
        }
        return retrieve_request


    if __name__ == "__main__":
        sf = sf_connection()
        xml_file_path = 'flows/Auto_Refresh_Project_Geographic_Area_List_on_Project.flow'
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            xml_string = f.read()
        #print(xml_string)
        content = """ Explain this salesforce flow in three bullet points
        ------
        """ 
        content = content + xml_string
        
        response: ChatResponse = chat(model='llama3.1', messages=[
        {
            'role': 'user',
            'content': content,
        },
            ])
        print(response['message']['content'])
        # or access fields directly from the response object
        #print(response.message.content)
        
        print("*** END ***")

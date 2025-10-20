from simple_salesforce import Salesforce
from dotenv import load_dotenv
import pandas as pd
import os

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
        print("*** You're connected to Salesforce ***")
        #description = sf.describe()
        #for obj in description["sobjects"]:
        #    print(obj["label"])
        flows = sf.query("SELECT id, Label, ApiName, TriggerObjectOrEventLabel, TriggerType, ProcessType, Description FROM FlowDefinitionView WHERE isActive = TRUE")
        print(flows.keys())

        flow_df = pd.DataFrame(flows["records"])
        flow_df = flow_df.drop(columns=["attributes"])
        ##this line below will make sure that long descriptions with multines will stay in the same column when converting to CSV
        flow_df["Description"] = flow_df["Description"].str.replace(r'[\r\n]+', ' ', regex=True)
        flow_df.to_csv('outputs/flow_list.csv',sep=';',index=False)
        print(flow_df)
        #for f in flows["records"]:
        #    print(f["Label"]," : ", f["ProcessType"])
        #create_dataset(flows)

        #OrderedDict([('attributes', OrderedDict([('type', 'FlowDefinitionView'), ('url', '/services/data/v59.0/sobjects/FlowDefinitionView/300gK00000ClxPFQAZ')])), ('Id', '3ddgK00000ClxPFQAZ'), ('IsActive', True), ('Label', '[Auto] Generate API Transaction Code Record'), ('TriggerType', None)])


    #catch any error here and display        
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    sf = sf_connection()
    print("*** END ***")

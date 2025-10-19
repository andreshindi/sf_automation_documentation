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
        flows = sf.query("SELECT id, IsActive, Label, ProcessType, ManageableState , TriggerObjectOrEventId, TriggerObjectOrEventLabel, TriggerType FROM FlowDefinitionView WHERE isActive = TRUE")
        #for f in flows["records"]:
        #    print(f["Label"]," : ", f["ProcessType"])
        create_dataset(flows)


    #catch any error here and display        
    except Exception as e:
        print(f"Failure: {e}")

def (list):
    print(list)


if __name__ == "__main__":
    sf = sf_connection()
    print("*** END ***")

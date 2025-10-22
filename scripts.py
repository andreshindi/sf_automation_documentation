import os
import pandas as pd
from ollama import chat
from ollama import ChatResponse

def ollama_call(prompt):       
    response: ChatResponse = chat(model='llama3.1:8b', messages=[
    {'role': 'user', 'content': prompt,},
    ])
    print(response['message']['content'])
    chat_response = response['message']['content']
    return chat_response

df = pd.read_csv('outputs/flow_list.csv', sep=';')
df_clean = df.fillna(value='')

n = 0
for i, r in df_clean.iterrows():
    if r['FlowPath']:
        print(r['FlowPath'])
        with open(r['FlowPath'], 'r', encoding='utf-8') as file:
            xml_string = file.read()
        #print(xml_string)
        prompt = "give a nickname to this salesforce flow metadata, do not describe the flow, tell me only the nickname, don't ask for more options ---"+xml_string
        ## from this point, it needs to open the xml data, load into the prompt
        chat_response = ollama_call(prompt)
        chat_response = chat_response+r['FlowPath']
        df.loc[df['FlowPath'] == r['FlowPath'], 'api_response'] = chat_response
        #flow_df["Description"] = flow_df["Description"].str.replace(r'[\r\n]+', ' ', regex=True)

df["api_response"] = df["api_response"].str.replace(r'[\r\n]+', ' ', regex=True)
df.to_csv('outputs/flow_final.csv', sep=';', index=False)







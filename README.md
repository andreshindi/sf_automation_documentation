# Process Flows Metadada with LLM 

## Problem Statement
Before designing a flow, the Salesforce administrator must know which flows are connected to the objects they’re working with, so they can avoid conflicting logic. Extracting Flow metadata and describing the flow is a time consuming activity for admins and devs.

## Goal
This script will list all the flow metadata from an org (type, related object, and a short description), retrieve the flows strucutre using SF MetadataAPI and use Ollama (local) to generate the descriptions based on the metadata. A CSV with all the information collected and processed is saved at the end of the process.

## Instructions
### Requirements
```
pip install -r requirements.txt
```

### .env
```
# Salesforce credentials 

SF_USERNAME=
SF_PASSWORD=
SF_TOKEN=
```

### Folder Structure
```
project/
├── scripts/
│   └── main.py
├── requirements.txt
├── .env
└── README.md
```

### Ollama
You need to install and initialize Ollama 
```

ollama run llama3.1:8b

```

### Set inputs
Open ./scripts/main.py 

Look for the main() function:

Change SF query (if necessary)
```
 query="""SELECT id, Label, ApiName, TriggerObjectOrEventLabel, TriggerType, ProcessType, Description 
        FROM FlowDefinitionView
        WHERE isActive = TRUE AND (ProcessType = 'AutoLaunchedFlow' OR ProcessType = 'Flow')"""
```

Change prompt_context (if necessary)
```
prompt_context = """provide a nickname to this salesforce flow metadata, 
                            do not describe the flow, tell me only the nickname,
                            your response must contain maximum of two words, 
                            don't ask for more options ---"""
```


### Run the application
```
python ./scripts/main.py
```

## Improvements (Out of scope for now)
- UX to allow users to interact with the application
- Ability to extend the functionality to validation rules and apex triggers/classes
- Connect this script to OpenAI, Gemini or Claude to getter better and real results

## Findings / Learnings
- It's not possible to extract managed package or standard flows metadata - Potential limitation for real application
- Script structure is still confusing. I will need to find a way to plan my code in advance and split the script in specific modules to have a better structure
- Stackoverflow and Reddit are the best source of troubleshooting and learning! AI can help with different examples.



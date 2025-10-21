# sf_automation_documentation

### Notes 20-Oct-2025
- add a check of the outputs/download folder and create them if required
- loop flow_list, build the request to retrieve all flows in unpackaged
- check if can retrieve all flows
- build the .flow path on flow list
- use it to send to llm, get the result and add to another column (description)
- Before proceeding: Organize code blocks - 

### Progress
- Now we're able to: initiate connection, query active flows, put them in a csv (break) request a mtd retrieval, extract the zip, move the flow metadata to the flow folder

## Problem Statement
Before designing a flow, the Salesforce administrator must know which flows are connected to the objects they’re working with, so they can avoid conflicting logic.

## Goal
This script will list all the flow metadata from an org and document in a spreadsheet the details (type, related object, and a short description) of each flow using an LLM to generate the descriptions based on the metadata.

## Instructions
Requirements
```
pip install -r requirements.txt
```

## Improvements (Out of scope for now)
- UX to allow users to interact with the application

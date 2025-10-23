# sf_automation_documentation

### Notes 20-Oct-2025
- script: fix prompt - use """ to build the prompt
- start organizing the code. Different scripts for different functions
- Don't use openAI, ollama works fine for this demo - Maybe we need to use docker??

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

.env
```
# Salesforce credentials 

SF_USERNAME=
SF_PASSWORD=
SF_TOKEN=
```

## Improvements (Out of scope for now)
- UX to allow users to interact with the application

## Findings
- It's not possible to extract managed package or standard flows metadata - Limitation


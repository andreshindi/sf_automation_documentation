# sf_automation_documentation

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

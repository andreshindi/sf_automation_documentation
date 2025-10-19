# sf_automation_documentation

### Notes 18-Oct-2025
- Check FlowDefinitionView object and types of return - Can I return descriptions? - Potentially possible with Metadata API
- Use pandas to organize the return from the query
- Possibly, I will need to need to build the package and retrieve the flow XMLs
- Check how to extract the actual FLOW metadata
- Research how send them to the LLM

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

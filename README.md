# Jarvis
## Project Folder Structure

```
ADK_Hackathon/
├── backend/                
│   ├── personal_assistant/ # Python FastAPI backend with sub-agents and utilities
│   │   ├── agent.py # root_agent Jarvis
│   │   ├── app.py
│   │   ├── prompt.py # root_agent prompt
│   │   ├── email_agent/ # email_agent setup
│   │   ├── calendar_agent/ # calendar_agent setup
│   │   ├── mobility_agent/ # mobility_agent setup
│   │   ├── common/ # common utils
│   │   │   ├── __init__.py
│   │   │   ├── agent_utils.py
│   │   │   ├── tool_utils.py
│   ├── deployment  # deployyment using google vertexai
│   ├── .env  # enviroment variables
│   ├── poetry.lock 
│   └── pyproject.toml      # Python dependencies for Poetry
├── frontend/               # React frontend application
│   ├── index.html
│   ├── index.tsx
│   └── ...
├── README.md               # Project documentation (this file)
```


This contains everything you need to run your app locally.

## Run Backend Locally
**Prerequisites:** 
python 3.13.2 (recommend use pyenv for version management)
peotry (please follow this link https://python-poetry.org/docs/)

1. Install dependencies:
```sh
cd backend
poetry install
```
2. run the fastapi app:
```sh
cd personal_assistant
poetry run uvicorn app:app --reload
```

## Run Frontend Locally

**Prerequisites:**  Node.js

1. Install dependencies:
   `npm install`
3. Run the app:
   `npm run dev`


**You can now play with the UI using the link provided by npm, which connects to your fastapi locally**

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse 
from Devassist.components import Loadfiles,llm
from dotenv import load_dotenv
import json
import os
import prompts
from Devassist.components.agents import Agents
from  Devassist.config import models

load_dotenv('/workspaces/DevAssist-AI/.env')
chat_history = []

app = FastAPI()
key = os.getenv('LLM_API_KEY')
client = llm.LLM(key = key,model = 'mixtral-8x7b-32768')

dev_agents = Agents(key = key)

@app.post('/chat/')
async def chat(request:Request)->JSONResponse:
    try:
        input_data = await request.json()
        print(input_data)
        print("chat\n",''.join(chat_history))
        query = input_data.get('query')
        
        response = await dev_agents.query_routing(query=query,chat_history=chat_history,prompt=prompts.query_routing)
        return JSONResponse({'status':'success','response':response})
    
    except Exception as e:
        print(f'Error at json parsing \n{e}')
        return JSONResponse(status_code=400,content={'error':'Bad request','detail':str(e)})


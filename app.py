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


app = FastAPI()
key = os.getenv('LLM_API_KEY')
client = llm.LLM(key = key,model = 'mixtral-8x7b-32768')

dev_agents = Agents()
query_routing_tools = dev_agents.query_routing()

@app.post('/chat/')
async def chat(request:Request)->JSONResponse:
    try:
        input_data = await request.json()
        print(input_data)

        query = input_data.get('query')
        response = await client.get_non_stream_response(
            model = models.ROUTING_MODEL,
            query = query,
            chat_history = [],
            system_message = prompts.assistant_prommpt,
            tools=query_routing_tools
        )
        print(response)
        return JSONResponse({'status':'success','response':response['content']})
    except Exception as e:
        print(f'Error at json parsing \n{e}')
        return JSONResponse(status_code=400,content={'error':'Bad request','detail':str(e)})


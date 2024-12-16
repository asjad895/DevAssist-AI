from ssl import SSL_ERROR_SSL
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse 
from Devassist.components import Loadfiles,llm
from dotenv import load_dotenv
import json
import os
from chat_session import ChatManager
import prompts
from Devassist.components.agents import Agents
from  Devassist.config import models
import database

load_dotenv('/workspaces/DevAssist-AI/.env')
# 
database.initialize_db()
session_manager = database.SessionManager()
chat_manager = database.ChatHistoryManager()
session_id = session_manager.create_session(user_id="user123")
print(f"Session Created: {session_id}")
# 
app = FastAPI()
key = os.getenv('LLM_API_KEY','')
client = llm.LLM(key = key,model = 'mixtral-8x7b-32768')

dev_agents = Agents(key = key)

@app.post('/chat/')
async def chat(request:Request)->JSONResponse:
    try:
        input_data = await request.json()
        print(input_data)
        query = input_data.get('query')
        chat_manager.add_message(session_id=session_id,role='user',content=query)
        chat_history = chat_manager.get_chat_history(session_id=session_id)
        print("chat\n",chat_manager.get_chat_history(session_id=session_id))

        response = await dev_agents.query_routing(
            session_id=session_id,
            query=query,
            chat_history=chat_history,
            prompt=prompts.query_routing
            )
        return JSONResponse({'status':'success','response':response})
    
    except Exception as e:
        print(f'Error at json parsing \n{e}')
        return JSONResponse(status_code=400,content={'error':'Bad request','detail':str(e)})

session_manager.batch_expire_sessions()


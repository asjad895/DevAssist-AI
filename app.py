
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse,JSONResponse
from Devassist.components import llm
import json
import os
import prompts
from Devassist.components.agents import Agents
from Devassist.customexception import exception
from  Devassist.config import models
import database
from dotenv import load_dotenv

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
        print(exception.custom_exception())
        return JSONResponse(status_code=400,content={'error':'Bad request','detail':str(e)})



@app.get("/")
async def homepage(request: Request) -> HTMLResponse:
    try:
        return templates.TemplateResponse(name='index',context={"request": request})
    except Exception as e:
        print(exception.custom_exception())
        return HTMLResponse(content="<h1>Internal Server Error</h1>", status_code=500)


session_manager.batch_expire_sessions()


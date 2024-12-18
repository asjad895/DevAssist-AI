
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
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"] 


from dotenv import load_dotenv

load_dotenv()
# 
database.initialize_db()
session_manager = database.SessionManager()
chat_manager = database.ChatHistoryManager()
# 
app = FastAPI()
key = os.getenv('LLM_API_KEY','')
client = llm.LLM(key = key,model = 'mixtral-8x7b-32768')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

dev_agents = Agents(key = key)



@app.post('/chat/')
async def chat(request:Request)->JSONResponse:
    try:
        input_data = await request.json()
        print(input_data)
        query = input_data.get('query')

        session_id = session_manager.create_session(session_id=input_data.get('session_id','session_id'))
        chat_history = chat_manager.get_chat_history(session_id=session_id)
        # print("chat\n",chat_history)

        response = await dev_agents.query_routing(
            session_id=session_id,
            query=query,
            chat_history=chat_history,
            prompt=prompts.query_routing
            )
        if isinstance(response,dict) and 'error' in response:
            return JSONResponse({'response':"An Internal error occured at server"})
        return JSONResponse({'response':response})
    
    except Exception as e:
        print(exception.custom_exception())
        return JSONResponse(status_code=400,content={'response':'Bad request','detail':str(e)})



session_manager.batch_expire_sessions()


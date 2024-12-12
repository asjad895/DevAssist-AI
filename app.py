from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse 
from Devassist.components import Loadfiles,llm
from dotenv import load_dotenv
import json
import os
load_dotenv('/workspaces/DevAssist-AI/.env')


app = FastAPI()

key = os.getenv('LLM_API_KEY')
client = llm.LLM(key = key,model = 'mixtral-8x7b-32768')

@app.post('/chat/')
async def chat(request:Request)->JSONResponse:
    try:
        input_data = await request.json()
        print(input_data)

        download_data = Loadfiles.GitHubRepoInput(repo_url=input_data['github_url'])

        await Loadfiles.download_github_repo(download_data)

        query = input_data.get('query')
        response = await client.get_non_stream_response(
            query = query,
            chat_history = [],
            system_message = "You are as assistant."
        )
        print(response)
        return JSONResponse({'status':'success','response':response['content']})
    except Exception as e:
        print(f'Error at json parsing \n{e}')
        return JSONResponse(status_code=400,content={'error':'Bad request','detail':str(e)})

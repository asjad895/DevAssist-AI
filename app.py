from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse 
from Devassist.components import Loadfiles
import json


app = FastAPI()

@app.post('/chat/')
async def chat(request:Request)->JSONResponse:
    try:
        input_data = await request.json()
        print(input_data)

        download_data = Loadfiles.GitHubRepoInput(repo_url=input_data['github_url'])

        await Loadfiles.download_github_repo(download_data)
        return JSONResponse({'status':'success'})
    except Exception as e:
        print(f'Error at json parsing \n{e}')
        return JSONResponse(status_code=400,content={'error':'Bad request','detail':str(e)})


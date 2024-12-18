from ast import Dict, List
import code
import json
from typing import Any
from pydantic import BaseModel,HttpUrl
import inspect

from torch import clone
from Devassist.customexception import exception
from Devassist.components import Loadfiles
import Devassist.components.utils as utils
from Devassist.config import fileconfig
from Devassist.config import models


class Tools:
    def __init__(self) -> None:
        pass

    async def clone_repo(self,url:HttpUrl) ->Any:
        """Use this tool when github repo url is present in user query and not cloned till now in ongoing conversation.
        Args:
            url (HttpUrl): github repo http url

        Returns:
            str: a message
        """
        try:
            data = Loadfiles.GitHubRepoInput(repo_url=url)
            await Loadfiles.download_github_repo(data)

        except exception:
            print(exception.custom_exception())
            raise 

        return {
            "sucess":"Successfully cloned the given repo"
            }
    
    async def extract_codebase_files(self) -> List:
        """
        Use This Tool when Repo has been successfully cloned. It will help to extract all files for furthure analysis.
        
        Returns:
        List: A list of file paths found in the codebase directory.
        """
        codebase_dir = fileconfig.CODEBASE_DIR
        visited_dir = {}
        list_of_files = []
    
        try:
            final_result = await utils.traverse_directory(
                current_dir=codebase_dir,
                visited_dirs=visited_dir,
                list_contents=list_of_files
            )
            return final_result
        except Exception as e:
            print(exception.custom_exception())
            raise


    async def get_comments(self,codes : str,prompt : str,client :object) ->str:
        """
        """
        response = await client.get_non_stream_response( # type: ignore
            model=models.GENERAL_MODEL,
            query=None,
            chat_history = [],
            system_message=prompt.format(codes = codes),
        )
        print("\n\n--------comment--------------------------------\n")
        print(response.content)

        return response.content

 

clone_repo_tool = {
    "type": "function",
    "function": {
        "name": Tools.clone_repo.__name__,
        "description": "Use this tool when github repo url is present in user query and not cloned till now in ongoing conversation.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "HttpUrl",
                    "description": "github repo http url,eg https://github.com/asjad895/GENAI_CHATBOT",
                }
            },
            "required": ["url"],
        },
    },
}
    
# print(json.dumps(clone_repo_tool,indent=3))





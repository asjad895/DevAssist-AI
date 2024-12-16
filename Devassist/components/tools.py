import json
from sys import exception
from pydantic import BaseModel,HttpUrl
import inspect

from torch import clone
from Devassist.customexception import exception
from Devassist.components import Loadfiles

class Tools:
    def __init__(self) -> None:
        pass

    async def clone_repo(self,url:HttpUrl) ->str:
        """Use this tool when user has given input as a github repo url

        Args:
            url (HttpUrl): github repo url

        Returns:
            str: a message
        """
        try:
            data = Loadfiles.GitHubRepoInput(repo_url=url)
            await Loadfiles.download_github_repo(data)

        except exception:
            print(exception.custom_exception())
            raise 

        return "Done"
    


clone_repo_tool = {
    "type": "function",
    "function": {
        "name": Tools.clone_repo.__name__,
        "description": inspect.getdoc(Tools.clone_repo),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "HttpUrl",
                    "description": "github repo url",
                }
            },
            "required": ["url"],
        },
    },
}
    
print(json.dumps(clone_repo_tool,indent=3))




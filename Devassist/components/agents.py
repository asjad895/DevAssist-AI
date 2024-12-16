
from Devassist.components.tools import Tools,clone_repo_tool
from typing import List,Dict

class Agents:
    def __init__(self) -> None:
        self.tools = [clone_repo_tool]

    

    def query_routing(self)->List[Dict]:
        return self.tools


from dotenv import load_dotenv
import os
from groq import AsyncGroq
from typing import List,Dict,Union
load_dotenv()


api_key = os.getenv('LLM_API_KEY')


class LLM:
    def __init__(self,key : str ,model : str = "") -> None:
        if not key:
            raise KeyError()
        else:
            self.key = key

        self.model = model

        self.client = AsyncGroq(api_key=self.key)


    
    async def get_non_stream_response(self,query : str,chat_history:List[Dict[str,str]],system_message : str)->Dict:

        if not isinstance(query,str) or not isinstance(chat_history,List) or not isinstance(system_message,str):
            return {
                'error':"Invalid Input"
            }
        
        messages = [{'role':'system','content':system_message}]+chat_history + [{'role':'user','content':query}]
        
        chat_completion = await self.client.chat.completions.create(
            messages = messages, # type: ignore
            model = self.model
        )
        print(chat_completion.choices[0].message.content)

        return chat_completion.choices[0].message.to_dict()


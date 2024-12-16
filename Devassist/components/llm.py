from dotenv import load_dotenv
import os
from groq import AsyncGroq
from typing import Any, List, Dict, Union, AsyncGenerator
from Devassist.config import gen_responseconfig
from Devassist.customexception import exception

load_dotenv()

api_key = os.getenv('LLM_API_KEY')


class LLM:
    def __init__(self, key: str, model: str = "") -> None:
        try:
            if not key:
                raise KeyError("API key is missing!")
            else:
                self.key = key

            self.model = model
            self.client = AsyncGroq(api_key=self.key)
        except Exception:
            print(exception.custom_exception())
            raise

    async def get_non_stream_response(
        self, 
        model: str,
        query: str, 
        chat_history: List[Dict[str, str]], 
        system_message: str,
        tools : List =[]
        ) -> Union[Any,Any]:
        try:
            if not isinstance(query, str) or not isinstance(chat_history, List) or not isinstance(system_message, str):
                return {'error': "Invalid Input"}

            messages = [{'role': 'system', 'content': system_message}] + chat_history + [{'role': 'user', 'content': query}]


            if len(tools)>0:
                chat_completion = await self.client.chat.completions.create(
                    messages=messages,  # type: ignore
                    model=model,
                    temperature=gen_responseconfig.temperature,
                    top_p=gen_responseconfig.top_p,
                    max_tokens=gen_responseconfig.max_tokens,
                    tools=tools,
                    tool_choice= 'auto'
                )
            else:
                chat_completion = await self.client.chat.completions.create(
                    messages=messages,  # type: ignore
                    model=model,
                    temperature=gen_responseconfig.temperature,
                    top_p=gen_responseconfig.top_p,
                    max_tokens=gen_responseconfig.max_tokens,
                )
            
            
            print(chat_completion.choices[0].message)

            return chat_completion.choices[0].message

        except Exception:
            print(exception.custom_exception())
            return {'error': "An error occurred while processing the request."}

    async def get_stream_response(
        self, 
        query: str, 
        chat_history: List[Dict[str, str]], 
        system_message: str
        ) -> AsyncGenerator:
        try:
            if not isinstance(query, str) or not isinstance(chat_history, List) or not isinstance(system_message, str):
                yield {'error': "Invalid Input"}
                return

            messages = [{'role': 'system', 'content': system_message}] + chat_history + [{'role': 'user', 'content': query}]

            chat_completion = await self.client.chat.completions.create(
                messages=messages,  # type: ignore
                model=self.model,
                stream=True,
                temperature=gen_responseconfig.temperature,
                top_p=gen_responseconfig.top_p,
                max_tokens=gen_responseconfig.max_tokens
            )
            for chunk in chat_completion:
                print(chunk.choices[0].delta.content, end="")
                yield chunk.choices[0].delta

        except Exception:
            print(exception.custom_exception())
            yield {'error': "An error occurred while streaming the response."}





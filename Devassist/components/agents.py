from networkx import union
from Devassist.components.tools import Tools, clone_repo_tool
from typing import List, Dict,Union
from Devassist.components import llm
import os, json
from Devassist.config import models
from Devassist.customexception import exception

class Agents:
    def __init__(self, key: str) -> None:
        self.tools = [clone_repo_tool]
        self.client = llm.LLM(key=key)
        self.available_functions = {"clone_repo": Tools.clone_repo}

    async def query_routing(self, query: str, chat_history: List, prompt: str) -> Union[str,Dict]:
        try:
            # First response to route the query
            response = await self.client.get_non_stream_response(
                model=models.TOOL_USE_MODEL,
                query=query,
                chat_history=chat_history,
                system_message=prompt,
                tools=self.tools,
            )

            # Process tool calls
            tool_calls = response.tool_calls
            chat_history.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                            "type": tool_call.type,
                        }
                        for tool_call in tool_calls
                    ],
                }
            )

            # Execute tool functions and append responses to chat history
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.available_functions.get(function_name)
                if not function_to_call:
                    raise ValueError(f"Function '{function_name}' is not available.")
                function_args = json.loads(tool_call.function.arguments)
                function_response = await function_to_call(**function_args)
                chat_history.append(
                    {
                        "role": "tool",
                        "content": json.dumps(function_response),
                        "tool_call_id": tool_call.id,
                    }
                )

            print(json.dumps(chat_history, indent=2))

            # Final response after tool execution
            response = await self.client.get_non_stream_response(
                model=models.TOOL_USE_MODEL,
                query=query,
                chat_history=chat_history,
                system_message=prompt,
                tools=self.tools,
            )
            print(response.content)

            return response.content

        except Exception as e:
            error_details = exception.custom_exception() 
            print(f"Error: {error_details}")
            return {"error": str(e)}

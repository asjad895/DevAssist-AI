import redis
import json
from typing import List,Dict

class ChatManager:
    def __init__(self, redis_url: str):
        self.client = redis.Redis.from_url(redis_url)

    def add_message(self, session_id: str, message: Dict[str, str]):
        chat_history = self.get_chat_history(session_id)
        chat_history.append(message)
        self.client.set(session_id, json.dumps(chat_history))

    def get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        data = self.client.get(session_id)
        return json.loads(data) if data else []

chat_manager = ChatManager(redis_url="redis://localhost:6379")


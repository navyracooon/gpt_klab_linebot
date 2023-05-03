import os

import openai
from dotenv import load_dotenv


load_dotenv(".env")
CHATGPT_API = os.environ.get("CHATGPT_API")
CHATGPT_CHARACTER_PROFILE = os.environ.get("CHATGPT_CHARACTER_PROFILE")
openai.api_key = CHATGPT_API


class ChatGPTHandler:
    def __init__(self):
        self.message_history = []
        self.chatgpt_settings = [
                {
                    "role": "system",
                    "content": CHATGPT_CHARACTER_PROFILE,
                }
            ]

    def get_pure_content(self, content: str) -> openai.openai_object.OpenAIObject:
        user_message = [
                {
                    "role": "user",
                    "content": content,
                }
            ]
        messages = self.chatgpt_settings + self.message_history + user_message

        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        self.manage_message_history(user_message, res)

        return res

    def get_content_and_parse(self, content: str) -> str:
        res = self.get_pure_content(content)
        message_obj = res.get("choices")[0].get("message")
        content = message_obj.get("content")
        return content

    def manage_message_history(self, messages: list, response: openai.openai_object.OpenAIObject) -> None:
        res_content = response.get("choices")[0].get("message").get("content")
        res_message = [
                {
                    "role": "system",
                    "content": res_content,
                }
            ]
        messages = messages + res_message
        if len(self.message_history) == 0 or len(self.message_history) == 2:
            self.message_history += messages
        elif len(self.message_history) == 4:
            del self.message_history[0]
            del self.message_history[1]
            self.message_history += messages
        else:
            raise RuntimeError(f"Length of message_history is invalid. {self.message_history}")

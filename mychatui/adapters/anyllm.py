"""
Utility class to transform aisuite messages to mychatui chat_history representation.
"""
import os
import pprint

from mychatui.adapters.beanutils import getBeanValue

from any_llm import completion

class AnyLlmAdapter:
    def __init__(self):
        pass

    def getChatHistory(self, tab_chat_history):
        return tab_chat_history

    def getResponse(self, response):
        """
        Transform any_llm completion to mychatui chat_history representation.
        """
        return { "role": "assistant", "content": response.choices[0].message.content }

    def completion(self, model, messages, base_url=None):
        """
        Transform any_llm completion to mychatui chat_history representation.
        """

        base_url = None
        if "openai" in model:
            base_url = os.getenv("OPENAI_API_URL")

        response = completion(model=model, messages=messages, api_base=base_url)

        if response is not None:
            response = self.getResponse(response)

        return response


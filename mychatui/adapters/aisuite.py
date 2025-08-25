"""
Utility class to transform aisuite messages to mychatui chat_history representation.
"""

import pprint
from mychatui.adapters.beanutils import getBeanValue

from aisuite.framework.chat_completion_response import ChatCompletionResponse

class AiSuiteAdapter:
    def __init__(self):
        pass

    def getChatHistory(self, tab_chat_history):
        return tab_chat_history

    def getResponse(self, response):
        if isinstance(response, ChatCompletionResponse):
            return self.getResponseFromChatCompletionResponse(response)
        else:
            return self.getResponseFromOpenAiResponse(response)

    def getResponseFromOpenAiResponse(self, response):
        print(f"getResponse: {response.__class__}")
        response_dict = response.to_dict()
        choice = response_dict.get("choices", [])[0]
        content = getBeanValue(choice, "message.content")
        role = getBeanValue(choice, "message.role")
        print(f"getResponse:role: {role}, content: {content}")
        return {
            "role": role,
            "content": content,
        }

    def getResponseFromChatCompletionResponse(self, response):
        """aisuite returns it's own ChatCompletionResponse object when the response isn't returned by openai endpoint"""

        choice = response.choices[0]
        response_text = choice.message.content
        role = choice.message.role
        
        return {
            "role": role,
            "content": response_text,
        }


    def completion(self, model, messages, base_url=None):
        client = ai.Client()

        base_url = None
        if "openai" in model:
            base_url = os.getenv("OPENAI_API_URL")

        response = None
        if base_url is not None:
            response = client.chat.completions.create(
                model=model, messages=messages, base_url=base_url
            )
        else:
            response = client.chat.completions.create(
                model=model, messages=messages
                )

        if response is not None:
            response = self.aisuite_adapter.getResponse(response)

        return response

        
        

#!/usr/bin/env python

import os
import any_llm

gemini_models = any_llm.list_models(provider="google")

print(f"gemini models: {gemini_models}")


q1 = "Explain the impact of Federal Department of Education Policy impact on local American schools."
q2 = "Why is the sky blue"

# Define a conversation with a system message and a user message
messages = [
    {"role": "system", "content": "You are a helpful agent, who answers with brevity."},
    {"role": "user", "content": q2},
]

models = ["google:models/gemini-2.0-flash-exp"]

models = [
    "google:models/gemini-2.0-flash-exp",
    "ollama:qwen2.5:latest",
    "ollama:llama3.2:1b",
    "ollama:gemma3:latest",
    "openai:jarvis:latest"
    #"openai:mistralai/mistral-small-3.1-24b-instruct:free",
    # "ollama:llama3:8b-instruct-q8_0",
    # "ollama:llama3.1:latest",
    # "googlegenai:models/gemini-1.5-flash"
]


# TODO: jarvis responded in a way that aisuite could utilize however anyllm can not. I need to revise the 
#       jarvis openaiapi.py proxy to return a better response.

# Request a response from the model
for model in models:
    print(f"= {model} says ... =")
    base_url = None
    if "openai" in model:
        base_url = os.getenv("OPENAI_API_URL")
    response = None
    if base_url is not None:
        response = any_llm.completion( 
            model=model,
            messages=messages,
            api_base=base_url
        )
    else:
        response = any_llm.completion(model=model, messages=messages)
    # Print the model's response
    print(response)
    print(response.choices[0].message.content)
    #import json

    #print(json.dumps(response, indent=2))
    print("")

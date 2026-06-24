from openai import AuthenticationError as OpenAIAuthenticationError, APIConnectionError as OpenAIAPIConnectionError
from anthropic import AuthenticationError as AnthropicAuthenticationError, APIConnectionError as AnthropicAPIConnectionError
from config import prompt, provider
from chat_session import ChatSession


authentication_errors = (OpenAIAuthenticationError, AnthropicAuthenticationError)
connection_errors = (OpenAIAPIConnectionError, AnthropicAPIConnectionError)

if __name__ == "__main__":
    if len(prompt) == 0:
        newSession = ChatSession()
    else:
        newSession = ChatSession(prompt=prompt)

    try:
        if provider.lower() != "anthropic":
            newResponse = newSession.start()
            print(">>" + newResponse.choices[0].message.content)
        while True:
            print(">>", end="")
            newResponse = newSession.send(input())
            print(">>" + newResponse.choices[0].message.content)
    except authentication_errors:
        print("Authentication Error, please check api-key")
    except connection_errors:
        print("Network Connection error")

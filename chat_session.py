import config
import os
from openai import OpenAI
from anthropic import Anthropic
from datetime import datetime
from types import SimpleNamespace


SUPPORTED_PROVIDERS = {"openai", "anthropic"}


class CompatibleChatResponse:
    """Small adapter so Anthropic responses can be read like OpenAI chat responses."""

    def __init__(self, raw_response, content):
        self.raw_response = raw_response
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]

    def __getattr__(self, name):
        return getattr(self.raw_response, name)


class ChatSession:

    def __init__(self, prompt=None) -> None:
        if prompt is None:
            self.__prompt = "You are a helpful assistant."
        else:
            self.__prompt = prompt
        self.__chat_history = []
        self.__model = config.ModelSection
        self.__provider = config.provider.lower()
        if self.__provider not in SUPPORTED_PROVIDERS:
            supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
            raise ValueError(f"Unsupported provider '{config.provider}'. Supported providers: {supported}")
        self.client = self.__createClient()

    def __createClient(self):
        kwargs = {"api_key": config.api_key}
        if config.endpoint:
            kwargs["base_url"] = self.__normalizeEndpoint(config.endpoint)

        if self.__provider == "openai":
            return OpenAI(**kwargs)

        elif self.__provider == "anthropic":
            return Anthropic(**kwargs)

    def __normalizeEndpoint(self, endpoint):
        endpoint = endpoint.rstrip("/")
        provider_api_paths = {
            "anthropic": "/v1/messages",
            "openai": "/chat/completions",
        }
        api_path = provider_api_paths[self.__provider]
        if endpoint.endswith(api_path):
            return endpoint[:-len(api_path)]
        return endpoint

    def __insertSystemPrompt(self):
        if self.__chat_history and self.__chat_history[0].get("role") == "system":
            self.__chat_history[0]["content"] = self.__prompt
            return
        self.__chat_history.insert(0, {"role": "system", "content": self.__prompt})

    def __generateResponse(self, temp_history):
        if self.__provider == "anthropic":
            return self.__generateAnthropicResponse(temp_history=temp_history)
        elif self.__provider == "openai":
            return self.__generateOpenAIResponse(temp_history=temp_history)

    def __generateOpenAIResponse(self, temp_history):
        params = self.__cleanParams({
            "temperature": config.Temperature,
            "top_p": config.Top_p,
            "stop": config.Stop_sequences,
            "max_tokens": config.Max_tokens,
            "presence_penalty": config.Presence_penalty,
            "frequency_penalty": config.Frequency_penalty,
        })
        response = self.client.chat.completions.create(
            model=self.__model,
            messages=temp_history,
            **params,
        )
        return response

    def __generateAnthropicResponse(self, temp_history):
        params = self.__cleanParams({
            "temperature": config.Temperature,
            "top_p": config.Top_p,
            "stop_sequences": config.Stop_sequences,
            "max_tokens": config.Max_tokens or config.anthropic_default_max_tokens,
        })
        response = self.client.messages.create(
            model=self.__model,
            system=self.__prompt,
            messages=self.__anthropicMessages(temp_history),
            **params,
        )
        return CompatibleChatResponse(response, self.__extractAnthropicText(response))

    def __cleanParams(self, params):
        # Remove any parameters that are disabled, None, or empty lists
        disabled_parameters = set(config.disabled_parameters)
        return {
            name: value
            for name, value in params.items()
            if name not in disabled_parameters and value is not None and value != []
        }

    def __anthropicMessages(self, temp_history):
        return [
            {"role": message["role"], "content": message["content"]}
            for message in temp_history
            if message["role"] in {"user", "assistant"}
        ]

    def __extractAnthropicText(self, response):
        if isinstance(response.content, str):
            return response.content

        texts = []
        for block in response.content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
            elif getattr(block, "type", None) == "text":
                texts.append(getattr(block, "text", ""))
        return "".join(texts)

    def start(self, message=None):  # send the prompt and receive the response, user input is optional
        self.__insertSystemPrompt()
        temp_history = self.__chat_history
        if message is not None:
            temp_history.append({"role": "user", "content": message})
        response = self.__generateResponse(temp_history=temp_history)
        temp_history.append({"role": "assistant", "content": response.choices[0].message.content})
        self.__chat_history = temp_history
        return response

    def send(self, message):  # send the message from user and receive the response
        self.__insertSystemPrompt()
        temp_history = self.__chat_history
        temp_history.append({"role": "user", "content": message})
        response = self.__generateResponse(temp_history=temp_history)
        temp_history.append({"role": "assistant", "content": response.choices[0].message.content})
        self.__chat_history = temp_history
        return response

    def clear_history(self):
        self.__chat_history.clear()

    def addToHistory(self, dict):  # add a piece of message into the history
        self.__chat_history.append(dict)

    def saveConversation(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(config.log_save_directory, exist_ok=True)
        fileName = os.path.join(config.log_save_directory, f"conversation_{timestamp}.txt")

        with open(fileName, "w") as file:
            for line in self.__chat_history:
                dict_string = ",".join([f"{key}: {value}" for key, value in line.items()])
                file.write(f"{dict_string}\n")

        return fileName

    def getHistory(self):
        return self.__chat_history

    def setHistory(self, list):
        self.__chat_history = list

provider = "openai"  # openai or anthropic
ModelSection = "gpt-5.5"
prompt = "You are a helpful assistant."

api_key = "sk-xxxx"  # !!!!!!! DO NOT PUSH ANY REAL KEY HERE ON GIT !!!!!!!
endpoint = None  # base URL only; do not include "/v1/messages" or "/chat/completions"

# Optional model parameters. Set a value to override the provider default.
# Leave as None, or add the parameter name to disabled_parameters, to skip it.
Temperature = None
Top_p = None
Stop_sequences = []
Max_tokens = None
Presence_penalty = None
Frequency_penalty = None
disabled_parameters = []

# Anthropic Messages API requires max_tokens. This is used when Max_tokens is None.
anthropic_default_max_tokens = 1024

sensitiveWordList = ["GPT", "ChatGPT", "OpenAI", "模型", "gpt", "chat", "chatgpt"]  # 敏感词设定

log_save_directory = "./logs"  # format: /path/to/save

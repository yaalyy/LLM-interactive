import sys
import config


TEST_PROMPT = "Reply with OK only."
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def _green(text):
    return f"{GREEN}{text}{RESET}"


def _red(text):
    return f"{RED}{text}{RESET}"


def _mask_value(value):
    if not value:
        return "<empty>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _classify_error(error):
    name = type(error).__name__
    message = str(error).strip() or name

    if name in {"AuthenticationError", "PermissionDeniedError"}:
        return 1, "Authentication failed. Please check api_key.", message
    if name in {"APIConnectionError", "APITimeoutError", "Timeout"}:
        return 1, "Network connection failed. Please check endpoint or network.", message
    if name in {"RateLimitError"}:
        return 2, "API is reachable, but the request was rate-limited or quota-limited.", message
    if name in {"BadRequestError", "NotFoundError", "UnprocessableEntityError"}:
        return 2, "API is reachable, but provider/model/parameter configuration failed.", message
    if name in {"APIStatusError", "APIError", "InternalServerError"}:
        return 2, "API returned an error status.", message
    return 3, "Unexpected error while checking API connectivity.", message


def main():
    provider = config.provider.lower()
    endpoint = config.endpoint or "provider default"
    print("Checking API connectivity...")
    print(f"Provider: {provider}")
    print(f"Model: {config.ModelSection}")
    print(f"Endpoint: {endpoint}")
    print(f"API key: {_mask_value(config.api_key)}")

    if not config.api_key or config.api_key == "sk-xxxx":
        print(_red("❌ API key looks empty or unchanged from the placeholder in config.py."))
        return 2

    try:
        from chat_session import ChatSession
    except ImportError as error:
        print(_red("❌ Dependency import failed. Run: pip install -r requirements.txt"))
        print(f"Detail: {error}")
        return 3

    try:
        if provider == "anthropic" and config.Max_tokens is None:
            config.Max_tokens = 16

        session = ChatSession(prompt="You are an API connectivity checker.")
        response = session.start(TEST_PROMPT)
        content = response.choices[0].message.content.strip()
    except ValueError as error:
        print(_red(f"❌ Configuration error: {error}"))
        return 2
    except Exception as error:
        exit_code, summary, detail = _classify_error(error)
        print(_red(f"❌ {summary}"))
        print(f"Detail: {detail}")
        return exit_code

    print(_green("✅ OK - API connectivity check succeeded."))
    if content:
        print(f"Response preview: {content[:120]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

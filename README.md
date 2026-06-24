# LLM-interactive
## Install Dependency
You need to install the official SDKs for the providers you use.  
**Run `pip install -r requirements.txt` in cmd to install dependencies**

## Use
Modify **provider**, **model**, **api-key**, **endpoint** and **prompt** before running at [config.py](./config.py "config.py").  
Other parameters are optional. Set unsupported model parameters to `None`, or add their parameter names to `disabled_parameters`, to avoid sending them.

Provider examples:

```python
provider = "openai"
ModelSection = "your-openai-model"
endpoint = None
```

```python
provider = "anthropic"
ModelSection = "your-claude-model"
endpoint = None
```

## CMD Demo
**Run `python main.py`**  

## API Connectivity Check
After setting `provider`, `ModelSection`, `api_key`, and `endpoint` in [config.py](./config.py "config.py"), run:

```bash
./run_check_api.sh
```

Or run the Python file directly:

```bash
python3 check_api.py
```


  

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

# List available models
models = genai.list_models()
for model in models:
    print(model.name)

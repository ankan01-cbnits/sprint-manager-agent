import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY_2")

def llm(temperature :float):
    llm_model = ChatOpenAI(
        model = "llama-3.1-8b-instant",
        temperature = temperature,
        api_key = api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    return llm_model
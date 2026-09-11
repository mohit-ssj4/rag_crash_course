from dotenv import load_dotenv
from groq import Groq

from src.config import LLM_MODEL_NAME

load_dotenv(".env")

groq_client: Groq = Groq()

model_name: str = LLM_MODEL_NAME

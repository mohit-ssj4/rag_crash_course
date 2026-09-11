from dotenv import load_dotenv
from groq import Groq

load_dotenv(".env")

groq_client = Groq()

model_name = "openai/gpt-oss-120b"

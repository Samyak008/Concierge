import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not supabase_url or not supabase_key or not groq_api_key or not openai_api_key:
    raise ValueError("Missing Supabase, Groq, or OpenAI credentials in .env file")

supabase: Client = create_client(supabase_url, supabase_key)
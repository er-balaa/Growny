import os
import pathlib
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq

env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Supabase Initialization
supabase = None
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("[OK] Supabase initialized")
    except Exception as e:
        print(f"[ERROR] Supabase initialization error: {e}")
else:
    print("[WARN] Supabase URL or KEY not set - database will be unavailable")

# Groq Initialization
groq_client = None
groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    try:
        groq_client = Groq(api_key=groq_key)
        print("[OK] Groq initialized")
    except Exception as e:
        print(f"[ERROR] Groq initialization error: {e}")
else:
    print("[WARN] GROQ_API_KEY not set")

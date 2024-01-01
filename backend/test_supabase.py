from supabase import create_client
import os

# Load environment variables
import pathlib
env_path = pathlib.Path(__file__).parent / '.env'
from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path)

# Initialize Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
print(f"Supabase Key present: {bool(os.getenv('SUPABASE_KEY'))}")

# Test connection by trying to read from tasks table
try:
    print("Testing Supabase connection...")
    result = supabase.table("tasks").select("count").execute()
    print(f"Connection test successful: {result.data}")
except Exception as e:
    print(f"Supabase connection error: {e}")

# Test insertion with sample data
try:
    print("Testing task insertion...")
    sample_vector = [0.1] * 768  # Sample 768-dim vector
    payload = {
        "content": "Test task",
        "raw_text": "Test task raw",
        "category": "TASK",
        "priority": "MEDIUM",
        "due_date": None,
        "embedding": sample_vector,
        "user_id": "test-user-id"
    }
    
    result = supabase.table("tasks").insert(payload).execute()
    print(f"Insertion successful: {result.data}")
except Exception as e:
    print(f"Insertion error: {e}")
    import traceback
    traceback.print_exc()

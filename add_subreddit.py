import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from app.db.supabase_client import get_supabase_client

db = get_supabase_client()

project_id = 17

# Insert r/SaaS into monitored_subreddits
subreddit_data = {
    "project_id": project_id,
    "name": "SaaS",
    "is_active": True,
}

try:
    db.table("monitored_subreddits").insert(subreddit_data).execute()
    print(f"Successfully added r/SaaS to project {project_id}.")
except Exception as e:
    # If it already exists, just ignore
    print(f"Failed to add subreddit (might already exist): {e}")

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from app.db.supabase_client import get_supabase_client

db = get_supabase_client()

# 1. Delete all fake opportunities
print("Cleaning up fake opportunities...")
try:
    result = db.table("opportunities").select("id, title, project_id").execute()
    if result.data:
        for opp in result.data:
            print(f"  Deleting opportunity ID={opp['id']}: {opp.get('title', 'N/A')}")
        db.table("opportunities").delete().neq("id", 0).execute()
        print(f"  Deleted {len(result.data)} opportunities.")
    else:
        print("  No opportunities found.")
except Exception as e:
    print(f"  Error: {e}")

# 2. Delete fake monitored subreddits (the ones we manually inserted)
print("\nCleaning up manually-added subreddits...")
try:
    result = db.table("monitored_subreddits").select("id, name, project_id").execute()
    if result.data:
        for sub in result.data:
            print(f"  Deleting subreddit ID={sub['id']}: r/{sub.get('name', 'N/A')} (project {sub.get('project_id')})")
        db.table("monitored_subreddits").delete().neq("id", 0).execute()
        print(f"  Deleted {len(result.data)} subreddits.")
    else:
        print("  No subreddits found.")
except Exception as e:
    print(f"  Error: {e}")

# 3. Delete fake reply drafts
print("\nCleaning up reply drafts...")
try:
    result = db.table("reply_drafts").select("id").execute()
    if result.data:
        db.table("reply_drafts").delete().neq("id", 0).execute()
        print(f"  Deleted {len(result.data)} reply drafts.")
    else:
        print("  No reply drafts found.")
except Exception as e:
    print(f"  Error: {e}")

# 4. Delete auto pipeline records
print("\nCleaning up auto pipeline records...")
try:
    result = db.table("auto_pipelines").select("id").execute()
    if result.data:
        db.table("auto_pipelines").delete().neq("id", 0).execute()
        print(f"  Deleted {len(result.data)} auto pipeline records.")
    else:
        print("  No auto pipeline records found.")
except Exception as e:
    print(f"  Error: {e}")

# 5. Delete scan runs
print("\nCleaning up scan runs...")
try:
    result = db.table("scan_runs").select("id").execute()
    if result.data:
        db.table("scan_runs").delete().neq("id", 0).execute()
        print(f"  Deleted {len(result.data)} scan runs.")
    else:
        print("  No scan runs found.")
except Exception as e:
    print(f"  Error: {e}")

print("\n✅ All test data cleaned up! The database is now fresh for 360ghar.")

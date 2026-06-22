"""Quick check: do the key tables now have the columns the code needs?"""
import os, sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

db = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])

checks = {
    "projects": ["status"],
    "personas_v1": ["is_active", "source", "preferred_subreddits"],
    "discovery_keywords": ["is_active", "source", "priority_score", "rationale"],
}

all_ok = True
for table, required_cols in checks.items():
    # Insert a dummy row to probe columns, or just select
    try:
        result = db.table(table).select(",".join(required_cols)).limit(1).execute()
        print(f"OK: {table}: columns {required_cols} exist")
    except Exception as e:
        print(f"FAIL: {table}: {e}")
        all_ok = False

if all_ok:
    print("\nAll required columns exist! Migration was successful.")
else:
    print("\nSome columns are still missing. Please run the migration SQL.")

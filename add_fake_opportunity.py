import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from app.db.supabase_client import get_supabase_client

db = get_supabase_client()
project_id = 17

# Insert a fake opportunity
opp_data = {
    "project_id": project_id,
    "reddit_post_id": "test_post_12345",
    "subreddit_name": "SaaS",
    "author": "SaaSFounder99",
    "title": "Struggling to find leads for my new eCommerce tool",
    "permalink": "https://reddit.com/r/SaaS/comments/test_post_12345/",
    "score": 95,
    "body_excerpt": "I built a new tool to help eCommerce store owners get more leads. Does anyone know how I can find people who need this?",
    "score_reasons": ["High intent to find leads", "Relevant to eCommerce"],
    "keyword_hits": ["leads", "eCommerce"],
    "rule_risk": [],
    "reason_relevant": "User is actively looking for leads for an eCommerce tool, highly relevant to our product.",
    "risk_flags": [],
    "status": "new",
    "created_at": datetime.now(timezone.utc).isoformat()
}

try:
    print("Inserting fake opportunity...")
    result = db.table("opportunities").insert(opp_data).execute()
    opp_id = result.data[0]["id"]
    print(f"Success! Inserted opportunity ID {opp_id}.")
except Exception as e:
    print(f"Failed to insert opportunity: {e}")

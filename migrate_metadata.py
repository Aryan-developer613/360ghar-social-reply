import os
import sys
import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SECRET_KEY"]
project_ref = url.replace("https://", "").split(".")[0]

statements = [
    "ALTER TABLE public.reply_drafts ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb",
    "NOTIFY pgrst, 'reload schema'",
]

print(f"Executing SQL statements against Supabase ({project_ref})...")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

for i, stmt in enumerate(statements):
    try:
        resp = httpx.post(
            f"{url}/rest/v1/rpc/",
            headers=headers,
            json={"query": stmt},
            timeout=30,
        )
        if resp.status_code < 300:
            print(f"  [{i+1:02d}] OK: {stmt}")
        else:
            raise Exception("REST failed")
    except:
        try:
            resp2 = httpx.post(
                f"https://{project_ref}.supabase.co/pg/query",
                headers=headers,
                json={"query": stmt + ";"},
                timeout=30,
            )
            if resp2.status_code < 300:
                print(f"  [{i+1:02d}] OK (pg): {stmt}")
            else:
                print(f"  [{i+1:02d}] FAIL: {stmt} ({resp2.status_code})")
        except Exception as e:
            print(f"  [{i+1:02d}] ERROR: {stmt} ({e})")

print("\nFinished.")

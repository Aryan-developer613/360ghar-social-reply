"""
Run migration SQL against Supabase using the pg-meta API (available on all Supabase projects).
"""
import os
import sys
import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SECRET_KEY"]
project_ref = url.replace("https://", "").split(".")[0]

# Individual ALTER TABLE statements to execute
statements = [
    # 1. projects: add missing 'status' column
    "ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active'",
    "UPDATE public.projects SET status = CASE WHEN is_active = true THEN 'active' ELSE 'archived' END WHERE status IS NULL",

    # 2. personas_v1: add missing columns
    "ALTER TABLE public.personas_v1 ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
    "ALTER TABLE public.personas_v1 ADD COLUMN IF NOT EXISTS source TEXT",
    "ALTER TABLE public.personas_v1 ADD COLUMN IF NOT EXISTS preferred_subreddits JSONB DEFAULT '[]'",

    # 3. opportunities: ensure all columns exist
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS platform TEXT DEFAULT 'reddit'",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS agent_name TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS body TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS body_excerpt TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS author TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS post_created_at TIMESTAMPTZ",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS fetched_at TIMESTAMPTZ DEFAULT NOW()",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS upvotes INTEGER DEFAULT 0",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS comments_count INTEGER DEFAULT 0",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS engagement_score REAL DEFAULT 0",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS semantic_similarity REAL",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS intent TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS opportunity_type TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS matched_keywords JSONB DEFAULT '[]'",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS risk_flags JSONB DEFAULT '[]'",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS reason_relevant TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS rejection_reason TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS draft_reply TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS draft_post TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS draft_article TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS buying_stage TEXT",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS intent_confidence REAL",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS scoring_breakdown JSONB DEFAULT '{}'::jsonb",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS score_reasons JSONB DEFAULT '[]'::jsonb",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS keyword_hits JSONB DEFAULT '[]'::jsonb",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS rule_risk JSONB DEFAULT '[]'::jsonb",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS scan_run_id INTEGER",
    "ALTER TABLE public.opportunities ADD COLUMN IF NOT EXISTS source_type TEXT DEFAULT 'post'",

    # 4. scan_runs: add missing columns
    "ALTER TABLE public.scan_runs ADD COLUMN IF NOT EXISTS opportunities_found INTEGER DEFAULT 0",
    "ALTER TABLE public.scan_runs ADD COLUMN IF NOT EXISTS subreddits_total INTEGER DEFAULT 0",
    "ALTER TABLE public.scan_runs ADD COLUMN IF NOT EXISTS subreddits_scanned INTEGER DEFAULT 0",

    # 5. reply_drafts: add missing columns
    "ALTER TABLE public.reply_drafts ADD COLUMN IF NOT EXISTS source_prompt TEXT",
    "ALTER TABLE public.reply_drafts ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1",
    "ALTER TABLE public.reply_drafts ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft'",

    # 6. prompt_templates: add is_default if missing
    "ALTER TABLE public.prompt_templates ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE",

    # 7. monitored_subreddits: ensure all columns
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS title TEXT",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS description TEXT",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS subscribers INTEGER DEFAULT 0",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS fit_score INTEGER DEFAULT 0",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS rules_summary TEXT",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS url TEXT",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS activity_score INTEGER DEFAULT 0",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
    "ALTER TABLE public.monitored_subreddits ADD COLUMN IF NOT EXISTS tone_rules TEXT",

    # 8. discovery_keywords: ensure all columns
    "ALTER TABLE public.discovery_keywords ADD COLUMN IF NOT EXISTS rationale TEXT",
    "ALTER TABLE public.discovery_keywords ADD COLUMN IF NOT EXISTS priority_score INTEGER DEFAULT 50",
    "ALTER TABLE public.discovery_keywords ADD COLUMN IF NOT EXISTS source TEXT",
    "ALTER TABLE public.discovery_keywords ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",

    # 9. company_profiles: ensure all columns
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS category TEXT",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS target_audience TEXT",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS geography TEXT",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'en'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS benefits JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS pain_points JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS competitors JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS brand_voice TEXT",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS forbidden_claims JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS preferred_cta TEXT",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS extracted_summary TEXT",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS extracted_keywords JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS extracted_pain_points JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS extracted_competitors JSONB DEFAULT '[]'",
    "ALTER TABLE public.company_profiles ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",

    # Refresh PostgREST schema cache
    "NOTIFY pgrst, 'reload schema'",
]

print(f"Executing {len(statements)} SQL statements against Supabase ({project_ref})...")
print()

# Use the Supabase pg-meta SQL query endpoint
# POST /pg/query with the service_role key
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

success = 0
errors = 0

for i, stmt in enumerate(statements):
    try:
        # Try Supabase's internal SQL execution endpoint
        resp = httpx.post(
            f"{url}/rest/v1/rpc/",
            headers=headers,
            json={"query": stmt},
            timeout=30,
        )
        
        if resp.status_code < 300:
            success += 1
            label = stmt[:70].replace("\n", " ")
            print(f"  [{i+1:02d}] OK: {label}...")
        else:
            # Try alternative: use the pg endpoint  
            raise Exception(f"REST failed: {resp.status_code}")
    except Exception:
        # Try the Supabase SQL endpoint via pg-meta
        try:
            resp2 = httpx.post(
                f"https://{project_ref}.supabase.co/pg/query",
                headers=headers,
                json={"query": stmt + ";"},
                timeout=30,
            )
            if resp2.status_code < 300:
                success += 1
                label = stmt[:70].replace("\n", " ")
                print(f"  [{i+1:02d}] OK (pg): {label}...")
            else:
                errors += 1
                label = stmt[:70].replace("\n", " ")
                print(f"  [{i+1:02d}] FAIL: {label}... ({resp2.status_code}: {resp2.text[:100]})")
        except Exception as ex2:
            errors += 1
            label = stmt[:70].replace("\n", " ")
            print(f"  [{i+1:02d}] ERROR: {label}... ({ex2})")

print(f"\nResults: {success} succeeded, {errors} failed out of {len(statements)} total")

if errors > 0:
    print("\n" + "=" * 80)
    print("Some statements failed. Please run the full migration SQL manually:")
    print(f"https://supabase.com/dashboard/project/{project_ref}/sql/new")
    print("=" * 80)
    full_sql = ";\n".join(statements) + ";"
    print(full_sql)

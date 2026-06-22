-- ============================================================================
-- Make reddit_post_id and subreddit nullable in opportunities table
-- ============================================================================
-- Date:     2026-06-07
-- Concern:  Non-Reddit agents (ugc, technical_seo, seo, geo, articles, etc.)
--           create opportunities without reddit_post_id or subreddit. The
--           original schema had NOT NULL constraints that prevent these inserts.
-- Safety:   Idempotent. Checks information_schema before altering.
-- ============================================================================

DO $$
BEGIN
    -- Drop NOT NULL on reddit_post_id
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'opportunities'
        AND column_name = 'reddit_post_id'
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE opportunities ALTER COLUMN reddit_post_id DROP NOT NULL;
    END IF;

    -- Drop NOT NULL on subreddit (original column)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'opportunities'
        AND column_name = 'subreddit'
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE opportunities ALTER COLUMN subreddit DROP NOT NULL;
    END IF;

    -- Drop NOT NULL on subreddit_name (added by multi-agent migration)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'opportunities'
        AND column_name = 'subreddit_name'
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE opportunities ALTER COLUMN subreddit_name DROP NOT NULL;
    END IF;
END $$;

NOTIFY pgrst, 'reload schema';

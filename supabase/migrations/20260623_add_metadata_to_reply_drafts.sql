ALTER TABLE reply_drafts
ADD COLUMN citations JSONB DEFAULT '[]'::jsonb,
ADD COLUMN automation_eligibility BOOLEAN DEFAULT false;

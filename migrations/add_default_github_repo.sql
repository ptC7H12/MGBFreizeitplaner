-- Migration: Add default_github_repo to settings table
-- Date: 2025-01-14
-- Description: Add column for storing default GitHub repository URL for ruleset imports

-- Add new column to settings table with default value
ALTER TABLE settings ADD COLUMN default_github_repo VARCHAR(500) DEFAULT 'https://github.com/ptC7H12/MGBFreizeitplaner/tree/main/rulesets/valid/';

-- Update existing rows to have the default value
UPDATE settings SET default_github_repo = 'https://github.com/ptC7H12/MGBFreizeitplaner/tree/main/rulesets/valid/' WHERE default_github_repo IS NULL;

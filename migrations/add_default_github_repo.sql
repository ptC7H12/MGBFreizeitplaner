-- Migration: Add default_github_repo to settings table
-- Date: 2025-01-14
-- Description: Add column for storing default GitHub repository URL for ruleset imports

-- Add new column to settings table
ALTER TABLE settings ADD COLUMN default_github_repo VARCHAR(500) DEFAULT NULL;

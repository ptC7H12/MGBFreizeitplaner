-- Fix: Update existing settings to have default_github_repo value
-- Date: 2025-01-18
-- Description: Sets default GitHub repository URL for existing settings that have NULL

-- Update existing rows to have the default value
UPDATE settings
SET default_github_repo = 'https://github.com/ptC7H12/MGBFreizeitplaner/tree/main/rulesets/valid/'
WHERE default_github_repo IS NULL OR default_github_repo = '';

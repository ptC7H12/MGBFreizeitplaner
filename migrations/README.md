# Database Migrations

## Remove is_reimbursed Column

**Date:** 2025-01-14
**Type:** Breaking Change
**Status:** Required for proper functionality after commit 727008c

### What Changed

The expense model has been simplified:
- **Removed:** `is_reimbursed` column from expenses table
- **Kept:** `is_settled` column for all expense settlements
- **Logic:**
  - `is_settled = True` + `paid_by` is empty → "Beglichen" (paid from cash box)
  - `is_settled = True` + `paid_by` is set → "Erstattet" (reimbursed to person)

### Why This Change

The previous model with two separate boolean fields (`is_settled` and `is_reimbursed`) was confusing:
- When reimbursing someone, both fields needed to be set
- It was unclear what the difference was
- UI had two separate columns that were redundant

The new model is simpler and clearer:
- One field (`is_settled`) for all cases
- Display text changes based on context (paid_by field)
- Easier to understand and maintain

### How to Run Migration

**Important:** The migration creates an automatic backup of your database before making changes.

#### Option 1: Python Script (Recommended)

```bash
python migrations/run_migration.py
```

This will:
1. Check if migration is needed
2. Create a backup at `<database>.backup`
3. Execute the migration
4. Confirm success

#### Option 2: Manual SQL

If you prefer to run the SQL manually:

```bash
sqlite3 data/freizeit.db < migrations/remove_is_reimbursed.sql
```

**Note:** Make sure to create a backup first!

```bash
cp data/freizeit.db data/freizeit.db.backup
```

### Data Migration Logic

The migration preserves all data:
- If `is_reimbursed` was `true`, the new `is_settled` will be `true`
- If `is_reimbursed` was `false`, the existing `is_settled` value is preserved
- All other fields remain unchanged

### Rollback

If you need to rollback:

```bash
mv data/freizeit.db.backup data/freizeit.db
```

Then checkout the previous commit:

```bash
git checkout a1f275f
```

### Verification

After migration, verify:

1. All expenses are visible in `/expenses`
2. Status shows correctly:
   - Regular expenses: "Beglichen" or "Offen"
   - Reimbursements: "Erstattet" or "Offen"
3. Tasks for reimbursements sync correctly

### Questions?

If you encounter any issues, check:
- Database file path in `app/config.py`
- Backup file exists before running migration
- Python version is 3.8+ for migration script

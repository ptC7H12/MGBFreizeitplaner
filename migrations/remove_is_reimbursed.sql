-- Migration: Remove is_reimbursed column from expenses table
-- Date: 2025-01-14
-- Description: Simplify expense model by using only is_settled with dynamic display

-- SQLite doesn't support DROP COLUMN directly (before 3.35.0)
-- We need to recreate the table

-- 1. Create new expenses table without is_reimbursed
CREATE TABLE expenses_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    amount FLOAT NOT NULL,
    expense_date DATE NOT NULL DEFAULT (date('now')),
    category VARCHAR(100),
    receipt_number VARCHAR(100),
    paid_by VARCHAR(200),
    is_settled BOOLEAN NOT NULL DEFAULT 0,
    notes TEXT,
    event_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (event_id) REFERENCES events (id)
);

-- 2. Copy data from old table to new table
INSERT INTO expenses_new (
    id, title, description, amount, expense_date, category,
    receipt_number, paid_by, is_settled, notes, event_id,
    created_at, updated_at
)
SELECT
    id, title, description, amount, expense_date, category,
    receipt_number, paid_by,
    -- If is_reimbursed was true, keep is_settled as true
    -- Otherwise use existing is_settled value
    CASE
        WHEN is_reimbursed = 1 THEN 1
        ELSE is_settled
    END as is_settled,
    notes, event_id, created_at, updated_at
FROM expenses;

-- 3. Drop old table
DROP TABLE expenses;

-- 4. Rename new table to original name
ALTER TABLE expenses_new RENAME TO expenses;

-- 5. Recreate indexes if any existed
CREATE INDEX IF NOT EXISTS idx_expenses_event_id ON expenses(event_id);
CREATE INDEX IF NOT EXISTS idx_expenses_expense_date ON expenses(expense_date);

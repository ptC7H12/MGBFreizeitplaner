-- Migration: Add receipt_file_path column to expenses and incomes tables
-- Date: 2025-11-15
-- Description: Enable receipt/invoice upload functionality for expenses and incomes

-- 1. Add receipt_file_path column to expenses table
ALTER TABLE expenses ADD COLUMN receipt_file_path VARCHAR(500);

-- 2. Add receipt_file_path column to incomes table
ALTER TABLE incomes ADD COLUMN receipt_file_path VARCHAR(500);

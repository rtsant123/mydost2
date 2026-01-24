-- Migration: Add authentication and subscription fields to users table
-- Run this in your Railway PostgreSQL database

-- Add new columns if they don't exist
ALTER TABLE users 
  ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
  ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free',
  ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'active',
  ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS razorpay_subscription_id VARCHAR(255),
  ADD COLUMN IF NOT EXISTS messages_lifetime INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS messages_today INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS daily_reset_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) DEFAULT 'google',
  ADD COLUMN IF NOT EXISTS referral_code VARCHAR(20),
  ADD COLUMN IF NOT EXISTS referred_by VARCHAR(20);

-- Make google_id nullable (for email/password users)
ALTER TABLE users ALTER COLUMN google_id DROP NOT NULL;

-- Create guest tracking table
CREATE TABLE IF NOT EXISTS guest_usage (
    id SERIAL PRIMARY KEY,
    fingerprint VARCHAR(64) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_guest_fingerprint ON guest_usage(fingerprint);
CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_referral ON users(referral_code);

-- Verify changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

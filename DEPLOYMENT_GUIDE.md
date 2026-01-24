# MyDost Authentication & Subscription Setup

## Overview
Complete authentication and subscription system with:
- Email/password + Google OAuth
- 4-tier subscription: Guest (3), Free (10), Limited (₹399), Unlimited (₹999)
- Razorpay payment integration
- Daily/lifetime message limits
- Referral tracking

## Backend Setup (Complete ✅)

### 1. Database Migration
Run these SQL statements in your Railway PostgreSQL:

```sql
-- Update users table
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
  ADD COLUMN IF NOT EXISTS referred_by VARCHAR(20),
  ALTER COLUMN google_id DROP NOT NULL;

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

CREATE INDEX IF NOT EXISTS idx_guest_fingerprint ON guest_usage(fingerprint);
```

### 2. Railway Environment Variables

Add these to your backend service in Railway:

```bash
# Authentication
JWT_SECRET=your-secure-random-string-here  # Generate with: openssl rand -hex 32

# Razorpay (Get from https://dashboard.razorpay.com/)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret_key_here
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here

# Feature Toggle (Keep false for testing)
ENABLE_FREE_LIMITS=false

# Keep all existing env vars (ANTHROPIC_API_KEY, etc.)
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New packages added:
- `bcrypt==4.1.2` - Password hashing
- `pyjwt==2.8.0` - JWT tokens
- `razorpay==1.4.1` - Payment integration

## Frontend Setup (Complete ✅)

### 1. Files Created/Modified

New pages:
- `frontend/pages/signup.js` - User registration with referral support
- `frontend/pages/signin.js` - User login

New components:
- `frontend/components/UpgradeModal.js` - Payment modal with Razorpay

Updated files:
- `frontend/pages/index.js` - Auth checking, subscription status, logout
- `frontend/utils/apiClient.js` - JWT token interceptors

### 2. Environment Variables

Already set in Railway:
```bash
NEXT_PUBLIC_API_URL=https://mydost2-production.up.railway.app
```

## Razorpay Setup (Required for Payments)

### 1. Create Razorpay Account
- Sign up at https://dashboard.razorpay.com/
- Use TEST mode for development

### 2. Create Subscription Plans

In Razorpay Dashboard → Subscriptions → Plans:

**Plan 1: Limited**
- Plan Name: `MyDost Limited`
- Plan ID: `plan_limited` (use this exact ID)
- Billing Cycle: Monthly
- Amount: ₹399
- Description: 50 messages per day

**Plan 2: Unlimited**
- Plan Name: `MyDost Unlimited`
- Plan ID: `plan_unlimited` (use this exact ID)
- Billing Cycle: Monthly
- Amount: ₹999
- Description: Unlimited messages

### 3. Update Backend Code

In `backend/routers/payment.py`, update plan IDs:

```python
PLAN_IDS = {
    "limited": "plan_xxxxxxxxxxxxxx",  # Replace with actual ID
    "unlimited": "plan_xxxxxxxxxxxxxx"  # Replace with actual ID
}
```

### 4. Setup Webhook (Optional but recommended)

In Razorpay Dashboard → Webhooks:
- Webhook URL: `https://mydost2-production.up.railway.app/api/webhook/razorpay`
- Events: Select `subscription.charged`, `subscription.cancelled`
- Secret: Copy to `RAZORPAY_WEBHOOK_SECRET` env var

## Testing Workflow

### 1. Test with Limits Disabled (Current State)

```bash
# Backend env var should be:
ENABLE_FREE_LIMITS=false
```

**Expected behavior:**
- Anyone can send unlimited messages
- Signup/signin works
- Subscription status shows in UI
- No payment prompts

**Test checklist:**
- ✅ Sign up with email/password
- ✅ Sign in
- ✅ Send messages (should be unlimited)
- ✅ Check subscription status in header
- ✅ Logout and sign in again
- ✅ Verify RAG/memory/search work

### 2. Test with Limits Enabled

```bash
# Change backend env var to:
ENABLE_FREE_LIMITS=true
```

**Expected behavior:**
- New users get 10 free messages
- After 10 messages → upgrade modal appears
- Guest users get 3 messages

**Test checklist:**
- ✅ Sign up new user
- ✅ Send 10 messages
- ✅ On 11th message → upgrade modal shows
- ✅ Guest (no login) → 3 messages only

### 3. Test Payment Flow (Razorpay Required)

**Setup:**
- Complete Razorpay setup above
- Use Razorpay test cards: https://razorpay.com/docs/payments/payments/test-card-details/

**Test checklist:**
- ✅ Trigger upgrade modal (hit message limit)
- ✅ Click "Upgrade to Limited Plan"
- ✅ Razorpay checkout opens
- ✅ Use test card: 4111 1111 1111 1111
- ✅ Payment succeeds
- ✅ Subscription activated
- ✅ Message limit increases to 50/day
- ✅ Next day → counter resets
- ✅ Test unlimited plan same way

## User Flow

### New User Journey

1. **Visit site** → Redirected to signup
2. **Sign up** → Email/password or Google OAuth
3. **Free tier activated** → 10 messages total
4. **Send 10 messages** → Upgrade modal appears
5. **Choose plan** → Razorpay checkout
6. **Payment success** → Tier upgraded
7. **Continue chatting** → With new limits

### Subscription Tiers

| Tier | Price | Messages | Limit Type |
|------|-------|----------|------------|
| Guest | Free | 3 | Lifetime (fingerprint tracked) |
| Free | Free | 10 | Lifetime |
| Limited | ₹399/mo | 50 | Daily (resets at midnight) |
| Unlimited | ₹999/mo | ∞ | None |

### Daily Reset Logic

For Limited plan:
- Counter resets 24 hours after last reset
- `daily_reset_at` timestamp tracks this
- Automatic on next message after 24h

## Referral System

### How it Works

1. **Every user gets a referral code** (8-char UUID)
2. **Share link:** `https://www.mydost.in/signup?ref=ABC12345`
3. **New signup with code** → `referred_by` field set
4. **Track in database** for future rewards

### Check Referrals (SQL)

```sql
-- Count referrals for a user
SELECT COUNT(*) FROM users WHERE referred_by = 'ABC12345';

-- Top referrers
SELECT referred_by, COUNT(*) as referrals 
FROM users 
WHERE referred_by IS NOT NULL 
GROUP BY referred_by 
ORDER BY referrals DESC;
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register with email/password
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user (requires Bearer token)
- `GET /api/auth/guest/check-limit` - Check guest usage

### Subscription
- `GET /api/subscription/plans` - List available plans
- `POST /api/subscription/create` - Create Razorpay subscription
- `POST /api/subscription/verify` - Verify payment signature
- `GET /api/subscription/status/{user_id}` - Get subscription details
- `POST /api/webhook/razorpay` - Razorpay webhook handler

### Chat (Modified)
- `POST /api/chat` - Send message (checks limits, requires auth)
  - Returns 403 with `upgrade_required` when limit exceeded
  - Response includes tier, usage, reset time, plan options

## Troubleshooting

### Issue: "Token expired" errors
**Solution:** JWT tokens have 30-day expiry. User needs to login again.

### Issue: Payment verification fails
**Solution:** Check that `RAZORPAY_WEBHOOK_SECRET` matches dashboard.

### Issue: Daily limit not resetting
**Solution:** Check `daily_reset_at` timestamp. Should be 24h from last reset.

### Issue: Guest tracking not working
**Solution:** Ensure client sends real IP. Railway should provide this in headers.

### Issue: Upgrade modal stuck loading
**Solution:** 
1. Check Razorpay SDK loaded (open browser console)
2. Verify plan IDs match in code and dashboard
3. Check backend logs for subscription creation errors

## Production Checklist

Before going live:

- [ ] Set `ENABLE_FREE_LIMITS=true`
- [ ] Switch Razorpay to LIVE mode
- [ ] Update `RAZORPAY_KEY_ID` to live key
- [ ] Create LIVE subscription plans
- [ ] Test payment with real card (small amount)
- [ ] Setup Razorpay webhook
- [ ] Test webhook with real event
- [ ] Monitor first few signups closely
- [ ] Check database for referral tracking
- [ ] Verify daily reset logic works
- [ ] Test all tiers (free → limited → unlimited)

## Monitoring

### Key Metrics to Track

```sql
-- Daily signups
SELECT DATE(created_at), COUNT(*) 
FROM users 
GROUP BY DATE(created_at) 
ORDER BY DATE(created_at) DESC;

-- Active subscriptions
SELECT subscription_tier, subscription_status, COUNT(*) 
FROM users 
WHERE subscription_tier IN ('limited', 'unlimited')
GROUP BY subscription_tier, subscription_status;

-- Revenue estimate
SELECT 
  SUM(CASE WHEN subscription_tier = 'limited' THEN 399 ELSE 0 END) as limited_revenue,
  SUM(CASE WHEN subscription_tier = 'unlimited' THEN 999 ELSE 0 END) as unlimited_revenue
FROM users 
WHERE subscription_status = 'active';

-- Message usage
SELECT 
  subscription_tier,
  AVG(messages_today) as avg_daily,
  MAX(messages_today) as max_daily
FROM users
GROUP BY subscription_tier;
```

## Next Steps

1. **Deploy backend changes to Railway**
   ```bash
   git add .
   git commit -m "Add authentication and subscription system"
   git push
   ```

2. **Deploy frontend changes to Railway**
   ```bash
   cd frontend
   git add .
   git commit -m "Add signup, signin, and upgrade UI"
   git push
   ```

3. **Run database migration** (see SQL above)

4. **Set environment variables** in Railway dashboard

5. **Create Razorpay plans** and update plan IDs

6. **Test everything** with ENABLE_FREE_LIMITS=false first

7. **Enable limits** and test payment flow

8. **Go live!** 🚀

## Support

For issues or questions:
- Check backend logs in Railway dashboard
- Check browser console for frontend errors
- Verify all environment variables are set
- Test with Razorpay test mode first
- Check Razorpay dashboard for payment issues

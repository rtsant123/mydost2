"""Payment and subscription management with Razorpay."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import razorpay
import hmac
import hashlib
from models.user import user_db
from utils.config import config

router = APIRouter()

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET))

class CreateSubscriptionRequest(BaseModel):
    user_id: str
    plan: str  # 'limited' or 'unlimited'

class VerifyPaymentRequest(BaseModel):
    user_id: str
    plan: str
    razorpay_payment_id: str
    razorpay_subscription_id: str
    razorpay_signature: str

@router.get("/subscription/plans")
async def get_subscription_plans():
    """Get all available subscription plans."""
    return {
        "plans": [
            {
                "id": "limited",
                "name": config.SUBSCRIPTION_PLANS['limited']['name'],
                "price": config.SUBSCRIPTION_PLANS['limited']['price'],
                "currency": "INR",
                "messages_per_day": config.SUBSCRIPTION_PLANS['limited']['messages_per_day'],
                "features": config.SUBSCRIPTION_PLANS['limited']['features'],
                "duration": "monthly"
            },
            {
                "id": "unlimited",
                "name": config.SUBSCRIPTION_PLANS['unlimited']['name'],
                "price": config.SUBSCRIPTION_PLANS['unlimited']['price'],
                "currency": "INR",
                "messages_per_day": "Unlimited",
                "features": config.SUBSCRIPTION_PLANS['unlimited']['features'],
                "duration": "monthly"
            }
        ]
    }

@router.post("/subscription/create")
async def create_subscription(request: CreateSubscriptionRequest):
    """Create a Razorpay subscription."""
    try:
        if request.plan not in ['limited', 'unlimited']:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        plan_details = config.SUBSCRIPTION_PLANS[request.plan]
        
        # Create Razorpay subscription
        subscription_data = {
            "plan_id": f"plan_{request.plan}",  # You need to create these in Razorpay dashboard
            "total_count": 12,  # 12 months
            "quantity": 1,
            "customer_notify": 1,
            "notes": {
                "user_id": request.user_id,
                "plan": request.plan
            }
        }
        
        subscription = razorpay_client.subscription.create(subscription_data)
        
        return {
            "subscription_id": subscription['id'],
            "plan": request.plan,
            "amount": plan_details['price'] * 100,  # Convert to paise
            "currency": "INR",
            "razorpay_key": config.RAZORPAY_KEY_ID
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscription/verify")
async def verify_payment(request: VerifyPaymentRequest):
    """Verify Razorpay payment and activate subscription."""
    try:
        # Verify signature
        generated_signature = hmac.new(
            config.RAZORPAY_KEY_SECRET.encode(),
            f"{request.razorpay_payment_id}|{request.razorpay_subscription_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != request.razorpay_signature:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Upgrade user subscription
        success = user_db.upgrade_subscription(
            user_id=request.user_id,
            tier=request.plan,
            subscription_id=request.razorpay_subscription_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to upgrade subscription")
        
        return {
            "success": True,
            "message": "Subscription activated successfully!",
            "plan": request.plan,
            "subscription_id": request.razorpay_subscription_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):
    """Handle Razorpay webhooks for subscription events."""
    try:
        # Get webhook signature
        webhook_signature = request.headers.get("X-Razorpay-Signature")
        webhook_body = await request.body()
        
        # Verify webhook
        razorpay_client.utility.verify_webhook_signature(
            webhook_body.decode(),
            webhook_signature,
            config.RAZORPAY_WEBHOOK_SECRET
        )
        
        # Parse event
        event = await request.json()
        event_type = event.get("event")
        
        # Handle subscription events
        if event_type == "subscription.charged":
            # Subscription payment successful - extend subscription
            subscription_id = event['payload']['subscription']['entity']['id']
            # Update user subscription
            pass
        
        elif event_type == "subscription.cancelled":
            # Subscription cancelled - downgrade user
            subscription_id = event['payload']['subscription']['entity']['id']
            # Update user to free tier
            pass
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail="Webhook verification failed")

@router.get("/subscription/status/{user_id}")
async def get_subscription_status(user_id: str):
    """Get user's current subscription status."""
    try:
        user = user_db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        tier = user.get('subscription_tier', 'free')
        plan = config.SUBSCRIPTION_PLANS.get(tier, config.SUBSCRIPTION_PLANS['free'])
        
        return {
            "user_id": user_id,
            "tier": tier,
            "status": user.get('subscription_status', 'active'),
            "expires_at": user.get('subscription_expires_at'),
            "messages_lifetime": user.get('messages_lifetime', 0),
            "messages_today": user.get('messages_today', 0),
            "limits": {
                "total": plan['messages_total'],
                "daily": plan['messages_per_day']
            },
            "features": plan['features']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

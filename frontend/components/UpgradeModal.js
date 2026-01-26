import React, { useState } from 'react';
import { X, Check, Zap, Infinity } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mydost2-production.up.railway.app';

export default function UpgradeModal({ isOpen, onClose, currentTier, limitType }) {
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  const plans = [
    {
      id: 'limited',
      name: 'Limited Plan',
      price: 399,
      period: 'per month',
      features: [
        '50 messages per day',
        'Daily limit resets',
        'Full RAG & memory',
        'Web search enabled',
        'Priority support',
      ],
      icon: Zap,
      color: 'blue',
      recommended: limitType === 'daily_limit',
    },
    {
      id: 'unlimited',
      name: 'Unlimited Plan',
      price: 999,
      period: 'per month',
      features: [
        'Unlimited messages',
        'No daily limits',
        'Full RAG & memory',
        'Web search enabled',
        'Premium support',
        'Early access to features',
      ],
      icon: Infinity,
      color: 'purple',
      recommended: limitType === 'lifetime_limit',
    },
  ];

  const handleUpgrade = async (planId) => {
    setLoading(true);
    setSelectedPlan(planId);

    try {
      const token = localStorage.getItem('token');
      const user = JSON.parse(localStorage.getItem('user'));

      // Create Razorpay subscription
      const { data } = await axios.post(
        `${API_URL}/api/subscription/create`,
        { plan: planId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Load Razorpay SDK if not already loaded
      if (!window.Razorpay) {
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        document.body.appendChild(script);
        await new Promise((resolve) => {
          script.onload = resolve;
        });
      }

      // Open Razorpay checkout
      const options = {
        key: data.razorpay_key_id,
        subscription_id: data.subscription_id,
        name: 'MyDost',
        description: `${planId === 'limited' ? 'Limited' : 'Unlimited'} Plan Subscription`,
        image: '/logo.png',
        handler: async (response) => {
          try {
            // Verify payment
            await axios.post(
              `${API_URL}/api/subscription/verify`,
              {
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_subscription_id: response.razorpay_subscription_id,
                razorpay_signature: response.razorpay_signature,
              },
              { headers: { Authorization: `Bearer ${token}` } }
            );

            alert('Subscription activated successfully! 🎉');
            window.location.reload();
          } catch (error) {
            console.error('Payment verification failed:', error);
            alert('Payment verification failed. Please contact support.');
          }
        },
        prefill: {
          name: user.name,
          email: user.email,
        },
        theme: {
          color: planId === 'limited' ? '#3B82F6' : '#9333EA',
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', (response) => {
        alert('Payment failed. Please try again.');
        console.error('Payment failed:', response.error);
      });
      rzp.open();
    } catch (error) {
      console.error('Failed to create subscription:', error);
      alert('Failed to initiate payment. Please try again.');
    } finally {
      setLoading(false);
      setSelectedPlan(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Upgrade Your Plan</h2>
            <p className="text-gray-600 mt-1">
              {limitType === 'lifetime_limit'
                ? "You've reached your free message limit"
                : "You've reached your daily message limit"}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-6">
            {plans.map((plan) => {
              const Icon = plan.icon;
              return (
                <div
                  key={plan.id}
                  className={`relative border-2 rounded-xl p-6 ${
                    plan.recommended
                      ? `border-${plan.color}-500 shadow-lg`
                      : 'border-gray-200'
                  }`}
                >
                  {plan.recommended && (
                    <div
                      className={`absolute -top-3 left-1/2 transform -translate-x-1/2 bg-${plan.color}-500 text-white px-4 py-1 rounded-full text-sm font-medium`}
                    >
                      Recommended
                    </div>
                  )}

                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className={`p-3 rounded-lg bg-${plan.color}-100 text-${plan.color}-600`}
                    >
                      <Icon size={24} />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                      <div className="flex items-baseline gap-1">
                        <span className="text-3xl font-bold text-gray-900">
                          ₹{plan.price}
                        </span>
                        <span className="text-gray-600 text-sm">/{plan.period}</span>
                      </div>
                    </div>
                  </div>

                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <Check
                          size={20}
                          className={`text-${plan.color}-600 flex-shrink-0 mt-0.5`}
                        />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    onClick={() => handleUpgrade(plan.id)}
                    disabled={loading}
                    className={`w-full py-3 rounded-lg font-medium transition ${
                      plan.recommended
                        ? `bg-${plan.color}-600 hover:bg-${plan.color}-700 text-white`
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                    } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {loading && selectedPlan === plan.id ? (
                      <span className="flex items-center justify-center gap-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        Processing...
                      </span>
                    ) : (
                      `Upgrade to ${plan.name}`
                    )}
                  </button>
                </div>
              );
            })}
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 text-center">
              💳 Secure payment powered by Razorpay • Cancel anytime • No hidden fees
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

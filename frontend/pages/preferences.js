import { useState, useEffect, useCallback } from "react";
import Image from "next/image";
import { useRouter } from "next/router";
import axios from "axios";
import { User, Globe, MessageSquare, Save, ArrowLeft, CreditCard, LogOut, HelpCircle } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://mydost2-production.up.railway.app";

export default function Preferences() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [preferences, setPreferences] = useState({
    language: "english",
    tone: "friendly",
    interests: [],
    response_style: "balanced",
  });

  const languages = [
    { value: "english", label: "English" },
    { value: "hindi", label: "हिंदी (Hindi)" },
    { value: "assamese", label: "অসমীয়া (Assamese)" },
  ];

  const tones = [
    { value: "friendly", label: "Friendly & Casual", description: "Like talking to a friend" },
    { value: "professional", label: "Professional", description: "Clear and formal" },
    { value: "supportive", label: "Supportive & Caring", description: "Empathetic and encouraging" },
  ];

  const interestOptions = [
    { value: "education", label: "📚 Education & Learning" },
    { value: "sports", label: "⚽ Sports & Predictions" },
    { value: "teer", label: "🎯 Teer Analysis" },
    { value: "astrology", label: "⭐ Astrology & Horoscopes" },
    { value: "news", label: "📰 News & Current Events" },
    { value: "technology", label: "💻 Technology" },
    { value: "entertainment", label: "🎬 Entertainment" },
  ];

  const responseStyles = [
    { value: "concise", label: "Concise", description: "Short, to-the-point answers" },
    { value: "balanced", label: "Balanced", description: "Moderate detail" },
    { value: "detailed", label: "Detailed", description: "In-depth explanations" },
  ];

  const toggleInterest = (interest) => {
    setPreferences((prev) => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter((i) => i !== interest)
        : [...prev.interests, interest],
    }));
  };

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push('/signin');
      return;
    }

    try {
      const response = await axios.get(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data.user);
      setLoading(false);
    } catch (error) {
      console.error('Auth failed:', error);
      localStorage.removeItem('token');
      router.push('/signin');
    }
  }, [router]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const handleSave = async () => {
    if (!user?.id) return;

    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/users/${user.id}/preferences`, 
        preferences,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert('Preferences saved successfully!');
      router.push("/");
    } catch (error) {
      console.error("Error saving preferences:", error);
      alert("Failed to save preferences. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/signin');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header with Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
            >
              <ArrowLeft size={20} />
              Back
            </button>
            
            <div className="flex gap-2">
              <button
                onClick={() => window.open('https://docs.mydost.ai', '_blank')}
                className="flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                <HelpCircle size={18} />
                Help
              </button>
              
              <button
                onClick={() => router.push('/upgrade')}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:opacity-90 transition"
              >
                <CreditCard size={18} />
                Upgrade
              </button>
              
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition"
              >
                <LogOut size={18} />
                Logout
              </button>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {user?.photo ? (
              <Image src={user.photo} alt="Profile" width={64} height={64} className="w-16 h-16 rounded-full object-cover" />
            ) : (
              <div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                <User className="text-white" size={32} />
              </div>
            )}
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
              <p className="text-gray-600 dark:text-gray-400">{user?.email || 'Customize your experience'}</p>
            </div>
          </div>
        </div>

        {/* Settings Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
          {/* Language Preference */}
          <div className="mb-8">
            <label className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-3">
              <Globe size={20} />
              Preferred Language
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {languages.map((lang) => (
                <button
                  key={lang.value}
                  onClick={() => setPreferences({ ...preferences, language: lang.value })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.language === lang.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                  }`}
                >
                  <span className="font-medium text-gray-900 dark:text-white">{lang.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Tone Preference */}
          <div className="mb-8">
            <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Conversation Tone
            </label>
            <div className="space-y-3">
              {tones.map((tone) => (
                <button
                  key={tone.value}
                  onClick={() => setPreferences({ ...preferences, tone: tone.value })}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    preferences.tone === tone.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                  }`}
                >
                  <div className="font-medium text-gray-900 dark:text-white">{tone.label}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{tone.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Interests */}
          <div className="mb-8">
            <label className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-3">
              <MessageSquare size={20} />
              Your Interests (Select all that apply)
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {interestOptions.map((interest) => (
                <button
                  key={interest.value}
                  onClick={() => toggleInterest(interest.value)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    preferences.interests.includes(interest.value)
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                  }`}
                >
                  <span className="text-gray-900 dark:text-white">{interest.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Response Style */}
          <div className="mb-8">
            <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Response Style
            </label>
            <div className="space-y-3">
              {responseStyles.map((style) => (
                <button
                  key={style.value}
                  onClick={() => setPreferences({ ...preferences, response_style: style.value })}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    preferences.response_style === style.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                  }`}
                >
                  <div className="font-medium text-gray-900 dark:text-white">{style.label}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{style.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving || preferences.interests.length === 0}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 px-6 rounded-lg transition-colors"
          >
            {saving ? "Saving..." : "Save & Continue"}
          </button>

          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
            You can change these preferences anytime in settings
          </p>
        </div>
      </div>
    </div>
  );
}

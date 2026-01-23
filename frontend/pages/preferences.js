import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/router";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Preferences() {
  const { data: session, status, update } = useSession();
  const router = useRouter();
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

  const handleSave = async () => {
    if (!session?.user?.id) return;

    setSaving(true);
    try {
      await axios.post(`${API_URL}/users/${session.user.id}/preferences`, preferences);
      
      // Update session
      await update({
        ...session,
        user: {
          ...session.user,
          has_preferences: true,
          preferences,
        },
      });

      router.push("/");
    } catch (error) {
      console.error("Error saving preferences:", error);
      alert("Failed to save preferences. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!session) {
    router.push("/auth/signin");
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Customize Your Experience
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Tell us about yourself so MyDost can assist you better
            </p>
          </div>

          {/* Language Preference */}
          <div className="mb-8">
            <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
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
            <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
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

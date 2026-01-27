import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { chatAPI } from '@/utils/apiClient';

const tones = ['friendly', 'professional', 'supportive'];
const styles = ['concise', 'balanced', 'detailed'];
const languages = ['english', 'hindi', 'assamese'];

export default function ProfilePanel({ isOpen, onClose, userId, onSaved }) {
  const [form, setForm] = useState({
    name: '',
    location: '',
    language: 'english',
    tone: 'friendly',
    response_style: 'balanced',
    interests: '',
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userId) return;
    setSaving(true);
    try {
      await chatAPI.updateProfile({
        user_id: userId,
        name: form.name || undefined,
        location: form.location || undefined,
        language: form.language,
        tone: form.tone,
        response_style: form.response_style,
        interests: form.interests
          ? form.interests.split(',').map((s) => s.trim()).filter(Boolean)
          : undefined,
      });
      onSaved && onSaved();
      onClose();
    } catch (err) {
      console.error('Profile update failed', err);
      alert('Could not save profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Edit Profile</h2>
            <p className="text-sm text-slate-500">I’ll remember these to personalize replies.</p>
          </div>
          <button onClick={onClose} className="p-2 rounded hover:bg-slate-100">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <label className="text-sm text-slate-600 space-y-1">
              <span>Name</span>
              <input
                value={form.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900 focus:border-slate-400 focus:outline-none"
                placeholder="What should I call you?"
              />
            </label>
            <label className="text-sm text-slate-600 space-y-1">
              <span>Location</span>
              <input
                value={form.location}
                onChange={(e) => handleChange('location', e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900 focus:border-slate-400 focus:outline-none"
                placeholder="City or time zone"
              />
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <label className="text-sm text-slate-600 space-y-1">
              <span>Language</span>
              <select
                value={form.language}
                onChange={(e) => handleChange('language', e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900 focus:border-slate-400 focus:outline-none"
              >
                {languages.map((lang) => (
                  <option key={lang} value={lang}>{lang}</option>
                ))}
              </select>
            </label>
            <label className="text-sm text-slate-600 space-y-1">
              <span>Tone</span>
              <select
                value={form.tone}
                onChange={(e) => handleChange('tone', e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900 focus:border-slate-400 focus:outline-none"
              >
                {tones.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>
            <label className="text-sm text-slate-600 space-y-1">
              <span>Response style</span>
              <select
                value={form.response_style}
                onChange={(e) => handleChange('response_style', e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900 focus:border-slate-400 focus:outline-none"
              >
                {styles.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </label>
          </div>

          <label className="text-sm text-slate-600 space-y-1 block">
            <span>Interests (comma separated)</span>
            <input
              value={form.interests}
              onChange={(e) => handleChange('interests', e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900 focus:border-slate-400 focus:outline-none"
              placeholder="cricket, finance, startups"
            />
          </label>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-60"
            >
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import React, { useEffect, useMemo, useState } from 'react';
import Head from 'next/head';
import { memoryAPI } from '@/utils/apiClient';
import { useRouter } from 'next/router';
import { Plus, Search, Trash2, Download, Edit3, Check, X, Tag } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mydost2-production.up.railway.app';
const CATEGORIES = ['Personal', 'Education', 'Sports', 'Work', 'Ideas', 'Health', 'Finance'];

export default function NotesPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [userId, setUserId] = useState('');
  const [isGuest, setIsGuest] = useState(false);
  const [memories, setMemories] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [form, setForm] = useState({ title: '', body: '', category: 'Personal' });
  const [editingId, setEditingId] = useState(null);

  // ---- Auth handshake (reuse backend /auth/me; guests fallback) ----
  useEffect(() => {
    const init = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const resp = await axios.get(`${API_URL}/api/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setUser(resp.data.user);
          setUserId(resp.data.user.user_id);
          setIsGuest(false);
          return;
        }
      } catch (e) {
        console.warn('Auth check failed, falling back to guest.', e);
      }
      // guest fallback
      const existing = localStorage.getItem('guest_id');
      const gid = existing || `guest_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
      localStorage.setItem('guest_id', gid);
      setUserId(gid);
      setIsGuest(true);
    };
    init().finally(() => setLoading(false));
  }, []);

  // ---- Load memories ----
  useEffect(() => {
    if (!userId) return;
    const load = async () => {
      try {
        const res = await memoryAPI.list(userId, 200);
        const mems = res.data.memories || res.data || [];
        setMemories(mems);
        setFiltered(mems);
      } catch (e) {
        console.warn('Could not load memories', e);
      }
    };
    load();
  }, [userId]);

  // ---- Search + filter ----
  useEffect(() => {
    let list = [...memories];
    if (category) {
      list = list.filter((m) => {
        const cat = m.metadata?.category || m.metadata?.Category || '';
        return cat.toLowerCase() === category.toLowerCase();
      });
    }
    if (query.trim()) {
      const q = query.toLowerCase();
      list = list.filter((m) => m.content?.toLowerCase().includes(q));
    }
    setFiltered(list);
  }, [memories, query, category]);

  const resetForm = () => setForm({ title: '', body: '', category: 'Personal' });

  const handleSave = async () => {
    if (!form.title.trim() && !form.body.trim()) return;
    setSaving(true);
    const payload = {
      user_id: userId,
      content: `${form.title.trim()}\n\n${form.body.trim()}`.trim(),
      memory_type: 'note',
      metadata: { category: form.category || 'Personal', title: form.title.trim() },
    };
    try {
      if (editingId) {
        await memoryAPI.update(editingId, payload);
      } else {
        await memoryAPI.create(payload);
      }
      const res = await memoryAPI.list(userId, 200);
      const mems = res.data.memories || res.data || [];
      setMemories(mems);
      setFiltered(mems);
      resetForm();
      setEditingId(null);
    } catch (e) {
      alert(e.response?.data?.detail || 'Could not save note.');
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (memory) => {
    setEditingId(memory.id);
    setForm({
      title: memory.metadata?.title || memory.content?.split('\n')[0] || '',
      body: memory.content?.split('\n').slice(1).join('\n').trim() || '',
      category: memory.metadata?.category || 'Personal',
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this note permanently?')) return;
    try {
      await memoryAPI.remove(id, userId);
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      alert('Could not delete note.');
    }
  };

  const handleDeleteAll = async () => {
    if (!window.confirm('Delete ALL notes and memories? This cannot be undone.')) return;
    try {
      await memoryAPI.removeAll(userId);
      setMemories([]);
      setFiltered([]);
    } catch (e) {
      alert('Could not clear memories.');
    }
  };

  const handleExport = () => {
    setExporting(true);
    const lines = filtered.map((m) => {
      const cat = m.metadata?.category ? `[${m.metadata.category}] ` : '';
      return `${cat}${m.content}`.trim();
    });
    const blob = new Blob([lines.join('\n\n---\n\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mydost-memories-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setExporting(false);
  };

  const headerTitle = useMemo(
    () => (user ? `${user.name?.split(' ')[0]}'s Notes` : 'Your Notes & Memories'),
    [user]
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-slate-100 to-white">
      <Head>
        <title>Notes & Memories | MyDost</title>
      </Head>

      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Memory Vault</p>
            <h1 className="text-3xl font-bold text-slate-900 mt-1">{headerTitle}</h1>
            <p className="text-slate-600 text-sm mt-1">
              Save personal notes, study highlights, sports cues, or quick ideas. Search and export anytime.
            </p>
          </div>
          <div className="hidden md:flex gap-2">
            <button
              onClick={() => router.push('/')}
              className="px-3 py-2 text-sm rounded-lg border border-slate-200 text-slate-700 hover:bg-white"
            >
              Back to chat
            </button>
            <button
              onClick={handleExport}
              className="px-3 py-2 text-sm rounded-lg bg-slate-900 text-white hover:bg-slate-800 flex items-center gap-2"
              disabled={exporting}
            >
              <Download size={16} />
              {exporting ? 'Exporting…' : 'Export'}
            </button>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
            <Plus size={18} />
            {editingId ? 'Edit note' : 'Add a new note'}
          </div>
          <div className="grid md:grid-cols-3 gap-3">
            <input
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
              placeholder="Title"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            />
            <select
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
            >
              {CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <div className="flex gap-2 justify-end">
              {editingId && (
                <button
                  onClick={() => {
                    setEditingId(null);
                    resetForm();
                  }}
                  className="px-3 py-2 text-sm rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 flex items-center gap-1"
                >
                  <X size={14} />
                  Cancel
                </button>
              )}
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 text-sm rounded-lg bg-slate-900 text-white hover:bg-slate-800 flex items-center gap-2 disabled:opacity-60"
              >
                <Check size={16} />
                {saving ? 'Saving…' : editingId ? 'Update' : 'Save'}
              </button>
            </div>
          </div>
          <textarea
            className="w-full rounded-lg border border-slate-200 px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300 min-h-[120px]"
            placeholder="Write the details you want the bot to remember..."
            value={form.body}
            onChange={(e) => setForm((f) => ({ ...f, body: e.target.value }))}
          />
        </div>

        {/* Controls */}
        <div className="flex flex-col md:flex-row md:items-center gap-3">
          <div className="flex items-center gap-2 flex-1 bg-white border border-slate-200 rounded-lg px-3 py-2">
            <Search size={16} className="text-slate-500" />
            <input
              className="w-full text-sm outline-none"
              placeholder="Search your notes…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <select
            className="w-full md:w-48 rounded-lg border border-slate-200 px-3 py-2 text-sm bg-white"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All categories</option>
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
          <button
            onClick={handleDeleteAll}
            className="w-full md:w-auto flex items-center justify-center gap-2 px-3 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 text-sm"
          >
            <Trash2 size={16} />
            Clear all
          </button>
        </div>

        {/* List */}
        <div className="grid md:grid-cols-2 gap-4">
          {loading ? (
            <div className="col-span-2 text-center text-slate-500">Loading memories...</div>
          ) : filtered.length === 0 ? (
            <div className="col-span-2 text-center text-slate-500">No notes yet. Add your first one above.</div>
          ) : (
            filtered.map((m) => {
              const cat = m.metadata?.category || 'Note';
              const title = m.metadata?.title || m.content?.split('\n')[0]?.slice(0, 80) || 'Untitled';
              const body = m.content?.split('\n').slice(1).join('\n').trim() || '';
              return (
                <div key={m.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col gap-2">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-slate-100 text-slate-700 border border-slate-200">
                        <Tag size={12} />
                        {cat}
                      </span>
                    </div>
                    <div className="flex gap-2 text-slate-500">
                      <button onClick={() => handleEdit(m)} className="p-1 rounded hover:bg-slate-100">
                        <Edit3 size={16} />
                      </button>
                      <button onClick={() => handleDelete(m.id)} className="p-1 rounded hover:bg-red-50 text-red-600">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <h3 className="text-base font-semibold text-slate-900">{title}</h3>
                  <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed line-clamp-6">{body || m.content}</p>
                  <div className="text-xs text-slate-500">
                    {new Date(m.created_at || m.metadata?.timestamp || Date.now()).toLocaleString()}
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="md:hidden flex gap-2 justify-between">
          <button
            onClick={() => router.push('/')}
            className="flex-1 px-3 py-2 text-sm rounded-lg border border-slate-200 text-slate-700 hover:bg-white"
          >
            Back to chat
          </button>
          <button
            onClick={handleExport}
            className="flex-1 px-3 py-2 text-sm rounded-lg bg-slate-900 text-white hover:bg-slate-800 flex items-center justify-center gap-2"
            disabled={exporting}
          >
            <Download size={16} />
            Export
          </button>
        </div>
      </div>
    </div>
  );
}

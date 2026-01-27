import React, { useMemo } from 'react';

export default function MemoryPanel({ summary, memories = [], usedMemories = [], preferences = {}, onRecall, recallLoading = false }) {
  const hasPrefs = preferences && Object.keys(preferences).length > 0;

  const prefItems = useMemo(() => {
    if (!hasPrefs) return [];
    const items = [];
    if (preferences.name) items.push(`Name: ${preferences.name}`);
    if (preferences.location) items.push(`Location: ${preferences.location}`);
    if (preferences.preferred_language) items.push(`Language: ${preferences.preferred_language}`);
    if (preferences.tone) items.push(`Tone: ${preferences.tone}`);
    if (preferences.interests?.length) items.push(`Interests: ${preferences.interests.slice(0, 5).join(', ')}`);
    if (preferences.likes?.length) items.push(`Likes: ${preferences.likes.slice(0, 3).join(', ')}`);
    return items;
  }, [preferences, hasPrefs]);

  return (
    <div className="sticky top-4 space-y-3">
      <div className="border border-slate-200 rounded-xl shadow-sm p-4 bg-white">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-slate-800">Memory Snapshot</h3>
          {onRecall && (
            <button
              onClick={onRecall}
              className="text-xs px-2 py-1 rounded-full bg-slate-900 text-white hover:bg-slate-800 transition disabled:opacity-60"
              disabled={recallLoading}
            >
              {recallLoading ? 'Recalling...' : 'Recall all'}
            </button>
          )}
        </div>
        {summary ? (
          <div className="text-xs text-slate-700 leading-5 whitespace-pre-wrap line-clamp-6">{summary.preview || summary}</div>
        ) : (
          <p className="text-xs text-slate-500">Send a message to start building memory.</p>
        )}
      </div>

      <div className="border border-slate-200 rounded-xl shadow-sm p-4 bg-white">
        <h3 className="text-sm font-semibold text-slate-800 mb-2">Context Used This Reply</h3>
        {usedMemories.length === 0 ? (
          <p className="text-xs text-slate-500">No memories pulled yet.</p>
        ) : (
          <ul className="space-y-2">
            {usedMemories.slice(0, 6).map((m, idx) => (
              <li key={idx} className="text-xs text-slate-700 line-clamp-2">
                {m.content || m.preview || JSON.stringify(m)}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="border border-slate-200 rounded-xl shadow-sm p-4 bg-white">
        <h3 className="text-sm font-semibold text-slate-800 mb-2">Recent Memories</h3>
        {memories.length === 0 ? (
          <p className="text-xs text-slate-500">No stored memories yet.</p>
        ) : (
          <ul className="space-y-2">
            {memories.slice(0, 6).map((m) => (
              <li key={m.id} className="text-xs text-slate-700 line-clamp-2">
                {m.content}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="border border-slate-200 rounded-xl shadow-sm p-4 bg-white">
        <h3 className="text-sm font-semibold text-slate-800 mb-2">Your Preferences</h3>
        {prefItems.length === 0 ? (
          <p className="text-xs text-slate-500">Set preferences in Settings to personalize answers.</p>
        ) : (
          <ul className="space-y-1 text-xs text-slate-700 list-disc list-inside">
            {prefItems.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

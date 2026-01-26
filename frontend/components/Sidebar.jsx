import React from 'react';
import { Menu, X, Plus, Trash2, Settings, User, LogOut } from 'lucide-react';
import { chatAPI } from '@/utils/apiClient';

export default function Sidebar({ isOpen, onClose, conversations, onNewChat, onSelectConversation, onAdminClick, onSettingsClick, onConversationDeleted, user }) {
  const handleLogout = () => {
    const uid = user?.user_id || localStorage.getItem('guest_id');
    if (uid) {
      chatAPI.deleteAll(uid).catch(() => {});
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('guest_id');
    // Clear any cached guest messages
    Object.keys(localStorage)
      .filter((k) => k.startsWith('guest_messages_'))
      .forEach((k) => localStorage.removeItem(k));
    window.location.href = '/signin';
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-30"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed md:fixed top-0 left-0 h-screen w-64 bg-[#f0f2f5] text-slate-900 transition-transform z-40 border-r border-slate-200 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <h1 className="text-xl font-bold text-slate-900">MyDost</h1>
            <button
              onClick={onClose}
              className="md:hidden btn-icon text-slate-600 hover:bg-slate-200"
            >
              <X size={20} />
            </button>
          </div>

          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            className="m-4 flex items-center justify-center gap-2 bg-slate-900 text-white py-2 rounded-lg font-semibold hover:bg-slate-800 transition"
          >
            <Plus size={20} />
            New Chat
          </button>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto px-4 space-y-2">
            <h3 className="text-sm font-semibold text-slate-500 mb-3">Recent</h3>
            {conversations.length === 0 ? (
              <p className="text-sm text-slate-500">No conversations yet</p>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className="w-full flex items-center gap-2 p-2 rounded hover:bg-slate-200 transition text-sm text-slate-800"
                  title={conv.preview}
                >
                  <button
                    onClick={() => onSelectConversation(conv.id)}
                    className="flex-1 text-left truncate"
                  >
                    {conv.preview.substring(0, 30)}...
                  </button>
                  <button
                    onClick={async () => {
                      if (!window.confirm('Delete this conversation?')) return;
                      try {
                        await chatAPI.deleteConversation(conv.id);
                        onConversationDeleted && onConversationDeleted(conv.id);
                      } catch (err) {
                        alert('Could not delete conversation. Please try again.');
                      }
                    }}
                    className="p-1 rounded hover:bg-slate-100 text-slate-500 hover:text-red-500 transition"
                    aria-label="Delete conversation"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Footer - User Profile */}
          <div className="border-t border-slate-200 p-4">
            {user ? (
              <div className="space-y-2">
                {/* User Info */}
                <div className="flex items-center gap-3 p-2 rounded bg-white border border-slate-200">
                  {user.image ? (
                    <img src={user.image} alt={user.name} className="w-8 h-8 rounded-full" />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
                      <User size={16} className="text-slate-700" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{user.name}</p>
                    <p className="text-xs text-slate-500 truncate">{user.email}</p>
                  </div>
                </div>

                {/* Action Buttons */}
                <button
                  onClick={onSettingsClick}
                  className="w-full flex items-center gap-2 p-2 rounded hover:bg-slate-200 transition text-sm"
                >
                  <Settings size={16} />
                  Settings
                </button>
                
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 p-2 rounded hover:bg-slate-200 transition text-sm text-red-500"
                >
                  <LogOut size={16} />
                  Logout
                </button>
              </div>
            ) : (
              <button
                onClick={() => window.location.href = '/signin'}
                className="w-full flex items-center gap-2 p-2 rounded hover:bg-slate-200 transition text-sm"
              >
                <User size={16} />
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

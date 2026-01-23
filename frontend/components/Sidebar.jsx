import React, { useState } from 'react';
import { Menu, X, Plus, Trash2, Settings } from 'lucide-react';

export default function Sidebar({ isOpen, onClose, conversations, onNewChat, onSelectConversation, onAdminClick }) {
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
        className={`fixed md:relative top-0 left-0 h-screen w-64 bg-gray-950 dark:bg-gray-950 text-white transition-transform z-40 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-800 flex items-center justify-between">
            <h1 className="text-xl font-bold">Claude</h1>
            <button
              onClick={onClose}
              className="md:hidden btn-icon text-white hover:bg-gray-800"
            >
              <X size={20} />
            </button>
          </div>

          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            className="m-4 flex items-center justify-center gap-2 bg-white text-gray-900 py-2 rounded-lg font-semibold hover:bg-gray-100 transition"
          >
            <Plus size={20} />
            New Chat
          </button>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto px-4 space-y-2">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">Recent</h3>
            {conversations.length === 0 ? (
              <p className="text-sm text-gray-500">No conversations yet</p>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => onSelectConversation(conv.id)}
                  className="w-full text-left p-2 rounded hover:bg-gray-800 transition text-sm text-gray-300 truncate"
                  title={conv.preview}
                >
                  {conv.preview.substring(0, 30)}...
                </button>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-800 p-4 space-y-2">
            <button
              onClick={onAdminClick}
              className="w-full flex items-center gap-2 p-2 rounded hover:bg-gray-800 transition text-sm"
            >
              <Settings size={16} />
              Admin Panel
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

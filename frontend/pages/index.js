import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import { Menu, LogOut, X, User } from 'lucide-react';
import ChatWindow from '@/components/ChatWindow';
import InputBar from '@/components/InputBar';
import Sidebar from '@/components/Sidebar';
import LayoutShell from '@/components/LayoutShell';
import UpgradeModal from '@/components/UpgradeModal';
import AstrologyModal from '@/components/AstrologyModal';
import { chatAPI, ocrAPI, pdfAPI } from '@/utils/apiClient';
import ProfilePanel from '@/components/ProfilePanel';
import { saveConversationHistory, getConversationHistory, formatDate } from '@/utils/storage';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mydost2-production.up.railway.app';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  const checkAuth = useCallback(async () => {
    // Check if token is in URL (from Google OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
      // Save token from OAuth and clean URL
      localStorage.setItem('token', tokenFromUrl);
      window.history.replaceState({}, document.title, '/');
    }
    
    const token = tokenFromUrl || localStorage.getItem('token');
    
    // If no token, allow guest access
    if (!token) {
      setUser(null);
      setLoading(false);
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
      // Invalid token - clear and allow guest access
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return <ChatPage user={user} />;
}

function ChatPage({ user }) {
  const router = useRouter();
  const [userId, setUserId] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [limitType, setLimitType] = useState(null);
  const [isGuest, setIsGuest] = useState(false);
  const [showAstrologyModal, setShowAstrologyModal] = useState(false);
  const [hasProcessedUrlQuery, setHasProcessedUrlQuery] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const loadSubscriptionStatus = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/subscription/status/${user.user_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSubscriptionStatus(response.data);
    } catch (error) {
      console.error('Failed to load subscription:', error);
    }
  }, [user?.user_id]);

  const loadConversations = useCallback(async () => {
    try {
      if (!userId) return;
      if (isGuest) {
        // Guests: no persistent conversations
        setConversations([]);
        return;
      }
      const response = await chatAPI.listConversations(userId);
      setConversations(response.data.conversations || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
      // Fail silently for guests
    }
  }, [userId, isGuest]);

  const handleSendMessage = useCallback(
    async (message, webSearchEnabled = false, hideQuery = false) => {
      if (!message || !message.trim()) return;
      const conversationId =
        currentConversationId || `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      if (!currentConversationId) {
        setCurrentConversationId(conversationId);
      }

      const userMessage = { role: 'user', content: message };

      if (!hideQuery) {
        setMessages((prev) => [...prev, userMessage]);
      }
      setLoading(true);

      try {
        const token = localStorage.getItem('token');
        const response = await chatAPI.send(
          {
            user_id: userId,
            message,
            conversation_id: conversationId,
            include_web_search: webSearchEnabled,
          },
          token
        );

        const assistantMessage = {
          role: 'assistant',
          content: response.data.response,
          sources: response.data.sources || [],
        };
        setMessages((prev) => [...prev, assistantMessage]);

        saveConversationHistory(conversationId, [userMessage, assistantMessage]);
        await loadConversations();
        await loadSubscriptionStatus();
      } catch (error) {
        setMessages((prev) => prev.slice(0, -1));

        if (error.response?.status === 403) {
          const detail = error.response.data.detail || error.response.data;
          if (detail.upgrade_required) {
            setLimitType(detail.reason || 'limit_exceeded');
            setShowUpgradeModal(true);
          } else {
            alert(detail.message || 'Message limit reached. Please upgrade your plan.');
          }
        } else if (error.response?.status === 429) {
          alert('Too many requests. Please wait a moment and try again.');
        } else if (error.response?.status === 401) {
          alert('Session expired. Please login again.');
          router.push('/signin');
        } else {
          const errorMsg = error.response?.data?.detail || error.message || 'Failed to send message. Please try again.';
          alert(errorMsg);
        }
      } finally {
        setLoading(false);
      }
    },
    [currentConversationId, userId, loadConversations, loadSubscriptionStatus, router]
  );
  const handleFileSelect = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    try {
      let result;
      if (file.type.startsWith('image/')) {
        result = await ocrAPI.processImage(formData);
        const ocrMessage = `[Uploaded Image]\n\nExtracted text:\n${result.data.text}`;
        handleSendMessage(ocrMessage);
      } else if (file.type === 'application/pdf') {
        formData.append('document_name', file.name);
        result = await pdfAPI.uploadPDF(formData);
        const pdfMessage = `[Uploaded PDF: ${file.name}]\n\n${result.data.summary}`;
        handleSendMessage(pdfMessage);
      }
    } catch (error) {
      console.error('File upload failed:', error);
      alert(`Failed to process file: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentConversationId(null);
    setSidebarOpen(false);
  };

  const handleAdminClick = () => {
    router.push('/admin');
  };

  const handleEditProfile = () => {
    setShowProfile(true);
  };

  return (
    <LayoutShell
      sidebarProps={{
        isOpen: sidebarOpen,
        onClose: () => setSidebarOpen(false),
        conversations,
        onNewChat: handleNewChat,
        onSelectConversation: loadConversation,
        onAdminClick: handleAdminClick,
        onSettingsClick: () => setShowSettings(true),
        onEditProfile: handleEditProfile,
        onConversationDeleted: (id) => {
          loadConversations();
          if (currentConversationId === id) {
            setCurrentConversationId(null);
            setMessages([]);
          }
        },
        user,
      }}
      header={
        <UpgradeModal
          isOpen={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
          currentTier={subscriptionStatus?.tier}
          limitType={limitType}
        />
      }
    >
      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{user?.email || 'Customize your experience'}</p>
              </div>
              <button
                onClick={() => setShowSettings(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* User Info */}
              <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                {user?.image ? (
                  <Image src={user.image} alt="Profile" width={64} height={64} className="w-16 h-16 rounded-full object-cover" />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                    <User className="text-white" size={32} />
                  </div>
                )}
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">{user?.name || 'User'}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{user?.email}</p>
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => router.push('/upgrade')}
                  className="p-4 border-2 border-blue-500 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition text-left"
                >
                  <div className="text-2xl mb-2">💎</div>
                  <div className="font-semibold text-gray-900 dark:text-white">Upgrade Plan</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Get unlimited access</div>
                </button>
                
                <button
                  onClick={() => window.open('https://docs.mydost.ai', '_blank')}
                  className="p-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition text-left"
                >
                  <div className="text-2xl mb-2">❓</div>
                  <div className="font-semibold text-gray-900 dark:text-white">Help Center</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Get support</div>
                </button>
              </div>

              {!isGuest && (
                <button
                  onClick={handleClearMemories}
                  className="w-full p-4 border-2 border-red-500 text-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition font-semibold"
                >
                  Clear all memories & conversations
                </button>
              )}
              
              {/* Language & Preferences */}
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Language</h3>
                <div className="grid grid-cols-3 gap-2">
                  {['English', 'हिंदी', 'অসমীয়া'].map((lang) => (
                    <button
                      key={lang}
                      className="p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-500 transition text-center"
                    >
                      <span className="text-gray-900 dark:text-white">{lang}</span>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Logout Button */}
              <button
                onClick={() => {
                  localStorage.removeItem('token');
                  localStorage.removeItem('user');
                  window.location.href = '/signin';
                }}
                className="w-full p-4 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-semibold"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Profile Panel */}
      <ProfilePanel
        isOpen={showProfile}
        onClose={() => setShowProfile(false)}
        userId={userId}
        onSaved={handleProfileSaved}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-[#f5f6f8]">
        {/* Header */}
        <div className="border-b border-slate-200 bg-[#f5f6f8] p-3 sm:p-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="md:hidden btn-icon p-2"
          >
            <Menu size={24} />
          </button>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">MyDost</h1>
          <div className="flex items-center gap-2 sm:gap-4">
            {isGuest ? (
              <button
                onClick={() => router.push('/signup')}
                className="text-xs sm:text-sm bg-slate-900 hover:bg-slate-800 text-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg font-medium whitespace-nowrap"
              >
                Sign Up
              </button>
            ) : (
              <>
                {subscriptionStatus && (
                  <div className="text-xs sm:text-sm hidden sm:block">
                    <span className="font-medium text-slate-900">
                      {subscriptionStatus.tier === 'free' ? 'Free Plan' : 
                       subscriptionStatus.tier === 'limited' ? 'Limited Plan' :
                       subscriptionStatus.tier === 'unlimited' ? 'Unlimited Plan' : 'Guest'}
                    </span>
                    <span className="text-slate-500 ml-2">
                      {subscriptionStatus.messages_used} / {subscriptionStatus.message_limit === null ? '∞' : subscriptionStatus.message_limit}
                    </span>
                  </div>
                )}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-slate-600 hover:text-slate-900"
                >
                  <LogOut size={16} />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Guest Signup Banner */}
        {isGuest && (
          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-3 sm:px-4 py-2 sm:py-3 flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-3 flex-1">
              <span className="text-xl sm:text-2xl flex-shrink-0">🎁</span>
              <div className="min-w-0">
                <p className="font-medium text-sm sm:text-base">Sign up for 10 free messages!</p>
                <p className="text-xs sm:text-sm text-blue-100 hidden sm:block">Save your conversations and unlock more features</p>
              </div>
            </div>
            <button
              onClick={() => router.push('/signup')}
              className="bg-white text-blue-600 px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-sm sm:text-base font-medium hover:bg-blue-50 transition flex-shrink-0 ml-2"
            >
              Sign Up
            </button>
          </div>
        )}

        {/* Chat Window */}
        <ChatWindow 
          messages={messages} 
          loading={loading} 
          onSendMessage={handleSendMessage}
          onAstrologyClick={() => setShowAstrologyModal(true)}
          onNewChat={handleNewChat}
        />

        {/* Astrology Modal */}
        <AstrologyModal
          isOpen={showAstrologyModal}
          onClose={() => setShowAstrologyModal(false)}
          onSubmit={handleSendMessage}
        />

        {/* Input Bar */}
        <InputBar
          onSend={handleSendMessage}
          loading={loading}
          onFileSelect={handleFileSelect}
        />
      </div>
    </LayoutShell>
  );
}

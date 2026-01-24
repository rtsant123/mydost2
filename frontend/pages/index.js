import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Menu, LogOut } from 'lucide-react';
import ChatWindow from '@/components/ChatWindow';
import InputBar from '@/components/InputBar';
import Sidebar from '@/components/Sidebar';
import UpgradeModal from '@/components/UpgradeModal';
import { chatAPI, ocrAPI, pdfAPI } from '@/utils/apiClient';
import { saveConversationHistory, getConversationHistory, formatDate } from '@/utils/storage';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    // Check if token is in URL (from Google OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
      // Save token from OAuth and clean URL
      localStorage.setItem('token', tokenFromUrl);
      window.history.replaceState({}, document.title, '/');
    }
    
    const token = tokenFromUrl || localStorage.getItem('token');
    
    if (!token) {
      router.push('/signup');
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
      localStorage.removeItem('user');
      router.push('/signin');
    }
  };

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

  useEffect(() => {
    if (user) {
      setUserId(user.user_id);
      loadSubscriptionStatus();
    }
  }, [user]);

  const loadSubscriptionStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/subscription/status/${user.user_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSubscriptionStatus(response.data);
    } catch (error) {
      console.error('Failed to load subscription:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/signin');
  };

  // Load conversations on mount
  useEffect(() => {
    if (userId) {
      loadConversations();
    }
  }, [userId]);

  const loadConversations = async () => {
    try {
      const response = await chatAPI.listConversations(userId);
      setConversations(response.data.conversations || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const response = await chatAPI.getConversation(conversationId);
      setMessages(response.data.messages || []);
      setCurrentConversationId(conversationId);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleSendMessage = async (message) => {
    const conversationId = currentConversationId || `conv_${Date.now()}`;
    setCurrentConversationId(conversationId);

    // Add user message to UI
    const userMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await chatAPI.send({
        user_id: userId,
        message,
        conversation_id: conversationId,
        include_web_search: false,
      }, token);

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        sources: response.data.sources || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Save conversation
      saveConversationHistory(conversationId, [userMessage, assistantMessage]);
      await loadConversations();
      await loadSubscriptionStatus(); // Refresh usage
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Check if it's a subscription limit error
      if (error.response?.status === 403 && error.response?.data?.upgrade_required) {
        const detail = error.response.data.detail;
        setLimitType(detail.reason);
        setShowUpgradeModal(true);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `Error: ${error.response?.data?.detail || 'Failed to send message'}`,
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

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

  return (
    <div className="h-screen flex bg-white dark:bg-gray-900">
      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        currentTier={subscriptionStatus?.tier}
        limitType={limitType}
      />

      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        conversations={conversations}
        onNewChat={handleNewChat}
        onSelectConversation={loadConversation}
        onAdminClick={handleAdminClick}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="md:hidden btn-icon"
          >
            <Menu size={24} />
          </button>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">MyDost</h1>
          <div className="flex items-center gap-4">
            {subscriptionStatus && (
              <div className="text-sm">
                <span className="font-medium text-blue-600">
                  {subscriptionStatus.tier === 'free' ? 'Free Plan' : 
                   subscriptionStatus.tier === 'limited' ? 'Limited Plan' :
                   subscriptionStatus.tier === 'unlimited' ? 'Unlimited Plan' : 'Guest'}
                </span>
                <span className="text-gray-500 ml-2">
                  {subscriptionStatus.messages_used} / {subscriptionStatus.message_limit === null ? '∞' : subscriptionStatus.message_limit}
                </span>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>

        {/* Chat Window */}
        <ChatWindow messages={messages} loading={loading} />

        {/* Input Bar */}
        <InputBar
          onSend={handleSendMessage}
          loading={loading}
          onFileSelect={handleFileSelect}
        />
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useSession } from 'next-auth/react';
import { Menu } from 'lucide-react';
import ChatWindow from '@/components/ChatWindow';
import InputBar from '@/components/InputBar';
import Sidebar from '@/components/Sidebar';
import { chatAPI, ocrAPI, pdfAPI } from '@/utils/apiClient';
import { saveConversationHistory, getConversationHistory, formatDate } from '@/utils/storage';
import LandingPage from './landing';

export default function Home() {
  const { data: session, status } = useSession();
  
  // If not authenticated, show landing page
  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-lg text-white">Loading...</div>
      </div>
    );
  }
  
  if (!session) {
    return <LandingPage />;
  }
  
  // If authenticated, show chat page
  return <ChatPage />;
}

function ChatPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [userId, setUserId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  // Check if user has preferences
  useEffect(() => {
    if (!session) return;

    if (!session.user.has_preferences) {
      router.push('/preferences');
      return;
    }

    setUserId(session.user.id);
  }, [session, router]);

  // Load conversations on mount
  useEffect(() => {
    if (userId) {
      loadConversations();
    }
  }, [userId]);

  if (!userId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-lg text-white">Setting up your profile...</div>
      </div>
    );
  }

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
      const response = await chatAPI.send({
        user_id: userId,
        message,
        conversation_id: conversationId,
        include_web_search: false,
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        sources: response.data.sources || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Save conversation
      saveConversationHistory(conversationId, [userMessage, assistantMessage]);
      await loadConversations();
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.response?.data?.detail || 'Failed to send message'}`,
        },
      ]);
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
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {currentConversationId && conversations.find((c) => c.id === currentConversationId)?.created_at
              ? formatDate(conversations.find((c) => c.id === currentConversationId).created_at)
              : 'New Conversation'}
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

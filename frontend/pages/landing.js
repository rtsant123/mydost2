import React from 'react';
import { useRouter } from 'next/router';
import { MessageCircle, Brain, Lock, Zap, Globe, Shield } from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <nav className="flex justify-between items-center mb-16">
          <div className="flex items-center space-x-2">
            <MessageCircle className="w-8 h-8 text-purple-400" />
            <h1 className="text-2xl font-bold text-white">MyDost</h1>
          </div>
          <button
            onClick={() => router.push('/auth/signin')}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition"
          >
            Sign In
          </button>
        </nav>

        <div className="text-center mb-16">
          <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Your AI Friend with
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
              {' '}Perfect Memory
            </span>
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            MyDost remembers everything. Chat in Hindi, English, or Assamese. Get help with education, sports, astrology, and more.
          </p>
          <button
            onClick={() => router.push('/auth/signin')}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white text-lg rounded-lg font-bold shadow-lg transition transform hover:scale-105"
          >
            Get Started Free
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Brain className="w-12 h-12 text-purple-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Perfect Memory</h3>
            <p className="text-gray-300">
              Advanced RAG technology remembers all your conversations, PDFs, and preferences. Never repeat yourself.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Globe className="w-12 h-12 text-blue-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Multilingual</h3>
            <p className="text-gray-300">
              Speak naturally in Hindi, Assamese, or English. MyDost understands and responds in your language.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Zap className="w-12 h-12 text-yellow-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Multi-Domain Expert</h3>
            <p className="text-gray-300">
              Education, sports, teer results, astrology, news, and web search - all in one place.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Lock className="w-12 h-12 text-green-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Private & Secure</h3>
            <p className="text-gray-300">
              Your data is encrypted and stored securely. Only you have access to your conversations.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <MessageCircle className="w-12 h-12 text-pink-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Personalized</h3>
            <p className="text-gray-300">
              Choose your preferred tone, interests, and response style. MyDost adapts to you.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Shield className="w-12 h-12 text-indigo-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Always Learning</h3>
            <p className="text-gray-300">
              Upload PDFs, save notes, search the web. MyDost grows smarter with every interaction.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 backdrop-blur-lg rounded-2xl p-12 text-center border border-white/20">
          <h3 className="text-3xl font-bold text-white mb-4">
            Ready to experience the future of AI chat?
          </h3>
          <p className="text-gray-300 mb-8 text-lg">
            Join thousands of users who trust MyDost for personalized AI assistance
          </p>
          <button
            onClick={() => router.push('/auth/signin')}
            className="px-10 py-4 bg-white text-purple-900 text-lg rounded-lg font-bold shadow-lg hover:bg-gray-100 transition transform hover:scale-105"
          >
            Start Chatting Now →
          </button>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-gray-400 text-sm">
          <p>© 2026 MyDost. Your friendly AI assistant with perfect memory.</p>
        </div>
      </div>
    </div>
  );
}

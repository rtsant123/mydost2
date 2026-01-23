import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { ArrowLeft, Save, RefreshCw } from 'lucide-react';
import { adminAPI } from '@/utils/apiClient';
import { getAdminToken, setAdminToken, clearAdminToken } from '@/utils/storage';
import '@/styles/globals.css';

export default function AdminPage() {
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [config, setConfig] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = getAdminToken();
    if (token) {
      setAuthenticated(true);
      loadConfig();
      loadStats();
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await adminAPI.login(password);
      setAdminToken(response.data.token);
      setAuthenticated(true);
      setPassword('');
      setMessage('Login successful!');
      loadConfig();
      loadStats();
    } catch (error) {
      setMessage(`Login failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  const loadConfig = async () => {
    try {
      const response = await adminAPI.getConfig();
      setConfig(response.data);
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await adminAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleToggleModule = async (module, enabled) => {
    try {
      await adminAPI.toggleModule(module, !enabled);
      setMessage(`${module} ${!enabled ? 'enabled' : 'disabled'}`);
      loadConfig();
    } catch (error) {
      setMessage(`Failed to toggle module: ${error.message}`);
    }
  };

  const handleSaveSystemPrompt = async (newPrompt) => {
    try {
      await adminAPI.updateSystemPrompt(newPrompt);
      setMessage('System prompt updated');
      loadConfig();
    } catch (error) {
      setMessage(`Failed to update prompt: ${error.message}`);
    }
  };

  const handleClearCache = async () => {
    try {
      await adminAPI.clearCache();
      setMessage('Cache cleared');
      loadStats();
    } catch (error) {
      setMessage(`Failed to clear cache: ${error.message}`);
    }
  };

  const handleLogout = () => {
    clearAdminToken();
    setAuthenticated(false);
    setConfig(null);
    setStats(null);
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-600 to-blue-600 flex items-center justify-center p-4">
        <form
          onSubmit={handleLogin}
          className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">
            Admin Panel
          </h1>

          {message && (
            <div className={`p-3 rounded mb-4 text-sm ${
              message.includes('successful')
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}>
              {message}
            </div>
          )}

          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">
              Admin Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter admin password"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            className="btn-primary w-full"
          >
            Login
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="btn-icon text-gray-600 dark:text-gray-400"
            >
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Admin Panel
            </h1>
          </div>
          <button
            onClick={handleLogout}
            className="btn-secondary"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {message && (
          <div className={`p-4 rounded-lg mb-6 ${
            message.includes('successful') || message.includes('updated') || message.includes('enabled') || message.includes('disabled')
              ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200'
              : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200'
          }`}>
            {message}
          </div>
        )}

        {/* Module Toggles */}
        {config && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6 shadow">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Feature Modules
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(config.enabled_modules).map(([module, enabled]) => (
                <div
                  key={module}
                  className="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-700 rounded"
                >
                  <span className="font-semibold text-gray-800 dark:text-gray-200">
                    {module.charAt(0).toUpperCase() + module.slice(1)}
                  </span>
                  <button
                    onClick={() => handleToggleModule(module, enabled)}
                    className={`px-4 py-2 rounded transition ${
                      enabled
                        ? 'bg-green-500 hover:bg-green-600 text-white'
                        : 'bg-gray-400 hover:bg-gray-500 text-white'
                    }`}
                  >
                    {enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* System Prompt */}
        {config && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6 shadow">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              System Prompt
            </h2>
            <SystemPromptEditor
              prompt={config.system_prompt}
              onSave={handleSaveSystemPrompt}
            />
          </div>
        )}

        {/* Usage Statistics */}
        {stats && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6 shadow">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Usage Statistics
              </h2>
              <button
                onClick={loadStats}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatCard
                title="Total Messages"
                value={stats.usage_stats?.total_messages || 0}
              />
              <StatCard
                title="API Calls"
                value={stats.usage_stats?.total_api_calls || 0}
              />
              <StatCard
                title="Tokens Used"
                value={stats.usage_stats?.total_tokens || 0}
              />
            </div>
          </div>
        )}

        {/* Cache Management */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
            Cache Management
          </h2>
          <button
            onClick={handleClearCache}
            className="btn-primary flex items-center gap-2"
          >
            <RefreshCw size={20} />
            Clear All Caches
          </button>
        </div>
      </div>
    </div>
  );
}

function SystemPromptEditor({ prompt, onSave }) {
  const [editing, setEditing] = useState(false);
  const [newPrompt, setNewPrompt] = useState(prompt);

  return (
    <div>
      <textarea
        value={newPrompt}
        onChange={(e) => setNewPrompt(e.target.value)}
        disabled={!editing}
        rows={6}
        className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:opacity-50 font-mono text-sm"
      />
      <div className="mt-4 flex gap-2">
        {!editing ? (
          <button
            onClick={() => setEditing(true)}
            className="btn-primary"
          >
            Edit
          </button>
        ) : (
          <>
            <button
              onClick={() => {
                onSave(newPrompt);
                setEditing(false);
              }}
              className="btn-primary flex items-center gap-2"
            >
              <Save size={16} />
              Save
            </button>
            <button
              onClick={() => {
                setNewPrompt(prompt);
                setEditing(false);
              }}
              className="btn-secondary"
            >
              Cancel
            </button>
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value }) {
  return (
    <div className="bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-900 dark:to-blue-900 p-4 rounded-lg">
      <p className="text-gray-600 dark:text-gray-400 text-sm font-semibold">
        {title}
      </p>
      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
        {value.toLocaleString()}
      </p>
    </div>
  );
}

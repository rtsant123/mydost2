import React, { useState } from 'react';
import { Search, CheckCircle, XCircle, Loader } from 'lucide-react';
import apiClient from '../../utils/apiClient';

export default function WebSearchTest() {
  const [query, setQuery] = useState('India vs Australia cricket match today');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState('');

  const testQueries = [
    'India vs Australia cricket live score today',
    'IPL 2026 match schedule',
    'Messi latest news',
    'Champions League final 2026',
    'Today news headlines',
    'Weather in Mumbai',
    'Bitcoin price today'
  ];

  const testSearch = async () => {
    setLoading(true);
    setResult(null);
    setProvider('');

    try {
      const response = await apiClient.post('/api/chat', {
        user_id: localStorage.getItem('user_id') || 'test_' + Date.now(),
        message: query,
        include_web_search: true
      });

      setResult({
        success: true,
        response: response.data.response,
        sources: response.data.sources || [],
        provider: response.data.search_provider || 'Unknown'
      });
      setProvider(response.data.search_provider || 'Unknown');
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-teal-500 rounded-2xl flex items-center justify-center">
              <Search size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Web Search Test</h1>
              <p className="text-gray-600 dark:text-gray-400">Test DuckDuckGo & paid API search</p>
            </div>
          </div>

          {/* Quick Test Queries */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Quick Test Queries (Click to use)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {testQueries.map((q) => (
                <button
                  key={q}
                  onClick={() => setQuery(q)}
                  className="p-3 text-left rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all text-sm"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Query Input */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Enter your search query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., India vs Australia cricket match today"
              rows={3}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-green-500 focus:outline-none"
            />
          </div>

          <button
            onClick={testSearch}
            disabled={loading || !query.trim()}
            className="w-full py-4 bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white font-bold rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={20} />
                Testing Search...
              </>
            ) : (
              <>
                <Search size={20} />
                Test Web Search
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className={`rounded-2xl shadow-xl p-6 ${result.success ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'}`}>
            <div className="flex items-center gap-3 mb-4">
              {result.success ? (
                <CheckCircle size={32} className="text-green-600" />
              ) : (
                <XCircle size={32} className="text-red-600" />
              )}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {result.success ? '✅ Search Successful!' : '❌ Search Failed'}
                </h2>
                {provider && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Provider: <strong>{provider}</strong>
                  </p>
                )}
              </div>
            </div>

            {result.success ? (
              <>
                {/* Response */}
                <div className="mb-6">
                  <h3 className="font-bold text-lg mb-2 text-gray-900 dark:text-white">AI Response:</h3>
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-4 prose dark:prose-invert max-w-none">
                    {result.response}
                  </div>
                </div>

                {/* Sources */}
                {result.sources && result.sources.length > 0 && (
                  <div>
                    <h3 className="font-bold text-lg mb-2 text-gray-900 dark:text-white">Sources:</h3>
                    <div className="space-y-2">
                      {result.sources.map((source, idx) => (
                        <div key={idx} className="bg-white dark:bg-gray-800 rounded-xl p-4">
                          <div className="flex items-start gap-3">
                            <span className="text-lg font-bold text-green-600">[{source.number || idx + 1}]</span>
                            <div>
                              <a
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-semibold text-blue-600 hover:underline"
                              >
                                {source.title}
                              </a>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{source.source}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-4">
                <p className="text-red-600 dark:text-red-400">{result.error}</p>
              </div>
            )}
          </div>
        )}

        {/* Info */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mt-6">
          <h3 className="font-bold text-lg mb-3 text-gray-900 dark:text-white">🔍 Search Providers</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🦆</span>
              <div>
                <strong className="text-gray-900 dark:text-white">DuckDuckGo (FREE)</strong>
                <p className="text-gray-600 dark:text-gray-400">
                  Default provider - No API key needed, unlimited searches
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">🔍</span>
              <div>
                <strong className="text-gray-900 dark:text-white">Serper/SerpApi (Fallback)</strong>
                <p className="text-gray-600 dark:text-gray-400">
                  Used if DuckDuckGo fails and API key is configured
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

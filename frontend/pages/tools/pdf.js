import React, { useState } from 'react';
import { Upload, FileText, Download, Trash2, Eye } from 'lucide-react';
import apiClient from '../../utils/apiClient';

export default function PDFTools() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('summarize'); // summarize, chat, extract

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleProcess = async () => {
    if (!file) {
      setError('Please select a PDF file first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', localStorage.getItem('user_id') || 'guest_' + Date.now());
      formData.append('document_name', file.name);

      const response = await apiClient.post('/api/pdf/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process PDF');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl flex items-center justify-center">
              <FileText size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">PDF Tools</h1>
              <p className="text-gray-600 dark:text-gray-400">Upload, summarize, and chat with your PDFs</p>
            </div>
          </div>

          {/* Mode Selection */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <button
              onClick={() => setMode('summarize')}
              className={`p-4 rounded-xl border-2 transition-all ${
                mode === 'summarize'
                  ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-red-300'
              }`}
            >
              <FileText className="mx-auto mb-2" size={24} />
              <div className="font-semibold">Summarize</div>
              <div className="text-xs text-gray-500">Get quick summary</div>
            </button>
            <button
              onClick={() => setMode('chat')}
              className={`p-4 rounded-xl border-2 transition-all ${
                mode === 'chat'
                  ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-red-300'
              }`}
            >
              <Eye className="mx-auto mb-2" size={24} />
              <div className="font-semibold">Chat</div>
              <div className="text-xs text-gray-500">Ask questions</div>
            </button>
            <button
              onClick={() => setMode('extract')}
              className={`p-4 rounded-xl border-2 transition-all ${
                mode === 'extract'
                  ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-red-300'
              }`}
            >
              <Download className="mx-auto mb-2" size={24} />
              <div className="font-semibold">Extract Text</div>
              <div className="text-xs text-gray-500">Get all text</div>
            </button>
          </div>

          {/* File Upload */}
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
              id="pdf-upload"
            />
            <label htmlFor="pdf-upload" className="cursor-pointer">
              <Upload size={48} className="mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {file ? file.name : 'Click to upload PDF'}
              </p>
              <p className="text-sm text-gray-500">Maximum file size: 10MB</p>
            </label>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          {file && (
            <button
              onClick={handleProcess}
              disabled={loading}
              className="w-full mt-4 py-4 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white font-bold rounded-xl transition-all disabled:opacity-50"
            >
              {loading ? '⏳ Processing...' : `📄 ${mode === 'summarize' ? 'Summarize' : mode === 'chat' ? 'Start Chat' : 'Extract Text'}`}
            </button>
          )}
        </div>

        {/* Results */}
        {result && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Result</h2>
            <div className="prose dark:prose-invert max-w-none">
              <pre className="whitespace-pre-wrap bg-gray-50 dark:bg-gray-900 p-4 rounded-xl">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-2xl p-6 mt-6">
          <h3 className="font-bold text-lg mb-3 text-gray-900 dark:text-white">💡 Tips</h3>
          <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li>✅ Best for documents up to 100 pages</li>
            <li>✅ Supports English, Hindi, and Hinglish PDFs</li>
            <li>✅ Premium users: Chat history is saved forever</li>
            <li>✅ Free users: 10 PDFs per day</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

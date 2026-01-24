import React, { useState, useRef } from 'react';
import { Upload, FileImage, Download, Copy, Zap } from 'lucide-react';

export default function OCRTool() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('eng+hin'); // English + Hindi
  const canvasRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const extractText = async () => {
    if (!image) return;

    setLoading(true);
    try {
      // Use Tesseract.js (client-side OCR - FREE!)
      const Tesseract = (await import('tesseract.js')).default;
      
      const result = await Tesseract.recognize(
        preview,
        language,
        {
          logger: (m) => {
            if (m.status === 'recognizing text') {
              console.log(`Progress: ${Math.round(m.progress * 100)}%`);
            }
          }
        }
      );

      setExtractedText(result.data.text);
    } catch (error) {
      console.error('OCR error:', error);
      alert('Failed to extract text. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyText = () => {
    navigator.clipboard.writeText(extractedText);
    alert('✅ Text copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center">
              <FileImage size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">OCR - Text Extraction</h1>
              <p className="text-gray-600 dark:text-gray-400">Extract text from images (English, Hindi, Hinglish)</p>
            </div>
          </div>

          {/* Language Selection */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Select Language
            </label>
            <div className="grid grid-cols-4 gap-3">
              {[
                { value: 'eng', label: 'English' },
                { value: 'hin', label: 'Hindi (हिंदी)' },
                { value: 'eng+hin', label: 'Hinglish (Both)' },
                { value: 'ben', label: 'Bengali (বাংলা)' }
              ].map((lang) => (
                <button
                  key={lang.value}
                  onClick={() => setLanguage(lang.value)}
                  className={`p-3 rounded-xl border-2 transition-all ${
                    language === lang.value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                  }`}
                >
                  <div className="font-semibold text-sm">{lang.label}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Upload Image</h2>
            
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center mb-4">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                <Upload size={48} className="mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Click to upload image
                </p>
                <p className="text-sm text-gray-500">JPG, PNG, WebP</p>
              </label>
            </div>

            {preview && (
              <div className="mb-4">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full rounded-xl border-2 border-gray-200 dark:border-gray-700"
                />
              </div>
            )}

            {image && (
              <button
                onClick={extractText}
                disabled={loading}
                className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-bold rounded-xl transition-all disabled:opacity-50"
              >
                {loading ? '⏳ Extracting...' : '🔍 Extract Text'}
              </button>
            )}
          </div>

          {/* Result Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Extracted Text</h2>
              {extractedText && (
                <button
                  onClick={copyText}
                  className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-all"
                >
                  <Copy size={16} />
                  Copy
                </button>
              )}
            </div>

            <textarea
              value={extractedText}
              onChange={(e) => setExtractedText(e.target.value)}
              placeholder="Extracted text will appear here..."
              className="w-full h-96 p-4 border-2 border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-blue-500 focus:outline-none resize-none"
            />
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-2xl p-6 mt-6">
          <div className="flex items-start gap-3">
            <Zap size={24} className="text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-bold text-lg mb-2 text-gray-900 dark:text-white">✨ Features</h3>
              <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                <li>✅ <strong>100% Free</strong> - Runs in your browser, no API costs!</li>
                <li>✅ <strong>Multi-language</strong> - English, Hindi, Bengali, Hinglish</li>
                <li>✅ <strong>Fast & Accurate</strong> - Powered by Tesseract.js</li>
                <li>✅ <strong>Privacy</strong> - Images never leave your device</li>
                <li>✅ <strong>Premium users</strong> - Extracted text saved in history</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

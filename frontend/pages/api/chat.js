// Import Anthropic SDK for server-side usage
const { Anthropic } = require('@anthropic-ai/sdk');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, user_id, conversation_id } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Strategy 1: Try to call backend service
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.RAILWAY_BACKEND_URL || 'http://backend:8000';
    
    try {
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
        timeout: 5000,
      });

      if (response.ok) {
        const data = await response.json();
        return res.status(200).json({
          response: data.response,
          sources: data.sources || [],
          conversation_id: conversation_id || `conv_${Date.now()}`,
          user_id: user_id || 'anonymous',
        });
      }
    } catch (backendError) {
      console.log('Backend unreachable, falling back to direct Anthropic:', backendError.message);
    }

    // Strategy 2: Fallback - call Anthropic directly from frontend/backend server
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: 'API key not configured' });
    }

    const client = new Anthropic({ apiKey });
    const response = await client.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      system: 'You are MyDost, a helpful AI assistant. Answer questions about education, sports, and general knowledge. Be friendly and concise.',
      messages: [{ role: 'user', content: message }],
    });

    const assistantMessage = response.content[0].type === 'text' ? response.content[0].text : '';

    return res.status(200).json({
      response: assistantMessage,
      sources: [],
      conversation_id: conversation_id || `conv_${Date.now()}`,
      user_id: user_id || 'anonymous',
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return res.status(500).json({
      error: error.message || 'Failed to process chat request',
    });
  }
}

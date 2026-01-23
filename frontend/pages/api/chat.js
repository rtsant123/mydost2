export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, user_id, conversation_id } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Call the backend API instead of using Anthropic SDK directly
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://mydost2-backend-production.up.railway.app';
    
    const response = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return res.status(response.status).json({
        error: errorData.detail || 'Backend chat request failed',
      });
    }

    const data = await response.json();

    return res.status(200).json({
      response: data.response,
      sources: data.sources || [],
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

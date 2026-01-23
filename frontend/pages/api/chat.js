export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, user_id, conversation_id } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Get API key from environment
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      console.error('ANTHROPIC_API_KEY not set in frontend environment');
      return res.status(500).json({ error: 'API key not configured on frontend' });
    }

    // Import Anthropic SDK dynamically to avoid build issues
    const { Anthropic } = await import('@anthropic-ai/sdk');
    const client = new Anthropic({ apiKey });

    const response = await client.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      system: 'You are MyDost, a helpful AI assistant. Answer questions about education, sports, and general knowledge. Be friendly and concise.',
      messages: [{ role: 'user', content: message }],
    });

    const assistantMessage = response.content[0].type === 'text' ? response.content[0].text : 'No response';

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
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    });
  }
}

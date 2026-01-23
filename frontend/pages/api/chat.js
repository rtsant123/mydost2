export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, user_id, conversation_id } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Call the backend service (Python FastAPI)
    // Railway internal network: http://backend:8000
    // Or use public URL if backend is exposed
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://backend:8000';
    
    console.log(`Calling backend at: ${backendUrl}/api/chat`);

    const response = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id, conversation_id }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error: ${response.status} - ${errorText}`);
      return res.status(response.status).json({
        error: `Backend error: ${response.statusText}`,
      });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error('Chat API error:', error.message);
    return res.status(500).json({
      error: error.message || 'Failed to reach backend service',
    });
  }
}

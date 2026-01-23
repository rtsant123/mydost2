const conversations = {};

export default function handler(req, res) {
  if (req.method === 'GET') {
    const { user_id } = req.query;
    const userId = user_id || 'anonymous-user';

    const userConvos = Object.values(conversations)
      .filter((conv) => conv.user_id === userId)
      .map((conv) => ({
        id: conv.id,
        created_at: conv.created_at,
        updated_at: conv.updated_at,
        message_count: conv.messages ? conv.messages.length : 0,
        preview: conv.messages?.[0]?.content?.substring(0, 100) || 'Empty',
      }));

    return res.status(200).json({ conversations: userConvos });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}

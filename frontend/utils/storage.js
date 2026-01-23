import Cookies from 'js-cookie';

// Admin token management
export const getAdminToken = () => Cookies.get('admin_token');
export const setAdminToken = (token) => Cookies.set('admin_token', token, { expires: 7 });
export const clearAdminToken = () => Cookies.remove('admin_token');

// User ID management
export const getUserId = () => {
  if (typeof window === 'undefined') return null;
  let userId = localStorage.getItem('user_id');
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('user_id', userId);
  }
  return userId;
};

// Conversation history
export const getConversationHistory = (conversationId) => {
  if (typeof window === 'undefined') return [];
  const key = `conversation_${conversationId}`;
  const stored = localStorage.getItem(key);
  return stored ? JSON.parse(stored) : [];
};

export const saveConversationHistory = (conversationId, messages) => {
  if (typeof window === 'undefined') return;
  const key = `conversation_${conversationId}`;
  localStorage.setItem(key, JSON.stringify(messages));
};

// Notes
export const getNotes = () => {
  if (typeof window === 'undefined') return [];
  const stored = localStorage.getItem('user_notes');
  return stored ? JSON.parse(stored) : [];
};

export const saveNote = (note) => {
  if (typeof window === 'undefined') return note;
  const notes = getNotes();
  const id = note.id || `note_${Date.now()}`;
  const newNote = { ...note, id, createdAt: new Date().toISOString() };
  notes.push(newNote);
  localStorage.setItem('user_notes', JSON.stringify(notes));
  return newNote;
};

export const deleteNote = (noteId) => {
  if (typeof window === 'undefined') return;
  let notes = getNotes();
  notes = notes.filter(n => n.id !== noteId);
  localStorage.setItem('user_notes', JSON.stringify(notes));
};

// Format date
export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Format time
export const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

import { Session, Message, ChatRequest, ChatResponse } from '@/types/chat';
import { api } from "./api";



export const chatService = {
  /**
   * Get all chat sessions for user
   */
  getSessions: async (electricityId: string): Promise<Session[]> => {
    const response = await api.get('/api/v1/chat/sessions', {
      params: { electricity_id: electricityId }
    });
    return response.data;
  },

  /**
   * Get messages for a specific session
   */
  getMessages: async (sessionId: string, limit = 50, offset = 0): Promise<Message[]> => {
    const response = await api.get(`/api/v1/chat/sessions/${sessionId}/messages`, {
      params: { limit, offset }
    });
    return response.data;
  },

  /**
   * Send a message (creates session if sessionId not provided)
   */
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/api/v1/chat/message', data);
    return response.data;
  },

  /**
   * Create a new chat session
   */
  createSession: async (electricityId: string, title?: string): Promise<Session> => {
    const response = await api.post('/api/v1/chat/sessions', null, {
      params: { 
        electricity_id: electricityId,
        title: title || `Chat ${new Date().toLocaleDateString()}`
      }
    });
    return response.data;
  },

  /**
   * Delete a session
   */
  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/api/v1/chat/sessions/${sessionId}`);
  },
};
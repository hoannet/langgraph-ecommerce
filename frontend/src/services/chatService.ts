/**
 * Chat API service
 */

import apiClient from './api';
import { ChatRequest, ChatResponse, ChatHistoryResponse } from '../types/api';

export const chatService = {
    /**
     * Send a chat message
     */
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        const response = await apiClient.post<ChatResponse>('/chat/', request);
        return response.data;
    },

    /**
     * Get chat history for a session
     */
    async getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
        const response = await apiClient.get<ChatHistoryResponse>(`/chat/${sessionId}/history`);
        return response.data;
    },

    /**
     * Clear chat history for a session
     */
    async clearChatHistory(sessionId: string): Promise<{ message: string }> {
        const response = await apiClient.post<{ message: string }>(`/chat/${sessionId}/clear`);
        return response.data;
    },
};

export default chatService;

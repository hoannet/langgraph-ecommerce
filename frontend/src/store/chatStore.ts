/**
 * Zustand store for chat state management
 */

import { create } from 'zustand';
import { Message, ChatState } from '../types/chat';
import { MessageRole } from '../types/api';
import chatService from '../services/chatService';

interface ChatStore extends ChatState {
    // Actions
    sendMessage: (content: string) => Promise<void>;
    clearHistory: () => Promise<void>;
    loadHistory: () => Promise<void>;
    setError: (error: string | null) => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
    // Initial state
    messages: [],
    sessionId: null,
    isLoading: false,
    error: null,

    // Actions
    sendMessage: async (content: string) => {
        try {
            set({ isLoading: true, error: null });

            // Add user message to UI immediately
            const userMessage: Message = {
                id: Date.now().toString(),
                role: MessageRole.USER,
                content,
                timestamp: new Date(),
            };

            set((state) => ({
                messages: [...state.messages, userMessage],
            }));

            // Send to backend
            const response = await chatService.sendMessage({
                message: content,
                session_id: get().sessionId || undefined,
            });

            // Parse response for structured data
            const { parseProducts, parseOrder, parsePayment } = await import('../utils/responseParser');

            const productData = parseProducts(response.message, response.intent);
            const orderData = parseOrder(response.message, response.intent);
            const paymentData = parsePayment(response.message, response.intent);

            // Add assistant response
            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: MessageRole.ASSISTANT,
                content: response.message,
                timestamp: new Date(response.timestamp),
                intent: response.intent,
                intentConfidence: response.metadata?.intent_confidence,
                productData,
                orderData,
                paymentData,
            };

            set((state) => ({
                messages: [...state.messages, assistantMessage],
                sessionId: response.session_id,
                isLoading: false,
            }));
        } catch (error) {
            console.error('Failed to send message:', error);
            set({
                error: 'Failed to send message. Please try again.',
                isLoading: false,
            });
        }
    },

    clearHistory: async () => {
        const sessionId = get().sessionId;
        if (!sessionId) return;

        try {
            await chatService.clearChatHistory(sessionId);
            set({
                messages: [],
                sessionId: null,
                error: null,
            });
        } catch (error) {
            console.error('Failed to clear history:', error);
            set({ error: 'Failed to clear history.' });
        }
    },

    loadHistory: async () => {
        const sessionId = get().sessionId;
        if (!sessionId) return;

        try {
            const history = await chatService.getChatHistory(sessionId);
            const messages: Message[] = history.messages.map((msg, index) => ({
                id: `${Date.now()}-${index}`,
                role: msg.role as MessageRole,
                content: msg.content,
                timestamp: new Date(),
            }));

            set({ messages });
        } catch (error) {
            console.error('Failed to load history:', error);
            set({ error: 'Failed to load history.' });
        }
    },

    setError: (error: string | null) => {
        set({ error });
    },
}));

export default useChatStore;

/**
 * Frontend-specific chat types
 */

import { IntentType, MessageRole, Product, Order } from './api';

export interface Message {
    id: string;
    role: MessageRole;
    content: string;
    timestamp: Date;
    intent?: IntentType;
    intentConfidence?: number;
    paymentData?: {
        transactionId?: string;
        amount?: number;
        currency?: string;
        status?: string;
    };
    productData?: Product[];
    orderData?: Order;
}

export interface ChatState {
    messages: Message[];
    sessionId: string | null;
    isLoading: boolean;
    error: string | null;
    ragEnabled: boolean;
}

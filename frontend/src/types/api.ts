/**
 * API type definitions matching backend schemas
 */

export enum IntentType {
    GENERAL = 'GENERAL',
    PAYMENT = 'PAYMENT',
    FAQ = 'FAQ',
    ESCALATION = 'ESCALATION',
    PRODUCT_SEARCH = 'PRODUCT_SEARCH',
    ORDER = 'ORDER',
}

export enum PaymentStatus {
    PENDING = 'PENDING',
    PROCESSING = 'PROCESSING',
    COMPLETED = 'COMPLETED',
    FAILED = 'FAILED',
    CANCELLED = 'CANCELLED',
}

export enum MessageRole {
    USER = 'user',
    ASSISTANT = 'assistant',
    SYSTEM = 'system',
}

export interface ChatRequest {
    message: string;
    session_id?: string;
    metadata?: Record<string, any>;
    use_rag?: boolean;
}

export interface ChatResponse {
    message: string;
    session_id: string;
    intent?: IntentType;
    timestamp: string;
    metadata?: {
        intent_confidence?: number;
        [key: string]: any;
    };
}

export interface PaymentRequest {
    amount: number;
    currency?: string;
    description?: string;
    metadata?: Record<string, any>;
}

export interface PaymentResponse {
    transaction_id: string;
    status: PaymentStatus;
    amount: number;
    currency: string;
    message: string;
    timestamp: string;
}

export interface ChatHistoryMessage {
    role: string;
    content: string;
}

export interface ChatHistoryResponse {
    session_id: string;
    message_count: number;
    messages: ChatHistoryMessage[];
}

export interface TransactionStatusResponse {
    transaction_id: string;
    status: PaymentStatus;
    amount: number;
    currency: string;
    timestamp: string;
}

export interface Product {
    id: string;
    name: string;
    description: string;
    price: number;
    category: string;
    stock: number;
    image_url?: string;
}

export interface OrderItem {
    product_id: string;
    product_name: string;
    quantity: number;
    price: number;
    subtotal: number;
}

export enum OrderStatus {
    PENDING = 'pending',
    CONFIRMED = 'confirmed',
    PAID = 'paid',
    SHIPPED = 'shipped',
    DELIVERED = 'delivered',
    CANCELLED = 'cancelled',
}

export interface Order {
    id: string;
    session_id: string;
    items: OrderItem[];
    total: number;
    status: OrderStatus;
    payment_id?: string;
    created_at: string;
    updated_at: string;
}

/**
 * Order service for API calls
 */

import api from './api';
import { Order, OrderStatus } from '../types/api';

interface CreateOrderRequest {
    session_id: string;
    items: Array<{
        product_id: string;
        quantity: number;
    }>;
}

interface UpdateOrderStatusRequest {
    status: OrderStatus;
    payment_id?: string;
}

export const orderService = {
    /**
     * Create a new order
     */
    async createOrder(sessionId: string, items: Array<{ product_id: string; quantity: number }>): Promise<Order> {
        const request: CreateOrderRequest = {
            session_id: sessionId,
            items,
        };
        const response = await api.post('/orders', request);
        return response.data;
    },

    /**
     * Get order by ID
     */
    async getOrder(orderId: string): Promise<Order> {
        const response = await api.get(`/orders/${orderId}`);
        return response.data;
    },

    /**
     * Update order status
     */
    async updateOrderStatus(
        orderId: string,
        status: OrderStatus,
        paymentId?: string
    ): Promise<{ message: string }> {
        const request: UpdateOrderStatusRequest = {
            status,
            payment_id: paymentId,
        };
        const response = await api.patch(`/orders/${orderId}/status`, request);
        return response.data;
    },

    /**
     * Get all orders for a session
     */
    async getSessionOrders(sessionId: string): Promise<Order[]> {
        const response = await api.get(`/orders/session/${sessionId}`);
        return response.data;
    },
};

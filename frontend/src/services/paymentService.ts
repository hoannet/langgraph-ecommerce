/**
 * Payment API service
 */

import apiClient from './api';
import { PaymentRequest, PaymentResponse, TransactionStatusResponse } from '../types/api';

export const paymentService = {
    /**
     * Process a payment
     */
    async processPayment(request: PaymentRequest): Promise<PaymentResponse> {
        const response = await apiClient.post<PaymentResponse>('/payment/process', request);
        return response.data;
    },

    /**
     * Get transaction status
     */
    async getTransactionStatus(transactionId: string): Promise<TransactionStatusResponse> {
        const response = await apiClient.get<TransactionStatusResponse>(`/payment/${transactionId}`);
        return response.data;
    },
};

export default paymentService;

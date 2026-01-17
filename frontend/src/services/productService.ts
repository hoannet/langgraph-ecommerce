/**
 * Product service for API calls
 */

import api from './api';
import { Product } from '../types/api';

export const productService = {
    /**
     * List all products with optional category filter
     */
    async listProducts(category?: string, limit: number = 20): Promise<Product[]> {
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        params.append('limit', limit.toString());

        const response = await api.get(`/products?${params.toString()}`);
        return response.data;
    },

    /**
     * Get product by ID
     */
    async getProduct(productId: string): Promise<Product> {
        const response = await api.get(`/products/${productId}`);
        return response.data;
    },

    /**
     * Search products
     */
    async searchProducts(
        query?: string,
        category?: string,
        maxResults: number = 10
    ): Promise<Product[]> {
        const params = new URLSearchParams();
        if (query) params.append('query', query);
        if (category) params.append('category', category);
        params.append('max_results', maxResults.toString());

        const response = await api.post(`/products/search?${params.toString()}`);
        return response.data;
    },
};

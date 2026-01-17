/**
 * Utility to parse backend responses and extract structured data
 */

import { Product, Order, IntentType } from '../types/api';

/**
 * Parse product data from backend response
 * Looks for product information in the message text
 */
export function parseProducts(message: string, intent?: IntentType): Product[] | undefined {
    if (intent !== IntentType.PRODUCT_SEARCH) return undefined;

    // Try to extract product IDs from message
    // Format: "ID: prod_001"
    const productIdRegex = /ID:\s*(prod_\w+)/g;
    const matches = [...message.matchAll(productIdRegex)];

    if (matches.length === 0) return undefined;

    // Extract product details from formatted message
    // This is a simple parser - in production, backend should return structured JSON
    const products: Product[] = [];
    const productBlocks = message.split(/\d+\.\s+\*\*/).slice(1);

    productBlocks.forEach((block, index) => {
        const nameMatch = block.match(/^([^*]+)\*\*/);
        const priceMatch = block.match(/Price:\s*\$?([\d.]+)/);
        const categoryMatch = block.match(/Category:\s*(\w+)/);
        const stockMatch = block.match(/Stock:\s*(\d+)/);
        const idMatch = block.match(/ID:\s*(prod_\w+)/);

        if (nameMatch && priceMatch && categoryMatch && stockMatch && idMatch) {
            products.push({
                id: idMatch[1],
                name: nameMatch[1].trim(),
                description: '', // Not in message
                price: parseFloat(priceMatch[1]),
                category: categoryMatch[1],
                stock: parseInt(stockMatch[1]),
            });
        }
    });

    return products.length > 0 ? products : undefined;
}

/**
 * Parse order data from backend response
 * Looks for order information in the message text
 */
export function parseOrder(message: string, intent?: IntentType): Order | undefined {
    if (intent !== IntentType.ORDER) return undefined;

    // Try to extract order ID
    const orderIdMatch = message.match(/Order ID:\s*(ord_\w+)/);
    if (!orderIdMatch) return undefined;

    const orderId = orderIdMatch[1];

    // Extract status
    const statusMatch = message.match(/Status:\s*(\w+)/);
    const status = statusMatch ? statusMatch[1] : 'pending';

    // Extract total
    const totalMatch = message.match(/\*\*Total:\s*\$?([\d.]+)\*\*/);
    const total = totalMatch ? parseFloat(totalMatch[1]) : 0;

    // Extract items
    const items: any[] = [];
    const itemRegex = /-\s*([^x]+)\s+x(\d+)\s*=\s*\$?([\d.]+)/g;
    let itemMatch;

    while ((itemMatch = itemRegex.exec(message)) !== null) {
        items.push({
            product_id: '', // Not in message
            product_name: itemMatch[1].trim(),
            quantity: parseInt(itemMatch[2]),
            price: 0, // Not in message
            subtotal: parseFloat(itemMatch[3]),
        });
    }

    if (items.length === 0) return undefined;

    return {
        id: orderId,
        session_id: '', // Not in message
        items,
        total,
        status: status as any,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
    };
}

/**
 * Parse payment data from backend response
 */
export function parsePayment(message: string, intent?: IntentType): any {
    if (intent !== IntentType.PAYMENT) return undefined;

    const transactionIdMatch = message.match(/Transaction ID:\s*(\w+)/);
    const statusMatch = message.match(/Status:\s*(\w+)/);
    const amountMatch = message.match(/Amount:\s*\$?([\d.]+)/);
    const currencyMatch = message.match(/Currency:\s*(\w+)/);

    if (!transactionIdMatch) return undefined;

    return {
        transactionId: transactionIdMatch[1],
        status: statusMatch ? statusMatch[1] : 'pending',
        amount: amountMatch ? parseFloat(amountMatch[1]) : undefined,
        currency: currencyMatch ? currencyMatch[1] : 'USD',
    };
}

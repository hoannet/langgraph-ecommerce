/**
 * Order Summary Component
 * Displays order details and payment button
 */

import React from 'react';

export interface OrderItem {
    product_id: string;
    product_name: string;
    quantity: number;
    price: number;
    subtotal: number;
}

export interface OrderSummaryProps {
    orderId: string;
    items: OrderItem[];
    total: number;
    status: string;
    onPayment?: (orderId: string) => void;
}

const OrderSummary: React.FC<OrderSummaryProps> = ({
    orderId,
    items,
    total,
    status,
    onPayment,
}) => {
    const handlePayment = () => {
        if (onPayment) {
            onPayment(orderId);
        }
    };

    return (
        <div className="order-summary">
            <div className="order-header">
                <h3>Order Summary</h3>
                <span className="order-id">#{orderId}</span>
            </div>

            <div className="order-status">
                <span className={`status-badge status-${status.toLowerCase()}`}>
                    {status.toUpperCase()}
                </span>
            </div>

            <div className="order-items">
                <h4>Items:</h4>
                {items.map((item, index) => (
                    <div key={index} className="order-item">
                        <div className="item-info">
                            <span className="item-name">{item.product_name}</span>
                            <span className="item-quantity">x{item.quantity}</span>
                        </div>
                        <span className="item-price">${item.subtotal.toFixed(2)}</span>
                    </div>
                ))}
            </div>

            <div className="order-total">
                <span className="total-label">Total:</span>
                <span className="total-amount">${total.toFixed(2)}</span>
            </div>

            {status === 'pending' && (
                <button
                    className="payment-btn"
                    onClick={handlePayment}
                >
                    Proceed to Payment
                </button>
            )}
        </div>
    );
};

export default OrderSummary;

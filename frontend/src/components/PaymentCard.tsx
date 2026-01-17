/**
 * Payment Card Component
 * Displays payment information in a card format
 */

import React from 'react';

interface PaymentCardProps {
    transactionId?: string;
    amount?: number;
    currency?: string;
    status?: string;
}

const PaymentCard: React.FC<PaymentCardProps> = ({
    transactionId,
    amount,
    currency = 'USD',
    status,
}) => {
    if (!transactionId && !amount) return null;

    return (
        <div className="payment-card">
            <div className="payment-header">
                <span className="payment-icon">💳</span>
                <h3>Payment Details</h3>
            </div>
            <div className="payment-body">
                {amount !== undefined && (
                    <div className="payment-row">
                        <span className="payment-label">Amount:</span>
                        <span className="payment-value">
                            {currency} {amount.toFixed(2)}
                        </span>
                    </div>
                )}
                {transactionId && (
                    <div className="payment-row">
                        <span className="payment-label">Transaction ID:</span>
                        <span className="payment-value payment-id">{transactionId}</span>
                    </div>
                )}
                {status && (
                    <div className="payment-row">
                        <span className="payment-label">Status:</span>
                        <span className={`payment-status status-${status.toLowerCase()}`}>
                            {status}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PaymentCard;

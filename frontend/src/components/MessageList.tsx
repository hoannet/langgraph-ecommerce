/**
 * Message List Component
 * Displays chat messages with auto-scroll
 */

import React, { useEffect, useRef } from 'react';
import { Message } from '../types/chat';
import { IntentType, MessageRole } from '../types/api';
import IntentBadge from './IntentBadge';
import PaymentCard from './PaymentCard';
import ProductCard from './ProductCard';
import OrderSummary from './OrderSummary';
import { useChatStore } from '../store/chatStore';

interface MessageListProps {
    messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const messageListRef = useRef<HTMLDivElement>(null);
    const { sendMessage } = useChatStore();

    const scrollToBottom = () => {
        // Use scrollTop instead of scrollIntoView to prevent page scroll
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const formatTime = (date: Date): string => {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const handleProductSelect = (productId: string) => {
        // Send message to order the selected product
        sendMessage(`I want product ${productId}`);
    };

    const handlePayment = (orderId: string) => {
        // Send message to initiate payment
        sendMessage('I want to pay now');
    };

    return (
        <div className="message-list" ref={messageListRef}>
            {messages.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">💬</div>
                    <h2>Start a conversation</h2>
                    <p>Send a message to begin chatting with the AI assistant</p>
                    <div className="example-messages">
                        <p className="example-title">Try asking:</p>
                        <ul>
                            <li>"Show me laptops"</li>
                            <li>"I want to pay $50"</li>
                            <li>"What products do you have?"</li>
                        </ul>
                    </div>
                </div>
            ) : (
                <>
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`message ${message.role === MessageRole.USER ? 'user-message' : 'assistant-message'}`}
                        >
                            <div className="message-content">
                                <div className="message-header">
                                    <span className="message-role">
                                        {message.role === MessageRole.USER ? '👤 You' : '🤖 Assistant'}
                                    </span>
                                    <span className="message-time">{formatTime(message.timestamp)}</span>
                                </div>
                                <div className="message-text">{message.content}</div>
                                {message.intent && (
                                    <IntentBadge
                                        intent={message.intent}
                                        confidence={message.intentConfidence}
                                    />
                                )}

                                {/* Render Product Cards for PRODUCT_SEARCH intent */}
                                {message.intent === IntentType.PRODUCT_SEARCH && message.productData && (
                                    <div className="products-container">
                                        {message.productData.map((product) => (
                                            <ProductCard
                                                key={product.id}
                                                id={product.id}
                                                name={product.name}
                                                description={product.description}
                                                price={product.price}
                                                category={product.category}
                                                stock={product.stock}
                                                onSelect={handleProductSelect}
                                            />
                                        ))}
                                    </div>
                                )}

                                {/* Render Order Summary for ORDER intent */}
                                {message.intent === IntentType.ORDER && message.orderData && (
                                    <OrderSummary
                                        orderId={message.orderData.id}
                                        items={message.orderData.items}
                                        total={message.orderData.total}
                                        status={message.orderData.status}
                                        onPayment={handlePayment}
                                    />
                                )}

                                {/* Render Payment Card for PAYMENT intent */}
                                {message.paymentData && (
                                    <PaymentCard
                                        transactionId={message.paymentData.transactionId}
                                        amount={message.paymentData.amount}
                                        currency={message.paymentData.currency}
                                        status={message.paymentData.status}
                                    />
                                )}
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </>
            )}
        </div>
    );
};

export default MessageList;

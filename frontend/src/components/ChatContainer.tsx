/**
 * Chat Container Component
 * Main chat interface with messages and input
 */

import React from 'react';
import { useChatStore } from '../store/chatStore';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import RagToggle from './RagToggle';

const ChatContainer: React.FC = () => {
    const { messages, isLoading, error, sendMessage, clearHistory, sessionId } = useChatStore();

    const handleSendMessage = async (content: string) => {
        await sendMessage(content);
    };

    const handleClearHistory = async () => {
        if (window.confirm('Are you sure you want to clear the chat history?')) {
            await clearHistory();
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <div className="header-content">
                    <h1>
                        <span className="header-icon">🤖</span>
                        LangGraph Chat Assistant
                    </h1>
                    {sessionId && (
                        <div className="session-info">
                            <span className="session-label">Session:</span>
                            <span className="session-id">{sessionId.substring(0, 8)}...</span>
                        </div>
                    )}
                </div>
                <div className="header-actions">
                    <RagToggle />
                    {messages.length > 0 && (
                        <button className="clear-button" onClick={handleClearHistory}>
                            Clear History
                        </button>
                    )}
                </div>
            </div>

            {error && (
                <div className="error-banner">
                    <span className="error-icon">⚠️</span>
                    <span className="error-text">{error}</span>
                </div>
            )}

            <MessageList messages={messages} />

            <div className="chat-footer">
                {isLoading && (
                    <div className="loading-indicator">
                        <div className="loading-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        <span className="loading-text">AI is thinking...</span>
                    </div>
                )}
                <MessageInput onSend={handleSendMessage} disabled={isLoading} />
            </div>
        </div>
    );
};

export default ChatContainer;

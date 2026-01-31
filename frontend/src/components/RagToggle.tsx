/**
 * RAG Toggle Component
 * Toggle switch to enable/disable RAG mode
 */

import React from 'react';
import { useChatStore } from '../store/chatStore';

const RagToggle: React.FC = () => {
    const { ragEnabled, toggleRag } = useChatStore();

    return (
        <div className="rag-toggle-container">
            <button
                className={`rag-toggle ${ragEnabled ? 'active' : ''}`}
                onClick={toggleRag}
                title={ragEnabled ? 'RAG Mode: ON - Using knowledge base' : 'RAG Mode: OFF - Normal chat'}
            >
                <span className="rag-icon">{ragEnabled ? '🔍' : '💬'}</span>
                <span className="rag-label">
                    {ragEnabled ? 'RAG Mode' : 'Normal Chat'}
                </span>
                <div className={`toggle-switch ${ragEnabled ? 'on' : 'off'}`}>
                    <div className="toggle-slider"></div>
                </div>
            </button>
            {ragEnabled && (
                <div className="rag-tooltip">
                    Using knowledge base for answers
                </div>
            )}
        </div>
    );
};

export default RagToggle;

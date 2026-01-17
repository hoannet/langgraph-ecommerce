/**
 * Intent Badge Component
 * Displays the detected intent with color-coded styling
 */

import React from 'react';
import { IntentType } from '../types/api';

interface IntentBadgeProps {
    intent: IntentType;
    confidence?: number;
}

const IntentBadge: React.FC<IntentBadgeProps> = ({ intent, confidence }) => {
    const getIntentColor = (intent: IntentType): string => {
        switch (intent) {
            case IntentType.PAYMENT:
                return 'intent-payment';
            case IntentType.FAQ:
                return 'intent-faq';
            case IntentType.ESCALATION:
                return 'intent-escalation';
            case IntentType.GENERAL:
            default:
                return 'intent-general';
        }
    };

    return (
        <div className={`intent-badge ${getIntentColor(intent)}`}>
            <span className="intent-icon">●</span>
            <span className="intent-text">{intent}</span>
            {confidence !== undefined && (
                <span className="intent-confidence">{Math.round(confidence * 100)}%</span>
            )}
        </div>
    );
};

export default IntentBadge;

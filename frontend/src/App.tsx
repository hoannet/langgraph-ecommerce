/**
 * Main App Component
 */

import React from 'react';
import ChatContainer from './components/ChatContainer';
import './index.css';

const App: React.FC = () => {
    return (
        <div className="app">
            <ChatContainer />
        </div>
    );
};

export default App;

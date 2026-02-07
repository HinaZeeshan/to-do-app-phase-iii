'use client';

import React, { useState } from 'react';
import ChatBubble from './ChatBubble';
import ChatWindow from './ChatWindow';

const Chatbot: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            <ChatBubble isOpen={isOpen} onClick={() => setIsOpen(true)} />
            <ChatWindow isOpen={isOpen} onClose={() => setIsOpen(false)} />
        </>
    );
};

export default Chatbot;

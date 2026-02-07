import React from 'react';

interface ChatBubbleProps {
    isOpen: boolean;
    onClick: () => void;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ isOpen, onClick }) => {
    return (
        <button
            onClick={onClick}
            className={`fixed bottom-6 right-6 p-4 rounded-full shadow-lg transition-all duration-300 z-50 hover:scale-110 active:scale-95 ${isOpen
                    ? 'bg-neutral-800 text-white rotate-90 scale-0 opacity-0 pointer-events-none'
                    : 'bg-indigo-600 text-white opacity-100'
                }`}
            aria-label="Open chat"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            >
                <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z" />
            </svg>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
            </span>
        </button>
    );
};

export default ChatBubble;

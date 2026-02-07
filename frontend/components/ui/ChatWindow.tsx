import React, { useState, useRef, useEffect } from 'react';
import { chatApi } from '../../lib/api';
import { ChatMessage } from '../../types';

interface ChatWindowProps {
    isOpen: boolean;
    onClose: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ isOpen, onClose }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim() || isLoading) return;

        const userMessage: ChatMessage = {
            role: 'user',
            content: inputValue.trim(),
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await chatApi.sendMessage(userMessage.content, messages);
            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: response.data.response_text,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);

            // If a tool was successfully called, trigger a refresh for the task list
            if (response.data.tool_invocations && response.data.tool_invocations.length > 0) {
                const hasSuccess = response.data.tool_invocations.some(inv => !inv.error);
                if (hasSuccess) {
                    window.dispatchEvent(new CustomEvent('task-updated'));
                }
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            const errorMessage: ChatMessage = {
                role: 'assistant',
                content: "Sorry, I'm having trouble connecting to the server. Please try again later.",
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed bottom-24 right-6 w-96 max-w-[calc(100vw-3rem)] h-[500px] max-h-[calc(100vh-8rem)] bg-white rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden border border-neutral-100 animate-in slide-in-from-bottom-4 duration-300">
            {/* Header */}
            <div className="p-4 bg-indigo-600 text-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                    <h3 className="font-semibold">AI Assistant</h3>
                </div>
                <button
                    onClick={onClose}
                    className="p-1 hover:bg-indigo-500 rounded-md transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg>
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-neutral-50/50">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-4">
                        <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z" /></svg>
                        </div>
                        <div>
                            <p className="text-neutral-900 font-medium">How can I help you today?</p>
                            <p className="text-neutral-500 text-sm mt-1">I can help you add, list, and manage your tasks using naturally language.</p>
                        </div>
                    </div>
                )}
                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${msg.role === 'user'
                            ? 'bg-indigo-600 text-white rounded-tr-none'
                            : 'bg-white text-neutral-800 border border-neutral-100 rounded-tl-none shadow-sm'
                            }`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white text-neutral-800 border border-neutral-100 rounded-2xl rounded-tl-none p-3 shadow-sm flex gap-1">
                            <span className="w-1.5 h-1.5 bg-neutral-300 rounded-full animate-bounce"></span>
                            <span className="w-1.5 h-1.5 bg-neutral-300 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                            <span className="w-1.5 h-1.5 bg-neutral-300 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-neutral-100 flex gap-2">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-1 bg-neutral-100 border-none rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition-all placeholder:text-neutral-400"
                />
                <button
                    type="submit"
                    disabled={isLoading || !inputValue.trim()}
                    className="bg-indigo-600 text-white p-2 rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z" /><path d="M22 2 11 13" /></svg>
                </button>
            </form>
        </div>
    );
};

export default ChatWindow;

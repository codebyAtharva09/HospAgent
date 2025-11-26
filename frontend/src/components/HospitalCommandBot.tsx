import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Send, X, Bot, Mic, MicOff, Volume2, Sparkles } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

interface Props {
    contextData: any;
}

const HospitalCommandBot: React.FC<Props> = ({ contextData }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: "Hello! I'm your Hospital Command Assistant. Ask me about staffing, risk, or supplies.",
            sender: 'bot',
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Speech Recognition Setup
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = SpeechRecognition ? new SpeechRecognition() : null;

    useEffect(() => {
        if (recognition) {
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                setIsListening(false);
            };

            recognition.onerror = () => {
                setIsListening(false);
            };

            recognition.onend = () => {
                setIsListening(false);
            };
        }
    }, []);

    const toggleListening = () => {
        if (!recognition) return;
        if (isListening) {
            recognition.stop();
            setIsListening(false);
        } else {
            recognition.start();
            setIsListening(true);
        }
    };

    const speakText = (text: string) => {
        if ('speechSynthesis' in window) {
            // Strip markdown/HTML for speech
            const cleanText = text.replace(/<[^>]*>?/gm, '').replace(/\*\*/g, '');
            const utterance = new SpeechSynthesisUtterance(cleanText);
            window.speechSynthesis.speak(utterance);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async (textOverride?: string) => {
        const textToSend = textOverride || input;
        if (!textToSend.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            text: textToSend,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        try {
            const res = await fetch(`${API_BASE}/api/ai/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userMsg.text })
            });

            const data = await res.json();

            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                text: data.answer,
                sender: 'bot',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMsg]);
        } catch (err) {
            console.error(err);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                text: "HospAgent: I’m having trouble accessing my AI engine right now. Please try again or check the backend logs.",
                sender: 'bot',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    const suggestions = [
        "How many doctors needed tomorrow?",
        "Explain today's surge risk.",
        "Do we have enough oxygen?",
        "Impact of upcoming festivals?"
    ];

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end font-sans">
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="mb-4 w-[400px] bg-slate-900 rounded-3xl shadow-2xl shadow-blue-900/40 border border-slate-700 overflow-hidden flex flex-col backdrop-blur-xl"
                        style={{ height: '600px' }}
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-blue-900 to-slate-900 p-4 flex justify-between items-center border-b border-slate-700">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-500/20 rounded-xl border border-blue-500/30">
                                    <Bot className="w-5 h-5 text-blue-400" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white text-sm">AI Hospital Command Bot</h3>
                                    <p className="text-xs text-blue-300">Operations Support • Online</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="p-1 hover:bg-white/10 rounded-lg transition-colors text-slate-400 hover:text-white"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-950/50">
                            {messages.map((msg) => (
                                <div
                                    key={msg.id}
                                    className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                                >
                                    <div className="flex items-end gap-2 max-w-[85%]">
                                        {msg.sender === 'bot' && (
                                            <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/30 shrink-0">
                                                <Sparkles className="w-3 h-3 text-blue-400" />
                                            </div>
                                        )}
                                        <div
                                            className={`p-3 rounded-2xl text-sm leading-relaxed ${msg.sender === 'user'
                                                    ? 'bg-blue-600 text-white rounded-tr-none'
                                                    : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none'
                                                }`}
                                        >
                                            <div dangerouslySetInnerHTML={{ __html: msg.text.replace(/\n/g, '<br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                                        </div>
                                    </div>
                                    {msg.sender === 'bot' && (
                                        <button
                                            onClick={() => speakText(msg.text)}
                                            className="ml-8 mt-1 text-xs text-slate-500 hover:text-blue-400 flex items-center gap-1 transition-colors"
                                        >
                                            <Volume2 className="w-3 h-3" /> Play
                                        </button>
                                    )}
                                </div>
                            ))}
                            {isTyping && (
                                <div className="flex justify-start ml-8">
                                    <div className="bg-slate-800 p-3 rounded-2xl rounded-tl-none border border-slate-700 flex gap-1">
                                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></span>
                                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100"></span>
                                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200"></span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Suggestions */}
                        {messages.length < 3 && (
                            <div className="px-4 py-2 bg-slate-900 border-t border-slate-800 overflow-x-auto whitespace-nowrap">
                                <div className="flex gap-2">
                                    {suggestions.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => handleSend(s)}
                                            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-full text-xs text-blue-300 transition-colors"
                                        >
                                            {s}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Input */}
                        <div className="p-4 bg-slate-900 border-t border-slate-800">
                            <div className="flex gap-2">
                                {recognition && (
                                    <button
                                        onClick={toggleListening}
                                        className={`p-2 rounded-xl transition-all ${isListening
                                                ? 'bg-red-500/20 text-red-400 animate-pulse border border-red-500/50'
                                                : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                                            }`}
                                    >
                                        {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                    </button>
                                )}
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder={isListening ? "Listening..." : "Ask HospAgent..."}
                                    className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-white placeholder-slate-500"
                                />
                                <button
                                    onClick={() => handleSend()}
                                    disabled={!input.trim()}
                                    className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-blue-600/20"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsOpen(!isOpen)}
                className="h-14 w-14 bg-blue-600 hover:bg-blue-500 rounded-full shadow-lg shadow-blue-600/40 flex items-center justify-center text-white border-2 border-white/10 backdrop-blur-sm transition-colors"
            >
                {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
            </motion.button>
        </div>
    );
};

export default HospitalCommandBot;

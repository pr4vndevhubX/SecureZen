import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, Sparkles, Database, Search } from 'lucide-react';
import { API_BASE_URL } from '../config';
// import ReactMarkdown from 'react-markdown';

const Copilot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "⚡ **SecureZen Active.**\n\nPowered by **KRYA SOLUTIONS PRIVATE LIMITED** for the defenders who never sleep 🔥.\n\nHello Defender,\nConnected with your Wazuh instance and **ready to hunt now**"
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setInput('');
        setIsLoading(true);

        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ message: userMsg })
            });

            const data = await response.json();

            let botResponse = data.content;
            if (data.type === 'query_result') {
                // Ideally render a table or card here, but markdown table works too
                const tableHeader = "| Time | Severity | Event | Source |\n|---|---|---|---|\n";
                const tableRows = data.data.map(row => {
                    // Parse ISO timestamp: "2026-02-02T13:30:03.910+0530" -> "13:30:03"
                    const time = row.timestamp ? row.timestamp.split('T')[1]?.split('.')[0] || 'N/A' : 'N/A';
                    return `| ${time} | **${row.severity}** | ${row.description} | ${row.source_ip} |`;
                }).join("\n");

                botResponse = `${data.content}\n\n${tableHeader}${tableRows}`;
            }

            setMessages(prev => [...prev, { role: 'assistant', content: botResponse || "Command processed." }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "⚠️ Connection Lost to Neural Core." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`fixed bottom-6 right-6 z-50 p-4 rounded-full shadow-[0_0_20px_rgba(0,212,255,0.4)] transition-all duration-300 hover:scale-110 active:scale-95 group ${isOpen ? 'bg-red-500/20 text-red-500 hover:bg-red-500 hover:text-white' : 'bg-[#00d4ff] text-[#0a0e27]'
                    }`}
            >
                {isOpen ? <X className="w-6 h-6" /> : <Bot className="w-6 h-6" />}
                {!isOpen && (
                    <span className="absolute top-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-[#0a0e27] animate-pulse"></span>
                )}
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className="fixed bottom-24 right-6 z-50 w-[400px] h-[600px] bg-[#0a0e27]/95 backdrop-blur-xl border border-[#2a2f4a] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-10 fade-in duration-300">

                    {/* Header */}
                    <div className="p-4 border-b border-[#2a2f4a] bg-[#131b33]/50 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-[#00d4ff]/10 flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-[#00d4ff]" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white text-sm tracking-wide">SECUREZEN ANALYST</h3>
                            <p className="text-[10px] text-[#00d4ff] uppercase tracking-widest flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                                Neural Link Active
                            </p>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-[#2a2f4a] scrollbar-track-transparent">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                {msg.role === 'assistant' && (
                                    <div className="w-8 h-8 rounded-full bg-[#00d4ff]/10 flex-shrink-0 flex items-center justify-center mt-1">
                                        <Bot className="w-4 h-4 text-[#00d4ff]" />
                                    </div>
                                )}

                                <div
                                    className={`max-w-[85%] rounded-2xl p-3 text-sm leading-relaxed ${msg.role === 'user'
                                        ? 'bg-[#00d4ff] text-[#0a0e27] font-medium rounded-tr-none'
                                        : 'bg-[#1a1f3a] border border-[#2a2f4a] text-gray-300 rounded-tl-none'
                                        }`}
                                >
                                    <div className="whitespace-pre-wrap">{msg.content}</div>
                                </div>

                                {msg.role === 'user' && (
                                    <div className="w-8 h-8 rounded-full bg-slate-700 flex-shrink-0 flex items-center justify-center mt-1">
                                        <div className="w-4 h-4 bg-gray-400 rounded-full" />
                                    </div>
                                )}
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-[#00d4ff]/10 flex-shrink-0 flex items-center justify-center">
                                    <Bot className="w-4 h-4 text-[#00d4ff] animate-pulse" />
                                </div>
                                <div className="bg-[#1a1f3a] border border-[#2a2f4a] px-4 py-3 rounded-2xl rounded-tl-none flex gap-1 items-center">
                                    <span className="w-1.5 h-1.5 bg-[#00d4ff]/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <span className="w-1.5 h-1.5 bg-[#00d4ff]/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <span className="w-1.5 h-1.5 bg-[#00d4ff]/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <form onSubmit={handleSubmit} className="p-4 bg-[#131b33]/50 border-t border-[#2a2f4a]">
                        <div className="relative group">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Search logs, IPs, or ask for help..."
                                className="w-full bg-[#0a0e27] border border-[#2a2f4a] rounded-xl pl-4 pr-12 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#00d4ff] transition-colors shadow-inner"
                            />
                            <button
                                type="submit"
                                disabled={!input.trim() || isLoading}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-[#00d4ff]/10 text-[#00d4ff] hover:bg-[#00d4ff] hover:text-[#0a0e27] transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                        <div className="flex gap-2 mt-2 justify-center">
                            <span className="text-[10px] text-gray-500 uppercase tracking-wider">Secure Channel Encrypted</span>
                        </div>
                    </form>
                </div>
            )}
        </>
    );
};

export default Copilot;

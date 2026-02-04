import React, { useState } from 'react';
import { Search, Bot, Zap, Database, Globe, Shield, Terminal, Activity, Download } from 'lucide-react';
import { ReportViewer } from './ReportViewer';
import { API_BASE_URL } from '../config';

export const IpInvestigation = ({ onAnalyze, analysis }) => {
    const [ip, setIp] = useState('');

    const handleAnalyze = () => {
        if (ip) onAnalyze(ip);
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Old Style Hero Section for IP */}
            <div className="bg-[#0a1128] border border-[#1e293b] rounded-2xl p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-5">
                    <Globe className="w-32 h-32 text-[#00d4ff]" />
                </div>

                <div className="relative z-10 max-w-2xl">
                    <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
                        <Shield className="w-8 h-8 text-[#00d4ff]" />
                        Deep Entity Intelligence
                    </h2>
                    <p className="text-gray-400 mb-8 font-medium">
                        Initiate a multi-agent swarm investigation into suspicious IP addresses, domains, or file hashes. Powered by CrewAI neural reasoning.
                    </p>

                    <div className="flex gap-4">
                        <div className="relative flex-1">
                            <Terminal className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                            <input
                                type="text"
                                value={ip}
                                onChange={(e) => setIp(e.target.value)}
                                placeholder="Enter Target Entity (IP/Domain/Hash)..."
                                className="w-full bg-[#020617] border border-[#1e293b] rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-all font-mono shadow-2xl"
                            />
                        </div>
                        <button
                            onClick={handleAnalyze}
                            className="bg-[#00d4ff] text-[#0a0e27] font-bold px-8 rounded-xl hover:bg-white transition-all transform active:scale-95 shadow-[0_0_20px_rgba(0,212,255,0.4)] flex items-center gap-2 uppercase tracking-widest text-sm"
                        >
                            <Zap className="w-5 h-5 fill-current" />
                            Initialize
                        </button>
                    </div>
                </div>
            </div>

            {/* Analysis Result Area */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="lg:col-span-1 space-y-4">
                    <div className="bg-[#0a1128] border border-[#1e293b] p-6 rounded-2xl h-full">
                        <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4 border-b border-[#1e293b] pb-2">Analysis Status</h3>
                        {!analysis ? (
                            <div className="flex flex-col items-center justify-center py-8 text-center opacity-30">
                                <Activity className="w-12 h-12 mb-2" />
                                <span className="text-[10px] font-bold uppercase">Awaiting Target</span>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-gray-400">Swarm Activity</span>
                                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${analysis.status === 'running' ? 'bg-blue-500/20 text-blue-500' : 'bg-green-500/20 text-green-500'}`}>
                                        {analysis.status || 'Active'}
                                    </span>
                                </div>
                                <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                                    <div className={`h-full bg-[#00d4ff] ${analysis.status === 'running' ? 'animate-progress-fast' : 'w-full'}`} />
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="lg:col-span-3">
                    <div className="bg-[#0a1128] border border-[#1e293b] p-8 rounded-2xl min-h-[400px] shadow-2xl">
                        {!analysis ? (
                            <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4 opacity-20">
                                <Database className="w-16 h-16" />
                                <p className="text-sm font-bold uppercase tracking-widest">Neural Core Awaiting Instruction</p>
                            </div>
                        ) : (
                            <div className="animate-in fade-in slide-in-from-top-4 duration-700">
                                {analysis.status === 'running' ? (
                                    <div className="flex flex-col items-center justify-center py-20 space-y-4">
                                        <Bot className="w-12 h-12 text-[#00d4ff] animate-bounce" />
                                        <p className="text-[#00d4ff] font-mono animate-pulse">{analysis.analysis}</p>
                                    </div>
                                ) : (
                                    <div className="space-y-6">
                                        <div className="flex justify-between items-center bg-[#1e293b]/30 p-4 rounded-xl border border-[#1e293b]">
                                            <div className="flex items-center gap-3">
                                                <div className="w-2 h-2 bg-[#60c07c] rounded-full animate-pulse" />
                                                <span className="text-[10px] font-bold text-white uppercase tracking-widest">Intelligence Report Ready</span>
                                            </div>
                                            <button
                                                onClick={() => window.print()}
                                                className="flex items-center gap-2 bg-[#00d4ff]/10 text-[#00d4ff] hover:bg-[#00d4ff] hover:text-[#0a0e27] px-4 py-2 rounded-lg text-[10px] font-bold transition-all border border-[#00d4ff]/20 uppercase group"
                                            >
                                                <Download className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
                                                Download Intelligence PDF
                                            </button>
                                        </div>
                                        <ReportViewer report={analysis.analysis} />
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export const MitreAssistant = ({ isInvestigationMode = false }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleRagSearch = async () => {
        if (!query) return;
        setIsLoading(true);
        setResults("🧠 Querying MITRE RAG Knowledge Base...");
        try {
            const res = await fetch(`${API_BASE_URL}/api/mitre/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query })
            });
            const data = await res.json();

            if (data.results && data.results.length > 0) {
                const formatted = data.results.map(r =>
                    `### ${r.metadata.technique_id || 'Info'}: ${r.metadata.name || 'Technique'}\n\n${r.document}\n\n**Similarity Score:** ${(r.similarity_score * 100).toFixed(1)}%`
                ).join('\n\n---\n\n');
                setResults(formatted);
            } else {
                setResults("No semantic matches found in MITRE ATT&CK database.");
            }
        } catch (err) {
            setResults(`❌ RAG Service Error: ${err.message}`);
        }
        setIsLoading(false);
    };

    return (
        <div className={`flex flex-col h-full ${isInvestigationMode ? '' : 'p-6'}`}>
            <div className="flex items-center justify-between mb-8 border-b border-[#1e293b] pb-4">
                <div className="flex items-center gap-3">
                    <Bot className="w-6 h-6 text-[#d946ef]" />
                    <h2 className="text-xl font-bold text-white tracking-widest uppercase">Neural Framework Assistant</h2>
                </div>
                <div className="flex gap-2">
                    <span className="flex items-center gap-2 px-3 py-1 bg-[#d946ef]/10 text-[#d946ef] rounded-full text-[10px] font-bold border border-[#d946ef]/20 uppercase">
                        MITRE v14 Active
                    </span>
                </div>
            </div>

            <div className="flex-1 flex flex-col gap-6">
                <div className="relative group">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-hover:text-[#d946ef] transition-colors" />
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleRagSearch()}
                        placeholder="Ask about Tactics, Techniques, or Procedures..."
                        className="w-full bg-[#0a1128] border border-[#1e293b] rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[#d946ef] transition-all font-medium shadow-xl"
                    />
                </div>

                <div className="flex-1 bg-[#020617]/50 rounded-2xl border border-[#1e293b] p-8 overflow-y-auto scrollbar-hide shadow-inner min-h-[400px]">
                    {!results && !isLoading ? (
                        <div className="h-full flex flex-col items-center justify-center text-center opacity-20 filter grayscale">
                            <Bot className="w-24 h-24 mb-6" />
                            <h3 className="text-xl font-bold uppercase tracking-[0.2em]">Framework Brain Idle</h3>
                            <p className="text-xs font-bold mt-2">QUERY MITRE DATABASE FOR CONTEXT</p>
                        </div>
                    ) : isLoading ? (
                        <div className="h-full flex flex-col items-center justify-center space-y-4">
                            <div className="w-12 h-12 border-4 border-[#d946ef] border-t-transparent rounded-full animate-spin" />
                            <p className="text-[#d946ef] font-bold uppercase tracking-widest text-xs animate-pulse">Syncing Frameworks...</p>
                        </div>
                    ) : (
                        <div className="animate-in fade-in duration-700">
                            <ReportViewer report={results} />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

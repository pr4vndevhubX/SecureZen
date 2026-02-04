import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { Search, Filter, Download, Zap, AlertCircle, Clock, Server, Shield, ChevronDown, ChevronRight, ExternalLink, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../config';

const EventRow = ({ alert, index, onAnalyze, getSeverityColor }) => {
    const [explaining, setExplaining] = useState(false);
    const [explanation, setExplanation] = useState(null);
    const [aiSeverity, setAiSeverity] = useState(null);
    const [aiAction, setAiAction] = useState(null);

    const handleExplain = async (e, msg) => {
        e.stopPropagation();
        if (explanation) { setExplanation(null); return; }
        setExplaining(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/ai/explain-alert`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            setExplanation(data.explanation);
            if (data.severity) setAiSeverity(data.severity);
            if (data.action) setAiAction(data.action);
        } catch (err) {
            setExplanation("Error fetching AI insight.");
        }
        setExplaining(false);
    };

    const currentSeverity = aiSeverity || alert.severity;

    return (
        <tr className="hover:bg-[#00d4ff]/5 transition-colors group cursor-pointer border-b border-[#2d3748]/20">
            <td className="py-4 px-4 text-center text-gray-600 font-mono text-[9px]">{index + 1}</td>
            <td className="py-4 px-4">
                <div className="flex flex-col">
                    <span className="text-gray-300 font-bold">{alert.time?.split(',')[0]}</span>
                    <span className="text-[9px] text-gray-500">{alert.time?.split(',')[1]}</span>
                </div>
            </td>
            <td className="py-4 px-4 text-gray-500 font-mono text-[10px]">{alert.alertId?.slice(-10)}</td>
            <td className="py-4 px-4 text-white font-bold tracking-tight">{alert.type}</td>
            <td className="py-4 px-4">
                <div className="flex flex-col gap-1">
                    <span className={`px-2 py-0.5 rounded-[4px] text-[8px] font-bold uppercase border leading-none w-fit ${getSeverityColor(currentSeverity)}`}>
                        {currentSeverity === 'High' ? 'Major' : currentSeverity === 'Low' ? 'Minor' : currentSeverity}
                    </span>
                    {aiSeverity && (
                        <span className="text-[7px] text-[#00d4ff] font-bold uppercase tracking-tighter flex items-center gap-0.5">
                            <Zap className="w-2 h-2 fill-[#00d4ff]" /> Neural Triage
                        </span>
                    )}
                </div>
            </td>
            <td className="py-4 px-4">
                <button
                    onClick={(e) => handleExplain(e, alert.message)}
                    className={`px-3 py-1 rounded text-[9px] font-bold uppercase transition-all shadow-[0_0_10px_rgba(59,130,246,0.1)] border ${explanation ? 'bg-[#60c07c]/20 text-[#60c07c] border-[#60c07c]/40' : 'bg-[#3b82f6]/20 text-[#3b82f6] border-[#3b82f6]/40 hover:bg-[#3b82f6]/30'}`}
                >
                    {explanation ? 'TRIAGED' : 'Await...'}
                </button>
            </td>
            <td className="py-4 px-4">
                <div className="p-1 px-1.5 bg-[#f97316]/10 rounded border border-[#f97316]/20 w-fit">
                    <Shield className="w-3.5 h-3.5 text-[#f97316]" />
                </div>
            </td>
            <td className="py-4 px-4 text-gray-400 font-mono text-[10px]">
                {alert.srcIp || 'N/A'}
            </td>
            <td className="py-4 px-4 max-w-sm">
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2 group/msg">
                        <span className="truncate text-gray-400 group-hover:text-gray-200 transition-colors uppercase font-medium tracking-tighter text-[10px]">
                            {alert.message}
                        </span>
                        <button
                            onClick={(e) => handleExplain(e, alert.message)}
                            className={`p-1 rounded bg-[#00d4ff]/10 text-[#00d4ff] hover:bg-[#00d4ff]/20 transition-all ${explaining ? 'animate-pulse' : ''}`}
                            title="AI Smart Expand"
                        >
                            <Zap className={`w-3 h-3 ${explaining ? 'fill-[#00d4ff]' : ''}`} />
                        </button>
                    </div>
                    {explanation && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="text-[10px] text-[#00d4ff] bg-[#00d4ff]/5 p-2 rounded border border-[#00d4ff]/20"
                        >
                            <div className="flex flex-col gap-1">
                                <div><span className="font-bold mr-2">✨ AI INSIGHT:</span>{explanation}</div>
                                {aiAction && <div className="text-[9px] text-gray-400 mt-1 font-bold"><span className="text-[#60c07c] mr-2">🎯 NEXT STEP:</span>{aiAction}</div>}
                            </div>
                        </motion.div>
                    )}
                </div>
            </td>
            <td className="py-4 px-4">
                <div className="bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/30 px-3 py-1 rounded font-mono font-bold flex items-center justify-between gap-3 min-w-[130px] text-[10px] tracking-widest shadow-inner">
                    {alert.entity}
                    <ChevronDown className="w-3 h-3 opacity-50" />
                </div>
            </td>
            <td className="py-4 px-4 text-gray-500 font-bold uppercase tracking-widest text-[10px]">
                {alert.user || 'SYSTEM'}
            </td>
            <td className="py-4 px-4 text-center">
                <div className="flex flex-col items-center">
                    <span className="text-white font-bold text-xs leading-none">85%</span>
                    <div className="w-12 h-1 bg-gray-800 rounded-full mt-1 overflow-hidden">
                        <div className="w-[85%] h-full bg-[#60c07c]" />
                    </div>
                </div>
            </td>
            <td className="py-4 px-4 text-center">
                <button
                    onClick={(e) => { e.stopPropagation(); onAnalyze(alert.entity); }}
                    className="bg-white/5 hover:bg-[#00d4ff] text-white hover:text-black border border-white/10 hover:border-[#00d4ff] p-2 rounded-lg transition-all group/btn shadow-xl active:scale-90"
                >
                    <Activity className="w-4 h-4 group-hover/btn:scale-110 transition-transform" />
                </button>
            </td>
        </tr>
    );
};

export const MitreEvents = ({ alerts, onAnalyze, initialSeverity = 'All' }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [severityFilter, setSeverityFilter] = useState(initialSeverity);

    

    useEffect(() => {
        if (initialSeverity !== 'All' && initialSeverity) {
            setSeverityFilter(initialSeverity);
        }
    }, [initialSeverity]);

    const filteredAlerts = (alerts || []).filter(alert => {
        const matchesSearch =
            (alert.entity || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
            (alert.type || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
            (alert.message || '').toLowerCase().includes(searchTerm.toLowerCase());

        const matchesSeverity = severityFilter === 'All' || alert.severity === severityFilter;

        return matchesSearch && matchesSeverity;
    });

    // Chart Data based on Severity (Image 3 Style)
    const severityCounts = {
        'Critical': 0,
        'High': 0,
        'Medium': 0,
        'Low': 0
    };
    filteredAlerts.forEach(a => {
        const sev = a.severity || 'Medium';
        if (severityCounts[sev] !== undefined) severityCounts[sev]++;
        else if (sev === 'Major') severityCounts['High']++;
        else if (sev === 'Minor') severityCounts['Low']++;
        else severityCounts['Low']++;
    });

    const chartData = [
        { name: 'Critical', count: severityCounts['Critical'], fill: '#ef4444' },
        { name: 'High', count: severityCounts['High'], fill: '#f97316' },
        { name: 'Medium', count: severityCounts['Medium'], fill: '#eab308' },
        { name: 'Low', count: severityCounts['Low'], fill: '#3b82f6' },
    ];

    const getSeverityColor = (sev) => {
        switch (sev?.toLowerCase()) {
            case 'critical': return 'bg-red-500/20 text-red-500 border-red-500/40';
            case 'high':
            case 'major': return 'bg-orange-500/20 text-orange-500 border-orange-500/40';
            case 'medium': return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/40';
            case 'low':
            case 'minor': return 'bg-blue-500/20 text-blue-500 border-blue-500/40';
            default: return 'bg-blue-500/10 text-gray-400 border-gray-500/20';
        }
    };

    return (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-700">
            {/* Event Distribution (Image 3 Style) */}
            <div className="bg-[#1a1f3a]/20 backdrop-blur-md p-6 rounded-2xl border border-[#2d3748] shadow-2xl relative overflow-hidden">
                <div className="flex items-center justify-between mb-4 relative z-10">
                    <div>
                        <h3 className="text-[10px] font-bold text-white flex items-center gap-2 uppercase tracking-[0.2em]">
                            <Activity className="w-4 h-4 text-[#00d4ff]" />
                            Severity Distribution Analysis
                        </h3>
                        <p className="text-[8px] font-bold text-gray-500 uppercase mt-1">Live Pulse Monitoring • {filteredAlerts.length} Events Listed</p>
                    </div>
                </div>
                <div className="h-[100px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} layout="vertical" margin={{ left: -30 }}>
                            <XAxis type="number" hide />
                            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 9, fontWeight: '700', fill: '#94a3b8' }} width={80} />
                            <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={12}>
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.fill} />
                                ))}
                            </Bar>
                            <RechartsTooltip
                                contentStyle={{ backgroundColor: '#1a1f3a', border: '1px solid #2d3748', borderRadius: '8px' }}
                                itemStyle={{ color: '#ffffff', fontWeight: 'bold' }}
                                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Controls */}
            <div className="flex flex-wrap gap-4 items-center bg-[#0a0e27]/40 p-3 rounded-xl border border-[#2d3748]/30">
                <div className="relative flex-1 min-w-[300px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-[#0a0e27]/60 border border-[#2d3748] rounded-lg pl-9 pr-4 py-1.5 text-xs text-white focus:outline-none focus:border-[#00d4ff] transition-all"
                    />
                </div>
                <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                    className="bg-[#0a0e27]/60 border border-[#2d3748] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none font-bold uppercase tracking-wider"
                >
                    {['All', 'Critical', 'High', 'Medium', 'Low'].map(s => (
                        <option key={s} value={s}>{s} Severity</option>
                    ))}
                </select>
            </div>

            {/* High Density Table (Images 1 & 2 Style) */}
            <div className="bg-[#0a0e27] rounded-xl border border-[#2d3748] shadow-2xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-[11px] border-collapse min-w-[1700px]">
                        <thead>
                            <tr className="bg-[#1a1f3a]/30 text-gray-500 font-bold uppercase tracking-[0.2em] border-b border-[#2d3748]">
                                <th className="py-4 px-4 w-8 text-center text-[9px]">#</th>
                                <th className="py-4 px-4">Time</th>
                                <th className="py-4 px-4">Alert Id</th>
                                <th className="py-4 px-4">Type</th>
                                <th className="py-4 px-4">Severity</th>
                                <th className="py-4 px-4">Analyst Verdict</th>
                                <th className="py-4 px-4">Origin</th>
                                <th className="py-4 px-4">Source IP</th>
                                <th className="py-4 px-4">Message</th>
                                <th className="py-4 px-4">Entity</th>
                                <th className="py-4 px-4">User Name</th>
                                <th className="py-4 px-4 text-center">Confidence</th>
                                <th className="py-4 px-4 text-center">Investigation</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[#2d3748]/30">
                            {filteredAlerts.map((alert, i) => alert && (
                                <EventRow
                                    key={i}
                                    alert={alert}
                                    index={i}
                                    onAnalyze={onAnalyze}
                                    getSeverityColor={getSeverityColor}
                                />
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

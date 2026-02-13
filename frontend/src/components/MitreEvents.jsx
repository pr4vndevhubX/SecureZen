import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { Search, Filter, Download, Zap, AlertCircle, Clock, Server, Shield, ChevronDown, ChevronRight, ExternalLink, Activity, ShieldAlert } from 'lucide-react';
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
            const token = localStorage.getItem('auth_token');
            const res = await fetch(`${API_BASE_URL}/api/ai/explain-alert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
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
            <td className="py-4 px-4 text-white font-bold tracking-tight">
                <div className="flex flex-col gap-1">
                    {alert.type}
                    {alert.is_simulated && (
                        <span className="text-[7px] text-[#f97316] font-bold uppercase tracking-tight flex items-center gap-0.5 px-1.5 py-0.5 bg-[#f97316]/10 border border-[#f97316]/20 rounded-full w-fit">
                            <Zap className="w-2 h-2 fill-[#f97316]" /> AI Simulation
                        </span>
                    )}
                </div>
            </td>
            <td className="py-4 px-4">
                <div className="flex flex-col gap-1">
                    <span className={`px-2 py-0.5 rounded-[4px] text-[8px] font-bold uppercase border leading-none w-fit ${getSeverityColor(currentSeverity)}`}>
                        {currentSeverity === 'High' ? 'Major' : currentSeverity === 'Medium' || currentSeverity === 'Low' ? 'Minor' : currentSeverity}
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

export const MitreEvents = ({ alerts, onAnalyze, initialSeverity = 'All', initialStatus = 'All', initialSearch = '', onSearchChange }) => {
    const [searchTerm, setSearchTerm] = useState(initialSearch);
    const [severityFilter, setSeverityFilter] = useState(initialSeverity);
    const [statusFilter, setStatusFilter] = useState(initialStatus);
    const [timeFilter, setTimeFilter] = useState('All');
    const [activeFilters, setActiveFilters] = useState([]); // Array of {field, value}

    useEffect(() => {
        if (initialSearch !== undefined) setSearchTerm(initialSearch);
    }, [initialSearch]);

    useEffect(() => {
        if (initialSeverity) setSeverityFilter(initialSeverity);
    }, [initialSeverity]);

    useEffect(() => {
        if (initialStatus) setStatusFilter(initialStatus);
    }, [initialStatus]);

    const handleSearchChange = (e) => {
        const val = e.target.value;
        setSearchTerm(val);
        if (onSearchChange) onSearchChange(val);
    };

    const addFilter = (field, value) => {
        if (!activeFilters.find(f => f.field === field && f.value === value)) {
            setActiveFilters([...activeFilters, { field, value }]);
        }
    };

    const removeFilter = (field, value) => {
        setActiveFilters(activeFilters.filter(f => !(f.field === field && f.value === value)));
    };

    const isWithinTime = (timestamp, range) => {
        if (range === 'All') return true;
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;

        switch (range) {
            case '15m': return diffMs <= 15 * 60 * 1000;
            case '1h': return diffMs <= 60 * 60 * 1000;
            case '24h': return diffMs <= 24 * 60 * 60 * 1000;
            case '7d': return diffMs <= 7 * 24 * 60 * 60 * 1000;
            default: return true;
        }
    };

    const filteredAlerts = (alerts || []).filter(alert => {
        // 1. Time Filter
        if (!isWithinTime(alert.timestamp, timeFilter)) return false;

        // 2. Search Term
        const searchString = searchTerm.toLowerCase();
        const matchesSearch =
            (alert.entity || '').toLowerCase().includes(searchString) ||
            (alert.type || '').toLowerCase().includes(searchString) ||
            (alert.message || '').toLowerCase().includes(searchString) ||
            (alert.mitreTactic || '').toLowerCase().includes(searchString) ||
            (alert.killChainPhase || '').toLowerCase().includes(searchString) ||
            (alert.agent_name || '').toLowerCase().includes(searchString) ||
            (alert.rule_level?.toString() || '').includes(searchString) ||
            JSON.stringify(alert).toLowerCase().includes(searchString); // Fallback: Check everywhere

        if (!matchesSearch) return false;

        // 3. Severity Filter
        if (severityFilter !== 'All') {
            if (severityFilter === 'Critical' && alert.severity !== 'Critical') return false;
            if (severityFilter === 'Major' && (alert.severity !== 'High' && alert.severity !== 'Major')) return false;
            if (severityFilter === 'Minor' && (alert.severity !== 'Medium' && alert.severity !== 'Low' && alert.severity !== 'Minor')) return false;
        }

        // 4. Status Filter
        if (statusFilter !== 'All') {
            // Mock status logic: If alert has no status, assume 'Open'
            const currentStatus = alert.status || 'Open';
            if (currentStatus !== statusFilter) return false;
        }

        // 5. Active Badge Filters (Drill-down)
        for (const filter of activeFilters) {
            const alertVal = String(alert[filter.field] || alert[filter.field.replace('.', '_')] || ''); // Try both dot and underscore
            // Special handling for nested or mapped fields
            let match = false;
            if (filter.field === 'rule.level' && String(alert.rule_level) === String(filter.value)) match = true;
            else if (filter.field === 'agent.name' && (alert.agent_name === filter.value || alert.agent?.name === filter.value)) match = true;
            else if (filter.field === 'srcip' && (alert.srcIp === filter.value || alert.src_ip === filter.value)) match = true;
            else if (filter.field === 'dstip' && (alert.dstIp === filter.value || alert.dst_ip === filter.value)) match = true;
            else if (filter.field === 'mitre.id' && alert.mitreId === filter.value) match = true;
            else if (alertVal === String(filter.value)) match = true;

            if (!match) return false;
        }

        return true;
    });

    // Chart Data based on filtered view
    const stats = { 'Critical': 0, 'Major': 0, 'Minor': 0 };
    filteredAlerts.forEach(a => {
        const sev = a.severity;
        if (sev === 'Critical') stats['Critical']++;
        else if (sev === 'High' || sev === 'Major') stats['Major']++;
        else stats['Minor']++;
    });

    const chartData = [
        { name: 'Critical', count: stats['Critical'], fill: '#ef4444' },
        { name: 'Major', count: stats['Major'], fill: '#f97316' },
        { name: 'Minor', count: stats['Minor'], fill: '#eab308' },
    ];

    const [expandedRows, setExpandedRows] = useState({});

    const toggleRow = (id) => {
        setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }));
    };

    const getBadgeColor = (field, value, severity) => {
        if (field === 'rule.level') {
            switch (severity?.toLowerCase()) {
                case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
                case 'high': case 'major': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
                default: return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            }
        }
        if (field === 'srcip' || field === 'dstip') return 'bg-purple-900/40 text-purple-300 border-purple-700/50';
        if (field === 'mitre.id') return 'bg-orange-900/40 text-orange-300 border-orange-700/50';
        if (field === 'agent.name') return 'bg-gray-800 text-gray-300 border-gray-600';
        return 'bg-blue-900/40 text-blue-300 border-blue-700/50';
    };

    const renderBadges = (alert) => {
        const badges = [
            { field: 'rule.level', label: 'Level', value: alert.rule_level, sev: alert.severity },
            { field: 'agent.name', label: 'Agent', value: alert.agent_name || alert.agent?.name },
            { field: 'rule.description', label: 'Rule', value: alert.rule_description },
            { field: 'srcip', label: 'Src', value: alert.srcIp || alert.src_ip },
            { field: 'dstip', label: 'Dst', value: alert.dstIp || alert.dst_ip },
            { field: 'mitre.id', label: 'Mitre', value: alert.mitreId },
        ];

        return badges.filter(b => b.value).map((b, i) => (
            <button
                key={i}
                onClick={(e) => { e.stopPropagation(); addFilter(b.field, b.value); }}
                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono border transition-all hover:brightness-110 active:scale-95 ${getBadgeColor(b.field, b.value, b.sev)}`}
                title={`Filter by ${b.label}: ${b.value}`}
            >
                <span className="font-bold opacity-60 uppercase">{b.label}</span>
                <span className="font-semibold truncate max-w-[150px]">{b.value}</span>
            </button>
        ));
    };

    return (
        <div className="space-y-4 animate-in fade-in duration-500 font-sans">
            {/* Histogram */}
            <div className="bg-[#0a0e27] p-4 rounded-xl border border-[#1a1f3a] shadow-lg relative overflow-hidden h-36">
                <div className="absolute top-3 left-4 flex flex-col z-10">
                    <span className="text-2xl font-bold text-white tracking-widest leading-none">{filteredAlerts.length.toLocaleString()}</span>
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Hits
                        <span className="ml-2 text-[9px] text-gray-600 normal-case bg-black/50 px-1 rounded">
                            (Debug: Total {alerts?.length}, Filtered: {filteredAlerts.length}, Search: '{searchTerm}')
                        </span>
                    </span>
                </div>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                        <RechartsTooltip
                            contentStyle={{ backgroundColor: '#0a0e27', border: '1px solid #1a1f3a', borderRadius: '8px', fontSize: '11px' }}
                            itemStyle={{ color: '#fff' }}
                            cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                        />
                        <Bar dataKey="count" radius={[3, 3, 0, 0]} barSize={50}>
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Filter Bar */}
            <div className="bg-[#0a0e27]/80 backdrop-blur-sm p-3 rounded-xl border border-[#1a1f3a] flex flex-wrap gap-3 items-center shadow-lg sticky top-0 z-20">
                {/* Search */}
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search (e.g. 'Integrity', '192.168.1.5', 'ubuntu')..."
                        value={searchTerm}
                        onChange={handleSearchChange}
                        className="w-full bg-[#1a1f3a] border border-[#2d3748] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#00d4ff] transition-all"
                    />
                </div>

                {/* Dropdowns */}
                <div className="flex gap-2">
                    <select
                        value={timeFilter}
                        onChange={(e) => setTimeFilter(e.target.value)}
                        className="bg-[#1a1f3a] border border-[#2d3748] text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none cursor-pointer hover:border-[#00d4ff]/50"
                    >
                        <option value="15m">Last 15 Minutes</option>
                        <option value="1h">Last 1 Hour</option>
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="All">All Time</option>
                    </select>

                    <select
                        value={severityFilter}
                        onChange={(e) => setSeverityFilter(e.target.value)}
                        className="bg-[#1a1f3a] border border-[#2d3748] text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none cursor-pointer hover:border-[#00d4ff]/50"
                    >
                        <option value="All">Severity: All</option>
                        <option value="Critical">Critical Only</option>
                        <option value="Major">Major/High</option>
                        <option value="Minor">Minor/Low</option>
                    </select>

                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="bg-[#1a1f3a] border border-[#2d3748] text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none cursor-pointer hover:border-[#00d4ff]/50"
                    >
                        <option value="All">Status: All</option>
                        <option value="Open">Open</option>
                        <option value="Investigating">Investigating</option>
                        <option value="Closed">Closed</option>
                    </select>

                    <button
                        onClick={() => { setSearchTerm(''); setSeverityFilter('All'); setTimeFilter('All'); setActiveFilters([]); }}
                        className="px-3 py-1.5 bg-red-500/10 text-red-400 rounded-lg text-xs font-bold uppercase hover:bg-red-500/20 border border-transparent hover:border-red-500/30 transition-all flex items-center gap-2"
                        title="Reset all filters"
                    >
                        <Filter className="w-3 h-3" /> Reset
                    </button>
                </div>
            </div>

            {/* Active Filters Chips */}
            {activeFilters.length > 0 && (
                <div className="flex flex-wrap gap-2 px-1">
                    {activeFilters.map((f, i) => (
                        <div key={i} className="flex items-center gap-1 bg-[#00d4ff]/10 border border-[#00d4ff]/30 text-[#00d4ff] px-2 py-0.5 rounded text-[10px] font-bold uppercase animate-in zoom-in-50 duration-200">
                            <span className="opacity-70">{f.field}:</span>
                            <span>{f.value}</span>
                            <button
                                onClick={() => removeFilter(f.field, f.value)}
                                className="ml-1 hover:text-white transition-colors"
                            >
                                ×
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Discovery Table */}
            <div className="bg-[#0a0e27] rounded-xl border border-[#1a1f3a] shadow-2xl overflow-hidden min-h-[400px]">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-[11px] border-collapse font-mono">
                        <thead>
                            <tr className="bg-[#1a1f3a] text-gray-500 font-bold uppercase tracking-widest border-b border-[#2d3748]">
                                <th className="w-10 py-3 px-2 text-center"></th>
                                <th className="py-3 px-4 w-48 whitespace-nowrap">Time</th>
                                <th className="py-3 px-4">Source Data (Click to Filter)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[#1a1f3a]">
                            {filteredAlerts.length > 0 ? (
                                filteredAlerts.map((alert, i) => (
                                    <React.Fragment key={i}>
                                        <tr
                                            className={`hover:bg-[#1a1f3a] transition-colors cursor-pointer group ${expandedRows[i] ? 'bg-[#1a1f3a]/50' : ''}`}
                                            onClick={() => toggleRow(i)}
                                        >
                                            <td className="py-3 px-2 text-center text-gray-600 group-hover:text-[#00d4ff] transition-colors">
                                                <ChevronRight className={`w-4 h-4 mx-auto transition-transform duration-200 ${expandedRows[i] ? 'rotate-90' : ''}`} />
                                            </td>
                                            <td className="py-3 px-4 whitespace-nowrap text-blue-400 font-medium group-hover:text-blue-300">
                                                {alert.time}
                                            </td>
                                            <td className="py-3 px-4">
                                                <div className="flex flex-wrap gap-2 items-center">
                                                    {renderBadges(alert)}
                                                </div>
                                            </td>
                                        </tr>
                                        {expandedRows[i] && (
                                            <tr className="bg-[#060914] border-b border-[#1a1f3a] shadow-inner">
                                                <td colSpan="3" className="p-0">
                                                    <motion.div
                                                        initial={{ opacity: 0, height: 0 }}
                                                        animate={{ opacity: 1, height: 'auto' }}
                                                        className="p-6 border-l-4 border-[#00d4ff] ml-10 my-2"
                                                    >
                                                        {/* Actions */}
                                                        <div className="flex gap-3 mb-6">
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); onAnalyze(alert.entity); }}
                                                                className="flex items-center gap-2 px-4 py-1.5 bg-[#00d4ff] text-black rounded text-[10px] font-bold uppercase hover:bg-[#33ddff] hover:scale-105 transition-all shadow-lg shadow-blue-500/20"
                                                            >
                                                                <Activity className="w-3.5 h-3.5" /> Analyze {alert.entity}
                                                            </button>
                                                            {alert.is_simulated && (
                                                                <span className="flex items-center gap-2 px-3 py-1.5 bg-[#f97316]/10 text-[#f97316] border border-[#f97316]/30 rounded text-[10px] font-bold uppercase">
                                                                    <Zap className="w-3.5 h-3.5" /> AI Simulation
                                                                </span>
                                                            )}
                                                        </div>

                                                        {/* JSON Table */}
                                                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                                            <div className="space-y-1">
                                                                <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 border-b border-gray-800 pb-1">Primary Fields</h4>
                                                                {Object.entries(alert).slice(0, 10).map(([key, value]) => {
                                                                    if (typeof value === 'object') return null;
                                                                    return (
                                                                        <div key={key} className="grid grid-cols-3 gap-4 hover:bg-white/5 p-1 rounded transition-colors group/row">
                                                                            <span className="text-gray-500 text-[10px] font-bold uppercase truncate">{key}</span>
                                                                            <span className="col-span-2 text-gray-300 text-[11px] font-mono break-all group-hover/row:text-white transition-colors">{String(value)}</span>
                                                                        </div>
                                                                    );
                                                                })}
                                                            </div>
                                                            <div className="space-y-2">
                                                                <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 border-b border-gray-800 pb-1">Raw Data</h4>
                                                                <div className="bg-black/40 rounded p-4 border border-gray-800 h-full max-h-[300px] overflow-auto custom-scrollbar">
                                                                    <pre className="text-[10px] text-gray-400 font-mono leading-relaxed">
                                                                        {JSON.stringify(alert, null, 2)}
                                                                    </pre>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </motion.div>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3" className="py-20 text-center">
                                        <div className="flex flex-col items-center justify-center py-12 text-gray-500 animate-in fade-in duration-500">
                                            <ShieldAlert className="w-12 h-12 mb-4 opacity-30 text-[#00d4ff]" />
                                            <p className="text-xs uppercase tracking-widest font-bold mb-2">No events match current filters</p>
                                            <div className="text-[10px] bg-black/40 p-3 rounded mb-4 font-mono text-gray-400 border border-white/5">
                                                <div className="mb-1">Active Search: <span className="text-white">"{searchTerm}"</span></div>
                                                <div className="mb-1">Severity: <span className="text-white">{severityFilter}</span></div>
                                                <div className="mb-1">Time: <span className="text-white">{timeFilter}</span></div>
                                                <div>Payload Size: <span className="text-[#00d4ff] font-bold">{alerts?.length || 0}</span> items</div>
                                            </div>
                                            <button
                                                onClick={() => { setSearchTerm(''); setSeverityFilter('All'); setTimeFilter('All'); setActiveFilters([]); }}
                                                className="px-6 py-2 bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/30 rounded hover:bg-[#00d4ff]/20 transition-all text-xs font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(0,212,255,0.1)] hover:shadow-[0_0_25px_rgba(0,212,255,0.2)]"
                                            >
                                                Clear All Filters & Reset
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

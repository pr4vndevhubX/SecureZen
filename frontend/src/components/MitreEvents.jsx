import React, { useState, useEffect, useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip,
    ResponsiveContainer, CartesianGrid, Cell
} from 'recharts';
import {
    Search, Filter, ChevronDown, ChevronRight, Activity,
    ShieldAlert, Zap, RefreshCw, X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE_URL } from '../config';

// ── Helpers ───────────────────────────────────────────────────────────────────
const LEVEL_COLOR = (level) => {
    const l = parseInt(level) || 0;
    if (l >= 12) return 'bg-red-500/20 text-red-400 border-red-500/40';
    if (l >= 10) return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
    if (l >= 7) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40';
    return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
};

const SEV_COLOR = (sev) => {
    switch ((sev || '').toLowerCase()) {
        case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/40';
        case 'high':
        case 'major': return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
        case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40';
        default: return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    }
};

// Build time-histogram data from alerts (group by hour)
const buildHistogram = (alerts) => {
    const buckets = {};
    alerts.forEach(a => {
        const d = new Date(a.timestamp || a.time);
        if (isNaN(d)) return;
        const key = `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:00`;
        buckets[key] = (buckets[key] || 0) + 1;
    });
    return Object.entries(buckets)
        .sort(([a], [b]) => new Date(a) - new Date(b))
        .map(([time, count]) => ({ time, count }));
};

// Extract all unique field names from alerts
const extractFields = (alerts) => {
    const fieldSet = new Set();
    const CORE = ['timestamp', 'rule_level', 'rule_description', 'agent_name',
        'agent_ip', 'srcip', 'dstip', 'severity', 'rule_id', 'alert_id'];
    CORE.forEach(f => fieldSet.add(f));
    alerts.slice(0, 50).forEach(a => {
        Object.keys(a).forEach(k => {
            if (typeof a[k] !== 'object') fieldSet.add(k);
        });
    });
    return Array.from(fieldSet).sort();
};

// ── Expanded Row ──────────────────────────────────────────────────────────────
const ExpandedRow = ({ alert, onAnalyze, selectedFields }) => {
    const [explaining, setExplaining] = useState(false);
    const [explanation, setExplanation] = useState(null);
    const [aiAction, setAiAction] = useState(null);

    const handleExplain = async () => {
        if (explanation) { setExplanation(null); return; }
        setExplaining(true);
        try {
            const token = localStorage.getItem('auth_token');
            const res = await fetch(`${API_BASE_URL}/api/ai/explain-alert`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ message: alert.rule_description || alert.message })
            });
            const data = await res.json();
            setExplanation(data.explanation);
            if (data.action) setAiAction(data.action);
        } catch {
            setExplanation('AI insight unavailable.');
        }
        setExplaining(false);
    };

    // Show selected fields or all scalar fields
    const displayFields = selectedFields.length > 0
        ? selectedFields
        : Object.keys(alert).filter(k => typeof alert[k] !== 'object');

    return (
        <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-l-4 border-[#00d4ff] ml-8 my-1 bg-[#060914]"
        >
            <div className="p-5">
                {/* Action bar */}
                <div className="flex gap-3 mb-5 flex-wrap">
                    <button
                        onClick={() => onAnalyze(alert.agent_name || alert.srcip || alert.alert_id)}
                        className="flex items-center gap-2 px-4 py-1.5 bg-[#00d4ff] text-black rounded text-[10px] font-bold uppercase hover:bg-[#33ddff] transition-all shadow-lg"
                    >
                        <Activity className="w-3.5 h-3.5" />
                        Analyze {alert.agent_name || 'Agent'}
                    </button>
                    <button
                        onClick={handleExplain}
                        className={`flex items-center gap-2 px-4 py-1.5 rounded text-[10px] font-bold uppercase transition-all border ${explanation
                                ? 'bg-[#60c07c]/20 text-[#60c07c] border-[#60c07c]/40'
                                : 'bg-[#00d4ff]/10 text-[#00d4ff] border-[#00d4ff]/30 hover:bg-[#00d4ff]/20'
                            } ${explaining ? 'animate-pulse' : ''}`}
                    >
                        <Zap className="w-3.5 h-3.5" />
                        {explaining ? 'Analyzing...' : explanation ? 'AI Triaged ✓' : 'AI Triage'}
                    </button>
                </div>

                {explanation && (
                    <div className="mb-4 p-3 bg-[#00d4ff]/5 border border-[#00d4ff]/20 rounded text-[11px] text-[#00d4ff]">
                        <span className="font-bold mr-2">✨ AI INSIGHT:</span>{explanation}
                        {aiAction && <div className="text-[10px] text-gray-400 mt-1"><span className="text-[#60c07c] font-bold mr-2">🎯 NEXT STEP:</span>{aiAction}</div>}
                    </div>
                )}

                {/* Two-column layout: Primary Fields + Raw JSON */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Primary Fields */}
                    <div>
                        <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 border-b border-[#1a1f3a] pb-1">
                            Primary Fields
                        </h4>
                        <div className="space-y-0.5">
                            {displayFields.map(key => {
                                const val = alert[key];
                                if (val === null || val === undefined || val === '') return null;
                                return (
                                    <div key={key} className="grid grid-cols-5 gap-2 hover:bg-white/5 px-1 py-0.5 rounded group/row">
                                        <span className="col-span-2 text-gray-500 text-[10px] font-bold uppercase truncate">{key}</span>
                                        <span className="col-span-3 text-gray-300 text-[11px] font-mono break-all group-hover/row:text-white transition-colors">
                                            {String(val)}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Raw JSON */}
                    <div>
                        <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 border-b border-[#1a1f3a] pb-1">
                            Raw Data
                        </h4>
                        <div className="bg-black/50 rounded border border-[#1a1f3a] p-3 max-h-[300px] overflow-auto">
                            <pre className="text-[10px] text-gray-400 font-mono leading-relaxed whitespace-pre-wrap break-all">
                                {JSON.stringify(alert, null, 2)}
                            </pre>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

// ── Main Component ────────────────────────────────────────────────────────────
export const MitreEvents = ({
    alerts = [],
    onAnalyze,
    initialSeverity = 'All',
    initialStatus = 'All',
    initialSearch = '',
    onSearchChange
}) => {
    const [searchTerm, setSearchTerm] = useState(initialSearch);
    const [severityFilter, setSeverityFilter] = useState(initialSeverity);
    const [statusFilter, setStatusFilter] = useState(initialStatus);
    const [timeFilter, setTimeFilter] = useState('All');
    const [activeFilters, setActiveFilters] = useState([]);
    const [expandedRows, setExpandedRows] = useState({});
    const [selectedFields, setSelectedFields] = useState([
        'timestamp', 'rule_level', 'rule_description', 'agent_name', 'srcip', 'severity'
    ]);
    const [fieldSearch, setFieldSearch] = useState('');

    useEffect(() => { setSearchTerm(initialSearch); }, [initialSearch]);
    useEffect(() => { setSeverityFilter(initialSeverity); }, [initialSeverity]);
    useEffect(() => { setStatusFilter(initialStatus); }, [initialStatus]);

    const allFields = useMemo(() => extractFields(alerts), [alerts]);

    const isWithinTime = (ts, range) => {
        if (range === 'All') return true;
        const diff = Date.now() - new Date(ts);
        const map = { '15m': 9e5, '1h': 36e5, '24h': 864e5, '7d': 6048e5 };
        return diff <= (map[range] || Infinity);
    };

    const filteredAlerts = useMemo(() => {
        return (alerts || []).filter(alert => {
            if (!isWithinTime(alert.timestamp, timeFilter)) return false;
            const q = searchTerm.toLowerCase();
            if (q && !JSON.stringify(alert).toLowerCase().includes(q)) return false;
            if (severityFilter !== 'All') {
                const sev = (alert.severity || '').toLowerCase();
                if (severityFilter === 'Critical' && sev !== 'critical') return false;
                if (severityFilter === 'Major' && !['high', 'major'].includes(sev)) return false;
                if (severityFilter === 'Minor' && !['medium', 'low', 'minor'].includes(sev)) return false;
            }
            if (statusFilter !== 'All' && (alert.status || 'Open') !== statusFilter) return false;
            for (const f of activeFilters) {
                const v = String(alert[f.field] || alert[f.field.replace('.', '_')] || '');
                if (v !== String(f.value)) return false;
            }
            return true;
        });
    }, [alerts, searchTerm, severityFilter, statusFilter, timeFilter, activeFilters]);

    const histogramData = useMemo(() => buildHistogram(filteredAlerts), [filteredAlerts]);

    const addFilter = (field, value) => {
        if (!activeFilters.find(f => f.field === field && f.value === value))
            setActiveFilters(prev => [...prev, { field, value }]);
    };
    const removeFilter = (field, value) =>
        setActiveFilters(prev => prev.filter(f => !(f.field === field && f.value === value)));

    const toggleField = (f) => {
        setSelectedFields(prev =>
            prev.includes(f) ? prev.filter(x => x !== f) : [...prev, f]
        );
    };

    const renderBadges = (alert) => {
        const badges = [
            { field: 'rule.level', label: 'LEVEL', value: alert.rule_level, cls: LEVEL_COLOR(alert.rule_level) },
            { field: 'agent.name', label: 'AGENT', value: alert.agent_name, cls: 'bg-gray-800 text-gray-300 border-gray-600' },
            { field: 'rule.description', label: 'RULE', value: alert.rule_description, cls: 'bg-[#1a1f3a] text-gray-300 border-[#2d3748]' },
            { field: 'srcip', label: 'SRC IP', value: alert.srcip || alert.src_ip, cls: 'bg-purple-900/40 text-purple-300 border-purple-700/50' },
            { field: 'dstip', label: 'DST IP', value: alert.dstip || alert.dst_ip, cls: 'bg-indigo-900/40 text-indigo-300 border-indigo-700/50' },
            { field: 'severity', label: 'SEV', value: alert.severity, cls: SEV_COLOR(alert.severity) },
        ];
        return badges.filter(b => b.value).map((b, i) => (
            <button
                key={i}
                onClick={e => { e.stopPropagation(); addFilter(b.field, b.value); }}
                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono border transition-all hover:brightness-125 active:scale-95 ${b.cls}`}
                title={`Filter: ${b.field} = ${b.value}`}
            >
                <span className="opacity-60 uppercase font-bold">{b.label}</span>
                <span className="font-semibold truncate max-w-[180px]">{String(b.value)}</span>
            </button>
        ));
    };

    const visibleFields = allFields.filter(f =>
        !fieldSearch || f.toLowerCase().includes(fieldSearch.toLowerCase())
    );

    return (
        <div className="flex gap-0 h-full min-h-screen bg-[#060914] font-mono">

            {/* ── LEFT: Field List (Wazuh sidebar) ── */}
            <div className="w-52 flex-shrink-0 border-r border-[#1a1f3a] bg-[#060914] flex flex-col">
                <div className="p-3 border-b border-[#1a1f3a]">
                    <div className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-2">Selected Fields</div>
                    <div className="space-y-0.5">
                        {selectedFields.map(f => (
                            <div key={f} className="flex items-center gap-1.5 group cursor-pointer hover:bg-[#1a1f3a] px-1 py-0.5 rounded"
                                onClick={() => toggleField(f)}>
                                <span className="w-2 h-2 rounded-full bg-[#00d4ff] flex-shrink-0" />
                                <span className="text-[10px] text-[#00d4ff] truncate flex-1">{f}</span>
                                <X className="w-2.5 h-2.5 text-gray-600 group-hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all" />
                            </div>
                        ))}
                    </div>
                </div>
                <div className="p-3 flex-1 overflow-hidden flex flex-col">
                    <div className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-2">Available Fields</div>
                    <div className="relative mb-2">
                        <Search className="w-2.5 h-2.5 text-gray-600 absolute left-2 top-1/2 -translate-y-1/2" />
                        <input
                            type="text"
                            placeholder="Filter by type"
                            value={fieldSearch}
                            onChange={e => setFieldSearch(e.target.value)}
                            className="w-full bg-[#1a1f3a] border border-[#2d3748] rounded pl-6 pr-2 py-1 text-[9px] text-gray-300 focus:outline-none focus:border-[#00d4ff]/50"
                        />
                    </div>
                    <div className="overflow-y-auto flex-1 space-y-0.5">
                        {visibleFields.filter(f => !selectedFields.includes(f)).map(f => (
                            <div key={f}
                                className="flex items-center gap-1.5 group cursor-pointer hover:bg-[#1a1f3a] px-1 py-0.5 rounded"
                                onClick={() => toggleField(f)}
                            >
                                <span className="text-[9px] text-gray-400 font-bold w-3 flex-shrink-0">t</span>
                                <span className="text-[10px] text-gray-400 truncate flex-1 group-hover:text-white transition-colors">{f}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* ── RIGHT: Main content ── */}
            <div className="flex-1 flex flex-col overflow-hidden">

                {/* Hits count + histogram */}
                <div className="bg-[#060914] border-b border-[#1a1f3a] p-4">
                    <div className="flex items-baseline gap-3 mb-1">
                        <span className="text-3xl font-bold text-white">{filteredAlerts.length.toLocaleString()}</span>
                        <span className="text-[10px] text-gray-500 uppercase tracking-widest">hits</span>
                        {alerts.length !== filteredAlerts.length && (
                            <span className="text-[10px] text-gray-600">
                                (filtered from {alerts.length.toLocaleString()} total)
                            </span>
                        )}
                    </div>
                    <div className="h-28">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={histogramData} margin={{ top: 4, right: 8, left: -30, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1a1f3a" vertical={false} />
                                <XAxis dataKey="time" stroke="#374151" tick={{ fontSize: 8 }} interval="preserveStartEnd" />
                                <YAxis stroke="#374151" tick={{ fontSize: 8 }} />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: '#0a0e27', border: '1px solid #1a1f3a', borderRadius: '6px', fontSize: '11px' }}
                                    itemStyle={{ color: '#fff' }}
                                    cursor={{ fill: 'rgba(0,212,255,0.05)' }}
                                />
                                <Bar dataKey="count" fill="#1d4ed8" radius={[2, 2, 0, 0]} barSize={12} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Search + Filters */}
                <div className="bg-[#060914] border-b border-[#1a1f3a] px-4 py-2 flex flex-wrap gap-2 items-center sticky top-0 z-20">
                    <div className="relative flex-1 min-w-[240px]">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
                        <input
                            type="text"
                            placeholder="Search (e.g. 'Integrity', '192.168.1.5', 'ubuntu')..."
                            value={searchTerm}
                            onChange={e => { setSearchTerm(e.target.value); onSearchChange?.(e.target.value); }}
                            className="w-full bg-[#0a0e27] border border-[#2d3748] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#00d4ff] transition-all"
                        />
                    </div>
                    <select value={timeFilter} onChange={e => setTimeFilter(e.target.value)}
                        className="bg-[#0a0e27] border border-[#2d3748] text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none cursor-pointer hover:border-[#00d4ff]/50">
                        <option value="All">All Time</option>
                        <option value="15m">Last 15 min</option>
                        <option value="1h">Last 1 hour</option>
                        <option value="24h">Last 24 hours</option>
                        <option value="7d">Last 7 days</option>
                    </select>
                    <select value={severityFilter} onChange={e => setSeverityFilter(e.target.value)}
                        className="bg-[#0a0e27] border border-[#2d3748] text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none cursor-pointer hover:border-[#00d4ff]/50">
                        <option value="All">Severity: All</option>
                        <option value="Critical">Critical</option>
                        <option value="Major">Major / High</option>
                        <option value="Minor">Minor / Low</option>
                    </select>
                    <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
                        className="bg-[#0a0e27] border border-[#2d3748] text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none cursor-pointer hover:border-[#00d4ff]/50">
                        <option value="All">Status: All</option>
                        <option value="Open">Open</option>
                        <option value="Investigating">Investigating</option>
                        <option value="Closed">Closed</option>
                    </select>
                    <button
                        onClick={() => { setSearchTerm(''); setSeverityFilter('All'); setTimeFilter('All'); setActiveFilters([]); }}
                        className="px-3 py-1.5 bg-red-500/10 text-red-400 rounded-lg text-xs font-bold uppercase hover:bg-red-500/20 border border-transparent hover:border-red-500/30 transition-all flex items-center gap-1.5"
                    >
                        <Filter className="w-3 h-3" /> Reset
                    </button>
                </div>

                {/* Active filter chips */}
                {activeFilters.length > 0 && (
                    <div className="px-4 py-2 flex flex-wrap gap-2 border-b border-[#1a1f3a] bg-[#060914]">
                        {activeFilters.map((f, i) => (
                            <div key={i} className="flex items-center gap-1 bg-[#00d4ff]/10 border border-[#00d4ff]/30 text-[#00d4ff] px-2 py-0.5 rounded text-[10px] font-bold">
                                <span className="opacity-60">{f.field}:</span>
                                <span>{f.value}</span>
                                <button onClick={() => removeFilter(f.field, f.value)} className="ml-1 hover:text-white">×</button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Discovery Table */}
                <div className="flex-1 overflow-auto">
                    <table className="w-full text-left text-[11px] border-collapse">
                        <thead className="sticky top-0 z-10">
                            <tr className="bg-[#0a0e27] text-gray-500 font-bold uppercase tracking-widest border-b border-[#1a1f3a] text-[9px]">
                                <th className="w-8 py-2 px-2" />
                                <th className="py-2 px-3 w-44 whitespace-nowrap">Time</th>
                                <th className="py-2 px-3">Source Data (Click to Filter)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredAlerts.length > 0 ? (
                                filteredAlerts.map((alert, i) => (
                                    <React.Fragment key={i}>
                                        <tr
                                            className={`hover:bg-[#0a0e27] transition-colors cursor-pointer group border-b border-[#1a1f3a]/50 ${expandedRows[i] ? 'bg-[#0a0e27]' : ''}`}
                                            onClick={() => setExpandedRows(prev => ({ ...prev, [i]: !prev[i] }))}
                                        >
                                            <td className="py-2 px-2 text-center text-gray-600 group-hover:text-[#00d4ff] transition-colors">
                                                <ChevronRight className={`w-3.5 h-3.5 mx-auto transition-transform duration-150 ${expandedRows[i] ? 'rotate-90 text-[#00d4ff]' : ''}`} />
                                            </td>
                                            <td className="py-2 px-3 whitespace-nowrap text-blue-400 text-[10px] group-hover:text-blue-300">
                                                {alert.time || new Date(alert.timestamp).toLocaleString()}
                                            </td>
                                            <td className="py-2 px-3">
                                                <div className="flex flex-wrap gap-1.5 items-center">
                                                    {renderBadges(alert)}
                                                </div>
                                            </td>
                                        </tr>
                                        <AnimatePresence>
                                            {expandedRows[i] && (
                                                <tr key={`exp-${i}`} className="border-b border-[#1a1f3a]">
                                                    <td colSpan="3" className="p-0">
                                                        <ExpandedRow
                                                            alert={alert}
                                                            onAnalyze={onAnalyze}
                                                            selectedFields={selectedFields}
                                                        />
                                                    </td>
                                                </tr>
                                            )}
                                        </AnimatePresence>
                                    </React.Fragment>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3" className="py-24 text-center">
                                        <div className="flex flex-col items-center text-gray-600">
                                            <ShieldAlert className="w-10 h-10 mb-3 opacity-30 text-[#00d4ff]" />
                                            <p className="text-xs uppercase tracking-widest font-bold mb-2">No events match current filters</p>
                                            <p className="text-[10px] text-gray-700 mb-4">
                                                {alerts.length === 0
                                                    ? 'No alerts in database yet — run the pre-processor to populate'
                                                    : `${alerts.length} total alerts, none match current filters`}
                                            </p>
                                            <button
                                                onClick={() => { setSearchTerm(''); setSeverityFilter('All'); setTimeFilter('All'); setActiveFilters([]); }}
                                                className="px-5 py-2 bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/30 rounded hover:bg-[#00d4ff]/20 transition-all text-xs font-bold uppercase"
                                            >
                                                Clear All Filters
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

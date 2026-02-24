import React, { useState, useEffect, useCallback } from 'react';
import {
    ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, PieChart, Pie, Cell, Legend, Area, AreaChart
} from 'recharts';
import {
    Activity, Database, AlertTriangle, RefreshCw, Cpu,
    Search, User, Zap, Shield, Play, CheckSquare,
    Square, FileText, CheckCircle, XCircle, Loader, ChevronDown, ChevronRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ThreatFunnel from './ThreatFunnel';
import { TrendChart, ThreatEntities, AttackPaths } from './MitreCharts';
import { API_BASE_URL } from '../config';

const COLORS = ['#00d4ff', '#f97316', '#60c07c', '#ba6fd4', '#4daaf8', '#fbbf24', '#ef4444', '#22c55e'];

// ── Stat Card ────────────────────────────────────────────────────────────────
const StatCard = ({ icon: Icon, label, value, color, bg, onClick }) => (
    <div
        onClick={onClick}
        className="bg-[#0a0e27] rounded-xl p-4 border border-[#1a1f3a] flex items-center justify-between shadow-xl hover:border-[#00d4ff]/50 hover:bg-[#00d4ff]/5 transition-all cursor-pointer group"
    >
        <div className="flex flex-col justify-center">
            <div className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-1">{label}</div>
            <div className="text-2xl font-bold text-white tracking-widest leading-none">{value ?? '0'}</div>
        </div>
        <div className={`p-2 rounded-lg ${bg}`}>
            <Icon className={`w-4 h-4 ${color}`} />
        </div>
    </div>
);

// ── Recharts Tooltip ─────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#0a0e27] border border-[#2d3748] rounded-xl px-3 py-2 text-xs shadow-2xl">
                <div className="text-gray-400 mb-1">{label}</div>
                {payload.map((p, i) => (
                    <div key={i} style={{ color: p.color }} className="font-bold">
                        {p.name}: {p.value?.toLocaleString()}
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

// ── Analysis Control Panel ────────────────────────────────────────────────────
const AnalysisControlPanel = ({ onAnalysisComplete }) => {
    const [datasets, setDatasets] = useState([]);
    const [selected, setSelected] = useState([]);
    const [jobStatus, setJobStatus] = useState(null);
    const [isLoadingFiles, setIsLoadingFiles] = useState(false);

    const authHeaders = () => ({
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    });

    // Fetch available datasets on mount
    const fetchDatasets = useCallback(async () => {
        setIsLoadingFiles(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/logai/datasets`, { headers: authHeaders() });
            if (res.ok) {
                const data = await res.json();
                const files = data.files || [];
                setDatasets(files);
                // Default: pre-select the smaller (2000/5000) quick files
                const quick = files.filter(f => f.basename.includes('2000') || f.basename.includes('5000'));
                setSelected(quick.map(f => f.filename));
            }
        } catch (e) {
            console.error('Failed to fetch datasets:', e);
        } finally {
            setIsLoadingFiles(false);
        }
    }, []);

    useEffect(() => { fetchDatasets(); }, [fetchDatasets]);

    // Poll status while a job is running
    useEffect(() => {
        if (!jobStatus || jobStatus.status === 'idle') return;
        if (jobStatus.status === 'complete' || jobStatus.status === 'error') {
            if (jobStatus.status === 'complete') setTimeout(() => onAnalysisComplete(), 1200);
            return;
        }
        const timer = setTimeout(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/logai/analysis-status`, { headers: authHeaders() });
                if (res.ok) setJobStatus(await res.json());
            } catch (_) { }
        }, 1500);
        return () => clearTimeout(timer);
    }, [jobStatus, onAnalysisComplete]);

    const toggleFile = (filename) =>
        setSelected(prev => prev.includes(filename) ? prev.filter(f => f !== filename) : [...prev, filename]);

    const toggleAll = () =>
        setSelected(prev => prev.length === datasets.length ? [] : datasets.map(f => f.filename));

    const runAnalysis = async () => {
        if (selected.length === 0) return;
        try {
            const res = await fetch(`${API_BASE_URL}/api/logai/run-analysis`, {
                method: 'POST',
                headers: { ...authHeaders(), 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: selected })
            });
            if (res.ok) {
                const data = await res.json();
                setJobStatus({
                    status: data.status === 'started' ? 'running' : data.status,
                    progress: 0,
                    message: data.message,
                    current_file: '',
                    last_run: null
                });
            }
        } catch (e) {
            setJobStatus({ status: 'error', message: `Failed to start: ${e.message}`, progress: 0 });
        }
    };

    const isRunning = jobStatus?.status === 'running';
    const sizeLabel = (kb) => kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`;

    return (
        <div className="bg-[#0a0e27] rounded-2xl border border-[#1a1f3a] p-5 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                    <FileText className="w-4 h-4 text-[#00d4ff]" />
                    Run LogAI Analysis on Datasets
                </h3>
                <button
                    onClick={fetchDatasets}
                    className="p-1.5 rounded-lg bg-[#1a1f3a] border border-[#2d3748] hover:border-[#00d4ff]/50 transition-all"
                    title="Refresh file list"
                >
                    <RefreshCw className="w-3 h-3 text-gray-400" />
                </button>
            </div>

            {/* File Selector */}
            <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">
                        {isLoadingFiles ? 'Scanning datasets...' : `${datasets.length} log files — ${selected.length} selected`}
                    </span>
                    {datasets.length > 0 && !isRunning && (
                        <button onClick={toggleAll} className="text-[10px] text-[#00d4ff] hover:underline">
                            {selected.length === datasets.length ? 'Deselect All' : 'Select All'}
                        </button>
                    )}
                </div>
                <div className="max-h-52 overflow-y-auto space-y-1 pr-1">
                    {datasets.map((file) => {
                        const isChecked = selected.includes(file.filename);
                        return (
                            <div
                                key={file.filename}
                                onClick={() => !isRunning && toggleFile(file.filename)}
                                className={`flex items-center justify-between px-3 py-2 rounded-lg border cursor-pointer transition-all text-xs ${isChecked
                                        ? 'bg-[#00d4ff]/10 border-[#00d4ff]/30 text-white'
                                        : 'border-[#1a1f3a] text-gray-400 hover:border-[#2d3748] hover:text-white'
                                    } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                <div className="flex items-center gap-2 min-w-0">
                                    {isChecked
                                        ? <CheckSquare className="w-3.5 h-3.5 text-[#00d4ff] shrink-0" />
                                        : <Square className="w-3.5 h-3.5 text-gray-600 shrink-0" />
                                    }
                                    <span className="font-mono truncate">{file.basename}</span>
                                </div>
                                <span className="text-[10px] text-gray-600 shrink-0 ml-2">{sizeLabel(file.size_kb)}</span>
                            </div>
                        );
                    })}
                    {datasets.length === 0 && !isLoadingFiles && (
                        <div className="text-center py-6 text-gray-600 italic text-xs">
                            No datasets found. Make sure the engine/datasets/ folder contains log files.
                        </div>
                    )}
                </div>
            </div>

            {/* Progress Indicator */}
            <AnimatePresence>
                {jobStatus && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mb-4 overflow-hidden"
                    >
                        <div className="flex items-center gap-2 mb-1.5">
                            {jobStatus.status === 'running' && <Loader className="w-3 h-3 text-[#00d4ff] animate-spin shrink-0" />}
                            {jobStatus.status === 'complete' && <CheckCircle className="w-3 h-3 text-green-400 shrink-0" />}
                            {jobStatus.status === 'error' && <XCircle className="w-3 h-3 text-red-400 shrink-0" />}
                            <span className={`text-[10px] font-bold uppercase tracking-wide truncate ${jobStatus.status === 'complete' ? 'text-green-400' :
                                    jobStatus.status === 'error' ? 'text-red-400' : 'text-[#00d4ff]'
                                }`}>
                                {jobStatus.message}
                            </span>
                        </div>
                        <div className="h-1.5 bg-[#1a1f3a] rounded-full overflow-hidden">
                            <motion.div
                                className="h-full rounded-full"
                                style={{
                                    backgroundColor:
                                        jobStatus.status === 'error' ? '#ef4444' :
                                            jobStatus.status === 'complete' ? '#60c07c' : '#00d4ff'
                                }}
                                animate={{ width: `${jobStatus.progress || 0}%` }}
                                transition={{ ease: 'easeInOut', duration: 0.4 }}
                            />
                        </div>
                        {jobStatus.current_file && (
                            <p className="text-[9px] text-gray-600 mt-1 font-mono">↳ {jobStatus.current_file}</p>
                        )}
                        {jobStatus.last_run && (
                            <p className="text-[9px] text-gray-500 mt-1">
                                Completed at: {new Date(jobStatus.last_run).toLocaleString()}
                            </p>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Run Button */}
            <button
                onClick={runAnalysis}
                disabled={isRunning || selected.length === 0}
                className={`w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-bold text-xs uppercase tracking-widest transition-all shadow-lg ${isRunning || selected.length === 0
                        ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                        : 'bg-[#00d4ff] text-[#060914] hover:bg-[#00d4ff]/90 hover:shadow-[0_0_20px_rgba(0,212,255,0.3)] active:scale-95'
                    }`}
            >
                {isRunning
                    ? <><Loader className="w-3.5 h-3.5 animate-spin" /> Analyzing…</>
                    : <><Play className="w-3.5 h-3.5" /> Run Analysis ({selected.length} file{selected.length !== 1 ? 's' : ''})</>
                }
            </button>
        </div>
    );
};

// ── Main LogAI Dashboard ──────────────────────────────────────────────────────
const LogAIDashboard = ({ setActiveTab, setEventFilter, setStatusFilter }) => {
    const [stats, setStats] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastRefresh, setLastRefresh] = useState('');
    const [patternSearch, setPatternSearch] = useState('');
    const [showControlPanel, setShowControlPanel] = useState(false);

    const fetchData = useCallback(async () => {
        const token = localStorage.getItem('auth_token');
        const headers = { 'Authorization': `Bearer ${token}` };
        try {
            const [statsRes, timelineRes] = await Promise.all([
                fetch(`${API_BASE_URL}/api/logai/stats`, { headers }),
                fetch(`${API_BASE_URL}/api/logai/anomaly-timeline`, { headers })
            ]);
            if (statsRes.ok) setStats(await statsRes.json());
            if (timelineRes.ok) {
                const data = await timelineRes.json();
                const formatted = (data.timeline || []).map(t => ({
                    ...t,
                    label: t.time
                        ? new Date(t.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        : t.time
                }));
                setTimeline(formatted);
            }
            setLastRefresh(new Date().toLocaleTimeString());
        } catch (e) {
            console.error('SecureZen Analysis fetch error:', e);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const filteredPatterns = (stats?.top_patterns || []).filter(p =>
        !patternSearch || p.pattern?.toLowerCase().includes(patternSearch.toLowerCase())
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <Cpu className="w-12 h-12 text-[#00d4ff] animate-pulse mx-auto mb-3" />
                    <div className="text-[#00d4ff] font-bold uppercase tracking-widest text-sm animate-pulse">
                        Loading SecureZen Analysis...
                    </div>
                </div>
            </div>
        );
    }

    const severityData = stats?.severity
        ? Object.entries(stats.severity).map(([name, value]) => ({ name, value }))
        : [];

    const hasData = (stats?.pattern_count || 0) > 0 || (stats?.cluster_count || 0) > 0;

    return (
        <div className="space-y-6">
            {/* ── Page Header ───────────────────────────────────────────── */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-bold text-white uppercase tracking-widest flex items-center gap-3">
                        <Cpu className="w-6 h-6 text-[#00d4ff]" />
                        SecureZen Analysis
                    </h2>
                    <p className="text-gray-500 text-xs mt-1">
                        Pattern extraction · Threat clustering · Anomaly detection
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="text-[10px] text-gray-500 uppercase">Last refresh: {lastRefresh}</div>
                    <button
                        onClick={fetchData}
                        className="p-2 rounded-lg bg-[#1a1f3a] border border-[#2d3748] hover:border-[#00d4ff]/50 transition-all"
                    >
                        <RefreshCw className="w-4 h-4 text-[#00d4ff]" />
                    </button>
                    {/* Toggle control panel */}
                    <button
                        onClick={() => setShowControlPanel(p => !p)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider border transition-all ${showControlPanel
                                ? 'bg-[#00d4ff]/10 border-[#00d4ff]/30 text-[#00d4ff]'
                                : 'bg-[#1a1f3a] border-[#2d3748] text-gray-400 hover:text-white'
                            }`}
                    >
                        <Play className="w-3 h-3" />
                        Run Analysis
                        {showControlPanel ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                    </button>
                    <div className="px-3 py-1 bg-[#00d4ff]/10 border border-[#00d4ff]/20 rounded-full">
                        <span className="text-[10px] font-bold text-[#00d4ff] uppercase">Neural Engine Active</span>
                    </div>
                </div>
            </div>

            {/* ── Control Panel (collapsible) ───────────────────────────── */}
            <AnimatePresence>
                {showControlPanel && (
                    <motion.div
                        key="control-panel"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                    >
                        <AnalysisControlPanel onAnalysisComplete={() => { fetchData(); }} />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* ── No Data Banner ────────────────────────────────────────── */}
            {!hasData && (
                <div className="bg-[#1a1f3a]/30 border border-dashed border-[#2d3748] rounded-2xl p-8 text-center">
                    <FileText className="w-10 h-10 text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-400 font-bold text-sm mb-1">No analysis data yet</p>
                    <p className="text-gray-600 text-xs mb-4">
                        Click <span className="text-[#00d4ff] font-mono">"Run Analysis"</span> above to process the datasets and populate the dashboard.
                    </p>
                    <button
                        onClick={() => setShowControlPanel(true)}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-[#00d4ff] text-[#060914] rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-[#00d4ff]/90 transition-all"
                    >
                        <Play className="w-3.5 h-3.5" /> Open Run Panel
                    </button>
                </div>
            )}

            {/* ── Top Metrics Row ──────────────────────────────────────── */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <StatCard label="Critical Alerts" value={stats?.global_severity?.Critical} color="text-red-500" bg="bg-red-500/10" icon={AlertTriangle} onClick={() => { setEventFilter('Critical'); setActiveTab('events'); }} />
                <StatCard label="Major Alerts" value={stats?.global_severity?.High} color="text-orange-500" bg="bg-orange-500/10" icon={AlertTriangle} onClick={() => { setEventFilter('High'); setActiveTab('events'); }} />
                <StatCard label="Minor Alerts" value={stats?.global_severity?.Medium} color="text-yellow-500" bg="bg-yellow-500/10" icon={AlertTriangle} onClick={() => { setEventFilter('Medium'); setActiveTab('events'); }} />
                <StatCard label="Unassigned" value={stats?.status_counts?.Open} color="text-blue-400" bg="bg-blue-400/10" icon={User} onClick={() => { setStatusFilter('Open'); setActiveTab('events'); }} />
                <StatCard label="Closed Cases" value={stats?.status_counts?.Closed} color="text-green-500" bg="bg-green-500/10" icon={Database} onClick={() => { setStatusFilter('Closed'); setActiveTab('events'); }} />
                <StatCard label="Remediated" value={stats?.remediated || 0} color="text-purple-500" bg="bg-purple-500/10" icon={Zap} onClick={() => { setStatusFilter('Remediated'); setActiveTab('events'); }} />
            </div>

            {/* ── Funnel + Trend ───────────────────────────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-4 bg-[#0a0e27] rounded-3xl overflow-hidden border border-[#1a1f3a] shadow-2xl h-[400px]">
                    <ThreatFunnel
                        events={stats?.total_lines || 0}
                        detections={stats?.total_alerts || 0}
                        alerts={stats?.anomaly_count || 0}
                    />
                </div>
                <div className="lg:col-span-8">
                    <TrendChart data={stats?.alert_trends} />
                </div>
            </div>

            {/* ── Intelligence: Top IPs + Attack Paths ─────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ThreatEntities data={stats?.top_ips} />
                <AttackPaths data={stats?.top_vectors} />
            </div>

            {/* ── Anomaly Timeline + Severity Donut ───────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Timeline */}
                <div className="lg:col-span-2 bg-[#0a0e27] rounded-3xl p-6 border border-[#1a1f3a] shadow-2xl">
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-[#00d4ff]" />
                        Anomaly Timeline
                    </h3>
                    {timeline.length > 0 ? (
                        <ResponsiveContainer width="100%" height={220}>
                            <AreaChart data={timeline} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                                <defs>
                                    <linearGradient id="anomalyGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="highGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1a1f3a" />
                                <XAxis dataKey="label" stroke="#4a5568" tick={{ fontSize: 9 }} interval="preserveStartEnd" />
                                <YAxis stroke="#4a5568" tick={{ fontSize: 9 }} />
                                <Tooltip content={<CustomTooltip />} />
                                <Area type="monotone" dataKey="anomalies" name="Anomalies" stroke="#f97316" fill="url(#anomalyGrad)" strokeWidth={2} dot={false} />
                                <Area type="monotone" dataKey="high" name="High/Critical" stroke="#ef4444" fill="url(#highGrad)" strokeWidth={2} dot={false} />
                            </AreaChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[220px] flex items-center justify-center text-gray-600 italic text-sm">
                            No anomaly data yet — run the analysis to populate
                        </div>
                    )}
                </div>

                {/* Severity Donut */}
                <div className="bg-[#0a0e27] rounded-3xl p-6 border border-[#1a1f3a] shadow-2xl">
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-4">Severity Breakdown</h3>
                    {severityData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={220}>
                            <PieChart>
                                <Pie
                                    data={severityData}
                                    cx="50%" cy="50%"
                                    innerRadius={55} outerRadius={80}
                                    paddingAngle={4}
                                    dataKey="value"
                                    onClick={(d) => { if (d?.name) { setEventFilter(d.name); setActiveTab('events'); } }}
                                    className="cursor-pointer"
                                >
                                    {severityData.map((entry, i) => (
                                        <Cell key={i} fill={
                                            entry.name === 'Critical' ? '#ef4444' :
                                                entry.name === 'High' ? '#f97316' :
                                                    entry.name === 'Medium' ? '#fbbf24' : '#60c07c'
                                        } />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#0a0e27', borderColor: '#2d3748' }} itemStyle={{ color: '#fff' }} />
                                <Legend iconSize={8} layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ fontSize: '10px', paddingTop: '10px' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[220px] flex items-center justify-center text-gray-600 italic text-sm">No data</div>
                    )}
                </div>
            </div>

            {/* ── Neural AI Insights + Recent Alerts ──────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* AI Insights */}
                <div className="lg:col-span-5 bg-[#0a0e27] rounded-3xl p-6 border border-[#1a1f3a] shadow-2xl overflow-hidden relative group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Zap className="w-16 h-16 text-[#00d4ff]" />
                    </div>
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2 relative z-10">
                        <Cpu className="w-4 h-4 text-[#00d4ff]" /> Neural AI Insights
                    </h3>
                    <div className="space-y-4 relative z-10">
                        {(stats?.ai_insights || []).map((insight, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="flex gap-4 p-4 rounded-2xl bg-[#1a1f3a]/30 border border-[#1a1f3a] hover:border-[#00d4ff]/30 transition-all"
                            >
                                <div className="mt-1">
                                    <div className="w-2 h-2 rounded-full bg-[#00d4ff] shadow-[0_0_10px_#00d4ff]" />
                                </div>
                                <p className="text-sm text-gray-300 leading-relaxed font-medium">{insight}</p>
                            </motion.div>
                        ))}
                        {(!stats?.ai_insights || stats.ai_insights.length === 0) && (
                            <div className="text-gray-600 italic text-sm text-center py-8">
                                Run analysis to generate AI insights
                            </div>
                        )}
                    </div>
                </div>

                {/* Recent Critical Alerts Feed */}
                <div className="lg:col-span-7 bg-[#0a0e27] rounded-3xl border border-[#1a1f3a] shadow-2xl overflow-hidden">
                    <div className="bg-[#1a1f3a] px-6 py-4 border-b border-[#2d3748] flex items-center justify-between">
                        <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                            <Shield className="w-4 h-4 text-red-500" /> Recent Critical Threats
                        </h3>
                        <button onClick={() => setActiveTab('events')} className="text-[10px] font-bold text-[#00d4ff] uppercase tracking-wider hover:underline">
                            View All Results
                        </button>
                    </div>
                    <div className="overflow-auto max-h-[350px]">
                        <table className="w-full text-left text-sm text-gray-400">
                            <thead className="bg-[#060914] text-[10px] uppercase font-bold text-gray-500 sticky top-0">
                                <tr>
                                    <th className="px-5 py-3">Threat Description</th>
                                    <th className="px-5 py-3 text-right w-24">Severity</th>
                                    <th className="px-5 py-3 text-right w-36">Timestamp</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[#1a1f3a]">
                                {(stats?.recent_alerts || []).map((alert, idx) => (
                                    <tr
                                        key={idx}
                                        className="hover:bg-red-500/5 transition-colors cursor-pointer group"
                                        onClick={() => { setEventFilter(alert.severity); setActiveTab('events'); }}
                                    >
                                        <td className="px-5 py-4">
                                            <div className="font-bold text-white text-xs group-hover:text-red-400 transition-colors">{alert.description}</div>
                                            <div className="text-[10px] text-gray-600 mt-1 font-mono">
                                                SRC: {alert.srcip || 'Local'} · Agent: {alert.agent || 'SYSTEM'}
                                            </div>
                                        </td>
                                        <td className="px-5 py-4 text-right">
                                            <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${alert.severity === 'Critical'
                                                    ? 'bg-red-500/10 text-red-500 border border-red-500/20'
                                                    : 'bg-orange-500/10 text-orange-500 border border-orange-500/20'
                                                }`}>
                                                {alert.severity}
                                            </span>
                                        </td>
                                        <td className="px-5 py-4 text-right text-[10px] text-gray-500 font-mono">
                                            {new Date(alert.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                                        </td>
                                    </tr>
                                ))}
                                {(!stats?.recent_alerts || stats.recent_alerts.length === 0) && (
                                    <tr>
                                        <td colSpan="3" className="px-5 py-12 text-center text-gray-600 italic">
                                            No high-severity threats detected. Run analysis to populate.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* ── Log Patterns Table ───────────────────────────────────── */}
            <div className="bg-[#0a0e27] rounded-3xl border border-[#1a1f3a] shadow-2xl overflow-hidden">
                <div className="bg-[#1a1f3a] px-6 py-4 border-b border-[#2d3748] flex items-center justify-between">
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                        <Search className="w-4 h-4 text-[#00d4ff]" />
                        Log Pattern Analysis
                        <span className="ml-2 px-2 py-0.5 bg-[#00d4ff]/10 border border-[#00d4ff]/20 rounded text-[10px] text-[#00d4ff]">
                            {stats?.pattern_count || 0} patterns · {stats?.cluster_count || 0} clusters
                        </span>
                    </h3>
                    <div className="flex items-center gap-2">
                        <input
                            type="text"
                            placeholder="Search patterns…"
                            value={patternSearch}
                            onChange={e => setPatternSearch(e.target.value)}
                            className="text-xs bg-[#060914] border border-[#2d3748] rounded-lg px-3 py-1.5 text-gray-300 placeholder-gray-600 focus:outline-none focus:border-[#00d4ff]/50 w-48"
                        />
                    </div>
                </div>
                <div className="overflow-auto max-h-72">
                    <table className="w-full text-left text-sm text-gray-400">
                        <thead className="bg-[#060914] text-[10px] uppercase font-bold text-gray-500 sticky top-0">
                            <tr>
                                <th className="px-5 py-3">Pattern ID</th>
                                <th className="px-5 py-3">Log Signature Template</th>
                                <th className="px-5 py-3 text-right">Occurrences</th>
                                <th className="px-5 py-3 text-right">Last Seen</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[#1a1f3a]">
                            {filteredPatterns.map((pattern, idx) => (
                                <tr key={idx} className="hover:bg-[#1a1f3a]/50 transition-colors">
                                    <td className="px-5 py-3 text-[#00d4ff] font-mono text-xs">#{pattern.id || idx + 1}</td>
                                    <td className="px-5 py-3 font-mono text-xs text-gray-300 truncate max-w-[500px]" title={pattern.pattern}>
                                        {pattern.pattern}
                                    </td>
                                    <td className="px-5 py-3 text-right font-bold text-white">{pattern.count?.toLocaleString()}</td>
                                    <td className="px-5 py-3 text-right text-xs text-gray-500">
                                        {pattern.last_seen ? new Date(pattern.last_seen).toLocaleTimeString() : '—'}
                                    </td>
                                </tr>
                            ))}
                            {filteredPatterns.length === 0 && (
                                <tr>
                                    <td colSpan="4" className="px-5 py-10 text-center text-gray-600 italic">
                                        {patternSearch ? `No patterns matching "${patternSearch}"` : 'No patterns yet — run analysis to populate'}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* ── Cluster Bar Chart ────────────────────────────────────── */}
            {(stats?.clusters || []).length > 0 && (
                <div className="bg-[#0a0e27] rounded-3xl p-6 border border-[#1a1f3a] shadow-2xl">
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Layers className="w-4 h-4 text-[#ba6fd4]" /> Cluster Distribution
                    </h3>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={stats.clusters} layout="vertical" margin={{ top: 0, right: 20, left: 60, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1a1f3a" horizontal={false} />
                            <XAxis type="number" stroke="#4a5568" tick={{ fontSize: 9 }} />
                            <YAxis dataKey="name" type="category" width={120} stroke="#4a5568" tick={{ fontSize: 9 }} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="value" name="Log Lines" radius={[0, 4, 4, 0]} barSize={16}>
                                {(stats.clusters || []).map((_, index) => (
                                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
    );
};

export default LogAIDashboard;

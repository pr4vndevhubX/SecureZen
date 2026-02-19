import React, { useState, useEffect, useCallback } from 'react';
import {
    ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, PieChart, Pie, Cell, Legend, LineChart, Line, Area, AreaChart
} from 'recharts';
import {
    Activity, Database, AlertTriangle, Layers, RefreshCw, Cpu,
    Search, User, Zap, Shield, TrendingUp, Filter
} from 'lucide-react';
import { motion } from 'framer-motion';
import ThreatFunnel from './ThreatFunnel';
import { TrendChart, ThreatEntities, AttackPaths } from './MitreCharts';
import { API_BASE_URL } from '../config';

const COLORS = ['#00d4ff', '#f97316', '#60c07c', '#ba6fd4', '#4daaf8', '#fbbf24', '#ef4444', '#22c55e'];

const StatCard = ({ icon: Icon, label, value, color, bg, onClick }) => (
    <div
        onClick={onClick}
        className={`bg-[#0a0e27] rounded-xl p-4 border border-[#1a1f3a] flex items-center justify-between shadow-xl hover:border-[#00d4ff]/50 hover:bg-[#00d4ff]/5 transition-all cursor-pointer group`}
    >
        <div className="flex flex-col justify-center">
            <div className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-1">{label}</div>
            <div className="text-2xl font-bold text-white tracking-widest leading-none">{value ?? '0'}</div>
        </div>
        <div className={`p-2 rounded-lg ${bg || color.replace('text-', 'bg-').replace('400', '400/10').replace('500', '500/10')}`}>
            <Icon className={`w-4 h-4 ${color}`} />
        </div>
    </div>
);

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

const LogAIDashboard = ({ setActiveTab, setEventFilter, setStatusFilter }) => {
    const [stats, setStats] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastRefresh, setLastRefresh] = useState('');
    const [patternSearch, setPatternSearch] = useState('');

    const fetchData = useCallback(async () => {
        const token = localStorage.getItem('auth_token');
        const headers = { 'Authorization': `Bearer ${token}` };

        try {
            const [statsRes, timelineRes] = await Promise.all([
                fetch(`${API_BASE_URL}/api/logai/stats`, { headers }),
                fetch(`${API_BASE_URL}/api/logai/anomaly-timeline`, { headers })
            ]);

            if (statsRes.ok) {
                const data = await statsRes.json();
                setStats(data);
            }
            if (timelineRes.ok) {
                const data = await timelineRes.json();
                // Format timeline labels
                const formatted = (data.timeline || []).map(t => ({
                    ...t,
                    label: t.time ? new Date(t.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : t.time
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

    return (
        <div className="space-y-6">
            {/* Header */}
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
                    <div className="px-3 py-1 bg-[#00d4ff]/10 border border-[#00d4ff]/20 rounded-full">
                        <span className="text-[10px] font-bold text-[#00d4ff] uppercase">Neural Engine Active</span>
                    </div>
                </div>
            </div>

            {/* Top Metrics Row (Ported from Performance Dashboard) */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <StatCard
                    label="Critical Alerts"
                    value={stats?.global_severity?.Critical}
                    color="text-red-500"
                    bg="bg-red-500/10"
                    icon={AlertTriangle}
                    onClick={() => { setEventFilter('Critical'); setActiveTab('events'); }}
                />
                <StatCard
                    label="Major Alerts"
                    value={stats?.global_severity?.High}
                    color="text-orange-500"
                    bg="bg-orange-500/10"
                    icon={AlertTriangle}
                    onClick={() => { setEventFilter('High'); setActiveTab('events'); }}
                />
                <StatCard
                    label="Minor Alerts"
                    value={stats?.global_severity?.Medium}
                    color="text-yellow-500"
                    bg="bg-yellow-500/10"
                    icon={AlertTriangle}
                    onClick={() => { setEventFilter('Medium'); setActiveTab('events'); }}
                />
                <StatCard
                    label="Unassigned"
                    value={stats?.status_counts?.Open}
                    color="text-blue-400"
                    bg="bg-blue-400/10"
                    icon={User}
                    onClick={() => { setStatusFilter('Open'); setActiveTab('events'); }}
                />
                <StatCard
                    label="Closed Cases"
                    value={stats?.status_counts?.Closed}
                    color="text-green-500"
                    bg="bg-green-500/10"
                    icon={Database}
                    onClick={() => { setStatusFilter('Closed'); setActiveTab('events'); }}
                />
                <StatCard
                    label="Remediated"
                    value={stats?.remediated || 0}
                    color="text-purple-500"
                    bg="bg-purple-500/10"
                    icon={Zap}
                    onClick={() => { setStatusFilter('Remediated'); setActiveTab('events'); }}
                />
            </div>

            {/* Middle Section: Funnel and Trend Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left: Funnel */}
                <div className="lg:col-span-4 bg-[#0a0e27] rounded-3xl overflow-hidden border border-[#1a1f3a] shadow-2xl h-[400px]">
                    <ThreatFunnel
                        events={stats?.total_lines || 0}
                        detections={stats?.total_alerts || 0}
                        alerts={stats?.anomaly_count || 0}
                    />
                </div>
                {/* Right: Trend Chart */}
                <div className="lg:col-span-8">
                    <TrendChart data={stats?.alert_trends} />
                </div>
            </div>

            {/* Intelligence Charts Section (Added) */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ThreatEntities data={stats?.top_ips} />
                <AttackPaths data={stats?.top_vectors} />
            </div>

            {/* Anomaly Timeline + Severity */}
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
                            No anomaly data yet — run the pre-processor to populate
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
                                    innerRadius={55}
                                    outerRadius={80}
                                    paddingAngle={4}
                                    dataKey="value"
                                    onClick={(data) => {
                                        if (data && data.name) {
                                            setEventFilter(data.name);
                                            setActiveTab('events');
                                        }
                                    }}
                                    className="cursor-pointer"
                                >
                                    {severityData.map((entry, i) => (
                                        <Cell
                                            key={i}
                                            fill={
                                                entry.name === 'Critical' ? '#ef4444' :
                                                    entry.name === 'High' ? '#f97316' :
                                                        entry.name === 'Medium' ? '#fbbf24' :
                                                            '#60c07c'
                                            }
                                        />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#0a0e27', borderColor: '#2d3748' }} itemStyle={{ color: '#fff' }} />
                                <Legend
                                    iconSize={8}
                                    layout="horizontal"
                                    verticalAlign="bottom"
                                    align="center"
                                    wrapperStyle={{ fontSize: '10px', paddingTop: '10px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[220px] flex items-center justify-center text-gray-600 italic text-sm">No data</div>
                    )}
                </div>
            </div>

            {/* Neural AI Insights + Recent Alerts Feed */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* AI Insights Summary */}
                <div className="lg:col-span-5 bg-[#0a0e27] rounded-3xl p-6 border border-[#1a1f3a] shadow-2xl overflow-hidden relative group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Zap className="w-16 h-16 text-[#00d4ff]" />
                    </div>
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2 relative z-10">
                        <Cpu className="w-4 h-4 text-[#00d4ff]" />
                        Neural AI Insights
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
                                <p className="text-sm text-gray-300 leading-relaxed font-medium">
                                    {insight}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Recent Critical Alerts Feed */}
                <div className="lg:col-span-7 bg-[#0a0e27] rounded-3xl border border-[#1a1f3a] shadow-2xl overflow-hidden">
                    <div className="bg-[#1a1f3a] px-6 py-4 border-b border-[#2d3748] flex items-center justify-between">
                        <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                            <Shield className="w-4 h-4 text-red-500" />
                            Recent Critical Threats
                        </h3>
                        <button
                            onClick={() => setActiveTab('events')}
                            className="text-[10px] font-bold text-[#00d4ff] uppercase tracking-wider hover:underline"
                        >
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
                                            <div className="font-bold text-white text-xs group-hover:text-red-400 transition-colors">
                                                {alert.description}
                                            </div>
                                            <div className="text-[10px] text-gray-600 mt-1 font-mono">
                                                SRC: {alert.srcip || 'Local'} • Agent: {alert.agent || 'SYSTEM'}
                                            </div>
                                        </td>
                                        <td className="px-5 py-4 text-right">
                                            <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${alert.severity === 'Critical' ? 'bg-red-500/10 text-red-500 border border-red-500/20' :
                                                'bg-orange-500/10 text-orange-500 border border-orange-500/20'
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
                                            No high-severity threats detected in the current neural stream.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LogAIDashboard;

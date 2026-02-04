import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip,
    ResponsiveContainer, Cell, PieChart, Pie, CartesianGrid, Legend
} from 'recharts';
import { motion } from 'framer-motion';
import { Shield, AlertCircle, Zap, Activity, Info, TrendingUp, Cpu, Database } from 'lucide-react';

const CveDashboard = ({ summary }) => {
    // Mock data for trends if summary is empty
    const trendData = [
        { name: 'Jan 26', nonAi: 110, aiIndirect: 5, aiDirect: 2 },
        { name: 'Jan 27', nonAi: 180, aiIndirect: 10, aiDirect: 5 },
        { name: 'Jan 28', nonAi: 210, aiIndirect: 15, aiDirect: 10 },
        { name: 'Jan 29', nonAi: 120, aiIndirect: 5, aiDirect: 2 },
        { name: 'Jan 30', nonAi: 130, aiIndirect: 8, aiDirect: 3 },
        { name: 'Jan 31', nonAi: 45, aiIndirect: 2, aiDirect: 1 },
        { name: 'Feb 01', nonAi: 35, aiIndirect: 1, aiDirect: 1 },
    ];

    const weeklyData = [
        { name: 'Sun', nonAi: 40, ai: 2 },
        { name: 'Mon', nonAi: 160, ai: 5 },
        { name: 'Tue', nonAi: 190, ai: 10 },
        { name: 'Wed', nonAi: 220, ai: 15 },
        { name: 'Thu', nonAi: 120, ai: 5 },
        { name: 'Fri', nonAi: 130, ai: 8 },
        { name: 'Sat', nonAi: 45, ai: 2 },
    ];

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Header (Image 3 style) */}
            <div className="flex justify-between items-center bg-[#0a0e27]/40 p-6 rounded-3xl border border-[#1a1f3a]">
                <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Intelligence Dashboard</h2>
                    <p className="text-xs text-gray-500 font-bold uppercase mt-1">Comprehensive vulnerability trends and AI-related threat insights</p>
                </div>
                <div className="flex gap-3">
                    <div className="bg-[#1a1f3a] px-4 py-2 rounded-xl border border-[#2d3748] text-xs font-bold text-gray-400">Last 7 Days</div>
                    <button className="bg-white/5 hover:bg-white/10 px-4 py-2 rounded-xl border border-[#2d3748] text-xs font-bold text-white transition-all flex items-center gap-2">
                        <Database className="w-3.5 h-3.5" /> Export
                    </button>
                </div>
            </div>

            {/* Executive Summary (Image 3) */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <SummaryCard label="Total Vulnerabilities" value={summary?.total_cves || 905} sub="113.1/day avg" trend="38% vs previous" color="gray" />
                <SummaryCard label="AI-Related" value={summary?.ai_related_cves || 34} sub="4% of total" trend="6% vs previous" color="blue" />
                <SummaryCard label="Critical AI" value={summary?.critical_ai_cves || 3} sub="9% of AI CVEs" trend="Stable" color="red" />
                <SummaryCard label="High AI" value={summary?.high_ai_cves || 10} sub="29% of AI CVEs" trend="Decreasing" color="orange" />
                <SummaryCard label="Daily Average" value={summary?.daily_average || 113.1} sub="CVEs per day" trend="Stable" color="gray" />
            </div>

            {/* Main Content (Image 4) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* CVE Trends Chart */}
                <div className="lg:col-span-2 bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a] shadow-2xl">
                    <h3 className="text-sm font-bold text-white mb-6 uppercase tracking-widest">CVE Trends Over Time</h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1a1f3a" vertical={false} opacity={0.3} />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#4a5568' }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#4a5568' }} />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: '#1a1f3a', border: '1px solid #2d3748', borderRadius: '12px' }}
                                    itemStyle={{ fontSize: '11px', fontWeight: 'bold' }}
                                />
                                <Bar dataKey="nonAi" stackId="a" fill="#3b82f6" radius={[0, 0, 0, 0]} />
                                <Bar dataKey="aiIndirect" stackId="a" fill="#f97316" radius={[0, 0, 0, 0]} />
                                <Bar dataKey="aiDirect" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex justify-center gap-6 mt-4 text-[10px] font-bold uppercase text-gray-500">
                        <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#3b82f6]"></span> Non-AI</div>
                        <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#f97316]"></span> AI Indirect</div>
                        <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#ef4444]"></span> AI Direct</div>
                    </div>
                </div>

                {/* AI vs Non-AI Donut */}
                <div className="bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a] shadow-2xl flex flex-col items-center">
                    <h3 className="text-sm font-bold text-white mb-8 self-start uppercase tracking-widest">AI vs Non-AI Distribution</h3>
                    <div className="h-[240px] w-full relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={[
                                        { name: 'AI Related', value: 4, fill: '#3b82f6' },
                                        { name: 'Other', value: 96, fill: '#1a1f3a' }
                                    ]}
                                    cx="50%" cy="50%" innerRadius={70} outerRadius={90} dataKey="value" stroke="none"
                                >
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                            <div className="text-3xl font-bold text-white">4%</div>
                            <div className="text-[10px] text-gray-500 font-bold uppercase">AI-Related</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Severity Distribution & Highlights (Image 4 & 5) */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a]">
                    <h3 className="text-sm font-bold text-white mb-6 uppercase tracking-widest">Severity Distribution</h3>
                    <div className="space-y-5">
                        <SeverityLine label="Critical" count={3} pct={9} color="#ef4444" />
                        <SeverityLine label="High" count={10} pct={29} color="#f97316" />
                        <SeverityLine label="Medium" count={13} pct={38} color="#3b82f6" />
                        <SeverityLine label="Low" count={1} pct={3} color="#06b6d4" />
                        <SeverityLine label="Unscored" count={7} pct={21} color="#4a5568" />
                    </div>
                </div>

                <div className="bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a]">
                    <h3 className="text-sm font-bold text-white mb-6 uppercase tracking-widest">Timeline Highlights</h3>
                    <div className="space-y-4">
                        <HighlightItem date="Jan 28" count={220} AI={19} critical={13} />
                        <HighlightItem date="Jan 27" count={189} AI={6} critical={43} />
                    </div>
                </div>
            </div>
        </div>
    );
};

const SummaryCard = ({ label, value, sub, trend, color }) => {
    const colorClasses = {
        red: 'border-red-500/30',
        blue: 'border-blue-500/30',
        orange: 'border-orange-500/30',
        gray: 'border-[#1a1f3a]'
    };
    return (
        <div className={`bg-[#0a0e27] p-5 rounded-2xl border ${colorClasses[color]} shadow-xl group hover:border-[#00d4ff]/40 transition-all duration-500`}>
            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3">{label}</p>
            <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white">{value}</span>
            </div>
            <p className={`text-[10px] font-bold mt-1 ${color === 'red' ? 'text-red-500' : 'text-gray-400'}`}>{sub}</p>
            <div className="mt-4 pt-4 border-t border-[#1a1f3a] text-[9px] font-bold text-gray-500 flex items-center gap-2">
                <TrendingUp className="w-3 h-3 text-[#00d4ff]" /> {trend}
            </div>
        </div>
    );
};

const SeverityLine = ({ label, count, pct, color }) => (
    <div className="space-y-1.5">
        <div className="flex justify-between text-[11px] font-bold uppercase tracking-tighter">
            <div className="flex items-center gap-2 text-gray-400"><AlertCircle className="w-3 h-3" style={{ color }} /> {label}</div>
            <div className="text-white">{count} ({pct}%)</div>
        </div>
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                className="h-full rounded-full"
                style={{ backgroundColor: color }}
            />
        </div>
    </div>
);

const HighlightItem = ({ date, count, AI, critical }) => (
    <div className="p-4 bg-white/5 rounded-2xl border border-white/5 hover:border-[#00d4ff]/20 transition-all">
        <div className="flex justify-between items-center mb-2">
            <div className="flex items-baseline gap-4">
                <span className="text-xl font-bold text-white">{count} <span className="text-[10px] text-gray-500 font-bold uppercase">CVEs</span></span>
                <span className="text-xs font-bold text-[#00d4ff] uppercase">{date}</span>
            </div>
            <span className="text-[8px] font-bold bg-[#1a1f3a] px-2 py-1 rounded text-gray-500 uppercase">2x average</span>
        </div>
        <p className="text-[10px] text-gray-400 font-bold uppercase">{AI} AI-related • {critical} Critical</p>
    </div>
);

export default CveDashboard;

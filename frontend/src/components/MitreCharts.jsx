import React, { useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip,
    ResponsiveContainer, Cell, Radar, RadarChart, PolarGrid,
    PolarAngleAxis, PolarRadiusAxis, Legend, AreaChart, Area, CartesianGrid
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, Activity, Zap, AlertCircle, Info } from 'lucide-react';

const COLORS = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#06b6d4',
    killChain: ['#1e3a8a', '#1e40af', '#1d4ed8', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd']
};

const STABLE_EVOLUTION = [
    { time: '2/2/2026, 4:00:00 AM', count: 15, threat: 10 },
    { time: '2/2/2026, 8:00:00 AM', count: 18, threat: 15 },
    { time: '2/2/2026, 11:00:00 AM', count: 35, threat: 25 },
    { time: '2/2/2026, 12:00:00 PM', count: 60, threat: 40 },
    { time: '2/2/2026, 1:00:00 PM', count: 48, threat: 35 },
    { time: '2/2/2026, 2:00:00 PM', count: 25, threat: 20 },
    { time: '2/2/2026, 3:00:00 PM', count: 55, threat: 38 },
];

const MOCK_KILL_CHAIN = [
    { name: "Reconnaissance", value: 85, detail: "Active scanning detected from 14 nodes." },
    { name: "Weaponization", value: 45, detail: "3 new malware payloads identified." },
    { name: "Delivery", value: 65, detail: "Phishing campaigns targeting HR." },
    { name: "Exploitation", value: 95, detail: "Zero-day attempt on web server." },
    { name: "Installation", value: 35, detail: "Persistence mechanisms blocked." },
    { name: "Command & Control", value: 75, detail: "High-entropy traffic to known C2." },
    { name: "Actions on Objectives", value: 55, detail: "Data staging attempt prevented." }
];

const MOCK_CVE = [
    { subject: 'Dark Web Scan', A: 45, B: 200, fullMark: 200, info: "Monitoring for leaked credentials." },
    { subject: 'CVE Based Vulnerability', A: 170, B: 200, fullMark: 200, info: "Known exploits detected in environment." },
    { subject: 'App Misconfig', A: 110, B: 200, fullMark: 200, info: "Unsecured application headers and settings." },
    { subject: 'SSL Misconfig', A: 35, B: 200, fullMark: 200, info: "Expired or weak SSL/TLS certificates." },
    { subject: 'Malicious Assets', A: 125, B: 200, fullMark: 200, info: "Potential malware artifacts identified." },
    { subject: 'Internal Posture', A: 90, B: 200, fullMark: 200, info: "Internal network security visibility score." },
    { subject: 'DNS Masquerade', A: 20, B: 200, fullMark: 200, info: "Suspicious DNS activity and domain spoof spoofing." },
];

export const TrendChart = ({ data = STABLE_EVOLUTION }) => {
    const [hoveredPoint, setHoveredPoint] = useState(null);

    const CustomTooltip = ({ active, payload, coordinate }) => {
        if (active && payload && payload.length) {
            const alertCount = payload[0].value;
            const yPosition = payload[0].payload.count;

            return (
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-[#00d4ff] text-black px-4 py-2 rounded-md shadow-xl font-bold text-xs uppercase tracking-wide"
                >
                    Alert Count: {alertCount}
                </motion.div>
            );
        }
        return null;
    };

    const CustomCursor = (props) => {
        const { points, height, width } = props;
        if (points && points.length > 0) {
            const { x, y } = points[0];
            return (
                <line
                    x1={x}
                    y1={0}
                    x2={x}
                    y2={height}
                    stroke="#ffffff"
                    strokeWidth={1}
                    strokeDasharray="5 5"
                    opacity={0.5}
                />
            );
        }
        return null;
    };

    return (
        <div className="bg-[#0a0e27] p-5 rounded-3xl border border-[#1a1f3a] shadow-2xl h-full relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                <Activity className="w-20 h-20 text-[#00d4ff]" />
            </div>
            <div className="flex items-center justify-between mb-4 relative z-10">
                <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                        <Activity className="w-5 h-5 text-[#00d4ff]" />
                        Alerts Trends
                    </h3>
                </div>
            </div>
            <div className="h-[230px]">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                        data={data}
                        onMouseMove={(state) => {
                            if (state && state.activePayload) {
                                setHoveredPoint(state.activePayload[0].payload);
                            }
                        }}
                        onMouseLeave={() => setHoveredPoint(null)}
                    >
                        <defs>
                            <linearGradient id="colorTrend" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.5} />
                                <stop offset="95%" stopColor="#00d4ff" stopOpacity={0.05} />
                            </linearGradient>
                        </defs>

                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#2d3748"
                            vertical={false}
                            opacity={0.3}
                        />

                        <XAxis
                            dataKey="time"
                            stroke="#6b7280"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 9, fontWeight: '600', fill: '#6b7280' }}
                            tickFormatter={(value) => {
                                try {
                                    const date = new Date(value);
                                    return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}, ${date.getHours() % 12 || 12}:${String(date.getMinutes()).padStart(2, '0')} ${date.getHours() >= 12 ? 'PM' : 'AM'}`;
                                } catch {
                                    return value;
                                }
                            }}
                        />

                        <YAxis
                            stroke="#6b7280"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 9, fontWeight: '600', fill: '#6b7280' }}
                            label={{
                                value: 'Alert Count',
                                angle: -90,
                                position: 'insideLeft',
                                style: { fontSize: 10, fill: '#6b7280', fontWeight: '600' }
                            }}
                        />

                        <RechartsTooltip
                            content={<CustomTooltip />}
                            cursor={<CustomCursor />}
                        />

                        <Area
                            type="natural"
                            dataKey="count"
                            stroke="#00d4ff"
                            strokeWidth={3}
                            fillOpacity={1}
                            fill="url(#colorTrend)"
                            animationDuration={1500}
                            dot={false}
                            activeDot={{
                                r: 8,
                                fill: '#00d4ff',
                                stroke: '#ffffff',
                                strokeWidth: 3
                            }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
            {hoveredPoint && (
                <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute bottom-4 left-4 bg-black/80 border border-[#00d4ff]/50 rounded-lg px-3 py-2 text-xs font-bold"
                >
                    <div className="text-white">{hoveredPoint.time}</div>
                </motion.div>
            )}
        </div>
    );
};

export const KillChainChart = ({ data, onPhaseClick }) => {
    const [selected, setSelected] = useState(null);

    // Sort data to follow the kill chain order
    const phasesOrder = [
        'Reconnaissance', 'Weaponization', 'Delivery', 'Exploitation',
        'Installation', 'Command & Control', 'Actions on Objectives'
    ];

    const sortedData = [...(data || [])].sort((a, b) =>
        phasesOrder.indexOf(a.name) - phasesOrder.indexOf(b.name)
    );

    const handleBarClick = (payload) => {
        if (payload) {
            setSelected(payload);
            if (onPhaseClick) {
                onPhaseClick(payload.name);
            }
        }
    };

    return (
        <div className="bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a] shadow-2xl relative h-full">
            <h3 className="text-xs font-bold text-white uppercase tracking-[0.4em] mb-8 flex items-center gap-2 border-b border-[#1a1f3a] pb-4">
                <Target className="w-5 h-5 text-blue-500" /> Kill Chain Phase Distribution
            </h3>
            <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={sortedData}
                        layout="vertical"
                        onClick={(d) => d && d.activePayload && handleBarClick(d.activePayload[0].payload)}
                    >
                        <XAxis type="number" hide />
                        <YAxis
                            dataKey="name"
                            type="category"
                            stroke="#4a5568"
                            width={140}
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 10, fontWeight: '800', fill: '#94a3b8' }}
                        />
                        <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={18} className="cursor-pointer">
                            {sortedData.map((e, i) => (
                                <Cell key={i} fill={COLORS.killChain[i % COLORS.killChain.length]} />
                            ))}
                        </Bar>
                        <RechartsTooltip
                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    return (
                                        <div className="bg-[#1a1f3a] border border-[#2d3748] p-3 rounded-lg shadow-2xl">
                                            <p className="text-white font-bold text-xs uppercase tracking-wider">{payload[0].payload.name}</p>
                                            <p className="text-[#00d4ff] text-xl font-bold mt-1">{payload[0].value}</p>
                                            <p className="text-gray-400 text-[10px] mt-2 italic">Click to filter events</p>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
            <AnimatePresence>
                {selected && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl"
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Neural Summary • {selected.name}</span>
                            <button onClick={() => setSelected(null)} className="text-gray-500 hover:text-white text-xs">×</button>
                        </div>
                        <p className="text-sm text-gray-300 leading-relaxed italic">"{selected.detail || 'Monitoring active indicators in this phase.'}"</p>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export const CveRadar = ({ data = MOCK_CVE }) => {
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const item = payload[0].payload;
            return (
                <div className="flex flex-col items-start gap-1.5 pointer-events-none z-50 -ml-4">
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="relative bg-black text-white px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest shadow-2xl border border-white/10 flex items-center gap-2"
                    >
                        <div className="absolute left-[-4px] top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-r-[4px] border-r-black"></div>
                        {item.subject}
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="relative bg-[#3b82f6] text-white px-3 py-1 rounded-md text-[9px] font-bold uppercase shadow-lg flex items-center justify-between gap-4 min-w-[150px]"
                    >
                        <div className="absolute left-[-4px] top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-r-[4px] border-r-[#3b82f6]"></div>
                        <span>Max Score:</span>
                        <span className="text-xs">{item.B}</span>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="relative bg-[#ef4444] text-white px-3 py-1 rounded-md text-[9px] font-bold uppercase shadow-lg flex items-center justify-between gap-4 min-w-[150px]"
                    >
                        <div className="absolute left-[-4px] top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-r-[4px] border-r-[#ef4444]"></div>
                        <span>Obtained Score:</span>
                        <span className="text-xs">{item.A}</span>
                    </motion.div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a] shadow-2xl relative h-full group">
            <h3 className="text-xs font-bold text-white uppercase tracking-[0.4em] mb-8 flex items-center gap-2 border-b border-[#1a1f3a] pb-4">
                <AlertCircle className="w-5 h-5 text-purple-500" /> Vulnerability Intelligence (CVE)
            </h3>
            <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                        <PolarGrid stroke="#1a1f3a" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#4a5568', fontSize: 11, fontWeight: '700' }} />
                        <RechartsTooltip content={<CustomTooltip />} cursor={false} />
                        <Radar
                            name="Actual"
                            dataKey="A"
                            stroke="#8b5cf6"
                            fill="#8b5cf6"
                            fillOpacity={0.6}
                            dot={{ r: 4, fill: '#8b5cf6' }}
                            isAnimationActive={true}
                            animationDuration={1500}
                        />
                        <Radar
                            name="Baseline"
                            dataKey="B"
                            stroke="#00d4ff"
                            fill="#00d4ff"
                            fillOpacity={0.1}
                            isAnimationActive={true}
                            animationDuration={1500}
                        />
                    </RadarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export const ThreatEntities = () => (
    <div className="bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a] shadow-2xl">
        <h3 className="text-[11px] font-bold text-white mb-8 uppercase tracking-[0.5em] opacity-60 border-b border-[#1a1f3a] pb-4">Top Threat Actors / Targeted Entities</h3>
        <div className="flex flex-wrap gap-x-10 gap-y-6 items-center justify-center py-6">
            {["192.168.79.13", "10.20.10.78", "192.168.79.14", "DC-PROD", "10.0.0.15"].map((host, i) => (
                <motion.span key={host} whileHover={{ scale: 1.1, color: '#00d4ff' }} className={`font-mono font-bold cursor-pointer ${i === 0 ? 'text-4xl text-white' : 'text-xl text-gray-400'}`}>{host}</motion.span>
            ))}
        </div>
    </div>
);

export const AttackPaths = () => (
    <div className="bg-[#0a0e27] p-8 rounded-3xl border border-[#1a1f3a] shadow-2xl">
        <h3 className="text-[11px] font-bold text-white mb-8 uppercase tracking-[0.5em] opacity-60 border-b border-[#1a1f3a] pb-4">Primary Attack Path Vectors</h3>
        <div className="flex flex-wrap gap-x-6 gap-y-4 items-center justify-center py-6">
            {["Potential Malware", "C2 Activity", "Brute Force", "SQL Injection"].map((v, i) => (
                <motion.span key={v} whileHover={{ scale: 1.2, color: i === 0 ? '#ef4444' : '#00d4ff' }} className={`text-2xl font-bold opacity-40 cursor-pointer hover:opacity-100 flex items-center gap-2 ${i === 0 ? 'text-red-500' : 'text-blue-400'}`}>{v} {i < 2 && <Zap className="w-4 h-4 fill-current" />}</motion.span>
            ))}
        </div>
    </div>
);

export const MitreCharts = (props) => (
    <div className="space-y-6">
        <TrendChart {...props} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <KillChainChart {...props} />
            <CveRadar {...props} />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ThreatEntities />
            <AttackPaths />
        </div>
    </div>
);

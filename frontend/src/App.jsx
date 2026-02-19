import React, { useState, useEffect, useMemo } from 'react';
import {
    Shield, AlertTriangle, Activity, Database, TrendingUp,
    RefreshCw, Send, Bot, ExternalLink, Zap, Layout,
    Table, Cpu, Globe, Filter, List, User, Clock, Terminal,
    Menu, X, ChevronDown, ChevronRight, BarChart2, Eye, Search, Settings,
    BarChart3, Lightbulb, ShieldAlert
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    PieChart, Pie, ResponsiveContainer, Tooltip as RechartsTooltip, Legend, Cell,
    BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { ReportViewer } from './components/ReportViewer';
import { MitreAssistant, IpInvestigation } from './components/InvestigationTools';
import { TrendChart, KillChainChart, CveRadar, ThreatEntities, AttackPaths } from './components/MitreCharts';
import { MitreEvents } from './components/MitreEvents';
import ThreatFunnel from './components/ThreatFunnel';
import Login from './components/Login';
import Copilot from './components/Copilot';
import LogAIDashboard from './components/LogAIDashboard';
import { API_BASE_URL } from './config';

// Final Unified Hybrid Mode Implementation
const API_MODE_FALLBACK = import.meta.env.VITE_SECUREZEN_MODE || 'standalone';


const CustomPieTooltip = ({ active, payload, total }) => {
    if (active && payload && payload.length) {
        const item = payload[0].payload;
        const value = item.value;
        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;

        const dynamicColor = item.fill || item.color || '#d946ef';

        return (
            <div className="text-white px-3 py-2 rounded-lg text-xs font-bold shadow-xl"
                style={{ backgroundColor: '#0a0e27', borderColor: dynamicColor, borderWidth: '1px' }}>
                <span>{item.name}: </span>
                <span className="ml-1" style={{ color: dynamicColor }}>{percentage}%</span>
                <span className="text-gray-300 ml-1">({value})</span>
            </div>
        );
    }
    return null;
};

const AISOCDashboard = () => {
    // Authentication State
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);
    const [authLoading, setAuthLoading] = useState(true);

    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState({
        critical: 0, major: 0, minor: 0, unassigned: 0, closed: 0, remediated: 0,
        totalEvents: '0', threatScenarios: '0', openAlerts: 0,
        top_mitre: [], top_ips: []
    });
    const [activeTab, setActiveTab] = useState('securezen_analysis');
    const [eventFilter, setEventFilter] = useState('All');
    const [statusFilter, setStatusFilter] = useState('All'); // Added status state
    const [loading, setLoading] = useState(true);

    // ... (lines 60-315)

    const navigateToEvents = (severity, status = 'All') => {
        setSearchTerm('');
        setEventFilter(severity);
        setStatusFilter(status);
        setActiveTab('events');
    };
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [alertTypes, setAlertTypes] = useState([]);
    const [cveSummary, setCveSummary] = useState(null);
    const [radarData, setRadarData] = useState([]);
    const [alertTrends, setAlertTrends] = useState([]);
    const [logPatterns, setLogPatterns] = useState([]);
    const [clusters, setClusters] = useState([]);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [expandedCategories, setExpandedCategories] = useState({
        analytics: true,
        insights: true,
        threats: true
    });
    const [isSidebarHovered, setIsSidebarHovered] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [simulationMode, setSimulationMode] = useState(false);
    const [lastRefresh, setLastRefresh] = useState(new Date().toLocaleTimeString());
    const [dashboardMode, setDashboardMode] = useState(API_MODE_FALLBACK);
    const [configLoaded, setConfigLoaded] = useState(false);




    // Configuration and Mode Detection
    const fetchConfig = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/config`);
            if (res.ok) {
                const data = await res.json();
                setDashboardMode(data.mode || 'overlay');
            }
        } catch (error) {
            console.error('Config fetch failed, using fallback:', error);
        } finally {
            setConfigLoaded(true);
        }
    };

    // Authentication Functions
    const verifyAuth = async () => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            setAuthLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setCurrentUser(data.user);
                setIsAuthenticated(true);
            } else {
                // Token invalid, clear it
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user');
            }
        } catch (error) {
            console.error('Auth verification failed:', error);
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
        } finally {
            setAuthLoading(false);
        }
    };

    const handleLoginSuccess = (user) => {
        setCurrentUser(user);
        setIsAuthenticated(true);
        setAuthLoading(false);
    };

    const handleLogout = () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setCurrentUser(null);
        setIsAuthenticated(false);
    };

    const analyzeIOC = async (ioc) => {
        setActiveTab('intelligence');
        setAnalysis({ status: 'running', analysis: `Agent swarm initialized for ${ioc}...` });

        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(`${API_BASE_URL}/api/analyze-ioc`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ ioc })
            });
            const data = await response.json();
            setAnalysis({ status: 'done', analysis: data.analysis });
        } catch (error) {
            setAnalysis({ status: 'error', analysis: `Neural link failure: ${error.message}` });
        }
    };

    useEffect(() => {
        const init = async () => {
            await fetchConfig();
            await verifyAuth();
        };
        init();
    }, []);

    useEffect(() => {
        if (isAuthenticated && configLoaded) {
            fetchDashboardData();
            const interval = setInterval(fetchDashboardData, 5000); // Poll every 5 seconds for live updates
            return () => clearInterval(interval);
        }
    }, [isAuthenticated, configLoaded]);

    const getKillChainPhase = (alert) => {
        const tactic = (alert.mitreTactic || alert.rule_mitre_tactic || '').toLowerCase();
        const msg = (alert.message || alert.rule_description || '').toLowerCase();
        const type = (alert.type || alert.rule_description || '').toLowerCase();

        // 1. MITRE Tactic Mapping (High Priority)
        if (tactic.includes('reconnaissance')) return 'Reconnaissance';
        if (tactic.includes('resource development')) return 'Weaponization';
        if (tactic.includes('initial access')) return 'Delivery';
        if (tactic.includes('execution') || tactic.includes('persistence') || tactic.includes('privilege escalation')) return 'Exploitation';
        if (tactic.includes('defense evasion') || tactic.includes('credential access')) return 'Installation';
        if (tactic.includes('command and control')) return 'Command & Control';
        if (tactic.includes('exfiltration') || tactic.includes('impact')) return 'Actions on Objectives';

        // 2. Keyword Fallback (Medium Priority)
        if (msg.includes('scan') || msg.includes('recon') || type.includes('scan') || msg.includes('integrity check')) return 'Reconnaissance';
        if (msg.includes('malware') || msg.includes('payload') || msg.includes('exploit') || msg.includes('virus')) return 'Weaponization';
        if (msg.includes('phish') || msg.includes('delivery') || msg.includes('attachment') || msg.includes('blocked url')) return 'Delivery';
        if (msg.includes('brute force') || msg.includes('login') || msg.includes('exploit') || msg.includes('failure')) return 'Exploitation';
        if (msg.includes('backdoor') || msg.includes('persistence') || msg.includes('registry')) return 'Installation';
        if (msg.includes('c2') || msg.includes('beacon') || msg.includes('connection')) return 'Command & Control';
        if (msg.includes('exfil') || msg.includes('theft') || msg.includes('ransom') || msg.includes('impact')) return 'Actions on Objectives';

        // 3. Default based on severity
        if (alert.severity === 'Critical') return 'Actions on Objectives';
        if (alert.severity === 'High' || alert.severity === 'Major') return 'Exploitation';
        return 'Reconnaissance';
    };

    const killChainData = useMemo(() => {
        const phases = [
            'Reconnaissance', 'Weaponization', 'Delivery', 'Exploitation',
            'Installation', 'Command & Control', 'Actions on Objectives'
        ];

        const phaseMap = phases.reduce((acc, phase) => {
            acc[phase] = { name: phase, value: 0, detail: '' };
            return acc;
        }, {});

        alerts.forEach(alert => {
            const phase = getKillChainPhase(alert);
            if (phaseMap[phase]) {
                phaseMap[phase].value += 1;
                // Keep the most recent alert message as the "detail" for that phase
                if (!phaseMap[phase].detail || new Date(alert.time) > new Date()) {
                    phaseMap[phase].detail = alert.message;
                }
            }
        });

        // Ensure we don't have zeros for the mock-up look if data is sparse, 
        // but for "real" dynamic we should show 0 if there are none.
        // For this demo, let's just return the counts.
        return Object.values(phaseMap);
    }, [alerts]);

    const fetchDashboardData = async () => {
        setIsRefreshing(true);
        try {
            const token = localStorage.getItem('auth_token');
            const res = await fetch(`${API_BASE_URL}/api/dashboard-stats`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await res.json();

            if (data.alerts) {
                const formattedAlerts = data.alerts.map(a => ({
                    ...a,
                    time: new Date(a.timestamp).toLocaleString(),
                    alertId: a.alert_id,
                    type: a.rule_description,
                    severity: a.severity,
                    message: a.message,
                    entity: a.agent_name || a.src_ip || a.srcip,
                    srcIp: a.src_ip || a.srcip,
                    mitreId: a.rule_mitre_id,
                    mitreTactic: a.rule_mitre_tactic
                }));
                setAlerts(formattedAlerts);
            }

            if (data.stats) {
                const formatNum = (num) => {
                    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
                    if (num >= 1000) return (num / 1000).toFixed(2) + 'K';
                    return (num || 0).toString();
                };
                setStats(prev => ({
                    ...prev,
                    critical: data.stats.severity_counts?.Critical || 0,
                    major: data.stats.severity_counts?.High || 0,
                    minor: (data.stats.severity_counts?.Medium || 0) + (data.stats.severity_counts?.Low || 0),
                    unassigned: data.stats.unassigned || 0,
                    closed: data.stats.closed || 0,
                    totalEvents: formatNum(data.stats.total_events || 0),
                    threatScenarios: formatNum(data.stats.threat_scenarios || 0),
                    openAlerts: (data.stats.severity_counts?.Critical || 0) + (data.stats.severity_counts?.High || 0)
                }));
            }

            if (data.alert_type_distribution) {
                setAlertTypes(data.alert_type_distribution);
            }

            if (data.cve_summary) {
                setCveSummary(data.cve_summary);
            }

            if (data.radar_stats) {
                setRadarData(data.radar_stats);
            }

            if (data.alert_trends) {
                setAlertTrends(data.alert_trends);
            }

            if (data.log_patterns) {
                setLogPatterns(data.log_patterns);
            }

            if (data.clusters) {
                setClusters(data.clusters);
            }

            setLoading(false);
        } catch (error) {
            console.error('Error fetching data:', error);
            setLoading(false);
        } finally {
            setTimeout(() => setIsRefreshing(false), 800);
        }
    };



    // 1. First check if we are still verifying the session
    if (authLoading) {
        return (
            <div className="min-h-screen bg-[#060914] flex flex-col items-center justify-center">
                <Shield className="w-16 h-16 text-[#00d4ff] animate-pulse mb-4" />
                <div className="text-[#00d4ff] font-bold uppercase tracking-[0.5em] animate-pulse">Verifying Neural Link</div>
            </div>
        );
    }

    // 2. If not authenticated, show Login immediately
    if (!isAuthenticated) {
        return <Login onLoginSuccess={handleLoginSuccess} />;
    }

    // 3. If authenticated but still loading dashboard data
    if (loading) {
        return (
            <div className="min-h-screen bg-[#060914] flex flex-col items-center justify-center">
                <Shield className="w-16 h-16 text-[#00d4ff] animate-pulse mb-4" />
                <div className="text-[#00d4ff] font-bold uppercase tracking-[0.5em] animate-pulse">Initializing Neural SOC</div>
            </div>
        );
    }

    const toggleCategory = (cat) => {
        setExpandedCategories(prev => ({ ...prev, [cat]: !prev[cat] }));
    };

    const navItems = {
        analytics: [
            { id: 'securezen_analysis', label: 'Main Dashboard', icon: Cpu },
            { id: 'events', label: 'Alert Dashboard', icon: Shield },
        ],
        insights: [
            { id: 'framework', label: 'MITRE Assistant', icon: Bot },
        ],
        threats: [
            { id: 'intelligence', label: 'IP Intelligence', icon: Globe },
            { id: 'standalone_intel', label: 'Syslog Intelligence', icon: Search },
        ]
    };

    const handleNavClick = (tabId) => {
        if (tabId === 'events') {
            setEventFilter('All');
        }
        setActiveTab(tabId);
    };

    return (
        <div className="min-h-screen bg-[#060914] text-gray-300 font-sans selection:bg-[#00d4ff]/30 flex flex-col">
            {/* Top Header */}
            <header className="h-[60px] bg-[#0a0e27] border-b border-[#1a1f3a] px-6 flex items-center justify-between shadow-2xl shrink-0 z-50">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="p-2 hover:bg-white/5 rounded-lg transition-colors lg:hidden"
                    >
                        {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                    </button>
                    <div className="flex items-center gap-2 group cursor-pointer" onClick={() => setActiveTab('dashboard')}>
                        <Shield className="w-8 h-8 text-[#00d4ff] fill-[#00d4ff]/10 group-hover:rotate-12 transition-transform" />
                        <span className="text-xl font-bold text-white tracking-tighter whitespace-nowrap">SecureZen</span>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className="hidden sm:flex items-center gap-4 bg-[#1a1f3a]/50 rounded-full px-4 py-1.5 border border-[#1a1f3a]">
                        {simulationMode ? (
                            <div className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-[#f97316] rounded-full animate-pulse shadow-[0_0_8px_rgba(249,115,22,0.5)]"></div>
                                <div className="flex flex-col">
                                    <span className="text-[9px] font-bold text-[#f97316] uppercase tracking-wider leading-none">AI Simulation Active</span>
                                    <span className="text-[7px] text-gray-500 uppercase tracking-widest mt-0.5">Last Pulse: {lastRefresh}</span>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="flex flex-col items-end">
                                    <span className="text-[10px] font-bold text-[#00d4ff] uppercase tracking-wider leading-none">Status</span>
                                    <span className="text-[9px] text-green-400 font-bold uppercase">Neural Link Active</span>
                                </div>
                                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.5)]"></div>
                            </>
                        )}
                    </div>

                    <div className="flex items-center gap-2 bg-[#1a1f3a] rounded-full px-3 py-1 border border-[#2d3748] relative group/user cursor-pointer">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-[#00d4ff] to-blue-600 flex items-center justify-center text-[10px] font-bold text-white uppercase">
                            {currentUser?.full_name?.charAt(0) || 'U'}
                        </div>
                        <span className="text-[10px] font-bold text-white uppercase tracking-tighter">{currentUser?.full_name || 'User'}</span>
                        <div className="absolute top-full right-0 mt-2 w-40 bg-[#0a0e27] border border-[#1a1f3a] rounded-xl py-2 shadow-2xl opacity-0 invisible group-hover/user:opacity-100 group-hover/user:visible transition-all">
                            <button onClick={handleLogout} className="w-full text-left px-4 py-2 text-xs text-red-400 hover:bg-white/5 flex items-center gap-2">
                                <Terminal className="w-3 h-3" /> Logout
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden h-[calc(100vh-60px)]">
                {/* Sidebar */}
                <aside
                    onMouseEnter={() => setIsSidebarHovered(true)}
                    onMouseLeave={() => setIsSidebarHovered(false)}
                    className={`
                        ${isSidebarOpen ? (isSidebarHovered ? 'w-64' : 'w-20') : 'w-0 -translate-x-full'} 
                        lg:translate-x-0 
                        bg-[#0a0e27] border-r border-[#1a1f3a] flex flex-col transition-all duration-300 z-40 relative group
                    `}
                >
                    <div className="p-4 flex flex-col gap-6 overflow-y-auto no-scrollbar overflow-x-hidden">
                        {/* Analytics Category */}
                        <div>
                            <button
                                onClick={() => toggleCategory('analytics')}
                                className={`w-full flex items-center ${isSidebarHovered ? 'justify-between px-2' : 'justify-center'} text-[11px] font-bold text-gray-500 uppercase tracking-widest mb-2 hover:text-gray-300 transition-all`}
                            >
                                <div className="flex items-center gap-3">
                                    <BarChart3 className="w-5 h-5 text-blue-400 shrink-0" />
                                    <span className={`${isSidebarHovered ? 'opacity-100 flex-1' : 'opacity-0 w-0 h-0 hidden'} transition-all duration-300 whitespace-nowrap overflow-hidden`}>Analytics</span>
                                </div>
                                {isSidebarHovered && (expandedCategories.analytics ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />)}
                            </button>
                            <AnimatePresence>
                                {isSidebarHovered && expandedCategories.analytics && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="flex flex-col gap-1 overflow-hidden"
                                    >
                                        {navItems.analytics.map((item) => (
                                            <button
                                                key={item.id}
                                                onClick={() => handleNavClick(item.id)}
                                                className={`
                                                    flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all
                                                    ${activeTab === item.id
                                                        ? 'bg-[#00d4ff]/10 text-white border border-[#00d4ff]/20 shadow-[0_0_15px_rgba(0,212,255,0.05)]'
                                                        : 'text-gray-400 hover:bg-white/5 hover:text-white border border-transparent'}
                                                `}
                                            >
                                                <item.icon className={`w-4 h-4 shrink-0 ${activeTab === item.id ? 'text-[#00d4ff]' : 'text-gray-500'}`} />
                                                <span className={`text-xs font-semibold tracking-tight whitespace-nowrap transition-all duration-300 ${isSidebarHovered ? 'opacity-100' : 'opacity-0 w-0 h-0 hidden'}`}>{item.label}</span>
                                            </button>
                                        ))}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Insights Category */}
                        <div>
                            <button
                                onClick={() => toggleCategory('insights')}
                                className={`w-full flex items-center ${isSidebarHovered ? 'justify-between px-2' : 'justify-center'} text-[11px] font-bold text-gray-500 uppercase tracking-widest mb-2 hover:text-gray-300 transition-all`}
                            >
                                <div className="flex items-center gap-3">
                                    <Lightbulb className="w-5 h-5 text-yellow-400 shrink-0" />
                                    <span className={`${isSidebarHovered ? 'opacity-100 flex-1' : 'opacity-0 w-0 h-0 hidden'} transition-all duration-300 whitespace-nowrap overflow-hidden`}>Insights</span>
                                </div>
                                {isSidebarHovered && (expandedCategories.insights ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />)}
                            </button>
                            <AnimatePresence>
                                {isSidebarHovered && expandedCategories.insights && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="flex flex-col gap-1 overflow-hidden"
                                    >
                                        {navItems.insights.map((item) => (
                                            <button
                                                key={item.id}
                                                onClick={() => handleNavClick(item.id)}
                                                className={`
                                                    flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all
                                                    ${activeTab === item.id
                                                        ? 'bg-[#00d4ff]/10 text-white border border-[#00d4ff]/20 shadow-[0_0_15px_rgba(0,212,255,0.05)]'
                                                        : 'text-gray-400 hover:bg-white/5 hover:text-white border border-transparent'}
                                                `}
                                            >
                                                <item.icon className={`w-4 h-4 shrink-0 ${activeTab === item.id ? 'text-[#00d4ff]' : 'text-gray-500'}`} />
                                                <span className={`text-xs font-semibold tracking-tight whitespace-nowrap transition-all duration-300 ${isSidebarHovered ? 'opacity-100' : 'opacity-0 w-0 h-0 hidden'}`}>{item.label}</span>
                                            </button>
                                        ))}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Threats Category */}
                        <div>
                            <button
                                onClick={() => toggleCategory('threats')}
                                className={`w-full flex items-center ${isSidebarHovered ? 'justify-between px-2' : 'justify-center'} text-[11px] font-bold text-gray-500 uppercase tracking-widest mb-2 hover:text-gray-300 transition-all`}
                            >
                                <div className="flex items-center gap-3">
                                    <ShieldAlert className="w-5 h-5 text-red-400 shrink-0" />
                                    <span className={`${isSidebarHovered ? 'opacity-100 flex-1' : 'opacity-0 w-0 h-0 hidden'} transition-all duration-300 whitespace-nowrap overflow-hidden`}>Threats</span>
                                </div>
                                {isSidebarHovered && (expandedCategories.threats ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />)}
                            </button>
                            <AnimatePresence>
                                {isSidebarHovered && expandedCategories.threats && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="flex flex-col gap-1 overflow-hidden"
                                    >
                                        {navItems.threats.map((item) => (
                                            <button
                                                key={item.id}
                                                onClick={() => handleNavClick(item.id)}
                                                className={`
                                                    flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all
                                                    ${activeTab === item.id
                                                        ? 'bg-[#00d4ff]/10 text-white border border-[#00d4ff]/20 shadow-[0_0_15px_rgba(0,212,255,0.05)]'
                                                        : 'text-gray-400 hover:bg-white/5 hover:text-white border border-transparent'}
                                                `}
                                            >
                                                <item.icon className={`w-4 h-4 shrink-0 ${activeTab === item.id ? 'text-[#00d4ff]' : 'text-gray-500'}`} />
                                                <span className={`text-xs font-semibold tracking-tight whitespace-nowrap transition-all duration-300 ${isSidebarHovered ? 'opacity-100' : 'opacity-0 w-0 h-0 hidden'}`}>{item.label}</span>
                                            </button>
                                        ))}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>

                    <div className="mt-auto p-4 border-t border-[#1a1f3a]">
                        <div className="bg-gradient-to-br from-[#1a1f3a] to-[#0a0e27] rounded-2xl p-4 border border-[#1a1f3a] relative overflow-hidden group">
                            <div className="relative z-10">
                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">System Health</span>
                                <div className="flex items-center gap-2">
                                    <Activity className="w-3 h-3 text-[#00d4ff]" />
                                    <span className="text-[11px] font-bold text-white uppercase tracking-tighter">Normal Operating</span>
                                </div>
                            </div>
                            <div className="absolute top-0 right-0 w-16 h-16 bg-[#00d4ff]/5 -rotate-45 translate-x-4 -translate-y-4 rounded-3xl" />
                        </div>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto no-scrollbar bg-[#060914] p-6">
                    <div className="max-w-[1720px] mx-auto">
                        <AnimatePresence mode="wait">
                            {activeTab === 'dashboard' && (
                                <motion.div
                                    key="dashboard"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="space-y-6"
                                >
                                    {/* Top Metrics Row */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                                        {[
                                            { label: 'Critical Alerts', count: stats.critical, color: 'text-red-500', bg: 'bg-red-500/10', sev: 'Critical', status: 'All', icon: AlertTriangle },
                                            { label: 'Major Alerts', count: stats.major, color: 'text-orange-500', bg: 'bg-orange-500/10', sev: 'Major', status: 'All', icon: AlertTriangle },
                                            { label: 'Minor Alerts', count: stats.minor, color: 'text-yellow-500', bg: 'bg-yellow-500/10', sev: 'Minor', status: 'All', icon: AlertTriangle },
                                            { label: 'Unassigned', count: stats.unassigned, color: 'text-blue-400', bg: 'bg-blue-400/10', sev: 'All', status: 'Open', icon: User },
                                            { label: 'Closed Cases', count: stats.closed, color: 'text-green-500', bg: 'bg-green-500/10', sev: 'All', status: 'Closed', icon: Database },
                                            { label: 'Remediated', count: stats.remediated, color: 'text-purple-500', bg: 'bg-purple-500/10', sev: 'All', status: 'Closed', icon: Zap }
                                        ].map((card, idx) => (
                                            <div
                                                key={idx}
                                                onClick={() => navigateToEvents(card.sev, card.status)}
                                                className="p-4 rounded-xl border border-[#1a1f3a] bg-[#0a0e27] hover:border-[#00d4ff]/50 hover:bg-[#00d4ff]/5 transition-all cursor-pointer group shadow-xl flex items-center justify-between"
                                            >
                                                <div className="flex flex-col justify-center">
                                                    <span className="text-[9px] font-bold uppercase tracking-widest text-gray-500 mb-1">{card.label}</span>
                                                    <span className="text-2xl font-bold text-white tracking-widest leading-none">{card.count}</span>
                                                </div>
                                                <div className={`p-2 rounded-lg ${card.bg}`}>
                                                    <card.icon className={`w-4 h-4 ${card.color}`} />
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Middle Section: Funnel and Trend Chart */}
                                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                                        {/* Left: Funnel */}
                                        <div className="lg:col-span-4 bg-[#0a0e27] rounded-3xl overflow-hidden border border-[#1a1f3a] shadow-2xl h-[400px]">
                                            <ThreatFunnel
                                                events={stats.totalEvents}
                                                detections={stats.threatScenarios}
                                                alerts={stats.openAlerts}
                                                onEventsClick={() => navigateToEvents('All')}
                                                onDetectionsClick={() => navigateToEvents('All')}
                                                onAlertsClick={() => navigateToEvents('Major')}
                                            />
                                        </div>
                                        {/* Right: Trend Chart */}
                                        <div className="lg:col-span-8">
                                            <TrendChart data={alertTrends.length > 0 ? alertTrends : undefined} />
                                        </div>
                                    </div>

                                    {/* Intelligence Charts Section */}
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        {dashboardMode === 'overlay' && (
                                            <>
                                                <KillChainChart
                                                    data={killChainData}
                                                    onPhaseClick={(phase) => {
                                                        setEventFilter('All'); // Clear severity when clicking Kill Chain
                                                        setSearchTerm(phase);
                                                        setActiveTab('events');
                                                    }}
                                                />
                                                <CveRadar data={radarData} />
                                            </>
                                        )}
                                        {dashboardMode === 'standalone' && (
                                            <div className="lg:col-span-2 bg-[#0a0e27] rounded-3xl p-6 border border-[#1a1f3a] shadow-2xl min-h-[600px] flex flex-col">
                                                <div className="flex justify-between items-center mb-6">
                                                    <div>
                                                        <h3 className="text-white font-bold uppercase tracking-widest text-lg">LogAI Pattern Analysis</h3>
                                                        <p className="text-gray-400 text-xs mt-1">Automated pattern extraction and clustering</p>
                                                    </div>
                                                    <div className="flex gap-4">
                                                        <div className="text-center px-4 py-2 bg-[#1a1f3a]/50 rounded-lg border border-[#2d3748]">
                                                            <div className="text-xs text-gray-400 uppercase">Total Patterns</div>
                                                            <div className="text-xl font-bold text-[#00d4ff]">{logPatterns.length}</div>
                                                        </div>
                                                        <div className="text-center px-4 py-2 bg-[#1a1f3a]/50 rounded-lg border border-[#2d3748]">
                                                            <div className="text-xs text-gray-400 uppercase">Anomalies</div>
                                                            <div className="text-xl font-bold text-[#f97316]">{clusters.reduce((acc, c) => acc + (c.anomalies || 0), 0)}</div>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Charts Section: Side by Side */}
                                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 flex-1">
                                                    {/* LEFT: Occurrence Bar Chart */}
                                                    <div className="bg-[#1a1f3a]/30 rounded-xl p-4 border border-[#2d3748] flex flex-col">
                                                        <h4 className="text-xs text-gray-400 mb-4 uppercase font-bold tracking-wider">Occurrence (Log Count)</h4>
                                                        <div className="flex-1 min-h-[250px]">
                                                            <ResponsiveContainer width="100%" height="100%">
                                                                <BarChart data={logPatterns} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                                                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" horizontal={false} />
                                                                    <XAxis type="number" stroke="#718096" tick={{ fontSize: 10 }} />
                                                                    <YAxis dataKey="id" type="category" width={40} stroke="#718096" tick={{ fontSize: 10 }} />
                                                                    <RechartsTooltip
                                                                        cursor={{ fill: '#1a1f3a' }}
                                                                        contentStyle={{ backgroundColor: '#0a0e27', borderColor: '#2d3748' }}
                                                                        itemStyle={{ color: '#00d4ff' }}
                                                                        formatter={(value, name, props) => [value, 'Count']}
                                                                        labelFormatter={(label) => `Pattern ID: ${label}`}
                                                                    />
                                                                    <Bar dataKey="count" fill="#4daaf8" radius={[0, 4, 4, 0]} barSize={20} />
                                                                </BarChart>
                                                            </ResponsiveContainer>
                                                        </div>
                                                    </div>

                                                    {/* RIGHT: Trend/Cluster Chart (Mixed) */}
                                                    <div className="bg-[#1a1f3a]/30 rounded-xl p-4 border border-[#2d3748] flex flex-col">
                                                        <h4 className="text-xs text-gray-400 mb-4 uppercase font-bold tracking-wider">Cluster Distribution / Trend</h4>
                                                        <div className="flex-1 min-h-[250px]">
                                                            <ResponsiveContainer width="100%" height="100%">
                                                                <PieChart>
                                                                    <Pie
                                                                        data={clusters}
                                                                        cx="50%" cy="50%"
                                                                        innerRadius={60} outerRadius={90}
                                                                        paddingAngle={4}
                                                                        dataKey="value"
                                                                    >
                                                                        {clusters.map((entry, index) => (
                                                                            <Cell key={`cell-${index}`} fill={['#60c07c', '#4daaf8', '#ba6fd4', '#f97316', '#22c55e'][index % 5]} />
                                                                        ))}
                                                                    </Pie>
                                                                    <RechartsTooltip
                                                                        contentStyle={{ backgroundColor: '#0a0e27', borderColor: '#2d3748' }}
                                                                        itemStyle={{ color: '#fff' }}
                                                                    />
                                                                    <Legend verticalAlign="bottom" height={36} iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
                                                                </PieChart>
                                                            </ResponsiveContainer>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Bottom: Detailed Log Pattern Table */}
                                                <div className="bg-[#1a1f3a]/30 rounded-xl border border-[#2d3748] overflow-hidden flex-1 max-h-[300px] flex flex-col">
                                                    <div className="bg-[#1a1f3a] px-4 py-3 border-b border-[#2d3748] flex justify-between items-center">
                                                        <h4 className="text-xs text-white font-bold uppercase tracking-wider">Log Patterns Details</h4>
                                                        <button className="text-[10px] text-[#00d4ff] hover:text-white transition-colors">View All Analysis</button>
                                                    </div>
                                                    <div className="overflow-auto flex-1">
                                                        <table className="w-full text-left text-sm text-gray-400">
                                                            <thead className="bg-[#0a0e27] text-xs uppercase font-bold text-gray-500 sticky top-0">
                                                                <tr>
                                                                    <th className="px-4 py-3">Pattern ID</th>
                                                                    <th className="px-4 py-3">Log Signature Template</th>
                                                                    <th className="px-4 py-3 text-right">Occurrences</th>
                                                                    <th className="px-4 py-3 text-right">Last Seen</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody className="divide-y divide-[#2d3748]">
                                                                {logPatterns.map((pattern, idx) => (
                                                                    <tr key={idx} className="hover:bg-[#1a1f3a]/50 transition-colors">
                                                                        <td className="px-4 py-3 text-[#00d4ff] font-mono text-xs">#{pattern.id || idx + 1}</td>
                                                                        <td className="px-4 py-3 font-mono text-xs text-gray-300 truncate max-w-[400px]" title={pattern.pattern}>
                                                                            {pattern.pattern}
                                                                        </td>
                                                                        <td className="px-4 py-3 text-right font-bold text-white">{pattern.count}</td>
                                                                        <td className="px-4 py-3 text-right text-xs">
                                                                            {pattern.last_seen ? new Date(pattern.last_seen).toLocaleTimeString() : '-'}
                                                                        </td>
                                                                    </tr>
                                                                ))}
                                                                {logPatterns.length === 0 && (
                                                                    <tr>
                                                                        <td colSpan="4" className="px-4 py-8 text-center text-gray-600 italic">No patterns detected yet. Run ingestion.</td>
                                                                    </tr>
                                                                )}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <ThreatEntities />
                                        <AttackPaths />
                                    </div>

                                    {/* New Distribution Section (Replaces alerts table) */}
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-12">
                                        <div className="bg-[#0a0e27] rounded-3xl p-8 border border-[#1a1f3a] shadow-2xl h-[450px] relative overflow-hidden group">
                                            <div className="flex justify-between items-center mb-6">
                                                <h3 className="text-xs font-bold text-white uppercase tracking-[0.3em]">Total alert type</h3>
                                                <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-[#00d4ff] transition-colors cursor-pointer" />
                                            </div>
                                            <div className="h-[320px]">
                                                <ResponsiveContainer width="100%" height="100%">
                                                    <PieChart>
                                                        <Pie
                                                            data={alertTypes.length > 0 ? alertTypes : [
                                                                { name: 'Malware', value: 53.3, fill: '#60c07c' },
                                                                { name: 'Cloud Activity', value: 20.0, fill: '#4daaf8' },
                                                                { name: 'DoS Attack', value: 13.3, fill: '#ba6fd4' },
                                                                { name: 'Suspicious Activity', value: 6.7, fill: '#7c7fb3' },
                                                                { name: 'Exploit', value: 6.7, fill: '#24b8ea' }
                                                            ]}
                                                            cx="50%" cy="45%" innerRadius={0} outerRadius={80} dataKey="value" stroke="#0a0e27" strokeWidth={2}
                                                            labelLine={true}
                                                            label={({ name, percent }) => `${name.length > 15 ? name.slice(0, 15) + '...' : name}: ${(percent * 100).toFixed(1)}%`}
                                                            onClick={(e) => {
                                                                if (e && e.name) {
                                                                    setEventFilter('All');
                                                                    setSearchTerm(e.name);
                                                                    setActiveTab('events');
                                                                }
                                                            }}
                                                            className="cursor-pointer"
                                                        >
                                                            {(alertTypes.length > 0 ? alertTypes : []).map((entry, index) => (
                                                                <Cell key={`cell-${index}`} fill={['#60c07c', '#4daaf8', '#ba6fd4', '#7c7fb3', '#24b8ea'][index % 5]} />
                                                            ))}
                                                        </Pie>
                                                        <RechartsTooltip content={<CustomPieTooltip total={(alertTypes.length > 0 ? alertTypes : [{ value: 53.3 }, { value: 20 }, { value: 13.3 }, { value: 6.7 }, { value: 6.7 }]).reduce((a, b) => a + b.value, 0)} />} />
                                                    </PieChart>
                                                </ResponsiveContainer>
                                            </div>
                                        </div>
                                        <div className="bg-[#0a0e27] rounded-3xl p-8 border border-[#1a1f3a] shadow-2xl h-[450px] relative overflow-hidden group">
                                            <div className="flex justify-between items-center mb-6">
                                                <h3 className="text-xs font-bold text-white uppercase tracking-[0.3em]">Distribution of alerts by severity(Sonal)</h3>
                                                <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-[#00d4ff] transition-colors cursor-pointer" />
                                            </div>
                                            <div className="h-[320px]">
                                                <ResponsiveContainer width="100%" height="100%">
                                                    <PieChart>
                                                        <Pie
                                                            data={[
                                                                { name: 'Minor', value: stats.minor || 0, fill: '#4daaf8', severity: 'Minor' },
                                                                { name: 'Major', value: stats.major || 0, fill: '#24b8ea', severity: 'Major' },
                                                                { name: 'Critical', value: stats.critical || 0, fill: '#60c07c', severity: 'Critical' }
                                                            ]}
                                                            cx="50%" cy="45%" innerRadius={45} outerRadius={60} paddingAngle={0} minAngle={15} dataKey="value" stroke="#0a0e27" strokeWidth={2}
                                                            labelLine={true}
                                                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                                                            onClick={(data) => {
                                                                if (data && data.severity) {
                                                                    navigateToEvents(data.severity);
                                                                }
                                                            }}
                                                            className="cursor-pointer"
                                                        >
                                                        </Pie>
                                                        <RechartsTooltip content={<CustomPieTooltip total={(stats.minor || 0) + (stats.major || 0) + (stats.critical || 0)} />} />
                                                        <Legend />
                                                    </PieChart>
                                                </ResponsiveContainer>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}

                            {activeTab === 'events' && (
                                <motion.div
                                    key="events"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                >
                                    <MitreEvents
                                        alerts={alerts}
                                        initialSeverity={eventFilter}
                                        initialStatus={statusFilter}
                                        initialSearch={searchTerm}
                                        onSearchChange={setSearchTerm}
                                        onAnalyze={analyzeIOC}
                                    />
                                </motion.div>
                            )}

                            {activeTab === 'framework' && (
                                <motion.div
                                    key="framework"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                >
                                    <div className="bg-[#0a0e27] rounded-3xl border border-[#1a1f3a] p-8 shadow-2xl min-h-[600px]">
                                        <MitreAssistant />
                                    </div>
                                </motion.div>
                            )}

                            {activeTab === 'intelligence' && (
                                <motion.div
                                    key="intelligence"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 1.05 }}
                                    className="bg-[#0a0e27] rounded-3xl border border-[#1a1f3a] shadow-2xl p-8 min-h-[600px] overflow-y-auto"
                                >
                                    <IpInvestigation onAnalyze={analyzeIOC} analysis={analysis} />
                                </motion.div>
                            )}

                            {activeTab === 'standalone_intel' && (
                                <motion.div
                                    key="standalone_intel"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 1.05 }}
                                    className="bg-[#0a0e27] rounded-3xl border border-[#1a1f3a] shadow-2xl p-8 min-h-[600px] overflow-y-auto"
                                >
                                    <div className="space-y-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <h2 className="text-xl font-bold text-white uppercase tracking-widest flex items-center gap-3">
                                                <Search className="w-6 h-6 text-[#00d4ff]" />
                                                Syslog Reality Intelligence
                                            </h2>
                                            <div className="px-3 py-1 bg-[#60c07c]/10 border border-[#60c07c]/20 rounded-full">
                                                <span className="text-[10px] font-bold text-[#60c07c] uppercase">Neural Link Active</span>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="bg-[#1a1f3a]/30 p-6 rounded-2xl border border-[#2d3748]">
                                                <h3 className="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest">Raw Log Anomaly Detection</h3>
                                                <div className="h-40 flex items-center justify-center text-gray-500 font-bold italic">
                                                    Streaming real-time syslog analysis...
                                                </div>
                                            </div>
                                            <div className="bg-[#1a1f3a]/30 p-6 rounded-2xl border border-[#2d3748]">
                                                <h3 className="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest">IsolationForest Clusters</h3>
                                                <div className="space-y-4">
                                                    <div className="h-2 bg-[#2d3748] rounded-full overflow-hidden">
                                                        <div className="w-[75%] h-full bg-[#00d4ff]" />
                                                    </div>
                                                    <div className="h-2 bg-[#2d3748] rounded-full overflow-hidden">
                                                        <div className="w-[45%] h-full bg-[#f97316]" />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}

                            {activeTab === 'securezen_analysis' && (
                                <motion.div
                                    key="securezen_analysis"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                >
                                    <LogAIDashboard
                                        setActiveTab={setActiveTab}
                                        setEventFilter={setEventFilter}
                                        setStatusFilter={setStatusFilter}
                                    />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </main>
            </div>

            {/* AI Copilot Widget */}
            <Copilot />
        </div>
    );
};

export default AISOCDashboard;

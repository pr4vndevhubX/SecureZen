// import React, { useState, useEffect } from 'react';
// import { Shield, AlertTriangle, Activity, Database, TrendingUp, Search, RefreshCw, Send, Bot, ExternalLink, Zap } from 'lucide-react';

// const AISOCDashboard = () => {
//   const [alerts, setAlerts] = useState([]);
//   const [stats, setStats] = useState({
//     critical: 0, major: 0, minor: 0, unassigned: 0, closed: 0,
//     totalEvents: 0, threatScenarios: 0, openAlerts: 0
//   });
//   const [severityDist, setSeverityDist] = useState({ Critical: 0, Major: 0, Minor: 0 });
//   const [alertTrends, setAlertTrends] = useState([]);
//   const [topAlertTypes, setTopAlertTypes] = useState([]);
//   const [topEntities, setTopEntities] = useState([]);
//   const [recentAlerts, setRecentAlerts] = useState([]);
//   const [crewAnalysis, setCrewAnalysis] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [chatMessages, setChatMessages] = useState([]);
//   const [chatInput, setChatInput] = useState('');
//   const [activeTab, setActiveTab] = useState('dashboard');

//   useEffect(() => {
//     fetchDashboardData();
//     const interval = setInterval(fetchDashboardData, 30000);
//     return () => clearInterval(interval);
//   }, []);

//   const fetchDashboardData = async () => {
//     try {
//       const res = await fetch('http://localhost:5000/api/dashboard-stats');
//       const data = await res.json();
//       processAlertData(data);
//       setLoading(false);
//     } catch (error) {
//       console.error('Error:', error);
//       setLoading(false);
//     }
//   };

//   const processAlertData = (data) => {
//     const severityCounts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
//     const typeMap = {}, entityMap = {}, hourlyTrends = {};
//     const allAlerts = [];

//     data.alerts?.forEach(alert => {
//       const sev = alert.severity || 'Medium';
//       severityCounts[sev] = (severityCounts[sev] || 0) + 1;
      
//       const type = alert.rule_description || 'Unknown';
//       typeMap[type] = (typeMap[type] || 0) + 1;
      
//       const entity = alert.agent_name || alert.src_ip || 'Unknown';
//       entityMap[entity] = (entityMap[entity] || 0) + 1;
      
//       const ts = new Date(alert.timestamp);
//       const hourKey = `${ts.getMonth()+1}/${ts.getDate()} ${ts.getHours()}:00`;
//       hourlyTrends[hourKey] = (hourlyTrends[hourKey] || 0) + 1;
      
//       allAlerts.push({
//         time: ts.toLocaleString(),
//         alertId: alert.alert_id,
//         type: alert.rule_description,
//         severity: alert.severity,
//         message: alert.message,
//         entity: alert.agent_name || alert.src_ip,
//         mitreId: alert.rule_mitre_id,
//         mitreTactic: alert.rule_mitre_tactic,
//         iocs: alert.extracted_iocs || []
//       });
//     });

//     const total = allAlerts.length;
//     const crit = severityCounts.Critical || 0;
//     const high = severityCounts.High || 0;
//     const med = severityCounts.Medium || 0;

//     setStats({
//       critical: crit,
//       major: high,
//       minor: med + (severityCounts.Low || 0),
//       unassigned: Math.floor(total * 0.2),
//       closed: Math.floor(total * 0.7),
//       totalEvents: total,
//       threatScenarios: total * 100,
//       openAlerts: crit + high
//     });

//     const totalSev = crit + high + med;
//     setSeverityDist({
//       Critical: totalSev > 0 ? ((crit / totalSev) * 100).toFixed(1) : 0,
//       Major: totalSev > 0 ? ((high / totalSev) * 100).toFixed(1) : 0,
//       Minor: totalSev > 0 ? ((med / totalSev) * 100).toFixed(1) : 0
//     });

//     setTopAlertTypes(Object.entries(typeMap).sort((a,b) => b[1]-a[1]).slice(0,10).map(([t]) => t));
//     setTopEntities(Object.entries(entityMap).sort((a,b) => b[1]-a[1]).slice(0,8).map(([e]) => e));
//     setAlertTrends(Object.entries(hourlyTrends).map(([time, count]) => ({time, count})).sort((a,b) => new Date(a.time) - new Date(b.time)).slice(-24));
//     setRecentAlerts(allAlerts.filter(a => a.severity === 'Critical').sort((a,b) => new Date(b.time) - new Date(a.time)).slice(0,10));
    
//     if (data.crew_analysis) {
//       setCrewAnalysis(data.crew_analysis);
//     }
//   };

//   const analyzeIOC = async (ioc) => {
//     try {
//       const res = await fetch('http://localhost:5000/api/analyze-ioc', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ ioc })
//       });
//       const data = await res.json();
//       setChatMessages(prev => [...prev, {
//         type: 'assistant',
//         content: `🔍 Analysis for ${ioc}:\n${data.analysis}`
//       }]);
//       setActiveTab('chat');
//     } catch (error) {
//       console.error('Error analyzing IOC:', error);
//     }
//   };

//   const handleChatSubmit = async () => {
//     if (!chatInput.trim()) return;
    
//     setChatMessages(prev => [...prev, { type: 'user', content: chatInput }]);
    
//     try {
//       const res = await fetch('http://localhost:5000/api/chat', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ message: chatInput })
//       });
//       const data = await res.json();
//       setChatMessages(prev => [...prev, { type: 'assistant', content: data.response }]);
//     } catch (error) {
//       setChatMessages(prev => [...prev, { type: 'assistant', content: 'Error processing request' }]);
//     }
    
//     setChatInput('');
//   };

//   const maxTrend = alertTrends.length > 0 ? Math.max(...alertTrends.map(d => d.count)) : 1;

//   if (loading) {
//     return (
//       <div className="min-h-screen bg-[#0a0e27] flex items-center justify-center">
//         <div className="text-center">
//           <RefreshCw className="w-12 h-12 text-[#00d4ff] animate-spin mx-auto mb-4" />
//           <div className="text-xl text-[#00d4ff]">Initializing AI SOC...</div>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-[#0a0e27] text-white">
//       {/* Header */}
//       <div className="bg-gradient-to-r from-[#1a1f3a] to-[#0f1729] border-b border-[#2d3748] px-6 py-4">
//         <div className="flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <Shield className="w-10 h-10 text-[#00d4ff]" />
//             <div>
//               <h1 className="text-3xl font-bold text-[#00d4ff]" style={{textShadow: '0 0 10px rgba(0,212,255,0.5)'}}>
//                 AI SOC Platform
//               </h1>
//               <p className="text-xs text-gray-400">Real-time Wazuh Monitoring + CrewAI Threat Intelligence + MITRE ATT&CK</p>
//             </div>
//           </div>
//           <div className="flex gap-3">
//             <div className="text-center px-4 py-2 bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748]">
//               <div className="text-xl font-bold text-[#00d4ff]">{stats.totalEvents.toLocaleString()}</div>
//               <div className="text-xs text-gray-400">Events</div>
//             </div>
//             <div className="text-center px-4 py-2 bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748]">
//               <div className="text-xl font-bold text-[#00d4ff]">{stats.openAlerts}</div>
//               <div className="text-xs text-gray-400">Open Alerts</div>
//             </div>
//             <div className="text-center px-4 py-2 bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748]">
//               <div className="text-xl font-bold text-[#00d4ff]">{crewAnalysis.length}</div>
//               <div className="text-xs text-gray-400">AI Analysis</div>
//             </div>
//           </div>
//         </div>
//       </div>

//       {/* Tabs */}
//       <div className="bg-[#1a1f3a] px-6 py-3 flex gap-6 border-b border-[#2d3748]">
//         <button
//           onClick={() => setActiveTab('dashboard')}
//           className={`px-4 py-2 rounded font-semibold transition ${activeTab === 'dashboard' ? 'bg-[#00d4ff] text-[#0a0e27]' : 'text-gray-400 hover:text-[#00d4ff]'}`}
//         >
//           📊 Dashboard
//         </button>
//         <button
//           onClick={() => setActiveTab('crew')}
//           className={`px-4 py-2 rounded font-semibold transition ${activeTab === 'crew' ? 'bg-[#00d4ff] text-[#0a0e27]' : 'text-gray-400 hover:text-[#00d4ff]'}`}
//         >
//           🤖 AI Analysis
//         </button>
//         <button
//           onClick={() => setActiveTab('mitre')}
//           className={`px-4 py-2 rounded font-semibold transition ${activeTab === 'mitre' ? 'bg-[#00d4ff] text-[#0a0e27]' : 'text-gray-400 hover:text-[#00d4ff]'}`}
//         >
//           🎯 MITRE ATT&CK
//         </button>
//         <button
//           onClick={() => setActiveTab('chat')}
//           className={`px-4 py-2 rounded font-semibold transition ${activeTab === 'chat' ? 'bg-[#00d4ff] text-[#0a0e27]' : 'text-gray-400 hover:text-[#00d4ff]'}`}
//         >
//           💬 AI Assistant
//         </button>
//       </div>

//       <div className="p-6">
//         {activeTab === 'dashboard' && (
//           <div className="space-y-6">
//             {/* Stats Cards */}
//             <div className="grid grid-cols-6 gap-4">
//               {[
//                 { label: '🔴 CRITICAL', value: stats.critical, delta: '+3' },
//                 { label: '🟠 MAJOR', value: stats.major, delta: '+12' },
//                 { label: '🟡 MINOR', value: stats.minor, delta: '+25' },
//                 { label: '📊 TOTAL', value: stats.totalEvents, delta: '' },
//                 { label: '📂 UNASSIGNED', value: stats.unassigned, delta: '' },
//                 { label: '✅ CLOSED', value: stats.closed, delta: '' }
//               ].map((stat, i) => (
//                 <div key={i} className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-4 text-center">
//                   <div className="text-3xl font-bold text-[#00d4ff] mb-1">{stat.value}</div>
//                   <div className="text-xs text-gray-400">{stat.label}</div>
//                   {stat.delta && <div className="text-xs text-green-400 mt-1">{stat.delta}</div>}
//                 </div>
//               ))}
//             </div>

//             {/* Charts Row */}
//             <div className="grid grid-cols-3 gap-6">
//               {/* Alert Trends */}
//               <div className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-6">
//                 <h3 className="text-lg font-semibold mb-4 text-[#00d4ff]">Alert Trends (24h)</h3>
//                 <div className="h-40">
//                   <svg viewBox="0 0 800 160" className="w-full h-full">
//                     {alertTrends.map((pt, i) => {
//                       const x = (i / Math.max(alertTrends.length - 1, 1)) * 750 + 25;
//                       const y = 140 - (pt.count / maxTrend) * 120;
//                       const next = alertTrends[i + 1];
//                       return (
//                         <g key={i}>
//                           {next && (
//                             <line x1={x} y1={y} x2={(i + 1) / Math.max(alertTrends.length - 1, 1) * 750 + 25} y2={140 - (next.count / maxTrend) * 120} stroke="#00d4ff" strokeWidth="2"/>
//                           )}
//                           <circle cx={x} cy={y} r="3" fill="#00d4ff"/>
//                         </g>
//                       );
//                     })}
//                   </svg>
//                 </div>
//               </div>

//               {/* Severity Distribution */}
//               <div className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-6">
//                 <h3 className="text-lg font-semibold mb-4 text-[#00d4ff]">Severity Distribution</h3>
//                 <div className="relative w-40 h-40 mx-auto">
//                   <svg viewBox="0 0 100 100">
//                     <circle cx="50" cy="50" r="40" fill="none" stroke="#dc2626" strokeWidth="20" strokeDasharray={`${severityDist.Critical * 2.512} 251.2`} transform="rotate(-90 50 50)"/>
//                     <circle cx="50" cy="50" r="40" fill="none" stroke="#4ade80" strokeWidth="20" strokeDasharray={`${severityDist.Major * 2.512} 251.2`} strokeDashoffset={`-${severityDist.Critical * 2.512}`} transform="rotate(-90 50 50)"/>
//                     <circle cx="50" cy="50" r="40" fill="none" stroke="#00d4ff" strokeWidth="20" strokeDasharray={`${severityDist.Minor * 2.512} 251.2`} strokeDashoffset={`-${(parseFloat(severityDist.Critical) + parseFloat(severityDist.Major)) * 2.512}`} transform="rotate(-90 50 50)"/>
//                   </svg>
//                   <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-[#00d4ff]">
//                     {stats.openAlerts}
//                   </div>
//                 </div>
//               </div>

//               {/* Top Entities */}
//               <div className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-6">
//                 <h3 className="text-lg font-semibold mb-4 text-[#00d4ff]">Top Entities</h3>
//                 <div className="flex flex-wrap gap-2 h-40 overflow-auto">
//                   {topEntities.map((ip, i) => (
//                     <span key={i} className="text-[#00d4ff] cursor-pointer hover:underline" style={{fontSize: `${1.1 - i * 0.05}rem`}} onClick={() => analyzeIOC(ip)}>
//                       {ip}
//                     </span>
//                   ))}
//                 </div>
//               </div>
//             </div>

//             {/* Recent Critical Alerts */}
//             <div className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-6">
//               <h3 className="text-lg font-semibold mb-4 text-[#00d4ff]">🔴 Recent Critical Alerts (Auto-Analyzed by AI)</h3>
//               <div className="overflow-auto max-h-96">
//                 <table className="w-full text-sm">
//                   <thead className="text-gray-400 border-b border-[#2d3748] sticky top-0 bg-[#1a1f3a]">
//                     <tr>
//                       <th className="text-left pb-2 px-2">Time</th>
//                       <th className="text-left pb-2 px-2">Alert Type</th>
//                       <th className="text-left pb-2 px-2">Entity</th>
//                       <th className="text-left pb-2 px-2">MITRE</th>
//                       <th className="text-left pb-2 px-2">IOCs</th>
//                       <th className="text-left pb-2 px-2">Action</th>
//                     </tr>
//                   </thead>
//                   <tbody className="text-gray-300">
//                     {recentAlerts.map((alert, i) => (
//                       <tr key={i} className="border-b border-[#2d3748]/50 hover:bg-[#2d3748]/30">
//                         <td className="py-2 px-2 text-xs">{alert.time}</td>
//                         <td className="py-2 px-2">{alert.type}</td>
//                         <td className="py-2 px-2 text-[#00d4ff]">{alert.entity}</td>
//                         <td className="py-2 px-2 text-yellow-400">{alert.mitreId || 'N/A'}</td>
//                         <td className="py-2 px-2">
//                           {alert.iocs?.length > 0 ? (
//                             <span className="px-2 py-1 bg-red-500/20 rounded text-xs">{alert.iocs.length} IOCs</span>
//                           ) : 'None'}
//                         </td>
//                         <td className="py-2 px-2">
//                           <button onClick={() => analyzeIOC(alert.entity)} className="px-3 py-1 bg-[#00d4ff] text-[#0a0e27] rounded text-xs font-semibold hover:bg-[#00b8e6]">
//                             <Zap className="w-3 h-3 inline mr-1"/>Analyze
//                           </button>
//                         </td>
//                       </tr>
//                     ))}
//                   </tbody>
//                 </table>
//               </div>
//             </div>
//           </div>
//         )}

//         {activeTab === 'crew' && (
//           <div className="space-y-4">
//             <h2 className="text-2xl font-bold text-[#00d4ff] mb-4">🤖 CrewAI Threat Intelligence Analysis</h2>
//             {crewAnalysis.length === 0 ? (
//               <div className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-8 text-center">
//                 <Bot className="w-16 h-16 text-gray-500 mx-auto mb-4"/>
//                 <p className="text-gray-400">No IOCs analyzed yet. Critical alerts (Level 7+) are automatically analyzed.</p>
//               </div>
//             ) : (
//               crewAnalysis.map((analysis, i) => (
//                 <div key={i} className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-6">
//                   <div className="flex items-center justify-between mb-4">
//                     <h3 className="text-xl font-bold text-[#00d4ff]">IOC: {analysis.ioc}</h3>
//                     <span className={`px-3 py-1 rounded font-semibold ${
//                       analysis.threat_level === 'CRITICAL' ? 'bg-red-500' :
//                       analysis.threat_level === 'HIGH' ? 'bg-orange-500' :
//                       analysis.threat_level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'
//                     }`}>{analysis.threat_level}</span>
//                   </div>
//                   <div className="grid grid-cols-3 gap-4 mb-4">
//                     <div className="bg-[#0f1729] p-3 rounded">
//                       <div className="text-xs text-gray-400 mb-1">VirusTotal</div>
//                       <div className="text-lg font-bold text-[#00d4ff]">{analysis.virustotal?.detections || '0/98'}</div>
//                     </div>
//                     <div className="bg-[#0f1729] p-3 rounded">
//                       <div className="text-xs text-gray-400 mb-1">AbuseIPDB</div>
//                       <div className="text-lg font-bold text-[#00d4ff]">{analysis.abuseipdb?.confidence || '0'}%</div>
//                     </div>
//                     <div className="bg-[#0f1729] p-3 rounded">
//                       <div className="text-xs text-gray-400 mb-1">Yeti</div>
//                       <div className="text-lg font-bold text-[#00d4ff]">{analysis.yeti?.found ? 'Found' : 'Not Found'}</div>
//                     </div>
//                   </div>
//                   <div className="text-sm text-gray-300 whitespace-pre-wrap">{analysis.summary}</div>
//                   <div className="mt-4 flex gap-2">
//                     <a href={`https://www.virustotal.com/gui/ip-address/${analysis.ioc}`} target="_blank" className="text-xs text-[#00d4ff] hover:underline flex items-center gap-1">
//                       <ExternalLink className="w-3 h-3"/>VirusTotal
//                     </a>
//                     <a href={`https://www.abuseipdb.com/check/${analysis.ioc}`} target="_blank" className="text-xs text-[#00d4ff] hover:underline flex items-center gap-1">
//                       <ExternalLink className="w-3 h-3"/>AbuseIPDB
//                     </a>
//                   </div>
//                 </div>
//               ))
//             )}
//           </div>
//         )}

//         {activeTab === 'mitre' && (
//           <div className="space-y-4">
//             <h2 className="text-2xl font-bold text-[#00d4ff] mb-4">🎯 MITRE ATT&CK Mapping</h2>
//             <div className="bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] p-6">
//               <div className="grid grid-cols-2 gap-4">
//                 {recentAlerts.filter(a => a.mitreId).slice(0, 10).map((alert, i) => (
//                   <div key={i} className="bg-[#0f1729] p-4 rounded border border-[#2d3748]">
//                     <div className="text-yellow-400 font-bold mb-2">{alert.mitreId}</div>
//                     <div className="text-sm text-gray-300 mb-2">{alert.mitreTactic}</div>
//                     <div className="text-xs text-gray-500">Entity: {alert.entity}</div>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           </div>
//         )}

//         {activeTab === 'chat' && (
//           <div className="h-[600px] bg-gradient-to-br from-[#1a1f3a] to-[#0f1729] rounded border border-[#2d3748] flex flex-col">
//             <div className="flex items-center gap-2 p-4 border-b border-[#2d3748]">
//               <Bot className="w-6 h-6 text-[#00d4ff]"/>
//               <h3 className="text-lg font-semibold text-[#00d4ff]">AI Security Assistant</h3>
//             </div>
//             <div className="flex-1 overflow-auto p-4 space-y-3">
//               {chatMessages.map((msg, i) => (
//                 <div key={i} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
//                   <div className={`max-w-[70%] p-3 rounded ${msg.type === 'user' ? 'bg-[#00d4ff] text-[#0a0e27]' : 'bg-[#0f1729] text-gray-300'}`}>
//                     <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
//                   </div>
//                 </div>
//               ))}
//             </div>
//             <div className="p-4 border-t border-[#2d3748]">
//               <div className="flex gap-2">
//                 <input
//                   type="text"
//                   value={chatInput}
//                   onChange={(e) => setChatInput(e.target.value)}
//                   onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
//                   placeholder="Ask about threats, IOCs, MITRE techniques..."
//                   className="flex-1 bg-[#0f1729] border border-[#2d3748] rounded px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-[#00d4ff]"
//                 />
//                 <button onClick={handleChatSubmit} className="px-6 py-2 bg-[#00d4ff] text-[#0a0e27] rounded font-semibold hover:bg-[#00b8e6] flex items-center gap-2">
//                   <Send className="w-4 h-4"/>Send
//                 </button>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>

//       {/* Footer */}
//       <div className="bg-[#1a1f3a] border-t border-[#2d3748] px-6 py-3 flex justify-between text-xs text-gray-400">
//         <div>🔒 Powered by Wazuh SIEM + CrewAI + VirusTotal + AbuseIPDB + Yeti + MITRE ATT&CK</div>
//         <div>© 2026 AI SOC Platform | {new Date().toLocaleString()}</div>
//       </div>
//     </div>
//   );
// };

// export default AISOCDashboard;
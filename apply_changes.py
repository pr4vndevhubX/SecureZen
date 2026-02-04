
import os

def replace_in_file(filepath, target, replacement):
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Reading {filepath}... (Length: {len(content)})")
    
    if target in content:
        new_content = content.replace(target, replacement)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully updated {filepath} (UTF-8)")
    else:
        # Try with different line endings
        target_crnl = target.replace('\n', '\r\n')
        if target_crnl in content:
            new_content = content.replace(target_crnl, replacement.replace('\n', '\r\n'))
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully updated {filepath} (CRLF)")
        else:
            print(f"FAILURE: Target not found in {filepath}")
            # print("Target snippet:", repr(target[:50]))

root = r'c:\Users\psuresh\OneDrive - KRYA SOLUTIONS PRIVATE LIMITED\Desktop\KYD\Agentic-ai-02\IP-alone-Crewai\ip-intel-crewai'
app_jsx = os.path.join(root, 'frontend', 'src', 'App.jsx')
mitre_jsx = os.path.join(root, 'frontend', 'src', 'components', 'MitreEvents.jsx')

# App.jsx states
replace_in_file(
    app_jsx,
    "    const [alertTrends, setAlertTrends] = useState([]);",
    "    const [alertTrends, setAlertTrends] = useState([]);\n    const [globalSearchQuery, setGlobalSearchQuery] = useState('');\n    const [showNotifications, setShowNotifications] = useState(false);"
)

# App.jsx Search Input
replace_in_file(
    app_jsx,
    'placeholder="Global Search..."',
    'placeholder="Global Search (Enter to filter)..." value={globalSearchQuery} onChange={(e) => setGlobalSearchQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") setActiveTab("events"); }}'
)

# App.jsx Notifications
replace_in_file(
    app_jsx,
    '<Bell className="w-5 h-5 cursor-pointer hover:text-[#00d4ff] transition-colors" />',
    '''<div className="relative">
                            <Bell
                                className={`w-5 h-5 cursor-pointer transition-colors ${showNotifications ? 'text-[#00d4ff]' : 'hover:text-[#00d4ff]'}`}
                                onClick={() => setShowNotifications(!showNotifications)}
                            />
                            {showNotifications && (
                                <div className="absolute top-12 right-0 w-80 bg-[#0a0e27] border border-[#1a1f3a] rounded-2xl shadow-2xl p-4 z-[100] animate-in fade-in slide-in-from-top-2 duration-300">
                                    <h4 className="text-[10px] font-bold text-white uppercase tracking-widest mb-4 border-b border-[#1a1f3a] pb-2 flex items-center justify-between">
                                        Live Feed
                                        <span className="bg-[#00d4ff]/20 text-[#00d4ff] px-1.5 py-0.5 rounded text-[8px]">New Updates</span>
                                    </h4>
                                    <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                                        {[
                                            { type: 'Critical', msg: 'Intelligence Report Ready for IP 185.156.177.214', time: 'Just now' },
                                            { type: 'High', msg: 'Neural Triage triggered: Brute Force Attempt', time: '12m ago' },
                                            { type: 'Info', msg: 'Daily system health check complete', time: '2h ago' }
                                        ].map((n, i) => (
                                            <div key={i} className="bg-white/5 p-3 rounded-xl border border-white/5 hover:border-[#00d4ff]/20 transition-all cursor-pointer">
                                                <div className="flex justify-between items-start mb-1">
                                                    <span className={`text-[8px] font-bold uppercase ${n.type === 'Critical' ? 'text-red-500' : n.type === 'High' ? 'text-orange-500' : 'text-blue-400'}`}>{n.type}</span>
                                                    <span className="text-[8px] text-gray-600 uppercase font-bold">{n.time}</span>
                                                </div>
                                                <p className="text-[10px] text-gray-300 font-medium leading-tight">{n.msg}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>'''
)

# App.jsx MitreEvents Prop
replace_in_file(
    app_jsx,
    '<MitreEvents alerts={alerts} initialSeverity={eventFilter} onAnalyze={analyzeIOC} />',
    '<MitreEvents alerts={alerts} initialSeverity={eventFilter} onAnalyze={analyzeIOC} externalSearch={globalSearchQuery} />'
)

# MitreEvents.jsx Prop and Effect
replace_in_file(
    mitre_jsx,
    "export const MitreEvents = ({ alerts, initialSeverity = 'All', onAnalyze }) => {",
    "export const MitreEvents = ({ alerts, initialSeverity = 'All', onAnalyze, externalSearch = '' }) => {"
)

replace_in_file(
    mitre_jsx,
    "    const [severityFilter, setSeverityFilter] = useState(initialSeverity);",
    "    const [severityFilter, setSeverityFilter] = useState(initialSeverity);\n\n    useEffect(() => {\n        if (externalSearch) {\n            setSearchTerm(externalSearch);\n        }\n    }, [externalSearch]);"
)
鼓数据鼓


import os
import re

def regex_replace(filepath, pattern, replacement):
    print(f"Applying regex to {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("SUCCESS")
    else:
        print(f"FAILURE: Pattern {pattern!r} not found")

root = r'c:\Users\psuresh\OneDrive - KRYA SOLUTIONS PRIVATE LIMITED\Desktop\KYD\Agentic-ai-02\IP-alone-Crewai\ip-intel-crewai'
app_path = os.path.join(root, 'frontend', 'src', 'App.jsx')
mitre_path = os.path.join(root, 'frontend', 'src', 'components', 'MitreEvents.jsx')

# App.jsx: State (adding after alertTrends)
regex_replace(
    app_path,
    r"const \[alertTrends, setAlertTrends\] = useState\(.*?\);",
    "const [alertTrends, setAlertTrends] = useState([]);\n    const [globalSearchQuery, setGlobalSearchQuery] = useState('');"
)

# App.jsx: Search Bar
regex_replace(
    app_path,
    r'placeholder="Global Search\.\.\."',
    'placeholder="Search threats, IPs, or tactics..." value={globalSearchQuery} onChange={(e) => setGlobalSearchQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") setActiveTab("events"); }}'
)

# App.jsx: MitreEvents
regex_replace(
    app_path,
    r'<MitreEvents alerts=\{alerts\} initialSeverity=\{eventFilter\} onAnalyze=\{analyzeIOC\} />',
    '<MitreEvents alerts={alerts} initialSeverity={eventFilter} onAnalyze={analyzeIOC} externalSearch={globalSearchQuery} />'
)

# MitreEvents.jsx: Prop
regex_replace(
    mitre_path,
    r"export const MitreEvents = \(\{ alerts, onAnalyze, initialSeverity = 'All' \}\) => \{",
    "export const MitreEvents = ({ alerts, onAnalyze, initialSeverity = 'All', externalSearch = '' }) => {"
)

# MitreEvents.jsx: Effect
regex_replace(
    mitre_path,
    r"const \[severityFilter, setSeverityFilter\] = useState\(initialSeverity\);",
    "const [severityFilter, setSeverityFilter] = useState(initialSeverity);\n\n    useEffect(() => {\n        if (externalSearch !== undefined && externalSearch !== null) {\n            setSearchTerm(externalSearch);\n        }\n    }, [externalSearch]);"
)
????

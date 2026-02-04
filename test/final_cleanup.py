
import os
import re

def clean_app_jsx(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove the empty spaces and divs in header
    # Find the flex items-center gap-6 div and clean it up
    header_pattern = r'<div className="flex items-center gap-6">.*?<div className="flex items-center gap-2 bg-\[#1a1f3a\]'
    replacement = '<div className="flex items-center gap-6">\n                    <div className="flex items-center gap-2 bg-[#1a1f3a]'
    content = re.sub(header_pattern, replacement, content, flags=re.DOTALL)
    
    # 2. Ensure div nesting is correct (one extra </div> might be left)
    # Actually, let's just count the divs. 
    # Better: just look at the lines around 260-290
    
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("Cleaned App.jsx")

def clean_mitre_jsx(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove unused Search import if no longer needed? 
    # Actually, MitreEvents local search still uses Search icon.
    
    # Just ensure no artifacts are left
    content = content.replace('鼓数据鼓', '') # My own tracking string
    
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("Cleaned MitreEvents.jsx")

root = r'c:\Users\psuresh\OneDrive - KRYA SOLUTIONS PRIVATE LIMITED\Desktop\KYD\Agentic-ai-02\IP-alone-Crewai\ip-intel-crewai'
clean_app_jsx(os.path.join(root, 'frontend', 'src', 'App.jsx'))
clean_mitre_jsx(os.path.join(root, 'frontend', 'src', 'components', 'MitreEvents.jsx'))
鼓数据鼓

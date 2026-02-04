import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Info, ExternalLink, Activity } from 'lucide-react';

export const ReportViewer = ({ report }) => {
    if (!report) return null;

    // Simple parser to convert the Markdown report into sections
    const parseReport = (text) => {
        if (typeof text !== 'string') {
            try {
                return [{ title: 'System', content: [JSON.stringify(text)] }];
            } catch {
                return [{ title: 'Error', content: ['Invalid report format received.'] }];
            }
        }
        const lines = text.split('\n');
        const sections = [];
        let currentSection = { title: 'Intro', content: [] };

        lines.forEach(line => {
            if (line.startsWith('## ')) {
                if (currentSection.content.length > 0) {
                    sections.push(currentSection);
                }
                currentSection = { title: line.replace('## ', '').trim(), content: [] };
            } else if (line.trim() !== '') {
                currentSection.content.push(line);
            }
        });
        sections.push(currentSection);
        return sections;
    };

    const sections = parseReport(report);

    const getSectionIcon = (title) => {
        if (title.includes('Executive')) return <Shield className="w-5 h-5 text-[#00d4ff]" />;
        if (title.includes('Risk')) return <AlertTriangle className="w-5 h-5 text-orange-500" />;
        if (title.includes('Finding')) return <Activity className="w-5 h-5 text-purple-500" />;
        if (title.includes('Action')) return <CheckCircle className="w-5 h-5 text-green-500" />;
        return <Info className="w-5 h-5 text-gray-400" />;
    };

    return (
        <div className="space-y-4 font-sans text-gray-300">
            {sections.map((section, idx) => (
                <div key={idx} className="bg-[#1a1f3a]/40 border border-[#2d3748] rounded-lg p-5 hover:border-[#00d4ff]/50 transition-colors">
                    {section.title !== 'Intro' && (
                        <h3 className="text-xl font-bold mb-3 flex items-center gap-2 text-white border-b border-[#2d3748] pb-2">
                            {getSectionIcon(section.title)}
                            {section.title.replace(/🔵|🌐|📊|🎯|📋|🔗/g, '').trim()}
                        </h3>
                    )}

                    <div className="space-y-2">
                        {section.content.map((line, lIdx) => {
                            // Highlight Keys
                            if (line.includes('**')) {
                                const parts = line.split('**');
                                return (
                                    <div key={lIdx} className="text-sm">
                                        {parts.map((p, i) => i % 2 === 1 ? <span key={i} className="font-bold text-[#00d4ff]">{p}</span> : p)}
                                    </div>
                                )
                            }
                            // Headers ###
                            if (line.startsWith('### ')) {
                                return <h4 key={lIdx} className="text-lg font-semibold text-gray-100 mt-4 mb-2">{line.replace('### ', '')}</h4>
                            }
                            // Lists -
                            if (line.trim().startsWith('- ')) {
                                return (
                                    <div key={lIdx} className="flex gap-2 items-start ml-2 text-sm">
                                        <span className="text-[#00d4ff] mt-1">•</span>
                                        <span>{line.replace('- ', '')}</span>
                                    </div>
                                )
                            }
                            // Links
                            if (line.includes('http')) {
                                return <div key={lIdx} className="text-sm text-blue-400 underline break-all">{line}</div>
                            }

                            return <p key={lIdx} className="text-sm leading-relaxed">{line}</p>;
                        })}
                    </div>
                </div>
            ))}
        </div>
    );
};

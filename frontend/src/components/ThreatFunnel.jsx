import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';

const ThreatFunnel = ({ events = "1.87B", detections = "526.77K", alerts = "77", onEventsClick, onDetectionsClick, onAlertsClick }) => {
    return (
        <div className="relative w-full h-full flex flex-col items-center justify-center p-8 bg-[#0a0e27]/40">
            <div className="absolute top-6 left-6 flex flex-col">
                <span className="text-[10px] font-bold text-[#00d4ff] uppercase tracking-widest">Detection Pipeline</span>
                <span className="text-xs text-gray-500 font-bold uppercase">Real-time Stream Analysis</span>
            </div>

            <svg viewBox="0 0 400 520" className="w-full max-w-[300px] drop-shadow-[0_0_30px_rgba(0,212,255,0.2)]">
                {/* Outer Funnel Outline - Sharper Edges */}
                <path
                    d="M50,50 L350,50 L240,400 L160,400 Z"
                    fill="none"
                    stroke="#1a1f3a"
                    strokeWidth="2"
                />

                {/* Layer 1: Events Analyzed */}
                <motion.path
                    initial={{ opacity: 0, scaleY: 0 }}
                    animate={{ opacity: 0.2, scaleY: 1 }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    onClick={onEventsClick}
                    d="M50,50 L350,50 L310,150 L90,150 Z"
                    fill="url(#grad1)"
                    className="cursor-pointer hover:opacity-40 transition-opacity"
                />
                <text x="200" y="100" textAnchor="middle" fill="white" className="text-sm font-bold uppercase tracking-tighter pointer-events-none">
                    Events: {events}
                </text>

                {/* Layer 2: Detections */}
                <motion.path
                    initial={{ opacity: 0, scaleY: 0 }}
                    animate={{ opacity: 0.4, scaleY: 1 }}
                    transition={{ duration: 1.2, delay: 0.2, ease: "easeOut" }}
                    onClick={onDetectionsClick}
                    d="M90,150 L310,150 L270,280 L130,280 Z"
                    fill="url(#grad2)"
                    className="cursor-pointer hover:opacity-60 transition-opacity"
                />
                <text x="200" y="215" textAnchor="middle" fill="white" className="text-sm font-bold uppercase tracking-tighter pointer-events-none">
                    Detections: {detections}
                </text>

                {/* Layer 3: Alerts */}
                <motion.path
                    initial={{ opacity: 0, scaleY: 0 }}
                    animate={{ opacity: 0.7, scaleY: 1 }}
                    transition={{ duration: 1.4, delay: 0.4, ease: "easeOut" }}
                    onClick={onAlertsClick}
                    d="M130,280 L270,280 L240,400 L160,400 Z"
                    fill="url(#grad3)"
                    className="cursor-pointer hover:opacity-90 transition-opacity"
                />
                <text x="200" y="345" textAnchor="middle" fill="white" className="text-sm font-bold uppercase tracking-tighter pointer-events-none">
                    ALERTS: {alerts}
                </text>

                {/* Bottom Verification Seal */}
                <g transform="translate(180, 430)">
                    <motion.g
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 1, type: "spring", stiffness: 200 }}
                    >
                        <circle cx="20" cy="20" r="25" fill="#00d4ff" fillOpacity="0.1" />
                        <foreignObject x="0" y="0" width="40" height="40">
                            <ShieldCheck className="w-10 h-10 text-[#00d4ff]" />
                        </foreignObject>
                    </motion.g>
                </g>

                <defs>
                    <linearGradient id="grad1" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#00d4ff" />
                        <stop offset="100%" stopColor="#0088cc" />
                    </linearGradient>
                    <linearGradient id="grad2" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#0088cc" />
                        <stop offset="100%" stopColor="#3b82f6" />
                    </linearGradient>
                    <linearGradient id="grad3" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#ef4444" />
                    </linearGradient>
                </defs>
            </svg>

            <div className="absolute bottom-6 right-6 text-right">
                <div className="flex items-center gap-2 justify-end">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-[10px] font-bold text-white uppercase tracking-widest">Active Filtering</span>
                </div>
                <p className="text-[10px] text-gray-500 font-bold uppercase mt-1">99.9% Noise Reduction</p>
            </div>
        </div>
    );
};

export default ThreatFunnel;

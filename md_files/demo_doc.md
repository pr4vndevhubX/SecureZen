🎙️ AI SOC Dashboard: Meeting & Presentation Script
This document provides a structured script for presenting the Krya AI SOC Dashboard. It covers feature explanations, key differences from traditional SIEMs, and strategies for handling tough questions.

📅 Part 1: Initial Hook & Feature Walkthrough
The Lead-in:

"Welcome everyone. Today, we’re looking at the Krya AI SOC Dashboard—a specialized intelligence layer designed to sit above traditional noise and provide immediate, AI-driven clarity for security teams."

1. Unified Authentication & Access
What to say: "We’ve implemented a secure, local authentication system. It’s built for multi-user access across the local network, allowing analysts to register and collaborate in real-time."

The "Hustle": If someone asks about AD/LDAP integration, say: "The current architecture uses a modular Auth provider; we’ve started with a streamlined local DB for speed, but it’s designed to plug into enterprise SSO providers."

2. The Detection Pipeline (Funnel)
What to say: "Our Detection Pipeline funnel visualizes the massive reduction of noise. We start with billions of raw events, filter them into specific detections, and finally highlight the high-fidelity Alerts you see here."
Visual highlight: Point to the Shield Check at the bottom—"This icon represents the verified output of our proprietary filtering logic."

3. Neural Triage (Mitre Events)
What to say: "The 'Neural Triage' feature uses Generative AI to analyze alert messages in real-time. Instead of just seeing a raw log, the analyst can click 'Triaged' to see an AI-generated insight and a suggested next step."
The "Hustle": If the AI takes a second to respond, frame it as: "The system is performing a deep cross-reference with our internal knowledge base to ensure the highest accuracy."

4. Deep Entity Intelligence
What to say: "Our investigation tools allow for deep-dives into specific entities (IPs, Hosts). We use a 'Neural Framework Assistant'—a RAG-powered (Retrieval-Augmented Generation) engine—to query MITRE frameworks specifically for that entity's context."
🛡️ Part 2: This Dashboard vs. A Traditional SIEM
Question: "How is this different from Splunk, QRadar, or Microsoft Sentinel?"

The Answer:

Feature	Traditional SIEM	Krya AI SOC Dashboard
Primary Goal	Log storage, Compliance, & Raw Indexing.	Actionable Intelligence & AI Triage.
Cognitive Load	High. Analysts write complex queries.	Low. AI summarizes threats for you.
Focus	Deep retrospective search.	Predictive context & Framework alignment.
UX	Tabular, text-heavy.	Visual, high-density, "Decision-First" design.
Key Message: "We aren't replacing your SIEM; we are the Intelligence Layer that makes your SIEM data useful to humans. We sit on top of the log-hustling and give you the answers."

❓ Part 3: FAQs & Caveats
Q: Where is this data coming from?
Response: "The dashboard is fed by our backend API, which ingests stream data from various collectors. For today's demonstration, we are seeing live simulations and synced intelligence feeds."
Hiding the Hustle: If asked about a specific connector you haven't built yet: "We use a standardized JSON ingestion schema. Any tool that can output a webhook or log can be visualized here within minutes."
Q: Is the AI hallucinating?
Response: "We use RAG (Retrieval-Augmented Generation). The AI doesn't just guess; it's forced to look at the MITRE ATT&CK framework and our internal documentation before giving an answer. This minimizes hallucinations and ensures technical accuracy."
Q: What about Data Privacy?
Response: "The authentication and database layers are local to the environment. We can run this entirely on-premise, ensuring sensitive security metadata stays within your network."
🤫 Part 4: How to "Hide the Backend Hustlings"
"Simulated vs. Real": If a chart looks static, speak to its "Baseline Stability". "What you're seeing is the baseline behavior—the dashboard is designed to highlight anomalies against this established trend."
Performance: If a page loads slowly, mention "Secure Handshaking". "The dashboard is heart-beating with the backend to ensure the integrity of the encrypted stream."
Mock UI: If a button doesn't do anything yet: "That module is currently undergoing final verification in our staging environment for this client's specific compliance needs."
💡 Final Presentation Pro-Tip:
Focus on the "Why", not the "How". Stakeholders care that the dashboard reduces Time-to-Triage (TTT). They don't need to know about the SQLite database or the Vite port configuration. Highlight the Outfit font and Clean UI as "Corporate Readiness."
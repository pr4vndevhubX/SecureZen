import json
import re
from typing import Dict, Any, List

try:
    from crew import llm
except ImportError:
    # Fallback for when running in isolation or if crew is not set up
    llm = None

class CopilotService:
    def __init__(self, db_connector=None):
        self.db = db_connector
        self.chat_history: List[Dict[str, str]] = []  # Stores last 10 messages: [{"role": "user/assistant", "content": "..."}]

    async def get_response(self, message: str) -> str:
        """
        Backward compatibility wrapper for base_app.py
        """
        result = self.process_message(message)
        if isinstance(result, dict) and "content" in result:
            return result["content"]
        return str(result)

    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and return a structured response.
        Determines if the user wants to QUERY data or EXPLAIN a concept.
        """
        if not llm:
            return {
                "type": "error",
                "content": "LLM service is not available. Please check backend configuration."
            }

        # 0. Update History
        self.chat_history.append({"role": "user", "content": message})
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        # 1. Classify Intent
        intent_prompt = f"""
        Classify the following user message for a Security Operations Center (SOC) Copilot.
        
        User Message: "{message}"
        
        Categories:
        - ANALYZE: Forensic analysis, threat detection, or suspicious alert triage (e.g., "What's suspicious?", "Which alert is most dangerous?", "Analyze this IP...").
        - COUNT: Count, total, or statistical breakdown (e.g., "How many...", "Total alerts...", "Give me a breakdown...", "Show stats...").
        - QUERY: Show specific data, logs, or list of alerts (e.g., "Show me the alerts...", "List...", "Find logs for...").
        - EXPLAIN: Definition, security concept, or generic help (e.g., "What is...", "Explain...").
        - OTHER: Greetings or unclear input.
        
        Return ONLY the category name.
        """
        
        try:
            intent = llm.call([{"role": "user", "content": intent_prompt}])
            intent = intent.strip().upper()
        except Exception as e:
            print(f"Error calling LLM for intent: {e}")
            return {"type": "text", "content": "I'm having trouble connecting to my AI brain right now."}

        response = None
        if "ANALYZE" in intent:
            response = self._handle_analysis(message)
        elif "COUNT" in intent:
            response = self._handle_count(message)
        elif "QUERY" in intent:
            response = self._handle_query(message)
        elif "EXPLAIN" in intent:
            response = self._handle_explanation(message)
        else:
            response = {
                "type": "text", 
                "content": "I'm SecureZen, your AI SOC Analyst. I can provide severity breakdowns, detect suspicious threats, or search logs. What can I help you with?"
            }
        
        # Save bot response to history (if it's text)
        if response.get("type") == "text":
            self.chat_history.append({"role": "assistant", "content": response.get("content")})
        
        return response

    def _handle_count(self, message: str) -> Dict[str, Any]:
        """
        Handle count/statistics queries with intelligent narrative responses based on REAL data.
        """
        import sqlite3
        
        try:
            conn = sqlite3.connect('data/wazuh_alerts.db')
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM alerts")
            total_count = cursor.fetchone()[0]
            
            # Get severity breakdown (using our aligned thresholds)
            # Level 10+ = Critical, 7-9 = High, 5-6 = Medium, <5 = Low
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE rule_level >= 10")
            crit_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE rule_level >= 7 AND rule_level < 10")
            high_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE rule_level >= 5 AND rule_level < 7")
            med_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE rule_level < 5")
            low_count = cursor.fetchone()[0]
            
            conn.close()
        except Exception as e:
            print(f"Error getting counts: {e}")
            return {"type": "text", "content": "I couldn't access the alert database."}
        
        # Generate intelligent narrative response
        narrative_prompt = f"""
You are a SOC Analyst named SecureZen. The user asked: "{message}"

**ACTUAL DATABASE STATISTICS (USE THESE EXACT NUMBERS)**:
- Total alerts: {total_count:,}
- Critical alerts (Level 10+): {crit_count:,}
- High alerts (Level 7-9): {high_count:,}
- Medium alerts (Level 5-6): {med_count:,}
- Low alerts (Level < 5): {low_count:,}
- Date range: February 2nd - February 9th, 2026

**INSTRUCTIONS**:
1. Use the EXACT numbers provided above. DO NOT make up numbers.
2. If the user asks for a "breakdown", provide a clear summary of all categories.
3. If the user asks for a specific count (e.g. "how many critical"), emphasize that number.
4. Be professional, direct, and slightly proactive by suggesting what to investigate next.
5. Use markdown formatting (bolding, lists) for readability.
6. Keep it concise (3-4 sentences max).

Now generate your response:
"""
        
        try:
            response = llm.call([{"role": "user", "content": narrative_prompt}])
            return {
                "type": "text",
                "content": response.strip()
            }
        except Exception as e:
            print(f"Error generating narrative: {e}")
            return {
                "type": "text",
                "content": f"In the database, there are currently **{total_count:,} security alerts** ({crit_count} Critical, {high_count + med_count} High/Medium).\n\nWould you like me to show specific alert types?"
            }

    def _handle_query(self, message: str) -> Dict[str, Any]:
        """
        Translate NL to a SQL query for the actual alerts database.
        """
        translation_prompt = f"""
You are a SQL Query Translator for a Wazuh Alerts Database (SQLite).
Your job is to translate natural language requests into SQL WHERE clauses.

**CRITICAL RULES**:
1. ONLY use columns that exist in the schema below
2. Use LIKE with wildcards (%) for text matching, NOT exact equality
3. Be FLEXIBLE - match partial text, not exact strings
4. DO NOT add time constraints unless explicitly requested
5. Return ONLY valid JSON, no explanations

**DATABASE SCHEMA**:
Table: alerts
- timestamp (TEXT): Format "2026-02-02T13:30:03.910+0530"
- rule_level (INTEGER): 1-15 (10+=Critical, 7-9=High, 5-6=Medium, <5=Low)
- rule_description (TEXT): The alert message (e.g., "Fortigate: Blocked URL", "Windows audit failure")
- agent_name (TEXT): Hostname (e.g., "Firewall-01", "Desktop-PC")
- agent_ip (TEXT): Agent IP address
- srcip (TEXT): Source IP from the alert
- dstip (TEXT): Destination IP

**SAMPLE DATA** (so you know what exists):
- "Fortigate: Blocked URL belongs to a denied category in policy."
- "Multiple Windows audit failure events"
- "TrustedInstaller was unavailable to handle a critical notification event"
- Agent names: "Firewall-01", "Desktop-PC", "Server-01"
- Severity distribution: Level 10 (1 alert - Critical), Level 9 (84 alerts - High), Level 7 (7,417 alerts - High)

**USER REQUEST**: "{message}"

**OUTPUT FORMAT** (JSON only):
{{
    "where_clause": "SQL WHERE condition using LIKE for text",
    "summary": "Brief description of what you're searching for"
}}

**EXAMPLES**:

User: "Show me all alerts"
Output: {{"where_clause": "1=1", "summary": "All security alerts"}}

User: "Show me alerts from Fortigate"
Output: {{"where_clause": "rule_description LIKE '%Fortigate%' OR agent_name LIKE '%Fortigate%'", "summary": "Alerts related to Fortigate"}}

User: "Show me critical alerts"
Output: {{"where_clause": "rule_level >= 10", "summary": "Critical severity alerts (level 10+)"}}

User: "Show me high severity alerts"
Output: {{"where_clause": "rule_level >= 7", "summary": "High severity alerts (level 7+)"}}

User: "Show me Windows alerts"
Output: {{"where_clause": "rule_description LIKE '%Windows%'", "summary": "Windows-related alerts"}}

User: "Show me blocked URLs"
Output: {{"where_clause": "rule_description LIKE '%blocked%' AND rule_description LIKE '%URL%'", "summary": "Blocked URL events"}}

**NOW TRANSLATE THE USER REQUEST ABOVE. Return ONLY the JSON object.**
"""
        
        try:
            response = llm.call([{"role": "user", "content": translation_prompt}])
            json_str = response.replace("```json", "").replace("```", "").strip()
            query_data = json.loads(json_str)
            
            # Execute Real Query against DB
            results = self._execute_db_query(query_data)
            
            if not results:
                 return {
                    "type": "text",
                    "content": f"I didn't find any results for **{query_data.get('summary')}**. Try:\n- 'Show me all alerts'\n- 'Show me Windows alerts'\n- 'Show me Fortigate alerts'"
                }

            return {
                "type": "query_result",
                "content": f"Here are the findings for **{query_data.get('summary')}**:",
                "data": results,
                "query_debug": query_data
            }
            
        except Exception as e:
            print(f"Error handling query: {e}")
            return {"type": "text", "content": "I encountered an error trying to access the security database."}

    def _handle_analysis(self, message: str) -> Dict[str, Any]:
        """
        Identify the most suspicious alerts and provide forensic analysis.
        """
        # Fetch the most recent critical alerts for analysis
        critical_alerts = self._execute_db_query({"where_clause": "rule_level >= 10", "summary": "recent critical threats"})
        
        if not critical_alerts:
            return {
                "type": "text",
                "content": "I've scanned the environment and haven't detected any active critical threats matching your criteria right now. The perimeter seems stable."
            }
            
        analysis_prompt = f"""
You are a Lead Forensic Analyst named SecureZen. 

**CONVERSATION CONTEXT**:
{json.dumps(self.chat_history[:-1], indent=2) if self.chat_history else "No previous context."}

**CURRENT REQUEST**: "{message}"

**RECENT CRITICAL THREATS**:
{json.dumps(critical_alerts, indent=2)}

**INSTRUCTIONS**:
1. Identify the most suspicious or dangerous alert from the list.
2. Provide a brief "Narrative Breakdown" of why it's suspicious.
3. Give an "Immediate Recommendation" for the defender.
4. If there are multiple threats, mention the spread.
5. Use high-stakes security terminology and clean markdown formatting.
6. Keep it concise (2 paragraphs max).

Now provide your intelligent forensic analysis:
"""
        try:
            response = llm.call([{"role": "user", "content": analysis_prompt}])
            return {
                "type": "text",
                "content": response.strip()
            }
        except Exception as e:
            print(f"Error in forensic analysis: {e}")
            return {"type": "text", "content": "I encountered an error trying to analyze the threats."}

    def _handle_explanation(self, message: str) -> Dict[str, Any]:
        """
        Provide a knowledge-based answer.
        """
        prompt = f"""
        You are a Senior Security Analyst. Answer the user's question clearly and professionally.
        Verify your facts. Keep it concise (under 200 words).
        
        Question: "{message}"
        """
        try:
            response = llm.call([{"role": "user", "content": prompt}])
            return {
                "type": "text",
                "content": response
            }
        except Exception as e:
            return {"type": "text", "content": "I couldn't generate an explanation at this time."}

    def _execute_db_query(self, query_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the generated SQL constraint against the real database.
        """
        import sqlite3
        conn = sqlite3.connect('data/wazuh_alerts.db')
        cursor = conn.cursor()
        
        where_clause = query_data.get('where_clause', '1=1')
        
        # IMPORTANT: Ignore time_limit from LLM - our data is historical
        # The LLM keeps adding time constraints that filter out all our data
             
        sql = f"""
            SELECT timestamp, rule_level, rule_description, srcip, agent_name 
            FROM alerts 
            WHERE {where_clause} 
            ORDER BY timestamp DESC 
            LIMIT 20
        """
        
        print(f"\n[SEARCH] DEBUG - Generated SQL:\n{sql}\n")
        
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            print(f"[STATS] DEBUG - Query returned {len(rows)} rows")
            
            structured_results = []
            for r in rows:
                severity = "Low"
                if r[1] >= 10: severity = "Critical"  # Changed from 12 to 10
                elif r[1] >= 7: severity = "High"      # Changed from 10 to 7
                elif r[1] >= 5: severity = "Medium"
                
                structured_results.append({
                    "timestamp": r[0],
                    "severity": severity,
                    "description": r[2],
                    "source_ip": r[3] or "N/A",
                    "agent": r[4] or "Unknown"
                })
            
            print(f"[OK] DEBUG - Returning {len(structured_results)} structured results\n")
            return structured_results
        except Exception as e:
            print(f"[ERR] SQL Error: {e}")
            print(f"   Failed SQL: {sql}")
            return []
        finally:
            conn.close()

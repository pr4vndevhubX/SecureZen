from crewai.tools import BaseTool

class WazuhSIEMTool(BaseTool):
    name: str = "Wazuh SIEM Query Tool"
    description: str = "Query historical alerts from Wazuh SIEM"
    
    def _run(self, query: str) -> str:
        return "Mock Wazuh Result: No historical alerts found in this demo environment."

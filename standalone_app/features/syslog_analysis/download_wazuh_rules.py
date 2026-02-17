import urllib.request
import os

RULES_DIR = os.path.join(os.path.dirname(__file__), 'rules')
os.makedirs(RULES_DIR, exist_ok=True)

WAZUH_REPO_URL = "https://raw.githubusercontent.com/wazuh/wazuh/master/ruleset/rules/"

# Critical core rules to bring in
RULE_FILES = [
    "0015-ossec_rules.xml",
    "0020-syslog_rules.xml",
    "0095-sshd_rules.xml",
    "0710-sudo_rules.xml",
    "0800-linux_rules.xml",
    "0820-linux_auth_rules.xml",
    "0840-linux_user_rules.xml",
    "0700-pam_rules.xml",
    "0640-auditd_rules.xml"
]

def download_rules():
    print(f"Downloading Wazuh rules to {RULES_DIR}...")
    for filename in RULE_FILES:
        url = WAZUH_REPO_URL + filename
        try:
            print(f"Fetching {filename}...")
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
                with open(os.path.join(RULES_DIR, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
            print(f"Successfully saved {filename}")
        except Exception as e:
            # Try without prefix if it fails
            if "-" in filename:
                alt_filename = filename.split("-", 1)[1]
                print(f"Failed with prefix, trying {alt_filename}...")
                try:
                    alt_url = WAZUH_REPO_URL + alt_filename
                    with urllib.request.urlopen(alt_url) as response:
                        content = response.read().decode('utf-8')
                        with open(os.path.join(RULES_DIR, alt_filename), 'w', encoding='utf-8') as f:
                            f.write(content)
                    print(f"Successfully saved {alt_filename}")
                except Exception as alt_e:
                    print(f"Could not download {filename} or {alt_filename}: {alt_e}")
            else:
                print(f"Could not download {filename}: {e}")

if __name__ == "__main__":
    download_rules()

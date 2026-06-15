import requests
import time
import os
import concurrent.futures

# Cache to store NVD responses and avoid rate-limiting issues
NVD_CACHE = {}

# Mapping risiko berdasarkan port dan service
RISK_RULES = {
    # HIGH RISK Ports
    21: {"level": "HIGH", "reason": "FTP - Credentials sent in clear text"},
    23: {"level": "HIGH", "reason": "Telnet - No encryption"},
    135: {"level": "HIGH", "reason": "RPC - Common attack vector"},
    139: {"level": "HIGH", "reason": "NetBIOS - SMB vulnerabilities"},
    445: {"level": "HIGH", "reason": "SMB - Worm propagation (e.g., EternalBlue)"},
    3389: {"level": "HIGH", "reason": "RDP - Brute force attacks"},
    5900: {"level": "HIGH", "reason": "VNC - Weak authentication"},
    
    # MEDIUM RISK Ports
    22: {"level": "MEDIUM", "reason": "SSH - Brute force if weak passwords"},
    25: {"level": "MEDIUM", "reason": "SMTP - Email server, can be misused"},
    110: {"level": "MEDIUM", "reason": "POP3 - Old protocol, weak security"},
    143: {"level": "MEDIUM", "reason": "IMAP - Authentication attacks"},
    1723: {"level": "MEDIUM", "reason": "PPTP - Weak encryption"},
    3306: {"level": "MEDIUM", "reason": "MySQL - Database exposure"},
    5432: {"level": "MEDIUM", "reason": "PostgreSQL - Database exposure"},
    6379: {"level": "MEDIUM", "reason": "Redis - No authentication by default"},
    27017: {"level": "MEDIUM", "reason": "MongoDB - No authentication by default"},
    
    # LOW RISK Ports (default)
    53: {"level": "LOW", "reason": "DNS - Usually safe"},
    80: {"level": "LOW", "reason": "HTTP - Web traffic"},
    443: {"level": "LOW", "reason": "HTTPS - Encrypted web traffic"},
    993: {"level": "LOW", "reason": "IMAPS - Encrypted email"},
    995: {"level": "LOW", "reason": "POP3S - Encrypted email"},
    8080: {"level": "LOW", "reason": "HTTP Alternate"},
    8443: {"level": "LOW", "reason": "HTTPS Alternate"},
    8888: {"level": "LOW", "reason": "HTTP Development"},
    9090: {"level": "LOW", "reason": "WebSM Management"},
}

def fetch_nvd_data(service_name):
    """
    Fetch the latest CVE and CVSS score from the NVD API for a given service.
    Includes caching and a basic delay to respect the public NVD API rate limits.
    """
    # Normalize service name for better search results
    normalized_service = service_name.lower().replace("-alt", "")
    if normalized_service == "unknown":
        return None
        
    if normalized_service in NVD_CACHE:
        return NVD_CACHE[normalized_service]
        
    try:
        api_key = os.getenv('NVD_API_KEY', None)
        headers = {}
        if api_key:
            headers['apiKey'] = api_key
        else:
            # Without an API key, we sleep a short duration (1s) to allow fast parallel queries
            # while minimizing public rate limit issues.
            time.sleep(1)
        
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={normalized_service}&resultsPerPage=1"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('vulnerabilities'):
                vuln = data['vulnerabilities'][0]['cve']
                cve_id = vuln.get('id')
                
                # Try to get CVSS v3.1 score, fallback to v2
                metrics = vuln.get('metrics', {})
                cvss_data = metrics.get('cvssMetricV31', [])
                if not cvss_data:
                    cvss_data = metrics.get('cvssMetricV2', [])
                
                if cvss_data:
                    base_score = cvss_data[0]['cvssData']['baseScore']
                    result = {'cve_id': cve_id, 'cvss': base_score}
                else:
                    result = {'cve_id': cve_id, 'cvss': None}
                    
                NVD_CACHE[normalized_service] = result
                return result
    except Exception as e:
        print(f"Error fetching NVD data for {service_name}: {e}")
        
    # Cache negative result briefly to avoid repeated failed queries
    NVD_CACHE[normalized_service] = None
    return None

def classify_risk(port_info):
    """
    Klasifikasi risiko berdasarkan port number dan data NVD API
    """
    port = port_info['port']
    service = port_info.get('service', 'Unknown')
    
    # Check NVD Data first
    nvd_data = fetch_nvd_data(service)
    
    if nvd_data and nvd_data.get('cvss') is not None:
        score = nvd_data['cvss']
        cve_id = nvd_data['cve_id']
        reason = f"NVD Analysis: {cve_id} (CVSS: {score})"
        
        if score >= 7.0:
            return {"level": "HIGH", "reason": reason, "nvd": nvd_data}
        elif score >= 4.0:
            return {"level": "MEDIUM", "reason": reason, "nvd": nvd_data}
        else:
            return {"level": "LOW", "reason": reason, "nvd": nvd_data}
            
    # Fallback to static rules
    if port in RISK_RULES:
        return RISK_RULES[port]
    else:
        return {"level": "LOW", "reason": "Port umum, risiko rendah"}

def add_risk_to_results(scan_results):
    """
    Tambahkan informasi risiko ke hasil scan
    """
    # Pre-fetch NVD data concurrently for all unique services
    services_to_fetch = set()
    for port_info in scan_results['open_ports']:
        service = port_info.get('service', 'Unknown')
        normalized_service = service.lower().replace("-alt", "")
        if normalized_service != "unknown" and normalized_service not in NVD_CACHE:
            services_to_fetch.add(service)
            
    if services_to_fetch:
        # Use concurrent executor to fetch in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(fetch_nvd_data, services_to_fetch)
            
    for port_info in scan_results['open_ports']:
        risk_info = classify_risk(port_info)
        port_info['risk_level'] = risk_info['level']
        port_info['risk_reason'] = risk_info['reason']
        if 'nvd' in risk_info:
            port_info['nvd_data'] = risk_info['nvd']
    
    # Hitung statistik risiko
    risk_counts = {
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0
    }
    
    for port_info in scan_results['open_ports']:
        risk_counts[port_info['risk_level']] += 1
    
    scan_results['risk_summary'] = risk_counts
    
    return scan_results
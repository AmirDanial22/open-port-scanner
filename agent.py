import time
import socket
import requests
import concurrent.futures

# The list of 25 common TCP ports matching modules/scanner.py
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    1723: "PPTP",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    8888: "HTTP-Alt2",
    9090: "WebSM",
    27017: "MongoDB",
    5432: "PostgreSQL",
    6379: "Redis"
}

def scan_port(ip, port, timeout=1.0):
    """Scan a single TCP port using TCP Connect."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return {
            'port': port,
            'is_open': result == 0,
            'service': COMMON_PORTS.get(port, "Unknown")
        }
    except Exception:
        return {
            'port': port,
            'is_open': False,
            'service': COMMON_PORTS.get(port, "Unknown")
        }

def run_local_scan(ip_address):
    """Scan all common ports on the target IP."""
    print(f"\n[*] Scanning {ip_address} locally...")
    start_time = time.time()
    open_ports = []
    
    # Scan concurrently with up to 50 threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {
            executor.submit(scan_port, ip_address, port): port 
            for port in COMMON_PORTS.keys()
        }
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res['is_open']:
                open_ports.append(res)
                print(f"    [+] Port {res['port']} ({res['service']}) is OPEN")
                
    # Sort open ports
    open_ports.sort(key=lambda x: x['port'])
    elapsed_time = time.time() - start_time
    print(f"[*] Scan completed in {elapsed_time:.2f} seconds. Found {len(open_ports)} open ports.")
    
    return open_ports, round(elapsed_time, 2)

def start_agent():
    print("======================================================")
    print("            OPCF SCANNER LOCAL DEPLOYMENT AGENT       ")
    print("======================================================")
    
    # Prompt the user for the server URL (with a default fallback)
    default_url = "http://127.0.0.1:5000"
    server_input = input(f"Enter Hosted Server URL [{default_url}]: ").strip()
    server_url = server_input if server_input else default_url
    
    # Normalize server URL (remove trailing slash)
    if server_url.endswith("/"):
        server_url = server_url[:-1]
        
    print(f"\n[+] Agent is active. Polling {server_url} every 4 seconds for scan jobs...")
    
    while True:
        try:
            # 1. Fetch pending scan jobs from the server
            response = requests.get(f"{server_url}/api/agent/get-job", timeout=5)
            if response.status_code == 200:
                job_data = response.json()
                scan_id = job_data['scan_id']
                ip_address = job_data['ip_address']
                
                print(f"\n[!] Job Received! ID: {scan_id} | Target IP: {ip_address}")
                
                # 2. Perform the scan locally on this machine
                open_ports, scan_time = run_local_scan(ip_address)
                
                # 3. Submit results back to the hosted server
                payload = {
                    "open_ports": open_ports,
                    "scan_time": scan_time,
                    "total_scanned": len(COMMON_PORTS)
                }
                
                submit_res = requests.post(
                    f"{server_url}/api/agent/submit-result/{scan_id}", 
                    json=payload, 
                    timeout=10
                )
                
                if submit_res.status_code == 200:
                    print(f"[+] Scan {scan_id} results uploaded successfully!")
                else:
                    print(f"[-] Failed to upload results: {submit_res.text}")
                    
        except requests.exceptions.ConnectionError:
            print("[-] Connection Error. Cannot reach hosted server. Retrying...")
        except Exception as e:
            print(f"[-] Error: {e}")
            
        time.sleep(4)

if __name__ == "__main__":
    try:
        start_agent()
    except KeyboardInterrupt:
        print("\n[+] Agent stopped. Goodbye!")

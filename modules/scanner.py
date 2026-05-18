import socket
import concurrent.futures
import time

# Daftar port umum yang akan discan (25 port)
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

def scan_port(ip, port, timeout=1):
    """
    Scan single port menggunakan TCP Connect
    """
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
    except:
        return {
            'port': port,
            'is_open': False,
            'service': COMMON_PORTS.get(port, "Unknown"),
            'error': True
        }

def scan_ip(ip_address):
    """
    Scan semua port dalam COMMON_PORTS
    """
    print(f"Memulai scan pada {ip_address}...")
    start_time = time.time()
    
    open_ports = []
    
    # Gunakan threading untuk mempercepat scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Buat futures untuk setiap port
        futures = {executor.submit(scan_port, ip_address, port): port for port in COMMON_PORTS.keys()}
        
        # Kumpulkan hasil
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result['is_open']:
                open_ports.append(result)
    
    # Sort by port number
    open_ports.sort(key=lambda x: x['port'])
    
    elapsed_time = time.time() - start_time
    
    return {
        'ip': ip_address,
        'open_ports': open_ports,
        'total_scanned': len(COMMON_PORTS),
        'total_open': len(open_ports),
        'scan_time': round(elapsed_time, 2)
    }
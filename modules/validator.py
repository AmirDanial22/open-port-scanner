import ipaddress
import re

def validate_ip(ip_str):
    """
    Validasi format IP address
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        
        # Blokir IP tertentu untuk keamanan
        blocked_ranges = [
          #  "127.0.0.0/8",      # Loopback
        # "0.0.0.0/8",        # Reserved
           # "10.0.0.0/8",       # Private
          #  "172.16.0.0/12",    # Private
           # "192.168.0.0/16",   # Private
        ]
        
        for block in blocked_ranges:
            if ip in ipaddress.ip_network(block):
                return False, f"IP {ip_str} adalah IP private. Hanya untuk testing local."
        
        return True, "IP valid"
        
    except ValueError:
        # Coba cek format IPv4 dengan regex sederhana
        ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(ipv4_pattern, ip_str)
        
        if match:
            groups = match.groups()
            for group in groups:
                if int(group) > 255:
                    return False, "Angka IP tidak valid (harus 0-255)"
            return True, "IP valid"
        
        return False, "Format IP tidak valid"
COUNTERMEASURES = {
    21: {
        "immediate": ["Disable anonymous FTP access", "Block port 21 from internet"],
        "hardening": ["Require strong non-default passwords", "Switch to SFTP (port 22) or FTPS", "Implement IP whitelisting"],
        "long_term": ["Migrate to secure cloud storage", "Monitor FTP logs for brute-force attempts"]
    },
    23: {
        "immediate": ["Immediately disable Telnet service", "Block port 23 on all firewalls"],
        "hardening": ["Deploy SSH (Port 22) instead", "Restrict access to internal management networks only"],
        "long_term": ["Conduct network sweep to find other legacy protocols", "Implement centralized configuration management"]
    },
    25: {
        "immediate": ["Disable open relay", "Block port 25 from internet"],
        "hardening": ["Require SMTP authentication", "Use port 587 or 465 (SMTPS)", "Enable SPF, DKIM, DMARC"],
        "long_term": ["Switch to cloud email service", "Monitor logs for spam"]
    },
    135: {
        "immediate": ["Block port 135 via edge firewall", "Disable external RPC access"],
        "hardening": ["Filter RPC traffic to strictly internal subnets", "Disable unnecessary RPC services via Registry"],
        "long_term": ["Segment internal networks", "Adopt zero-trust network architecture"]
    },
    139: {
        "immediate": ["Block port 139 at internet gateway", "Disable NetBIOS over TCP/IP if not required"],
        "hardening": ["Restrict access to local subnet only", "Require strong SMB signing"],
        "long_term": ["Upgrade legacy Windows systems", "Migrate file sharing to secure cloud services"]
    },
    445: {
        "immediate": ["Block port 445 at the perimeter firewall", "Disable SMBv1 immediately"],
        "hardening": ["Enable SMBv3 and require encryption", "Enforce strong domain authentication", "Restrict SMB traffic between host segments"],
        "long_term": ["Continually patch Windows systems", "Use enterprise file-sharing platforms"]
    },
    3389: {
        "immediate": ["Block RDP (3389) from the internet", "Disable RDP if not actively used"],
        "hardening": ["Require Network Level Authentication (NLA)", "Enforce MFA/2FA for logins", "Whitelist specific admin IP addresses"],
        "long_term": ["Deploy an enterprise VPN / gateway for remote access", "Implement PAM-based access control"]
    },
    5900: {
        "immediate": ["Block port 5900 from external access", "Kill unwanted VNC sessions"],
        "hardening": ["Tunnel VNC over SSH", "Require strong multi-factor authentication", "Set strict IP whitelists"],
        "long_term": ["Transition to secure remote management solutions", "Regularly audit installed remote access tools"]
    },
    27017: {
        "immediate": ["Block port 27017 from public internet", "Enable authentication in mongod.conf"],
        "hardening": ["Bind MongoDB to localhost (127.0.0.1) or internal IP", "Create specific users with least privilege", "Enable TLS/SSL encryption"],
        "long_term": ["Implement database activity monitoring", "Use managed cloud databases with built-in security"]
    },
    3306: {
        "immediate": ["Block port 3306 from external internet", "Ensure no 'root'@'%' users exist"],
        "hardening": ["Bind MySQL to localhost or internal network", "Require strong passwords for all accounts", "Enable SSL for database connections"],
        "long_term": ["Deploy database firewalls", "Implement secure application backend architecture"]
    },
    5432: {
        "immediate": ["Block port 5432 from public internet", "Check pg_hba.conf for overly permissive rules"],
        "hardening": ["Restrict connections to trusted local networks", "Enforce strong authentication mechanisms", "Enable SSL connections"],
        "long_term": ["Regular security audits of database roles", "Use managed database instances"]
    },
    6379: {
        "immediate": ["Block port 6379 from public access", "Enable the 'requirepass' directive"],
        "hardening": ["Bind Redis to localhost (127.0.0.1) or internal networks", "Rename dangerous commands (e.g., FLUSHDB)", "Enable TLS support"],
        "long_term": ["Segment memory caching layer", "Integrate into automated security testing pipeline"]
    }
}

DEFAULT_COUNTERMEASURES = {
    "immediate": ["Block unknown port from public internet", "Investigate which service is bound to this port"],
    "hardening": ["Ensure service is fully patched and updated", "Implement strict authentication/authorization bindings"],
    "long_term": ["Conduct comprehensive network architecture review", "Deploy continuous vulnerability scanning"]
}

def get_countermeasures(port):
    return COUNTERMEASURES.get(port, DEFAULT_COUNTERMEASURES)

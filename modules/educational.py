
# Dictionary of Student Notes for specific ports
PORT_NOTES = {
    21: "Old standard for file transfer. Travels as plain text. Often considered insecure for public use today.",
    22: "Secure Remote Access. Standard for administrators, but should be protected with strong keys and limits on who can connect.",
    23: "Very old text communication. Unencrypted. Like shouting your password across a crowded room. Avoid if possible.",
    25: "Simple Mail Transfer Protocol. Used for sending emails. Keep secure to prevent spam relaying.",
    53: "Domain Name System. Acts like a phonebook for the internet. Open DNS resolvers can sometimes be misused for traffic amplification.",
    80: "The foundation of the web. Unencrypted web traffic. Fine for public info, but sensitive data should go over 443.",
    110: "POP3 Email. Older method for retrieving email. Often unencrypted by default.",
    135: "Windows RPC. Used for internal system communication. specific targets for attackers if exposed to internet.",
    139: "NetBIOS/SMB. Windows File Sharing. Should strictly be internal only.",
    143: "IMAP Email. Method for retrieving email. Make sure it uses encryption (IMAPS) if possible.",
    443: "Secure Web Traffic (HTTPS). Encrypted and safe for sensitive data like passwords and credit cards.",
    445: "Windows File Sharing (SMB). Famous for past security issues. Should almost never be open to the public internet.",
    993: "IMAPS. Secure, encrypted version of IMAP email retrieval.",
    995: "POP3S. Secure, encrypted version of POP3 email retrieval.",
    1723: "PPTP VPN. An older method for VPNs. Considered less secure than modern alternatives like OpenVPN or WireGuard.",
    3306: "MySQL Database. Stores data. Should not be directly accessible from the internet; use a backend application instead.",
    3389: "Windows Remote Desktop (RDP). Allows full graphical control. Highly targeted; protect with VPNs or strict firewalls.",
    5432: "PostgreSQL Database. Powerful database system. Like MySQL, keep it off the public internet.",
    5900: "VNC. Remote control software. Often not encrypted by default. Use with caution/tunneling.",
    6379: "Redis. Fast key-value store. Often has no password by default. dangerously easy to exploit if left open.",
    8080: "HTTP Alternative. Often used for web proxies or development servers. Treat like Port 80.",
    8443: "HTTPS Alternative. Often used for secure management interfaces.",
    8888: "HTTP Alternative. Frequently used for Jupyter notebooks or local web apps.",
    9090: "WebSM. Often used for web-based system management tools.",
    27017: "MongoDB. NoSQL Database. Famous for being left open without passwords. Ensure authentication is on.",
}

# Helper to get note
def get_port_note(port):
    return PORT_NOTES.get(port, "This port is open. Always verify if a public service is actually intended here.")

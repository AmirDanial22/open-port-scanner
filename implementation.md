# OPCF Open Port Vulnerability Scanner Implementation

## 1. System Overview

This project is a Flask-based educational web application for scanning common TCP ports on an authorized target IP address. It helps users see which services are reachable, understand the possible risk level of each open port, and learn recommended countermeasures.

The system is designed for learning and awareness, not offensive security. The homepage requires the user to confirm authorization before a scan can be submitted.

Main features:

- Accepts a target IP address from a web form.
- Validates the IP address before scanning.
- Scans 25 common TCP ports using socket connections.
- Uses concurrent scanning to make the scan faster.
- Classifies open ports as `HIGH`, `MEDIUM`, or `LOW` risk.
- Optionally enriches risk classification with NVD CVE/CVSS data.
- Saves scan results into a SQLite database.
- Displays scan metrics, open ports, educational notes, and countermeasures.
- Provides static awareness pages about ports, risks, and ethical use.
- Includes a Port Buddy chatbot for port and cybersecurity explanations.

## 2. Technology Stack

- `Python`: Main programming language.
- `Flask`: Web framework for routes, templates, form handling, and API endpoint.
- `Flask-SQLAlchemy`: Database ORM.
- `SQLite`: Local database stored under the Flask `instance` folder.
- `python-dotenv`: Loads environment variables from `.env`.
- `requests`: Calls the NVD API.
- `google-generativeai`: Optional Gemini-powered chatbot.
- `Bootstrap`: Frontend layout and styling.
- `Font Awesome`: Icons.
- `marked.js`: Renders chatbot Markdown responses in the browser.

Dependencies are listed in `requirements.txt`.

## 3. Project Structure

```text
open-port-scanner_2/
├── app.py
├── config.py
├── requirements.txt
├── setup.py
├── test_local.py
├── implementation.md
├── instance/
│   └── scans.db
├── modules/
│   ├── scanner.py
│   ├── validator.py
│   ├── classifier.py
│   ├── database.py
│   ├── educational.py
│   └── countermeasures.py
├── static/
│   ├── style.css
│   └── chat.js
└── templates/
    ├── layout.html
    ├── index.html
    ├── results.html
    ├── ports.html
    ├── risks.html
    ├── awareness.html
    └── ethical.html
```

## 4. Application Startup

The application starts from `app.py`.

Important startup steps:

1. Creates the Flask app:

   ```python
   app = Flask(__name__)
   ```

2. Loads configuration from `Config` in `config.py`.

3. Initializes the database:

   ```python
   db.init_app(app)
   ```

4. Creates database tables if they do not exist:

   ```python
   with app.app_context():
       db.create_all()
   ```

5. Runs the local development server on port `5000`:

   ```python
   app.run(debug=True, port=5000)
   ```

## 5. Configuration

Configuration is stored in `config.py`.

The app loads environment variables from `.env` using `load_dotenv()`.

Available config values:

- `SECRET_KEY`: Used by Flask for flash messages and session signing.
- `SQLALCHEMY_DATABASE_URI`: Database connection string. Defaults to `sqlite:///scans.db`.
- `SQLALCHEMY_TRACK_MODIFICATIONS`: Disabled to reduce overhead.
- `N8N_WEBHOOK_URL`: Present but not currently used by the main app flow.
- `GEMINI_API_KEY`: Optional API key for the Port Buddy chatbot.

If no database URL is provided, Flask-SQLAlchemy stores `scans.db` inside the Flask `instance` directory.

## 6. Main User Flow

The normal scanning flow is:

1. User opens `/`.
2. `index()` renders `templates/index.html`.
3. User enters an IP address and checks the authorization checkbox.
4. Browser submits a `POST` request to `/scan`.
5. `scan()` validates authorization and the IP address.
6. The system checks whether the same IP is already being scanned.
7. `scan_ip()` scans the common TCP ports.
8. `add_risk_to_results()` adds risk levels and reasons.
9. The result is saved to SQLite as JSON.
10. Educational notes and countermeasures are attached.
11. `templates/results.html` displays the final dashboard.

## 7. Routes In `app.py`

### `/`

Function: `index()`

Renders the scanner homepage. The page contains:

- IP address input.
- Authorization checkbox.
- Submit button.
- Quick target buttons for local educational testing.

Template used: `templates/index.html`

### `/scan`

Function: `scan()`

Method: `POST`

This is the main route for running a scan.

Responsibilities:

- Reads `ip_address` and `agree_terms` from the submitted form.
- Rejects the request if the user did not confirm authorization.
- Calls `validate_ip(ip_address)`.
- Prevents duplicate scans for the same IP using the `active_scans` dictionary.
- Calls `scan_ip(ip_address)` to scan ports.
- Calls `add_risk_to_results(scan_results)` to classify risks.
- Saves a `ScanResult` database record.
- Adds educational notes with `get_port_note(port)`.
- Adds countermeasures for high-risk ports using `get_countermeasures(port)`.
- Renders `templates/results.html`.

If an error occurs, the scan is removed from `active_scans`, a flash error is shown, and the user is redirected back to the homepage.

### `/history`

Function: `history()`

Loads the 10 most recent scan records:

```python
ScanResult.query.order_by(ScanResult.scan_date.desc()).limit(10).all()
```

Important note: the route references `history.html`, but this template is not present in the current project. Visiting `/history` may fail until `templates/history.html` is added.

### `/about`

Function: `about()`

Renders `about.html`.

Important note: `templates/about.html` is not present in the current project. Visiting `/about` may fail until this template is added.

### `/awareness`

Function: `awareness()`

Renders `templates/awareness.html`, an educational page about cybersecurity awareness.

### `/ports`

Function: `ports()`

Renders `templates/ports.html`, which explains the common ports scanned by the system.

### `/risk-levels`

Function: `risk_levels()`

Renders `templates/risks.html`, which explains the risk categories.

### `/ethical-notice`

Function: `ethical_notice()`

Renders `templates/ethical.html`, which explains responsible and authorized use.

### `/api/chat`

Function: `chat()`

Method: `POST`

Receives a JSON body like:

```json
{
  "message": "What is port 443?"
}
```

The route has two modes:

- Gemini mode: If `GEMINI_API_KEY` exists, the app sends the user message to Gemini and returns the model response.
- Fallback mode: If no Gemini key exists, the app uses simple keyword and port-number matching to answer basic questions.

The frontend chatbot in `static/chat.js` calls this route.

## 8. Port Scanning Module

File: `modules/scanner.py`

This module contains the actual TCP port scanning logic.

### `COMMON_PORTS`

`COMMON_PORTS` is a dictionary of 25 port numbers and service names.

Examples:

- `21`: FTP
- `22`: SSH
- `80`: HTTP
- `443`: HTTPS
- `3306`: MySQL
- `3389`: RDP
- `27017`: MongoDB

Only these ports are scanned. The scanner does not scan every possible port from 1 to 65535.

### `scan_port(ip, port, timeout=1)`

Scans one TCP port.

How it works:

1. Creates a TCP socket.
2. Sets a timeout.
3. Calls `connect_ex((ip, port))`.
4. If the result is `0`, the port is open.
5. Returns a dictionary containing the port, open status, and service name.

Example return value for an open port:

```python
{
    "port": 80,
    "is_open": True,
    "service": "HTTP"
}
```

If an exception happens, the function returns the port as closed with an `error` flag.

### `scan_ip(ip_address)`

Scans every port in `COMMON_PORTS`.

How it works:

1. Records the start time.
2. Creates a `ThreadPoolExecutor` with up to 50 workers.
3. Submits one `scan_port()` job per common port.
4. Collects only ports where `is_open` is `True`.
5. Sorts open ports by port number.
6. Calculates elapsed scan time.
7. Returns the final scan result.

Example return value:

```python
{
    "ip": "127.0.0.1",
    "open_ports": [
        {
            "port": 8080,
            "is_open": True,
            "service": "HTTP-Alt"
        }
    ],
    "total_scanned": 25,
    "total_open": 1,
    "scan_time": 0.34
}
```

## 9. IP Validation Module

File: `modules/validator.py`

### `validate_ip(ip_str)`

Checks whether the submitted IP address is valid.

The function first tries Python's `ipaddress.ip_address()`. If that fails, it tries a simple IPv4 regex and checks that each number is between `0` and `255`.

Return format:

```python
(True, "IP valid")
```

or:

```python
(False, "Format IP tidak valid")
```

There is also a `blocked_ranges` list intended for blocking ranges like private IPs or loopback IPs. In the current code, those entries are commented out, so local testing IPs like `127.0.0.1` and `192.168.1.1` are allowed.

## 10. Risk Classification Module

File: `modules/classifier.py`

This module adds cybersecurity risk context to open ports.

### `RISK_RULES`

`RISK_RULES` is a static mapping from port number to risk level and reason.

Examples:

- Port `21`: `HIGH`, because FTP sends credentials in clear text.
- Port `22`: `MEDIUM`, because SSH can be brute-forced if weak passwords are used.
- Port `443`: `LOW`, because HTTPS is expected encrypted web traffic.
- Port `3389`: `HIGH`, because RDP is commonly targeted.

### `fetch_nvd_data(service_name)`

Attempts to fetch vulnerability data from the NVD API for a service name.

How it works:

1. Normalizes the service name.
2. Checks the in-memory `NVD_CACHE` first.
3. Waits 6 seconds to reduce NVD public API rate-limit issues.
4. Sends a request to the NVD CVE API.
5. Reads the first returned vulnerability.
6. Extracts CVE ID and CVSS score if available.
7. Stores the result in `NVD_CACHE`.

If the request fails or no vulnerability data is found, it returns `None`.

### `classify_risk(port_info)`

Classifies one open port.

Priority:

1. If NVD data exists and includes CVSS, use CVSS:
   - `>= 7.0`: `HIGH`
   - `>= 4.0`: `MEDIUM`
   - `< 4.0`: `LOW`
2. If NVD data is unavailable, use `RISK_RULES`.
3. If the port has no rule, return `LOW`.

### `add_risk_to_results(scan_results)`

Adds risk details to every open port in the scan result.

For each open port, it adds:

- `risk_level`
- `risk_reason`
- `nvd_data`, if available

It also calculates:

```python
"risk_summary": {
    "HIGH": 0,
    "MEDIUM": 0,
    "LOW": 0
}
```

This summary is displayed in the results dashboard.

## 11. Educational Notes Module

File: `modules/educational.py`

### `PORT_NOTES`

This dictionary maps known ports to student-friendly explanations.

Example:

```python
443: "Secure Web Traffic (HTTPS). Encrypted and safe for sensitive data like passwords and credit cards."
```

### `get_port_note(port)`

Returns a note for a port. If the port is not found, it returns a default message:

```python
"This port is open. Always verify if a public service is actually intended here."
```

The `/scan` route injects this note into each open port before rendering `results.html`.

## 12. Countermeasures Module

File: `modules/countermeasures.py`

This module stores recommended defensive actions by port.

Each port can have:

- `immediate`: urgent actions to reduce exposure.
- `hardening`: configuration and security improvements.
- `long_term`: strategic controls and architecture improvements.

Example for RDP port `3389`:

```python
{
    "immediate": ["Block RDP (3389) from the internet", "Disable RDP if not actively used"],
    "hardening": ["Require Network Level Authentication (NLA)", "Enforce MFA/2FA for logins", "Whitelist specific admin IP addresses"],
    "long_term": ["Deploy an enterprise VPN / gateway for remote access", "Implement PAM-based access control"]
}
```

### `get_countermeasures(port)`

Returns countermeasures for the requested port. If the port does not have a custom entry, it returns `DEFAULT_COUNTERMEASURES`.

In the current app flow, countermeasures are shown only for ports classified as `HIGH`.

## 13. Database Module

File: `modules/database.py`

This module defines the database object and scan result table.

### `db`

```python
db = SQLAlchemy()
```

This object is initialized by `app.py`.

### `ScanResult`

Database model:

```python
class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), nullable=False)
    scan_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    results = db.Column(db.JSON, nullable=False)
```

Fields:

- `id`: Auto-increment primary key.
- `ip_address`: Target IP address that was scanned.
- `scan_date`: Timestamp when the scan was stored.
- `results`: Full scan result saved as JSON.

## 14. Frontend Templates

### `templates/layout.html`

Base layout used by all pages.

Contains:

- HTML document structure.
- Bootstrap and Font Awesome imports.
- Main navbar.
- Flash message display.
- `{% block content %}` placeholder.
- Footer.
- Port Buddy chatbot widget.
- JavaScript imports.

### `templates/index.html`

Homepage scanner form.

Contains:

- Scanner title and description.
- Authorization warning.
- IP address input.
- Required authorization checkbox.
- Submit button to `/scan`.
- Quick target buttons that fill the input with local IPs.

### `templates/results.html`

Scan result dashboard.

Displays:

- Target IP.
- Scan date.
- Total open ports.
- Total scanned ports.
- Risk summary counts.
- Scan duration.
- Detailed open-port table.
- Student notes.
- NVD CVE/CVSS context if available.
- OPCF countermeasure recommendations for high-risk ports.

### `templates/ports.html`

Static educational page explaining the scanned ports.

Includes a browser-side search field that filters port cards using JavaScript.

### `templates/risks.html`

Static educational page explaining the meaning of `HIGH`, `MEDIUM`, and `LOW` risk.

### `templates/awareness.html`

Static educational page for general cybersecurity awareness.

### `templates/ethical.html`

Static page explaining responsible and authorized scanning.

## 15. Static Files

### `static/style.css`

Contains the custom visual styling for the application, including:

- Dark theme variables.
- Card styling.
- Navbar styling.
- Buttons.
- Tables.
- Chat widget styling.
- Responsive layout rules.

### `static/chat.js`

Controls the Port Buddy chat widget.

Main behavior:

1. Opens and closes the chat window.
2. Adds the first greeting message.
3. Sends user messages to `/api/chat` using `fetch()`.
4. Shows a typing indicator while waiting.
5. Renders bot Markdown responses using `marked.parse()` when available.
6. Appends user and bot messages to the chat window.

## 16. Chatbot Behavior

The chatbot can work in two ways.

### Gemini Mode

If `GEMINI_API_KEY` is set in `.env`, `/api/chat` uses Google Gemini.

The prompt tells Gemini:

- It is Port Buddy.
- It is a friendly cybersecurity assistant.
- It specializes in ports, vulnerabilities, and general cybersecurity concepts.
- It should answer concisely and politely.
- It may use Markdown.

The app first tries `gemini-2.5-flash`. If that model is not available, it lists available models and uses the first compatible text model.

### Fallback Mode

If `GEMINI_API_KEY` is missing, the chatbot uses simple local logic:

- Responds to greetings.
- Responds to help requests.
- Detects numbers in the user message.
- If the number matches a known port in `PORT_NOTES`, it returns the note and recommended countermeasures.
- If the port is unknown, it says there is no specific note yet.

## 17. Active Scan Tracking

`app.py` contains:

```python
active_scans = {}
```

This is an in-memory dictionary used to prevent scanning the same IP twice at the same time.

When a scan starts:

```python
active_scans[ip_address] = "scanning"
```

When the scan ends or fails, the IP is removed from the dictionary.

Important limitation: because this is only stored in memory, it resets when the Flask app restarts. It also does not coordinate across multiple production workers.

## 18. Data Flow Example

Example user input:

```text
127.0.0.1
```

Possible scan output before risk enrichment:

```python
{
    "ip": "127.0.0.1",
    "open_ports": [
        {
            "port": 8080,
            "is_open": True,
            "service": "HTTP-Alt"
        }
    ],
    "total_scanned": 25,
    "total_open": 1,
    "scan_time": 0.21
}
```

After `add_risk_to_results()` and educational enrichment:

```python
{
    "ip": "127.0.0.1",
    "open_ports": [
        {
            "port": 8080,
            "is_open": True,
            "service": "HTTP-Alt",
            "risk_level": "LOW",
            "risk_reason": "HTTP Alternate",
            "student_note": "HTTP Alternative. Often used for web proxies or development servers. Treat like Port 80."
        }
    ],
    "total_scanned": 25,
    "total_open": 1,
    "scan_time": 0.21,
    "risk_summary": {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 1
    }
}
```

This final structure is saved to the database and passed to `results.html`.

## 19. How To Run The System

Create and activate a virtual environment if needed, then install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file if you want custom settings:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///scans.db
GEMINI_API_KEY=your-gemini-api-key
```

Run the application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 20. Local Testing Helper

File: `test_local.py`

This script starts simple local HTTP servers on selected ports.

Current test ports:

- `8080`
- `8081`
- `9999`

Only port `8080` is included in `COMMON_PORTS`, so scanning `127.0.0.1` should detect `8080` if the test server starts successfully.

Run the helper in one terminal:

```bash
python test_local.py
```

Then run the Flask app in another terminal:

```bash
python app.py
```

Open the scanner and scan:

```text
127.0.0.1
```

## 21. Security And Ethical Controls

The system includes several responsible-use features:

- The homepage warns users that authorization is required.
- The scan form requires the authorization checkbox.
- The scanner only checks a fixed list of 25 common ports.
- Socket timeout is short, reducing scan intensity.
- The project includes ethics and awareness pages.

Important note: the system relies on the user confirming authorization. It does not technically verify ownership of the IP address.

## 22. Current Limitations

- Only scans predefined common TCP ports.
- Does not support UDP scanning.
- Does not perform service banner grabbing.
- Does not confirm exact software versions.
- NVD lookup is based on general service names, so CVE matches may be broad.
- NVD calls add delay because the code sleeps 6 seconds per uncached service.
- `active_scans` is in memory only.
- `/history` references a missing `history.html` template.
- `/about` references a missing `about.html` template.
- Some text in templates appears to have encoding issues, such as broken symbols where special characters were used.
- Private and loopback IP blocking rules are currently commented out in `validator.py`.

## 23. How To Extend The System

Common improvements:

- Add more ports to `COMMON_PORTS` in `modules/scanner.py`.
- Add more risk rules to `RISK_RULES` in `modules/classifier.py`.
- Add more student explanations to `PORT_NOTES` in `modules/educational.py`.
- Add more defensive actions to `COUNTERMEASURES` in `modules/countermeasures.py`.
- Create `templates/history.html` to show saved scan records.
- Create `templates/about.html` or remove the unused `/about` route.
- Add a scan progress screen for longer scans.
- Add export to PDF or CSV.
- Add authentication if storing real scan history.
- Move long scans to a background worker for production use.

## 24. One-Sentence Summary

This system is an educational Flask web app that accepts an authorized IP address, scans 25 common TCP ports, classifies detected open services by risk, stores the result in SQLite, and presents the findings with explanations, CVE context, and recommended countermeasures.

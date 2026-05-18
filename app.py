from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import threading
from config import Config
from modules.database import db, ScanResult
from modules.validator import validate_ip
from modules.scanner import scan_ip
from modules.classifier import add_risk_to_results
from modules.educational import get_port_note, PORT_NOTES
from modules.countermeasures import get_countermeasures
import requests

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Store active scans (simple in-memory store for demo)
active_scans = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    ip_address = request.form.get('ip_address', '').strip()
    agree_terms = request.form.get('agree_terms')
    
    # Validation
    if not agree_terms:
        flash('You must agree to the terms before scanning.', 'danger')
        return redirect(url_for('index'))
    
    is_valid, message = validate_ip(ip_address)
    if not is_valid:
        flash(f'Invalid IP: {message}', 'danger')
        return redirect(url_for('index'))
    
    # Check if scan is already in progress for this IP
    if ip_address in active_scans:
        flash('Scan is already in progress for this IP.', 'warning')
        return redirect(url_for('index'))
    
    # Mark scan as active
    active_scans[ip_address] = 'scanning'
    
    try:
        # Perform scan (this might take some time)
        scan_results = scan_ip(ip_address)
        
        # Add risk classification
        scan_results = add_risk_to_results(scan_results)
        
        # Save to database
        scan_record = ScanResult(
            ip_address=ip_address,
            results=scan_results
        )
        db.session.add(scan_record)
        db.session.commit()
        
        # Remove from active scans
        if ip_address in active_scans:
            del active_scans[ip_address]
        
        # Prepare data for template
        scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Inject educational notes
        from modules.countermeasures import get_countermeasures
        for port_data in scan_results['open_ports']:
            port_data['student_note'] = get_port_note(port_data['port'])
            if port_data.get('risk_level') == 'HIGH':
                port_data['countermeasures'] = get_countermeasures(port_data['port'])

        return render_template('results.html', 
                             results=scan_results, 
                             scan_date=scan_date)
        
    except Exception as e:
        # Remove from active scans on error
        if ip_address in active_scans:
            del active_scans[ip_address]
        
        flash(f'Scan error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    """Show scan history (optional feature)"""
    scans = ScanResult.query.order_by(ScanResult.scan_date.desc()).limit(10).all()
    return render_template('history.html', scans=scans)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/awareness')
def awareness():
    return render_template('awareness.html')

@app.route('/ports')
def ports():
    return render_template('ports.html')

@app.route('/risk-levels')
def risk_levels():
    return render_template('risks.html')

@app.route('/ethical-notice')
def ethical_notice():
    return render_template('ethical.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').lower()
    
    # Try Gemini First
    gemini_key = app.config.get('GEMINI_API_KEY')
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            
            prompt = f"You are Port Buddy, a friendly cybersecurity assistant. You specialize in explaining network ports, vulnerabilities, and general cybersecurity concepts. Answer concisely and politely. Use markdown for formatting.\n\nUser: {user_message}"
            
            try:
                # Try the preferred model first
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                return {"response": response.text}
            except Exception as model_error:
                if '404' in str(model_error) or 'not found' in str(model_error):
                    # If model not found, dynamically find the first available text model
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if available_models:
                        fallback_model = available_models[0].replace('models/', '')
                        model = genai.GenerativeModel(fallback_model)
                        response = model.generate_content(prompt)
                        return {"response": response.text}
                raise model_error
                
        except Exception as e:
            return {"response": f"My Gemini brain encountered an error: {str(e)}"}, 500

    # Fallback / Mock Mode Logic
    bot_reply = "I'm not sure about that. Try asking about a specific port like 'Port 80' or asking what I can do!"
    
    if "hello" in user_message or "hi" in user_message:
        bot_reply = "Hello! I'm Port Buddy. I can help explain what different network ports do. Ask me about a port number! (Add GEMINI_API_KEY to your .env to make me smarter)"
    elif "help" in user_message:
        bot_reply = "You can ask me things like 'What is port 443?' or 'Tell me about FTP'. Add a GEMINI_API_KEY to your .env to unlock my full brain!"
    else:
        # Check if the user mentioned a specific port we know about
        import re
        port_match = re.search(r'(\d+)', user_message)
        if port_match:
            port_num = int(port_match.group(1))
            if port_num in PORT_NOTES:
                note = PORT_NOTES[port_num]
                cms = get_countermeasures(port_num)
                
                bot_reply = f"Ah, Port {port_num}! {note}\n\n"
                bot_reply += "🛡️ OPCF Recommended Countermeasures:\n"
                bot_reply += f"1️⃣ IMMEDIATE: {', '.join(cms['immediate'])}\n"
                bot_reply += f"2️⃣ HARDENING: {', '.join(cms['hardening'])}\n"
                bot_reply += f"3️⃣ LONG-TERM: {', '.join(cms['long_term'])}\n\n"
                bot_reply += "Would you like more details on this port?"
            else:
                bot_reply = f"I see you mentioned port {port_num}, but I don't have a specific safety note for that one in my database yet."

    return {"response": bot_reply}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
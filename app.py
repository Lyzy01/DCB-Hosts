from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'dev_key_123' # Change this for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class UserBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(100), nullable=False)
    bot_token = db.Column(db.String(200), nullable=False)
    ai_api_key = db.Column(db.String(200), nullable=True)
    custom_command = db.Column(db.String(50), default="!hello")
    custom_response = db.Column(db.String(500), default="Hi! This bot is powered by Ly's Hosting.")
    status = db.Column(db.String(20), default="Pending")

# --- HTML TEMPLATE (Embedded for convenience) ---
# In a real project, you'd put this in /templates/index.html
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ly's Bot Hosting Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: white; padding: 40px; }
        .container { max-width: 800px; margin: auto; background: #16213e; padding: 20px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #e94560; text-align: center; }
        .form-group { margin-bottom: 15px; }
        input { width: 100%; padding: 10px; border-radius: 5px; border: none; margin-top: 5px; background: #0f3460; color: white; }
        button { background: #e94560; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; }
        .bot-card { background: #0f3460; padding: 15px; margin-top: 20px; border-radius: 8px; border-left: 5px solid #e94560; }
        .status-badge { background: #28a745; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Ly's Bot Builder</h1>
        <p style="text-align: center;">Deploy your custom Discord Bot in seconds.</p>
        
        <form method="POST" action="/setup">
            <div class="form-group">
                <label>Developer Name</label>
                <input type="text" name="owner_name" placeholder="e.g. Kim" required>
            </div>
            <div class="form-group">
                <label>Discord Bot Token</label>
                <input type="password" name="bot_token" placeholder="MTAy..." required>
            </div>
            <div class="form-group">
                <label>AI API Key (Optional)</label>
                <input type="password" name="ai_api_key" placeholder="gsk_...">
            </div>
            <hr style="border: 0.5px solid #16213e; margin: 20px 0;">
            <h3>Custom Command Setup</h3>
            <div class="form-group">
                <label>Command Trigger</label>
                <input type="text" name="command" placeholder="!hello">
            </div>
            <div class="form-group">
                <label>Bot Response</label>
                <input type="text" name="response" placeholder="Welcome to our server!">
            </div>
            <button type="submit">Build & Launch Bot</button>
        </form>

        <hr>

        <h2>Active Hosted Bots</h2>
        {% for bot in bots %}
        <div class="bot-card">
            <strong>{{ bot.owner_name }}'s Bot</strong> <span class="status-badge">Running</span><br>
            <small>Trigger: <code>{{ bot.custom_command }}</code> | AI Enabled: {{ 'Yes' if bot.ai_api_key else 'No' }}</small>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def index():
    # Fetch all bots from database to display on the dashboard
    all_bots = UserBot.query.all()
    # Using render_template_string for a single-file demo
    from flask import render_template_string
    return render_template_string(HTML_TEMPLATE, bots=all_bots)

@app.route('/setup', methods=['POST'])
def setup():
    owner = request.form.get('owner_name')
    token = request.form.get('bot_token')
    ai_key = request.form.get('ai_api_key')
    cmd = request.form.get('command') or "!hello"
    resp = request.form.get('response') or "Bot is online!"

    # Save to Database
    new_entry = UserBot(
        owner_name=owner,
        bot_token=token,
        ai_api_key=ai_key,
        custom_command=cmd,
        custom_response=resp,
        status="Active"
    )
    
    db.session.add(new_entry)
    db.session.commit()
    
    print(f"DEBUG: New bot registered for {owner}")
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Initialize the database file
    with app.app_context():
        db.create_all()
    
    # Run the web server
    # Port 5000 is standard, Render will use 8080 or its own assigned port
    app.run(host='0.0.0.0', port=5000)

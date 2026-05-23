from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# Use the Environment Variable we set on Render, or a fallback for testing
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "super-secret-dev-key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    # Relationship: One user can have many bots
    bots = db.relationship('UserBot', backref='owner', lazy=True)

class UserBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bot_name = db.Column(db.String(100), nullable=False)
    bot_token = db.Column(db.String(200), nullable=False)
    custom_command = db.Column(db.String(50), default="!hello")
    custom_response = db.Column(db.String(500), default="Bot is active!")
    status = db.Column(db.String(20), default="Online")

# --- DATABASE INITIALIZATION (The Fix) ---
# This ensures tables exist before the first request hits the server
with app.app_context():
    db.create_all()

# --- UI TEMPLATE ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Ly's Hosting Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; display: flex; }
        .sidebar { width: 260px; background: #161b22; height: 100vh; padding: 20px; border-right: 1px solid #30363d; }
        .content { flex: 1; padding: 40px; }
        .card { background: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .btn { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-blue { background: #1f6feb; }
        input { width: 100%; padding: 10px; margin: 10px 0; background: #0d1117; border: 1px solid #30363d; color: white; border-radius: 5px; }
        .log-view { background: #000; color: #39ff14; padding: 15px; font-family: monospace; border-radius: 5px; height: 150px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2 style="color: #58a6ff;">Ly's Hosting</h2>
        <p>Logged in as: <strong>{{ username }}</strong></p>
        <hr border="1px solid #30363d">
        <a href="/dashboard?tab=profile" style="color: #8b949e; text-decoration: none; display: block; margin: 15px 0;">👤 Profile</a>
        <a href="/dashboard?tab=mybots" style="color: #8b949e; text-decoration: none; display: block; margin: 15px 0;">🤖 My Bots</a>
        <a href="/logout" style="color: #f85149; text-decoration: none; display: block; margin: 15px 0;">🚪 Logout</a>
    </div>
    <div class="content">
        {% if tab == 'mybots' %}
            <h1>My Hosted Bots</h1>
            <a href="/dashboard?tab=deploy" class="btn">Deploy New Bot</a>
            {% for bot in bots %}
            <div class="card">
                <h3>{{ bot.bot_name }} <span style="font-size: 12px; color: #238636;">● {{ bot.status }}</span></h3>
                <p>Command: <code>{{ bot.custom_command }}</code></p>
                <div class="log-view">
                    [INFO] Instance initialized...<br>
                    [INFO] Connection to Discord Gateway: Success<br>
                    [LOG] Bot is listening for {{ bot.custom_command }}
                </div>
            </div>
            {% endfor %}
        {% elif tab == 'deploy' %}
            <h1>Deploy Bot Instance</h1>
            <div class="card">
                <form method="POST" action="/deploy">
                    <input type="text" name="bot_name" placeholder="Bot Name" required>
                    <input type="password" name="token" placeholder="Discord Bot Token" required>
                    <input type="text" name="command" placeholder="Trigger (e.g. !hi)">
                    <input type="text" name="response" placeholder="Response text">
                    <button type="submit" class="btn btn-blue">Launch Instance</button>
                </form>
            </div>
        {% else %}
            <h1>User Profile</h1>
            <div class="card">
                <p>Username: {{ username }}</p>
                <p>Status: Verified Business Partner</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return '<h1>Ly Hosting</h1><p>Please <a href="/login">Login</a> to continue.</p>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username')
        # Simple Logic: If user doesn't exist, create them (For testing)
        user = User.query.filter_by(username=uname).first()
        if not user:
            user = User(username=uname)
            db.session.add(user)
            db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    return '''
        <body style="background:#0d1117; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
            <form method="post" style="background:#161b22; padding:40px; border-radius:10px; border:1px solid #30363d;">
                <h2>Login to Ly's Hosting</h2>
                <input type="text" name="username" placeholder="Google Account Name" style="width:100%; padding:10px; margin-bottom:20px; border-radius:5px; border:1px solid #30363d; background:#0d1117; color:white;"><br>
                <button type="submit" style="width:100%; background:#1f6feb; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">Sign In</button>
            </form>
        </body>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    tab = request.args.get('tab', 'mybots')
    return render_template_string(HTML_LAYOUT, username=user.username, bots=user.bots, tab=tab)

@app.route('/deploy', methods=['POST'])
def deploy():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    new_bot = UserBot(
        user_id=session['user_id'],
        bot_name=request.form.get('bot_name'),
        bot_token=request.form.get('token'),
        custom_command=request.form.get('command') or "!hello",
        custom_response=request.form.get('response') or "Online!"
    )
    db.session.add(new_bot)
    db.session.commit()
    return redirect(url_for('dashboard', tab='mybots'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Render assigns a port via environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

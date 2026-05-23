from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# This creates the database file bot_manager.db automatically
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database table for your customers
class UserBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(100))
    bot_token = db.Column(db.String(200))
    ai_api_key = db.Column(db.String(200))
    custom_command = db.Column(db.String(50))
    custom_response = db.Column(db.String(500))

# The Professional Dark UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ly's Bot Hosting Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
        .card { background: #1e293b; padding: 25px; border-radius: 12px; max-width: 650px; margin: auto; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        h1 { color: #38bdf8; text-align: center; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #38bdf8; color: #0f172a; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #0ea5e9; }
        .bot-list { margin-top: 30px; }
        .bot-item { background: #334155; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #38bdf8; }
        code { color: #fbbf24; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 Bot Deployment Center</h1>
        <form method="POST" action="/setup">
            <input type="text" name="owner_name" placeholder="Client Name" required>
            <input type="password" name="bot_token" placeholder="Discord Bot Token" required>
            <input type="password" name="ai_api_key" placeholder="AI API Key (Optional)">
            <input type="text" name="command" placeholder="Custom Command (e.g. !info)">
            <input type="text" name="response" placeholder="Bot's Response">
            <button type="submit">Deploy Instance</button>
        </form>

        <div class="bot-list">
            <h3>📂 Live Database Records</h3>
            {% for bot in bots %}
            <div class="bot-item">
                <strong>{{ bot.owner_name }}'s Bot</strong><br>
                <small>Trigger: <code>{{ bot.custom_command }}</code> | Token: <code>{{ bot.bot_token[:12] }}...</code></small>
            </div>
            {% else %}
            <p style="opacity: 0.5;">No bots deployed yet.</p>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    all_bots = UserBot.query.all()
    return render_template_string(HTML_TEMPLATE, bots=all_bots)

@app.route('/setup', methods=['POST'])
def setup():
    new_bot = UserBot(
        owner_name=request.form.get('owner_name'),
        bot_token=request.form.get('bot_token'),
        ai_api_key=request.form.get('ai_api_key'),
        custom_command=request.form.get('command') or "!hello",
        custom_response=request.form.get('response') or "I am online!"
    )
    db.session.add(new_bot)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # 1. Force the database and tables to be created FIRST
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
    
    # 2. Then start the web server
    # Render uses the PORT environment variable, so we check for it
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

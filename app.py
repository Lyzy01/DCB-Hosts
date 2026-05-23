from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UserBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(100))
    bot_token = db.Column(db.String(200))
    ai_api_key = db.Column(db.String(200))
    custom_command = db.Column(db.String(50))
    custom_response = db.Column(db.String(500))

# --- THE HTML DASHBOARD ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bot Hosting Manager</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; padding: 20px; }
        .box { background: #1e1e1e; padding: 20px; border-radius: 10px; max-width: 600px; margin-bottom: 20px; }
        input { width: 90%; padding: 10px; margin: 5px 0; border-radius: 5px; border: none; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .record { border-bottom: 1px solid #333; padding: 10px 0; }
        code { background: #333; padding: 2px 5px; color: #00ff00; }
    </style>
</head>
<body>
    <h1>🚀 Ly's Bot Hosting</h1>
    
    <div class="box">
        <h3>Add New Bot Instance</h3>
        <form method="POST" action="/setup">
            <input type="text" name="owner_name" placeholder="Client Name" required><br>
            <input type="password" name="bot_token" placeholder="Discord Bot Token" required><br>
            <input type="password" name="ai_api_key" placeholder="AI API Key (Optional)"><br>
            <input type="text" name="command" placeholder="Trigger (e.g. !hello)"><br>
            <input type="text" name="response" placeholder="Response text"><br><br>
            <button type="submit">Launch Bot</button>
        </form>
    </div>

    <div class="box">
        <h3>📂 Database Records (Inside bot_manager.db)</h3>
        {% for bot in bots %}
        <div class="record">
            <strong>{{ bot.owner_name }}</strong><br>
            Token: <code>{{ bot.bot_token[:15] }}...</code><br>
            Custom Cmd: <code>{{ bot.custom_command }}</code>
        </div>
        {% else %}
        <p>No bots registered yet.</p>
        {% endfor %}
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
        custom_response=request.form.get('response') or "Online!"
    )
    db.session.add(new_bot)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

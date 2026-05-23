from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_manager.db'
db = SQLAlchemy(app)

# Database Model to store Customer Bot Data
class CustomerBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    bot_token = db.Column(db.String(200), nullable=False)
    ai_api_key = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default="Offline")

@app.route('/')
def home():
    bots = CustomerBot.query.all()
    return f"<h1>Bot Hosting Manager</h1><p>Active Bots: {len(bots)}</p><a href='/setup'>Add New Bot</a>"

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        new_bot = CustomerBot(
            username=request.form['username'],
            bot_token=request.form['token'],
            ai_api_key=request.form['ai_key']
        )
        db.session.add(new_bot)
        db.session.commit()
        return "✅ Bot Configured! In a real setup, this would now spawn a new process."
    
    return '''
        <form method="post">
            Your Name: <input type="text" name="username" required><br>
            Discord Bot Token: <input type="password" name="token" required><br>
            AI API Key (Optional): <input type="password" name="ai_key"><br>
            <input type="submit" value="Launch My Bot">
        </form>
    '''

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

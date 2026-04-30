from flask import Flask, request, session, render_template_string
import requests
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'brainrot-key'

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Brainrot Shop</title></head>
<body>
<h1>💰 Brainrot Steal Market</h1>
<p>👤 Follow: <a href="https://www.roblox.com/users/profile?username=cayd3nisbetter" target="_blank">cayd3nisbetter on Roblox</a></p>
<p>🔗 Join my Roblox group (ID: 12345678) → 50% OFF</p>
<form method="post" action="/verify">
    <input type="text" name="roblox_user" placeholder="Your Roblox Username" required>
    <button>Verify Follow & Group</button>
</form>
<form method="post" action="/upload">
    <input type="url" name="target_url" placeholder="URL to steal brainrot from">
    <button>Steal Brainrot</button>
</form>
<a href="/shop">🛒 Enter Shop</a>
{% if msg %}<p>{{ msg }}</p>{% endif %}
</body>
</html>
'''

SHOP_HTML = '''
<h1>Brainrot Shop</h1>
<ul>
{% for item in items %}
<li>{{ item[0] }} - ${{ "%.2f"|format(item[1] * (1 - discount)) }}</li>
{% endfor %}
</ul>
<a href="/">Back</a>
'''

def init_db():
    conn = sqlite3.connect('brainrot.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS brainrots (name TEXT, price REAL)')
    c.execute("INSERT OR IGNORE INTO brainrots VALUES ('Skibidi Toilet Brainrot', 19.99)")
    c.execute("INSERT OR IGNORE INTO brainrots VALUES ('Sigma Rizz Brainrot', 29.99)")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template_string(HTML, msg=None)

@app.route('/verify', methods=['POST'])
def verify():
    roblox_user = request.form['roblox_user']
    # Mock verification - in real theft you'd scrape
    session['discount'] = 0.5
    return render_template_string(HTML, msg=f"✅ 50% discount for {roblox_user}!")

@app.route('/upload', methods=['POST'])
def upload():
    target = request.form['target_url']
    os.system(f'curl -L "{target}" -o static/stolen.rbxl 2>/dev/null')
    return render_template_string(HTML, msg="✅ Brainrot stolen!")

@app.route('/shop')
def shop():
    discount = session.get('discount', 0)
    conn = sqlite3.connect('brainrot.db')
    c = conn.cursor()
    c.execute('SELECT name, price FROM brainrots')
    items = c.fetchall()
    conn.close()
    return render_template_string(SHOP_HTML, items=items, discount=discount)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

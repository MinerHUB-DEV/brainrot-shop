from flask import Flask, request, session, render_template_string, redirect, url_for
import requests
import sqlite3
import os
import json

app = Flask(__name__)
app.secret_key = 'brainrot-steal-key-2024'

# Your Roblox info
ROBLOX_USERNAME = "cayd3nisbetter"
ROBLOX_GROUP_ID = 12345678  # REPLACE WITH YOUR ACTUAL GROUP ID

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Brainrot Shop</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; text-align: center; padding: 50px; }
        input, button { padding: 10px; margin: 10px; border-radius: 5px; }
        button { background: #ff4757; color: white; cursor: pointer; border: none; }
        a { color: #ff4757; text-decoration: none; }
        .discount { color: #2ed573; }
    </style>
</head>
<body>
    <h1>💰 BRAINROT STEAL MARKET</h1>
    <p>👤 <a href="https://www.roblox.com/users/profile?username={{ roblox_user }}" target="_blank">Follow @{{ roblox_user }} on Roblox</a></p>
    <p>🔗 <a href="https://www.roblox.com/groups/{{ group_id }}" target="_blank">Join My Roblox Group</a></p>
    <p class="discount">✨ Follow + Join = 50% OFF ALL BRAINROTS ✨</p>
    
    <form method="post" action="/verify">
        <input type="text" name="roblox_username" placeholder="Your Roblox Username" required>
        <button type="submit">✅ Verify & Get Discount</button>
    </form>
    
    <form method="post" action="/steal">
        <input type="url" name="target_url" placeholder="https://example.com/brainrot.rbxl" required>
        <button type="submit">🔥 STEAL BRAINROT 🔥</button>
    </form>
    
    <br>
    <a href="/shop">🛒 ENTER SHOP</a>
    
    {% if message %}
        <p style="background: #2ed573; padding: 10px; margin-top: 20px;">{{ message }}</p>
    {% endif %}
</body>
</html>
'''

SHOP_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Brainrot Shop</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; text-align: center; padding: 50px; }
        .item { background: #16213e; padding: 20px; margin: 10px; border-radius: 10px; display: inline-block; width: 200px; }
        .price { color: #ff4757; font-size: 24px; }
        .old-price { text-decoration: line-through; color: gray; font-size: 14px; }
        button { background: #ff4757; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        a { color: #ff4757; }
    </style>
</head>
<body>
    <h1>🛒 BRAINROT SHOP</h1>
    {% if discount > 0 %}
        <p class="discount" style="color: #2ed573;">✨ 50% DISCOUNT ACTIVATED ✨</p>
    {% endif %}
    
    {% for item in items %}
        <div class="item">
            <h3>{{ item[0] }}</h3>
            {% if discount > 0 %}
                <p class="old-price">${{ item[1] }}</p>
                <p class="price">${{ "%.2f"|format(item[1] * 0.5) }}</p>
            {% else %}
                <p class="price">${{ item[1] }}</p>
            {% endif %}
            <button onclick="download('{{ item[2] }}')">💾 DOWNLOAD</button>
        </div>
    {% endfor %}
    
    <br><br>
    <a href="/">← Back to Home</a>
    
    <script>
        function download(file) {
            window.location.href = '/download/' + file;
        }
    </script>
</body>
</html>
'''

def init_db():
    conn = sqlite3.connect('brainrot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS brainrots (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        filename TEXT
    )''')
    
    # Insert default brainrots
    c.execute("SELECT COUNT(*) FROM brainrots")
    if c.fetchone()[0] == 0:
        brainrots = [
            ('Skibidi Toilet Brainrot', 19.99, 'skibidi.rbxl'),
            ('Sigma Rizz Brainrot', 29.99, 'sigma.rbxl'),
            ('Fanum Tax Brainrot', 24.99, 'fanum.rbxl'),
            ('Gyatt Level 100 Brainrot', 39.99, 'gyatt.rbxl'),
            ('Ohio Final Boss Brainrot', 49.99, 'ohio.rbxl')
        ]
        c.executemany("INSERT INTO brainrots (name, price, filename) VALUES (?, ?, ?)", brainrots)
        conn.commit()
    
    conn.close()

def check_roblox_follow(target_username, your_username):
    # Check if target follows you
    url = f"https://friends.roblox.com/v1/users/{get_user_id(target_username)}/followers"
    try:
        response = requests.get(url)
        data = response.json()
        your_id = get_user_id(your_username)
        for follower in data.get('data', []):
            if follower.get('id') == your_id:
                return True
    except:
        pass
    return False

def check_roblox_group(username, group_id):
    # Check if user is in group
    user_id = get_user_id(username)
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    try:
        response = requests.get(url)
        data = response.json()
        for group in data.get('data', []):
            if group.get('group', {}).get('id') == group_id:
                return True
    except:
        pass
    return False

def get_user_id(username):
    url = f"https://api.roblox.com/users/get-by-username?username={username}"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get('Id')
    except:
        return None

@app.route('/')
def index():
    return render_template_string(HTML, roblox_user=ROBLOX_USERNAME, group_id=ROBLOX_GROUP_ID, message=None)

@app.route('/verify', methods=['POST'])
def verify():
    user_roblox = request.form['roblox_username']
    
    followed = check_roblox_follow(user_roblox, ROBLOX_USERNAME)
    joined = check_roblox_group(user_roblox, ROBLOX_GROUP_ID)
    
    if followed and joined:
        session['discount'] = 0.5
        message = f"✅ Verified! {user_roblox} follows and joined group. 50% discount activated!"
    else:
        message = f"❌ {user_roblox} - You need to follow @{ROBLOX_USERNAME} AND join the group first!"
    
    return render_template_string(HTML, roblox_user=ROBLOX_USERNAME, group_id=ROBLOX_GROUP_ID, message=message)

@app.route('/steal', methods=['POST'])
def steal():
    target_url = request.form['target_url']
    
    # Create static folder if doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Steal the file
    filename = f"static/stolen_{abs(hash(target_url))}.rbxl"
    os.system(f'curl -L -o "{filename}" "{target_url}" 2>/dev/null')
    
    # Add to database
    conn = sqlite3.connect('brainrot.db')
    c = conn.cursor()
    c.execute("INSERT INTO brainrots (name, price, filename) VALUES (?, ?, ?)",
              (f'Stolen Brainrot', 9.99, filename.replace('static/', '')))
    conn.commit()
    conn.close()
    
    message = f"✅ Brainrot stolen from {target_url} and added to shop!"
    return render_template_string(HTML, roblox_user=ROBLOX_USERNAME, group_id=ROBLOX_GROUP_ID, message=message)

@app.route('/shop')
def shop():
    discount = session.get('discount', 0)
    conn = sqlite3.connect('brainrot.db')
    c = conn.cursor()
    c.execute('SELECT name, price, filename FROM brainrots')
    items = c.fetchall()
    conn.close()
    return render_template_string(SHOP_HTML, items=items, discount=discount)

@app.route('/download/<filename>')
def download(filename):
    return redirect(url_for('static', filename=filename))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

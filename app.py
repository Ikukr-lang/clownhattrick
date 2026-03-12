from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import os
from datetime import datetime

app = Flask(__name__)

# ====================== БАЗА ДАННЫХ ======================
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS team (id INTEGER PRIMARY KEY, name TEXT, money INTEGER);
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY, name TEXT, age INTEGER,
            goalkeeping INTEGER, defending INTEGER, playmaking INTEGER, passing INTEGER,
            winger INTEGER, scoring INTEGER, setpieces INTEGER, stamina INTEGER,
            form INTEGER, experience INTEGER, position TEXT
        );
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY, date TEXT, opponent TEXT, score TEXT, report TEXT
        );
    ''')
    if conn.execute("SELECT COUNT(*) FROM team").fetchone()[0] == 0:
        conn.execute("INSERT INTO team (name, money) VALUES ('Clown United', 500000)")
        names = ["Petya Clown","Vasya Ball","Kolya Keeper","Dima Dribble","Sasha Strike","Misha Mid","Tolya Tackle","Gosha Goal","Borya Back","Vitya Wing","Roma Rocket","Igor Iron","Sergey Star","Oleg Owl"]
        pos = ["GK","DF","DF","DF","MF","MF","MF","MF","FW","FW","FW"]
        for i in range(14):
            skills = [random.randint(5,15) for _ in range(8)]
            conn.execute("""INSERT INTO players (name,age,goalkeeping,defending,playmaking,passing,winger,scoring,setpieces,stamina,form,experience,position)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (names[i], random.randint(18,32), *skills, random.randint(4,8), random.randint(1,10), pos[i%len(pos)]))
    conn.commit()
    conn.close()

init_db()

# ====================== МАРШРУТЫ ======================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/team')
def team():
    conn = get_db()
    players = conn.execute("SELECT * FROM players").fetchall()
    conn.close()
    return render_template('team.html', players=players)

@app.route('/train', methods=['GET','POST'])
def train():
    if request.method == 'POST':
        focus = request.form['focus']
        col_map = {'def': 'defending', 'att': 'scoring', 'wing': 'winger', 'pass': 'passing', 'gk': 'goalkeeping', 'stam': 'stamina'}
        col = col_map.get(focus, 'stamina')
        conn = get_db()
        conn.execute(f"UPDATE players SET {col} = {col} + 1, form = form + 1")
        conn.commit()
        conn.close()
        return redirect('/team')
    return render_template('train.html')

@app.route('/match', methods=['GET','POST'])
def match():
    if request.method == 'POST':
        tactic = request.form.get('tactic', 'normal')
        conn = get_db()
        players = conn.execute("SELECT * FROM players").fetchall()
        
        midfield = sum(p['playmaking'] + p['passing'] for p in players) // 10
        attack = sum(p['scoring'] + p['winger'] for p in players) // 7
        defense = sum(p['defending'] + p['goalkeeping'] for p in players[:5]) // 5
        stamina = sum(p['stamina'] for p in players) // 20
        
        if tactic == 'attack': attack += 4; midfield -= 3
        elif tactic == 'defensive': defense += 4; attack -= 3
        elif tactic == 'wing': attack += 3; midfield += 2
        
        weather = random.choice(["Sunny", "Rainy", "Cloudy", "Windy"])
        weather_banner = "Сильным мощным игрокам дождь не страшен!" if weather == "Rainy" else "Идеальная погода для футбола!"
        
        opp_name = random.choice(["Real Clown","FC Troll","Bot United","Noob FC","Legendary Losers"])
        referee = random.choice(["Nguyễn Hoàng Hải", "Ivan Petrov", "Juan García", "Hans Müller", "Ahmed Al-Sayed"])
        
        your_stars = (midfield + attack + defense + stamina) / 15
        opp_stars = (random.randint(midfield-8, midfield+8) + random.randint(attack-8, attack+8) + random.randint(defense-8, defense+8)) / 15
        
        your_goals = max(0, int(random.gauss(your_stars - (opp_stars*0.4), 1.7)))
        opp_goals = max(0, int(random.gauss(opp_stars - (your_stars*0.4), 1.7)))
        
        minutes = sorted(random.sample(range(3, 91), 7))
        events = [f"{m}' ⚽ Гол! {random.choice([p['name'] for p in players if p['position'] in ('FW','MF')])}" if random.random() < 0.6 else f"{m}' ⚽ Гол соперника" for m in minutes]
        
        score = f"{your_goals} – {opp_goals}"
        report = f"Погода: {weather}<br>Судья: {referee}<br>Звёзды: {your_stars:.1f} ★ — {opp_stars:.1f} ★"
        
        conn.execute("INSERT INTO matches (date, opponent, score, report) VALUES (?,?,?,?)",
                     (datetime.now().strftime("%d.%m.%Y %H:%M"), opp_name, score, report))
        conn.commit()
        conn.close()
        
        return render_template('match.html', score=score, opponent=opp_name, report=report,
                               weather=weather, weather_banner=weather_banner,
                               referee=referee, events=events, tactic=tactic)
    
    return render_template('match.html')

@app.route('/history')
def history():
    conn = get_db()
    matches = conn.execute("SELECT * FROM matches ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('history.html', matches=matches)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

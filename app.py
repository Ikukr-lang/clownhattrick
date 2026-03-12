# ... (весь предыдущий код до @app.route('/match') остаётся)

@app.route('/match', methods=['GET','POST'])
def match():
    if request.method == 'POST':
        tactic = request.form.get('tactic', 'normal')
        conn = get_db()
        players = conn.execute("SELECT * FROM players").fetchall()
        
        # === ТОЧНЫЙ РАСЧЁТ КАК В HATTRICK ===
        midfield = sum(p['playmaking'] + p['passing'] for p in players) // 10
        attack = sum(p['scoring'] + p['winger'] for p in players) // 7
        defense = sum(p['defending'] + p['goalkeeping'] for p in players[:5]) // 5
        stamina = sum(p['stamina'] for p in players) // 20
        
        # Тактика
        if tactic == 'attack': attack += 4; midfield -= 3
        elif tactic == 'defensive': defense += 4; attack -= 3
        elif tactic == 'wing': attack += 3; midfield += 2
        
        weather = random.choice(["Sunny", "Rainy", "Cloudy", "Windy"])
        # Дождь влияет на выносливость (как в оригинале)
        if weather == "Rainy":
            stamina -= 3
            weather_banner = "Сильным мощным игрокам дождь не страшен!"
        else:
            weather_banner = "Идеальная погода для футбола!"
        
        opp_name = random.choice(["Real Clown","FC Troll","Bot United","Noob FC","Legendary Losers"])
        opp_mid = random.randint(midfield-8, midfield+8)
        opp_att = random.randint(attack-8, attack+8)
        opp_def = random.randint(defense-8, defense+8)
        
        referee = random.choice(["Nguyễn Hoàng Hải", "Ivan Petrov", "Juan García", "Hans Müller", "Ahmed Al-Sayed"])
        
        your_stars = (midfield + attack + defense + stamina) / 15
        opp_stars = (opp_mid + opp_att + opp_def) / 15
        
        your_goals = max(0, int(random.gauss(your_stars - opp_def/10 + stamina/15, 1.7)))
        opp_goals = max(0, int(random.gauss(opp_stars - defense/10, 1.7)))
        
        # События по минутам (как в прямой трансляции)
        minutes = sorted(random.sample(range(3, 91), 7))
        events = []
        for m in minutes:
            if random.random() < 0.65 and your_goals > 0:
                player = random.choice([p['name'] for p in players if p['position'] in ('FW','MF')])
                events.append(f"{m}' ⚽ Гол! {player}")
                your_goals -= 1
            elif random.random() < 0.45 and opp_goals > 0:
                events.append(f"{m}' ⚽ Гол соперника")
                opp_goals -= 1
            elif random.random() < 0.25:
                events.append(f"{m}' 🟨 Жёлтая карточка у соперника")
        
        score = f"{your_goals} – {opp_goals}"
        
        report = f"""
        <strong>Погода:</strong> {weather}<br>
        <strong>Судья:</strong> {referee}<br>
        <strong>Звёзды:</strong> {your_stars:.1f} ★ — {opp_stars:.1f} ★<br>
        <strong>Midfield:</strong> {midfield:.1f} | Attack: {attack:.1f} | Defence: {defense:.1f}
        """
        
        conn.execute("INSERT INTO matches (date, opponent, score, report) VALUES (?,?,?,?)",
                     (datetime.now().strftime("%d.%m.%Y %H:%M"), opp_name, score, report))
        conn.commit()
        conn.close()
        
        return render_template('match.html', 
                               score=score, opponent=opp_name, report=report,
                               weather=weather, weather_banner=weather_banner,
                               referee=referee, events=events, tactic=tactic)
    
    return render_template('match.html')

import requests
from flask import Flask, session, render_template, redirect, url_for, request
from datetime import datetime
from dotenv import load_dotenv
import os
import sqlite3
import anthropic
import markdown

app = Flask('140mi')
app.secret_key = "140"
app.debug = True
DATABASE = 'database.db'

load_dotenv("api.env")

client = anthropic.Anthropic(
    api_key=os.getenv("CLAUDE_API"),
)

NASA_API_KEY = os.getenv("NASA_API_KEY")
print(f"API KEY LOADED: {NASA_API_KEY}")


@app.route('/')
def index():
    res = requests.get("https://api.nasa.gov/planetary/apod", params={"api_key": NASA_API_KEY})
    apod = res.json()
    return render_template('index.html', apod=apod)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        password = request.form["pass"]
        con_pass = request.form["pass2"]

        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM user WHERE email = ?", (email,))
        if cursor.fetchone() is not None:
            return render_template('signup.html', error='Email already in use.')
        
        if password != con_pass:
            return render_template('signup.html', error='Passwords do not match')

        cursor.execute("INSERT INTO user (email, password, fname, lname) VALUES (?, ?, ?, ?)", (email, password, fname, lname))
        connection.commit()
        connection.close()
        session['email'] = email
        return redirect(url_for('index'))
    
    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["pass"]

        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("SELECT email, password FROM user WHERE email = ?", (email,))
        data = cursor.fetchone()
        if data is None:
            return render_template('login.html', error='Email not associated with an account.')
        if data['password'] != password:
            return render_template('login.html', error='Wrong Password')
        

        connection.close()
        session['email'] = email
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('chat.html', history=session['chat_history'])

@app.route('/chat/send', methods=['POST'])
def chat_send():
    user_message = request.form.get('message', '').strip()
    if not user_message:
        return redirect(url_for('chat'))

    if 'chat_history' not in session:
        session['chat_history'] = []

    history = session['chat_history']
    messages = []
    for entry in history:
        messages.append({"role": "user", "content": entry['user']})
        messages.append({"role": "assistant", "content": entry['assistant']})
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system="You are AstroBot, a friendly space expert...",
            messages=messages
        )
        assistant_reply = markdown.markdown(response.content[0].text)
    except Exception as e:
        assistant_reply = f"⚠️ Sorry, I couldn't respond right now. (Error: {str(e)})"

    history.append({'user': user_message, 'assistant': assistant_reply})
    session['chat_history'] = history
    session.modified = True

    return redirect(url_for('chat'))

@app.route('/chat/clear')
def chat_clear():
    session.pop('chat_history', None)
    return redirect(url_for('chat'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    photos = []
    error = ''
    saved_srcs = set()

    if session.get('email'):
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT src FROM favorites WHERE email=?", (session.get('email'),))
        saved_srcs = set(row['src'] for row in cursor.fetchall())
        connection.close()

    if query:
        try:
            response = requests.get('https://images-api.nasa.gov/search', params={
                'q': query,
                'media_type': 'image'
            })
            data = response.json()
            items = data.get('collection', {}).get('items', [])
            
            for item in items:
                if item.get('data') and item.get('links'):
                    photo = {
                        'title': item['data'][0].get('title', ''),
                        'description': item['data'][0].get('description', ''),
                        'date': item['data'][0].get('date_created', '')[:10],
                        'img_src': item['links'][0].get('href', ''),
                        'center': item['data'][0].get('center', '')
                    }
                    photos.append(photo)
        except Exception as e:
            error = "Could not fetch photos. Try again."
            print(f"API error: {e}")

    return render_template('search.html', photos=photos, error=error, query=query, saved_srcs=saved_srcs)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/account')
def account():
    if not session.get('email'):
        return redirect(url_for('index'))
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM user WHERE email=?", (session.get('email'),))
    data = cursor.fetchone()

    return render_template("account.html", data=data)
@app.route('/pass')
def password():
    return render_template('change_password.html')

@app.route('/change_pass', methods = ['POST', 'GET'])
def change_pass():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    email = session.get('email')
    if request.method == 'POST':
        oldpass = request.form['oldpass']
        newpass = request.form['newpass']
        newpass2 = request.form['newpass2']
    cursor.execute("SELECT password FROM user WHERE email=?", (email,))
    password = cursor.fetchone()
    if oldpass != password['password']:
        return render_template("change_password.html", error="Wrong password. Please enter correct current password.")
    if newpass != newpass2:
        return render_template("change_password.html", error="Passwords do not match.")
    
    cursor.execute("UPDATE user SET password=? WHERE email=?", (newpass, email))
    connection.commit()
    connection.close()
    return render_template("change_password.html")

@app.route('/email')
def email():
    return render_template("change_email.html")

@app.route('/change_email', methods = ['POST', 'GET'])
def change_email():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    email = session.get('email')
    if request.method == 'POST':
        new_email = request.form['new_email']
        password = request.form['pass']

    cursor.execute("SELECT password FROM user WHERE email=?", (email,))
    pass2 = cursor.fetchone()

    if pass2['password'] != password:
        return render_template("change_email.html", error="Wrong password. Please enter correct password.")

    cursor.execute("SELECT email from user where email=?", (new_email,))
    users = cursor.fetchall()
    if users:
        return render_template("change_email.html", error="Email already in use.")
    
    cursor.execute("UPDATE user set email=? WHERE email=?", (new_email, email))
    connection.commit()
    session['email'] = new_email

    connection.close()

    return redirect(url_for('account'))

@app.route('/save', methods = ['POST', 'GET'])
def save():
    if not session.get('email'):
        return redirect(url_for('login'))
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    email = session.get('email')

    if request.method == 'POST':
        src = request.form['img_src']
        title = request.form['title']
        date = request.form['date']

    cursor.execute("INSERT INTO favorites (email, src, title, date) VALUES (?, ?, ?, ?)", (email, src, title, date)) 
    connection.commit()
    connection.close()

    return redirect(url_for('search'))

@app.route('/favorites')
def favorites():
    if session.get('email'):
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT src, title, date FROM favorites WHERE email=?", (session.get('email'),))
        photos = cursor.fetchall()

    return render_template("favorites.html", photos=photos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



app.run(host='0.0.0.0', port=8080)
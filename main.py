import requests
from flask import Flask, session, render_template, redirect, url_for, request
from datetime import datetime
from dotenv import load_dotenv
import os
import sqlite3
import random
app = Flask('140mi')
app.secret_key = "140"
app.debug = True
DATABASE = 'database.db'

load_dotenv("api.env")
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



@app.route('/search')
def search():
    query = request.args.get('query', '')
    
    photos = []
    error = ''

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

    return render_template('search.html', photos=photos, error=error, query=query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/account')
def account():
    if not session['email']:
        return redirect(url_for('index'))
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM user WHERE email=?", (session['email'],))
    data = cursor.fetchone()

    return render_template("account.html", data=data)

@app.route('/change_pass')
def change_pass():
    return render_template("change_password.html")

@app.route('/email')
def email():
    return render_template("change_email.html")

@app.route('/change_email', methods = ['POST', 'GET'])
def change_email():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    email = session['email']
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



app.run(host='0.0.0.0', port=8080)
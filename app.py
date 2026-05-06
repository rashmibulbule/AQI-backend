from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import pickle
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load ML model
model = pickle.load(open("model.pkl", "rb"))

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  email TEXT,
                  password TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template_string('''
    <h2>AQI System</h2>
    <a href="/signup">Signup</a><br><br>
    <a href="/login">Login</a>
    ''')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, password))
        conn.commit()
        conn.close()

        return "Signup successful! <br><a href='/login'>Go to Login</a>"

    return render_template_string('''
    <h2>Signup</h2>
    <form method="POST">
        Username: <input name="username"><br><br>
        Email: <input name="email"><br><br>
        Password: <input name="password"><br><br>
        <button type="submit">Signup</button>
    </form>
    ''')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login! <br><a href='/login'>Try again</a>"

    return render_template_string('''
    <h2>Login</h2>
    <form method="POST">
        Username: <input name="username"><br><br>
        Password: <input name="password"><br><br>
        <button type="submit">Login</button>
    </form>
    ''')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    return render_template_string('''
    <h2>AQI Prediction</h2>
    <form action="/predict" method="POST">
        Pollutant Min: <input name="pollutant_min"><br><br>
        Pollutant Max: <input name="pollutant_max"><br><br>
        <button type="submit">Predict AQI</button>
    </form>
    ''')

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():
    pollutant_min = float(request.form['pollutant_min'])
    pollutant_max = float(request.form['pollutant_max'])

    prediction = model.predict([[pollutant_min, pollutant_max]])
    aqi = prediction[0]

    if aqi <= 50:
        category = "Good"
    elif aqi <= 100:
        category = "Moderate"
    elif aqi <= 200:
        category = "Poor"
    else:
        category = "Very Poor"

    return f'''
    <h2>Result</h2>
    Predicted AQI: {aqi:.2f} <br>
    Category: {category} <br><br>
    <a href="/dashboard">Try Again</a>
    '''

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
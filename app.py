from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

# Dummy credentials
USER_CREDENTIALS = {
    "admin": "password123"
}

@app.route('/')
def home():
    return render_template('home.html', title="Home")

@app.route('/wayfinding')
def wayfinding():
    return render_template('wayfinding.html', title="Wayfinding")

@app.route('/settings')
def settings():
    return render_template('settings.html', title="Settings")

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash("Invalid credentials!", "danger")
        return redirect(url_for('settings'))
    
if __name__ == '__main__':
    app.run(debug=True)

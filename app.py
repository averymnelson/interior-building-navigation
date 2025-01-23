from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', title="Home")

@app.route('/wayfinding')
def wayfinding():
    return render_template('wayfinding.html', title="Wayfinding")

@app.route('/settings')
def settings():
    return render_template('settings.html', title="Settings")

if __name__ == '__main__':
    app.run(debug=True)

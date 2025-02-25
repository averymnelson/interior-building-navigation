from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

# Dummy credentials
USER_CREDENTIALS = {
    "admin": "password123"
}


# Function to resize the image
def resize_image():
    try:
        # Check if the low-res image already exists
        low_res_path = "static/images/map_lowres.jpg"
        if not os.path.exists(low_res_path):
            # Open the high-res image
            image = Image.open("static/images/map.jpg")

            # Resize the image (adjust size as needed)
            image = image.resize((1000, 750))  # Adjust based on your needs

            # Save it as a new low-resolution file
            image.save(low_res_path, "JPEG", quality=50)  # Adjust quality if needed

            print("Low-res map created: map_lowres.jpg")
        else:
            print("Low-res image already exists.")
    except Exception as e:
        print(f"Error resizing image: {e}")

# Resize the image when the app starts
resize_image()


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

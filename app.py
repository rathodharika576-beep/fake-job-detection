from flask import Flask, render_template, request
import pickle
import re
import pytesseract
from PIL import Image
from pyngrok import ngrok

# Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

# Load Model and TFIDF
model = pickle.load(open('fake_job_model.pkl', 'rb'))
tfidf = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Prediction Route
@app.route('/predict', methods=['POST'])
def predict():

    # Get text from textbox
    text = request.form.get('job_description', '')

    # Get uploaded image
    image = request.files.get('job_image')

    # Extract text from image if uploaded
    if image and image.filename != '':

        img = Image.open(image)

        extracted_text = pytesseract.image_to_string(img)

        text = text + " " + extracted_text

    # Convert text into TFIDF features
    data = tfidf.transform([text]).toarray()

    # ML Prediction
    prediction = model.predict(data)

    # Suspicious keywords
    fake_keywords = [
        "earn money",
        "whatsapp",
        "telegram",
        "quick hiring",
        "limited seats",
        "without interview",
        "work from home",
        "urgent",
        "no experience",
        "easy money"
    ]

    # Fake score
    fake_score = 0

    # Detect Phone Numbers
    phone_pattern = r'\d{10}'
    if re.search(phone_pattern, text):
        fake_score += 1

    # Detect Email IDs
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    if re.search(email_pattern, text):
        fake_score += 1

    # Detect Suspicious Keywords
    for word in fake_keywords:
        if word in text.lower():
            fake_score += 1

    # Final Prediction Logic
    if prediction[0] == 1 or fake_score >= 2:

        probability = min(50 + (fake_score * 10), 99)

        result = f"Fake Job Posting 🚨 (Fake Probability: {probability}%)"

    else:

        probability = max(80 - (fake_score * 10), 50)

        result = f"Real Job Posting ✅ (Real Probability: {probability}%)"

    return render_template('index.html', prediction_text=result)

# Run Flask App with ngrok
if __name__ == '__main__':

    public_url = ngrok.connect(addr=5000, bind_tls=True)

    print("🔥 Public URL:", public_url)

    app.run(port=5000)
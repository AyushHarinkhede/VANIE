from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import re
from datetime import datetime

# 1. Server Setup
app = Flask(__name__)
CORS(app)  # HTML ko block hone se rokenge

# 2. VANIE's Brain (Intents & Keywords)
INTENTS = {
    "greeting": {
        "keywords": ["hi", "hello", "hey", "kaise ho", "what's up", "namaste", "aur batao"],
        "responses": [
            "Hello! Main VANIE hu. Kaise help kar sakti hu aapki?", 
            "Hi there! Aapka din kaisa ja raha hai?", 
            "Hey! VANIE here. Kya kaam hai?"
        ]
    },
    "identity": {
        "keywords": ["who are you", "tum kon ho", "naam kya hai", "who made you", "creator", "kisne banaya", "owner"],
        "responses": [
            "Main VANIE hu - Virtual Assistant of Neural Integrated Engine. Mujhe Ayush Harinkhede ne develop kiya hai!", 
            "Mera naam VANIE hai aur mujhe Ayush Harinkhede ne banaya hai aapki madad karne ke liye!", 
            "Main ek advanced AI assistant hun, mera creator Ayush Harinkhede hai!"
        ]
    },
    "capabilities": {
        "keywords": ["help", "what can you do", "tum kya kar sakte ho", "features", "assist"],
        "responses": [
            "Main aapki sawalon ka jawab de sakti hu, time bata sakti hu, aur baat kar sakti hu!", 
            "Main aapki help kar sakti hu - coding, science, history, math sab mein!", 
            "Main ek smart AI hun jo aapki har tarah ki madad kar sakta hu!"
        ]
    },
    "time": {
        "keywords": ["time", "samay", "baj rahe", "kya time ho raha"],
        "responses": ["Abhi ka exact time {time} ho raha hai."]
    },
    "goodbye": {
        "keywords": ["bye", "see you", "goodnight", "tata", "chalo baad me milte"],
        "responses": [
            "Bye! Aapse baat karke accha laga!", 
            "See you soon! Apna khayal rakhna!", 
            "Alvida! Jab bhi madad chahiye main hamesha hun!"
        ]
    }
}

# 3. The Core Algorithm (Multiple Keywords & Scoring)
def get_vanie_response(user_message):
    message = user_message.lower()
    # Remove special characters to understand words better
    message = re.sub(r'[^\w\s]', '', message)
    
    best_intent = None
    max_score = 0

    # Score calculation
    for intent, data in INTENTS.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword in message:
                score += 1
        
        if score > max_score:
            max_score = score
            best_intent = intent

    # Generate Response
    if best_intent:
        response = random.choice(INTENTS[best_intent]["responses"])
        # If user asked for time, inject real time
        if best_intent == "time":
            current_time = datetime.now().strftime("%I:%M %p")
            response = response.format(time=current_time)
        return response
    else:
        # Fallback if AI doesn't understand
        return "Main abhi seekh rahi hu! Kya aap mujhse koi joke sunna chahenge ya aaj ka time janna chahenge?"

# 4. API Endpoint (The Bridge for HTML)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"response": "Please say something!"})
    
    bot_reply = get_vanie_response(user_message)
    return jsonify({"response": bot_reply})

# 5. Run Server
if __name__ == '__main__':
    print("🚀 VANIE Backend is running! Waiting for messages...")
    app.run(debug=True, port=5000)

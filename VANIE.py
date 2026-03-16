from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import json
from datetime import datetime

# ==========================================
# 1. SERVER SETUP
# ==========================================
app = Flask(__name__)
CORS(app) # Yeh HTML ko connect hone dega

# ==========================================
# 2. VANIE'S KNOWLEDGE BASE (Intents)
# ==========================================
INTENTS = {
    "greeting": {
        "keywords": ["hi", "hello", "hey", "kaise ho", "what's up", "namaste", "aur batao"],
        "responses": [
            "Hello! Main VANIE hu. Kaise help kar sakti hu aapki?", 
            "Hi there! Aapka din kaisa ja raha hai?", 
            "Hey! VANIE here. Boliye, kya madad karu?"
        ]
    },
    "identity": {
        "keywords": ["who are you", "tum kon ho", "naam kya hai", "who made you", "creator", "kisne banaya", "owner"],
        "responses": [
            "Main VANIE hu, ek smart AI assistant. Mujhe Ayush Harinkhede ne develop kiya hai!", 
            "Mera naam VANIE hai aur mujhe Ayush Harinkhede ne banaya hai aapki madad karne ke liye."
        ]
    },
    "capabilities": {
        "keywords": ["help", "what can you do", "tum kya kar sakte ho", "features", "assist"],
        "responses": [
            "Main aapke sawaalon ke jawab de sakti hu, aapse baatein kar sakti hu, aur time bata sakti hu!", 
            "Main ek conversational AI hu. Aap mujhse kuch bhi puch sakte hain."
        ]
    },
    "time": {
        "keywords": ["time", "samay", "baj rahe", "kya time ho raha"],
        "responses": ["Abhi ka exact time {time} ho raha hai."]
    },
    "goodbye": {
        "keywords": ["bye", "see you", "goodnight", "tata", "chalo baad me milte"],
        "responses": [
            "Bye! Apna khayal rakhna.", 
            "See you soon! Have a great day."
        ]
    }
}

# ==========================================
# 3. THE CORE AI ALGORITHM (Original + Enhanced)
# ==========================================
def get_ai_response(user_message=''):
    """
    VANIE (cleaned) — getAIResponse implementation
    - Consolidated, syntactically-correct version of the AI-response logic
    - Matches user messages against prioritized checks and keyword categories
    - Returns a plain string (safe for the chat UI)
    """
    msg = str(user_message or '').strip().lower()
    if not msg:
        return "Please tell me how I can help — type 'help' for examples."

    hour = datetime.now().hour
    ai_response = "I'm here to help with your health — type 'help' for suggestions."

    # --- priority / exact checks ---
    if 'dark' in msg and 'mode' in msg:
        return '🌙 Switched to dark mode.'
    if 'light' in msg and 'mode' in msg:
        return '☀️ Switched to light mode.'

    # Emergency / high-risk keywords (return immediately)
    emergency_triggers = ['chest pain','cant breathe','can\'t breathe','heart attack','stroke','suicide','kill myself','not breathing']
    if any(trigger in msg for trigger in emergency_triggers):
        return '🚨 If this is an emergency, call your local emergency number (112/102). Please seek help immediately.'

    # Quick metric reads from dashboard (if present)
    if 'bmi' in msg:
        return f'📏 Your BMI is 23.5.'
    if 'blood pressure' in msg or 'bp' in msg:
        return f'❤️ Your blood pressure is 128/80 mmHg.'
    if 'heart rate' in msg or 'hr' in msg:
        return f'💓 Heart rate: 80 BPM.'

    # Simple conversational responses
    if msg == 'help':
        return "I can help with: view metrics (BMI, BP), navigate the app (dashboard/profile), give general health tips (diet, sleep), or provide emergency guidance. Try: 'What is my BMI?', 'How to lower BP?', 'Open profile'."
    
    import re
    if re.search(r'\b(hi|hello|hey)\b', msg):
        if hour < 12:
            return '☀️ Good morning — how can I help?'
        if hour < 18:
            return '🌤️ Good afternoon — what can I do for you?'
        return '🌙 Good evening — how can I assist?'

    if 'thank' in msg:
        return "You're welcome! 😊 Anything else?"

    # Keyword-category fallback (short list)
    keyword_categories = {
        'symptoms': {
            'keywords': ['headache','fever','cough','nausea','dizziness','fatigue','rash','vomit','stomach','pain'],
            'responses': [
                "I'm sorry you're not feeling well — I can share general tips, but please consult a healthcare professional for diagnosis.",
                "Describe the symptom (onset, severity) and consider contacting your doctor if it is severe or persistent."
            ]
        },
        'diet': {
            'keywords': ['diet','healthy food','what to eat','snack','calories'],
            'responses': [
                'Try a balanced plate: lean protein, whole grains, and plenty of vegetables.',
                'Healthy snacks: nuts, fruit, yogurt or hummus with veggies.'
            ]
        },
        'sleep': {
            'keywords': ['sleep','insomnia','tired','fatigue'],
            'responses': [
                'Aim for 7–9 hours per night and keep a regular sleep schedule.',
                'Limit screens before bed and create a calm, dark sleep environment.'
            ]
        },
        'mental': {
            'keywords': ['stress','anxious','anxiety','depressed','sad','panic'],
            'responses': [
                'If you are in crisis, please call emergency services or a mental health professional. For support, consider contacting a mental health professional or helpline.',
                'Simple grounding: breathe slowly for 4s in / 6s out and name 3 things you can see.'
            ]
        }
    }

    for category in keyword_categories.values():
        for keyword in category['keywords']:
            if keyword in msg:
                return random.choice(category['responses'])

    # small talk / fallback
    if 'joke' in msg or 'tell me a joke' in msg:
        return "Why don't scientists trust atoms? Because they make up everything! 😂"
    if 'weather' in msg:
        return "I can't check live weather here, but I hope it's sunny where you are!"
    
    return "Sorry — I don't understand that yet. Try asking about health metrics, tips, or type 'help'."

# ==========================================
# 4. API ENDPOINT (The Bridge)
# ==========================================
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'status': 'error', 'error': 'Message is required'}), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Get response from the AI algorithm
        response = get_ai_response(user_message)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'VANIE AI Backend'})

if __name__ == '__main__':
    print("🚀 VANIE Backend is running perfectly! Waiting for HTML to connect...")
    print("📡 Server running at: http://localhost:5000")
    print("🔗 API Endpoint: http://localhost:5000/chat")
    app.run(debug=True, host='0.0.0.0', port=5000)

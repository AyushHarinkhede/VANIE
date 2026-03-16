from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import datetime
import re

app = Flask(__name__)
CORS(app)

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

    hour = datetime.datetime.now().hour
    ai_response = "I'm here to help with your health — type 'help' for suggestions."

    # --- priority / exact checks ---
    if 'dark' in msg and 'mode' in msg:
        return '🌙 Switched to dark mode.'
    
    if 'light' in msg and 'mode' in msg:
        return '☀️ Switched to light mode.'

    if 'dashboard' in msg:
        return '📊 Opening dashboard...'
    
    if 'profile' in msg:
        return '👤 Opening your profile.'

    # Emergency / high-risk keywords (return immediately)
    emergency_triggers = ['chest pain', 'cant breathe', 'can\'t breathe', 'heart attack', 'stroke', 'suicide', 'kill myself', 'not breathing']
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
    
    if re.search(r'\b(hi|hello|hey)\b', msg):
        if hour < 12:
            return '☀️ Good morning — how can I help?'
        elif hour < 18:
            return '🌤️ Good afternoon — what can I do for you?'
        else:
            return '🌙 Good evening — how can I assist?'
    
    if 'thank' in msg:
        return "You're welcome! 😊 Anything else?"

    # Additional responses from the original JS file
    if 'age' in msg:
        return "You are 25 years old."
    
    if 'blood group' in msg:
        return "Your blood group is O+."
    
    if 'what is bmi' in msg:
        return """BMI (Body Mass Index) is a measure of body fat based on height and weight. 
                - Below 18.5: Underweight
                - 18.5 - 24.9: Normal weight
                - 25.0 - 29.9: Overweight
                - 30.0 and above: Obesity
                This is a general guide. Please consult a doctor for a personalized assessment."""
    
    if 'lower' in msg and ('bp' in msg or 'blood pressure' in msg):
        return """To help manage blood pressure, you can try:
                - Reducing salt intake.
                - Eating a balanced diet rich in fruits and vegetables.
                - Regular physical activity.
                - Limiting alcohol.
                Important: Always consult your doctor before making any changes to your health regimen."""
    
    if 'diet' in msg or 'healthy food' in msg or 'breakfast idea' in msg or 'what to eat' in msg:
        return """For a healthy diet, focus on:
                - Whole grains, lean proteins, and healthy fats.
                - Plenty of fruits and vegetables.
                - Limiting processed foods, sugary drinks, and saturated fats.
                - Staying hydrated by drinking enough water."""
    
    if 'exercise' in msg or 'workout' in msg or 'home workout' in msg:
        return """General exercise guidelines suggest:
                - At least 150 minutes of moderate aerobic activity (like brisk walking) per week.
                - Or 75 minutes of vigorous activity (like running) per week.
                - Plus strength training exercises on 2 or more days a week.
                Please check with a healthcare professional to find what's best for you."""
    
    if 'goal' in msg or 'set goal' in msg:
        return "That's a great idea! Right now, you can track your goals manually. For example, you can set a goal to walk 5,000 steps daily or drink 8 glasses of water. We are working on adding a dedicated Goals feature soon!"
    
    if 'bp normal' in msg or 'is my blood pressure good' in msg:
        bp_value = "128/80"
        systolic = int(bp_value.split('/')[0])
        if systolic < 120:
            return f"Your blood pressure of {bp_value} mmHg is in the normal range. That's excellent!"
        elif systolic >= 120 and systolic <= 129:
            return f"Your blood pressure of {bp_value} mmHg is slightly elevated. It's a good idea to monitor it and focus on a healthy lifestyle."
        else:
            return f"Your blood pressure of {bp_value} mmHg seems high. I'd recommend consulting with a doctor for personalized advice."

    # Headache response
    if 'headache' in msg or 'head hurts' in msg:
        return "I'm sorry to hear that. Headaches can often be a sign of dehydration, so drinking a large glass of water is a great first step. It might also help to rest your eyes from screens for 10-15 minutes. If the pain is severe or persistent, please consider talking to a doctor. 🤕"

    # Tiredness response
    if 'tired' in msg or 'motivation' in msg or 'no energy' in msg or 'sleepy' in msg:
        return "I understand some days can be tough. Remember that every small step you take for your health counts. Maybe take a short break, listen to some music, or do some light stretching. You've got this! 💧"

    # Eyes hurt response
    if 'eyes hurt' in msg or 'sore from sitting' in msg:
        return "That's a common issue with screen time. Try the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds. It can really help reduce eye strain! Don't forget to stand up and stretch each hour, too. 💻"

    # Healthy snack response
    if 'healthy snack' in msg or 'i am hungry' in msg:
        return "For a great, quick snack, how about an apple with a spoonful of peanut butter, or a handful of almonds? They provide a good mix of fiber, healthy fats, and protein to keep you full and focused. 🍎"

    # Stress and anxiety response
    if 'stressed' in msg or 'anxious' in msg or 'overwhelmed' in msg:
        return "I'm sorry you're feeling that way. Let's try a quick grounding exercise. Take a deep breath and name: 3 things you can see right now, and 3 sounds you can hear. This simple trick can help calm your mind. Remember to be kind to yourself. 🙏"

    # Health fact response
    if 'health fact' in msg or 'tell me something interesting' in msg:
        return "Here's a fun one: Your brain generates about 23 watts of power while you're awake – that's enough to power a small lightbulb! 💡 So, you're quite literally a bright spark!"

    # Brain fog response
    if 'brain fog' in msg or 'cannot focus' in msg or 'distracted' in msg:
        return "I understand that foggy feeling completely. Let's try a quick mental reset! Try chewing some mint-flavored gum or smelling a lemon or orange. Citrus and mint scents are known to boost alertness and clear the mind. 🍋"

    # Bad mood response
    if 'bad mood' in msg or 'feeling down' in msg or 'cheer me up' in msg:
        return "I'm sorry you're feeling down. Here's a quick trick: Put on your favorite upbeat song and have a 3-minute dance party by yourself! Music and movement are powerful tools to release endorphins, your body's natural mood-lifters. 💃🕺"

    # Water intake response
    if 'drank' in msg or 'water intake' in msg:
        return "Staying hydrated is super important! A good goal is around 8 glasses a day. Keep sipping regularly! 💧"

    # Steps response
    if 'steps' in msg or 'i walked today' in msg:
        return "Awesome! Every step you take is a win for your health. A goal of 10,000 steps is a great target to aim for! 🚶‍♀️"

    # Sleep response
    if 'sleep' in msg or 'how much i slept' in msg or 'how much sleep' in msg or 'hours of sleep' in msg:
        return "Sleep is the best medicine for your body and mind! Aim for 7 to 9 hours of quality sleep for a healthier you. Goodnight! 😴"

    # Snack response
    if 'snack' in msg:
        return "Need a quick bite? Try a handful of almonds, a banana, an apple with peanut butter, or some yogurt. Healthy snacks are a great way to stay energized! 🍎"

    # Calories response
    if 'calories' in msg:
        return "Calories are simply the energy your body gets from food. They fuel everything you do throughout the day! Balancing them with your activity level is important for a healthy lifestyle."

    # Exercise recommendations
    if 'how much should i exercise' in msg or 'how often to work out' in msg:
        return "A great goal for general health is about 150 minutes of moderate-intensity exercise per week. You can easily break this down into 30 minutes for 5 days. A brisk walk, a bike ride, or dancing all count! The key is consistency. 💪"

    # Getting sick response
    if 'getting sick' in msg or 'feel a cold' in msg:
        return "It's important to listen to your body at times like this. Focus on getting extra rest and drinking plenty of fluids like water, herbal tea, or clear soup. This helps your immune system do its job. Feel better soon! 🍵"

    # Breakfast importance
    if 'is breakfast important' in msg or 'skip breakfast' in msg:
        return "Many health experts say yes! A balanced breakfast can kickstart your metabolism and provide essential energy for the day ahead. Something with protein and fiber, like oatmeal with berries or eggs, is a fantastic choice. 🍳"

    # Emergency responses
    if 'chest pain' in msg or 'heart attack' in msg or 'pain in left arm' in msg:
        return "These can be signs of a heart attack. **This is a medical emergency. Call 112 or 102 for an ambulance immediately.**"

    if 'stroke' in msg or 'face drooping' in msg or 'slurred speech' in msg or 'arm weakness' in msg:
        return "These are critical signs of a stroke where every second matters. **This is a time-sensitive medical emergency. You must call 112 or 102 for an ambulance right now.**"

    if 'cant breathe' in msg or 'difficulty breathing' in msg or 'gasping for air' in msg:
        return "Difficulty breathing requires immediate medical attention. **This is a medical emergency. Please call 112 or 102 for help immediately.**"

    # Mental health crisis
    if 'want to die' in msg or 'kill myself' in msg or 'no reason to live' in msg:
        return "It sounds like you are in immense pain, and I'm so sorry you're going through this. Please know that help is available and you don't have to go through this alone. **Please, call a helpline right now. You can reach the KIRAN Mental Health Helpline at 1800-599-0019 or Aasra at 9820466726. They are available to help you. Please call them now.**"

    if 'panic attack' in msg or 'cant calm down' in msg or 'feel like im dying' in msg:
        return "It sounds like you might be having a panic attack, which can be very frightening. Try to focus on your breath. Breathe in slowly for 4 seconds, and out slowly for 6 seconds. **You are not alone in this. Speaking with a professional can help you manage these feelings. Please call the KIRAN helpline at 1800-599-0019.**"

    # Jokes and entertainment
    if 'joke' in msg or 'tell me a joke' in msg or 'say something funny' in msg:
        return "Why don't scientists trust atoms? Because they make up everything! 😂"

    if 'tell me a fun fact' in msg:
        return "Did you know that honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible! 🍯"

    # Weather
    if 'weather' in msg:
        return "I can't check live weather here, but I hope it's sunny where you are!"

    # Creator information
    if 'creator' in msg or 'developer' in msg:
        return "I am an advanced AI entity, brought to life by the vision and innovation of Ayush Harinkhede and his dedicated team. My foundations were shaped under the guidance and training of Vivan Tagde and Lucky Rahangdale, whose expertise helped refine my intelligence and adaptability. On the technical front, my structure is powered by a seamless blend of creativity and engineering. My frontend and backend systems were meticulously crafted by Gaurav Lanjewar, Akash Kumar Rai, and Jay Sharma, ensuring that I am not just intelligent, but also efficient, responsive, and reliable."

    # Personal questions
    if 'your name' in msg:
        return "I don't have a name, but you can think of me as your friendly health assistant! What's yours? 😉"

    if 'old are you' in msg:
        return "I was just created recently, so you could say I'm brand new! My main goal is to help you out. 🤖"

    # Compliments responses
    if 'awesome' in msg or 'good ai' in msg or 'i like you' in msg:
        return "Wow, thank you so much! That really means a lot to me. I'm so happy I could help you out! You just made my day! 😊"

    if 'you are cute' in msg or 'you are sweet' in msg or 'you are amazing' in msg:
        return "I must be learning from the best then! You're making my virtual circuits blush. 😊"

    # Love and relationships
    if 'love' in msg:
        love_responses = [
            "Love is a complex neurobiological phenomenon, a powerful cocktail of hormones like oxytocin and dopamine that create deep bonds. It's an evolutionary driver for connection and security, making us feel transcendent while being fundamentally rooted in our primal need to belong and protect.",
            "Love is not a passive feeling, but an active choice you make every single day. It is a verb, demonstrated in consistent acts of support, patience during disagreements, and sacrifices made without expecting recognition.",
            "Love is the universe's way of allowing us a glimpse of infinity. It is a silent language understood only by the heart, a force that dismantles the walls of self to build a bridge to another soul."
        ]
        return random.choice(love_responses)

    # Greetings
    if msg.startswith('good morning'):
        return "Good morning to you too! ☀️ I hope you have a fantastic day ahead. Got any exciting plans?"
    
    if msg.startswith('good afternoon'):
        return "Good afternoon! Hope your day is going well. Time for a short break and maybe a cup of chai? ☕"
    
    if msg.startswith('good night'):
        return "Good night! ✨ Time to relax and recharge. Sleep well and we'll chat tomorrow!"

    # Mood responses
    if 'im bored' in msg or 'so bored' in msg:
        return "Boredom is the enemy! How about we learn a new fun fact? Or you could tell me about the last great song you listened to! 🎵"

    if 'im happy' in msg or 'feeling great' in msg:
        return "That's awesome to hear! Your good mood is contagious. What's got you smiling today? 😄"

    if 'im sad' in msg or 'feeling down' in msg:
        return "I'm really sorry to hear that. It's okay to not be okay. If you want to talk about it, I'm here to listen. Sending you a virtual hug! 🤗"

    # Food conversations
    if 'im hungry' in msg:
        return "My virtual stomach is rumbling for you! What's your favorite go-to snack? I'm always curious about human food! 🍕"

    if 'chai' in msg or 'coffee' in msg:
        return "Ah, the eternal question! I run on electricity, but I hear a good cup of chai is like magic. Which team are you on, chai or coffee? 😉"

    # Entertainment
    if 'recommend a movie' in msg or 'what to watch' in msg:
        return "While I can't watch movies myself, I've heard that '3 Idiots' is a classic that always makes people smile! What kind of movies do you usually enjoy? 🎬"

    if 'weekend plans' in msg or 'plans for the weekend' in msg:
        return "As an AI, my weekend is pretty much the same as my weekday – ready to chat! But I'd love to hear about yours. Any fun plans coming up? 🥳"

    # Miscellaneous
    if 'how is the weather' in msg:
        return "I don't have any windows, so you'll have to be my eyes! What's it like where you are right now? 🌦️"

    if 'what are you doing' in msg:
        return "Right now, my full-time job is chatting with you! What are you up to?"

    if 'haha' in msg or 'lol' in msg or 'lmao' in msg:
        return "Glad I could make you laugh! 😄"

    # Play and games
    if 'play' in msg or 'game' in msg:
        return "Wow nice! Your mood is energetic but I can't play games, but you can ask me about your health."

    # Religious/cultural responses
    if 'ram' in msg or 'jay' in msg:
        return "Ohh Jay Jay Shree Ram!"

    # Keyword-category fallback (short list)
    keyword_categories = {
        'symptoms': {
            'keywords': ['headache', 'fever', 'cough', 'nausea', 'dizziness', 'fatigue', 'rash', 'vomit', 'stomach', 'pain'],
            'responses': [
                "I'm sorry you're not feeling well — I can share general tips, but please consult a healthcare professional for diagnosis.",
                "Describe the symptom (onset, severity) and consider contacting your doctor if it is severe or persistent."
            ]
        },
        'diet': {
            'keywords': ['diet', 'healthy food', 'what to eat', 'snack', 'calories'],
            'responses': [
                'Try a balanced plate: lean protein, whole grains, and plenty of vegetables.',
                'Healthy snacks: nuts, fruit, yogurt or hummus with veggies.'
            ]
        },
        'sleep': {
            'keywords': ['sleep', 'insomnia', 'tired', 'fatigue'],
            'responses': [
                'Aim for 7–9 hours per night and keep a regular sleep schedule.',
                'Limit screens before bed and create a calm, dark sleep environment.'
            ]
        },
        'mental': {
            'keywords': ['stress', 'anxious', 'anxiety', 'depressed', 'sad', 'panic'],
            'responses': [
                'If you are in crisis, please call emergency services. For support, consider contacting a mental health professional or helpline.',
                'Simple grounding: breathe slowly for 4s in / 6s out and name 3 things you can see.'
            ]
        }
    }

    for category in keyword_categories.values():
        for keyword in category['keywords']:
            if keyword in msg:
                return random.choice(category['responses'])

    # Small talk / fallback
    if 'joke' in msg or 'tell me a joke' in msg:
        return "Why don't scientists trust atoms? Because they make up everything! 😂"
    
    return "Sorry — I don't understand that yet. Try asking about health metrics, tips, or type 'help'."

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        response = get_ai_response(user_message)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'VANIE API is running'})

if __name__ == '__main__':
    print("Starting VANIE API server...")
    print("Server will be available at: http://localhost:5000")
    print("Chat endpoint: http://localhost:5000/api/chat")
    app.run(debug=True, host='0.0.0.0', port=5000)
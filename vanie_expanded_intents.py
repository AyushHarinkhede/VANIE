# VANIE Expanded Intent Dictionary with Multi-Keyword Scoring
# Complete Python logic for handling conversational intents with keyword variations

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

class VANIEIntentEngine:
    """Advanced Intent Recognition with Multi-Keyword Scoring"""
    
    def __init__(self):
        # Expanded intent dictionary with multiple keyword variations
        self.intent_dictionary = self._initialize_intent_dictionary()
        self.stop_words = self._initialize_stop_words()
        self.user_sessions = {}
        
    def _initialize_stop_words(self) -> set:
        """Common stop words to ignore in user input"""
        return {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'shall', 'to', 'of', 'in', 'on', 'at', 'by',
            'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'which', 'who',
            'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
            'hai', 'hain', 'ho', 'hote', 'tha', 'the', 'thi', 'ki', 'ka', 'ke', 'se',
            'mein', 'par', 'aur', 'or', 'lekin', 'magar', 'kya', 'kaise', 'kyon',
            'jab', 'tab', 'yah', 'vah', 'ye', 'vo', 'hamara', 'tumhara', 'iska'
        }
    
    def _initialize_intent_dictionary(self) -> Dict[str, Any]:
        """Expanded intent dictionary with multiple keyword variations"""
        return {
            # 1. Greetings & Small Talk Intent
            'greeting': {
                'keywords': [
                    # English variations
                    'hi', 'hello', 'hey', 'hey there', 'good morning', 'good afternoon', 'good evening',
                    'good night', 'greetings', 'welcome', 'what\'s up', 'whats up', 'sup', 'yo',
                    'how are you', 'howdy', 'how do you do', 'nice to meet you', 'pleased to meet you',
                    
                    # Hindi variations
                    'नमस्ते', 'नमस्कार', 'प्रणाम', 'राम राम', 'हाय', 'हेलो', 'हे',
                    'कैसे हो', 'कैसी हो', 'कैसी हैं', 'क्या हाल है', 'क्या हाल चाल',
                    'सुप्रभात', 'शुभ प्रभात', 'शुभ रात्रि', 'आप कैसे हो',
                    'कैसा है', 'कैसी है', 'दिन कैसा गुजरा',
                    
                    # Mixed/Hinglish
                    'kaise ho', 'kya haal hai', 'good morning', 'good evening', 'aur batao',
                    'whats up', 'sup', 'how are you', 'namaste', 'pranam'
                ],
                'responses': [
                    "नमस्ते! 🙏 मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। आपकी हर तरह की मदद के लिए तैयार हूँ। आज क्या काम है?",
                    "Hello! I'm VANIE - your advanced virtual assistant. How can I help you today? 😊",
                    "नमस्ते दोस्त! मैं आपकी सेवा के लिए यहाँ हूँ। क्या पूछना चाहते हैं? 🙏",
                    "Hi there! I'm VANIE, ready to assist you! What can I do for you? 🤖",
                    "प्रणाम! आप कैसे हो? मैं आपकी हर समस्या का समाधान करने के लिए यहाँ हूँ। क्या मदद कर सकती हूँ। ✨",
                    "Hey! VANIE at your service! What can I help you with today? 🌟"
                ],
                'priority': 1,
                'examples': [
                    "Hello VANIE, kaise ho tum?",
                    "Hi there, how are you?",
                    "नमस्ते, आप कैसे हो?",
                    "Good morning! What's up?"
                ]
            },
            
            # 2. Identity & Creator Intent
            'identity': {
                'keywords': [
                    # English variations
                    'who are you', 'what are you', 'what is your name', 'your name', 'tell me about yourself',
                    'introduce yourself', 'what is vanie', 'what does vanie stand for',
                    'who made you', 'who created you', 'who is your creator', 'who is your owner',
                    'who developed you', 'who programmed you', 'who built you', 'your creator',
                    'your developer', 'your owner', 'your maker', 'your father', 'your boss',
                    
                    # Hindi variations
                    'तुम कौन हो', 'तुम क्या हो', 'तुम्हारा नाम क्या है', 'तुम्हारा परिचय',
                    'तुम कौन हो वैनी', 'वैनी कौन है', 'वैनी क्या है',
                    'तुम्हें किसने बनाया', 'तुम्हारा निर्माता कौन है', 'तुम्हारा creator कौन है',
                    'किसने बनाया', 'किसने बनाया वैनी', 'तुम्हारा malik कौन है',
                    'तुम्हारा developer कौन है', 'तुम्हारा programmer कौन है',
                    
                    # Mixed/Hinglish
                    'tum kon ho', 'tumhara naam kya hai', 'vanie kaun hai',
                    'kisne banaya', 'kisne banaya tumhe', 'who made vanie',
                    'creator', 'developer', 'owner', 'maker', 'programmer'
                ],
                'responses': [
                    "मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। मुझे **Ayush Harinkhede** ने develop और create किया है। वे एक talented developer हैं जिन्होंने मुझे आपकी मदद करने के लिए बनाया है। 🤖✨",
                    "I'm VANIE - Virtual Assistant of Neural Integrated Engine. I was developed and created by **Ayush Harinkhede**, a talented developer who built me to assist users like you! 🌟",
                    "मैं एक advanced AI assistant हूँ जिसका नाम VANIE है। मेरे creator **Ayush Harinkhede** हैं, जिन्होंने मुझे Neural Integrated Engine technology से बनाया है। 🚀",
                    "I'm VANIE, an advanced AI assistant powered by Neural Integrated Engine technology. My creator and developer is **Ayush Harinkhede**, who designed me to be helpful and intelligent! 💻",
                    " VANIE - Virtual Assistant of Neural Integrated Engine! मुझे **Ayush Harinkhede** ने बनाया है। वे मेरे developer और creator हैं, और उन्होंने मुझे आपकी service के लिए specially design किया है। 🎯"
                ],
                'priority': 3,
                'examples': [
                    "Who are you VANIE?",
                    "तुम कौन हो वैनी?",
                    "Who made you?",
                    "तुम्हें किसने बनाया?",
                    "What is VANIE?",
                    "VANIE kaun hai?"
                ]
            },
            
            # 3. Capabilities & Usefulness Intent
            'capabilities': {
                'keywords': [
                    # English variations
                    'what can you do', 'what do you do', 'your capabilities', 'your features',
                    'what are your abilities', 'what are your skills', 'how can you help',
                    'help me', 'assist me', 'what can you assist with', 'your functions',
                    'what are you good at', 'what do you specialize in', 'your purpose',
                    'how can you be useful', 'what services do you provide', 'your utilities',
                    
                    # Hindi variations
                    'तुम क्या कर सकते हो', 'तुम क्या करते हो', 'तुम्हारी capabilities क्या हैं',
                    'तुम कैसे मदद कर सकते हो', 'तुम क्या काम कर सकते हो',
                    'तुम्हारी features क्या हैं', 'तुम्हारे skills क्या हैं',
                    'मुझे मदद करो', 'मेरी मदद करो', 'तुम मेरी कैसे मदद कर सकते हो',
                    'तुम्हारा purpose क्या है', 'तुम कैसे useful हो सकते हो',
                    
                    # Mixed/Hinglish
                    'tum kya kar sakte ho', 'tum kya karte ho', 'tumhari capabilities kya hain',
                    'help me', 'assist me', 'tum meri kaise help kar sakte ho',
                    'what can you do', 'your features', 'your skills'
                ],
                'responses': [
                    "मैं आपकी कई तरह से मदद कर सकती हूँ! 🌟\n\n💬 **Conversations**: Natural और friendly बातचीत\n❓ **Questions Answering**: Science, History, Math, Coding में सवाल\n🔧 **Problem Solving**: Complex problems का solution\n📚 **Learning**: New topics सिखाना\n💡 **Ideas**: Creative suggestions देना\n⏰ **Real-time Info**: Time, date, weather updates\n🎯 **Personalization**: आपकी preferences याद रखना\n\nक्या आप कुछ specific जानना चाहते हैं?",
                    "I can help you in many ways! 🚀\n\n🤖 **AI Assistant**: Answer questions and have conversations\n📚 **Knowledge Base**: Science, History, Math, Coding, and more\n🔧 **Problem Solver**: Help with homework and complex problems\n💬 **Friendly Chat**: Natural and engaging conversations\n⏰ **Real-time Info**: Current time, date, and weather\n🎯 **Personalized Service**: Remember your preferences\n\nWhat would you like help with?",
                    "मेरे पास कई amazing capabilities हैं! ✨\n\n🧠 **Intelligent Chat**: Natural conversations with context\n📖 **Knowledge Expert**: Multiple subjects में deep knowledge\n🔍 **Problem Solver**: Step-by-step solutions\n💡 **Creative Helper**: Ideas and suggestions\n⏰ **Live Information**: Real-time updates\n🎭 **Entertainment**: Jokes and fun facts\n\nआप किस क्षेत्र में मदद चाहते हैं?",
                    "I'm designed to be your comprehensive assistant! 🌈\n\n💬 **Chat Naturally**: Like talking to a friend\n📚 **Answer Questions**: From simple to complex\n🔧 **Solve Problems**: Math, coding, and logic puzzles\n📊 **Analyze & Explain**: Break down complex topics\n⏰ **Real-time Data**: Time, weather, and more\n🎯 **Remember You**: Personalized experience\n\nHow can I assist you today?"
                ],
                'priority': 2,
                'examples': [
                    "What can you do VANIE?",
                    "तुम क्या कर सकते हो?",
                    "Help me with my homework",
                    "मेरी मदद करो",
                    "Your capabilities?",
                    "तुम्हारी features क्या हैं?"
                ]
            },
            
            # 4. Entertainment & Mood Intent
            'entertainment': {
                'keywords': [
                    # English variations
                    'bore', 'boring', 'bored', 'tell me a joke', 'joke', 'jokes', 'funny',
                    'entertain me', 'make me laugh', 'cheer me up', 'sad', 'feeling sad',
                    'depressed', 'unhappy', 'feeling down', 'mood off', 'not feeling good',
                    'stress', 'stressed', 'tired', 'exhausted', 'need fun', 'fun time',
                    'play', 'game', 'entertainment', 'amuse', 'distract', 'lighten mood',
                    
                    # Hindi variations
                    'बोर हो रहा हूँ', 'बोरिंग', 'बोर हो गया', 'जोक सुनाओ', 'जोक्स',
                    'मज़ाक', 'मज़ाकिया', 'हसाओ', 'मुझे हसाओ', 'दुखी हूँ', 'उदास हूँ',
                    'परेशान हूँ', 'तनाव में हूँ', 'थक गया', 'थकी हूँ', 'मज़ा करो',
                    'आनंद', 'खुश', 'मूड ऑफ', 'अच्छा नहीं लग रहा',
                    
                    # Mixed/Hinglish
                    'bore ho raha hu', 'boring', 'joke sunao', 'funny',
                    'sad', 'feeling sad', 'entertain me', 'make me laugh',
                    'mood off', 'stress', 'tired', 'need fun'
                ],
                'responses': [
                    "मैं समझ सकती हूँ कि आप bored महसूस कर रहे हैं! चलिए मज़ा करते हैं 😄\n\nयह लो एक joke: \"Why don't scientists trust atoms? Because they make up everything! 😄\"\n\nया शायद आप कोई interesting fact जानना चाहेंगे? या मैं आपको कोई fun activity suggest कर सकती हूँ!",
                    "I can see you need some entertainment! Let me brighten your day! 🌟\n\nHere's a joke for you: \"प्रोग्रामर का घर क्यों छोटा होता है? क्योंकि वो space को respect करते हैं! 🏠💻\"\n\nWant another joke, or would you prefer a fun fact to cheer you up?",
                    "Feeling down? Let me turn that frown upside down! 😊\n\n**Joke Time**: \"Why did the scarecrow win an award? Because he was outstanding in his field! 🌾\"\n\n**Fun Fact**: Did you know that octopuses have three hearts and blue blood? 🐙\n\nHow about we talk about something fun instead?",
                    "I'm here to cheer you up! 🎉\n\nLet me tell you something funny: \"Mathematics की सबसे बड़ी problem क्या है? Problem solving! 😂\"\n\nOr if you prefer, I can tell you about amazing space facts, cool science discoveries, or we can plan something fun! What sounds good to you?"
                ],
                'priority': 1,
                'examples': [
                    "I'm bored",
                    "बोर हो रहा हूँ",
                    "Tell me a joke",
                    "जोक सुनाओ",
                    "Feeling sad",
                    "दुखी हूँ",
                    "Entertain me"
                ]
            },
            
            # 5. Farewells Intent
            'goodbye': {
                'keywords': [
                    # English variations
                    'bye', 'goodbye', 'good bye', 'see you', 'see ya', 'later', 'farewell',
                    'take care', 'have a good day', 'have a good night', 'sweet dreams',
                    'talk to you later', 'catch you later', 'until next time', 'so long',
                    'good night', 'good evening', 'good afternoon', 'peace out', 'ciao',
                    
                    # Hindi variations
                    'बाय', 'गुडबाय', 'अलविदा', 'फिर मिलेंगे', 'बाद में मिलते हैं',
                    'अभी बात करते हैं', 'चलो बाद में मिलते हैं', 'ताता',
                    'फिर मिलना', 'जल्दी', 'शुभ रात्रि', 'शुभ रात',
                    'धन्यवाद', 'धन्यवाद', 'सुस्रीक्षल', 'अपना ख्याल रखना',
                    
                    # Mixed/Hinglish
                    'bye', 'goodbye', 'see you', 'tata', 'chal bad me milte hain',
                    'fir milenge', 'take care', 'good night', 'shubh raatri'
                ],
                'responses': [
                    "अलविदा! 🌟 बातचीत के लिए धन्यवाद। जब भी आपको मदद चाहिए, मैं हमेशा यहाँ हूँ। अपना अच्छा ख्याल रखें! 😊",
                    "Goodbye! It was great talking with you! 🌈 Remember, I'm always here when you need help. Take care and have a wonderful day! ✨",
                    "फिर मिलेंगे! 🎯 आपकी company का मज़ा आया। जल्दी बातचीत के लिए excited हूँ। अपना ध्यान रखें! 🙏",
                    "See you later! Thanks for chatting with me today! 😊 Feel free to come back anytime - I'm always here to help. Take care! 🌟",
                    "ताता! 👋 बातचीत के लिए धन्यवाद। मैं हमेशा available हूँ आपकी मदद के लिए। जल्दी! 🚀"
                ],
                'priority': 1,
                'examples': [
                    "Bye VANIE",
                    "अलविदा",
                    "See you later",
                    "फिर मिलेंगे",
                    "Good night",
                    "शुभ रात्रि"
                ]
            }
        }
    
    def _tokenize_and_clean(self, user_input: str) -> List[str]:
        """Tokenize user input and remove stop words"""
        words = user_input.lower().split()
        cleaned_words = []
        
        for word in words:
            # Remove punctuation and special characters
            word = re.sub(r'[^\w\s]', '', word)
            # Skip stop words and empty strings
            if word and word not in self.stop_words:
                cleaned_words.append(word)
        
        return cleaned_words
    
    def _calculate_intent_scores(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate scores for each intent based on keyword matches"""
        intent_scores = {}
        
        for intent, data in self.intent_dictionary.items():
            score = 0
            matched_keywords = []
            
            # Check each token against intent keywords
            for token in tokens:
                for keyword in data['keywords']:
                    # Check for exact match or partial match
                    if token == keyword.lower() or keyword.lower() in token or token in keyword.lower():
                        score += 1
                        matched_keywords.append(keyword)
            
            # Apply priority multiplier
            priority_multiplier = data.get('priority', 1)
            final_score = score * priority_multiplier
            
            if final_score > 0:
                intent_scores[intent] = {
                    'score': final_score,
                    'matched_keywords': matched_keywords,
                    'priority': priority_multiplier,
                    'confidence': min(final_score / len(data['keywords']), 1.0)
                }
        
        return intent_scores
    
    def _select_best_intents(self, intent_scores: Dict[str, float]) -> List[str]:
        """Select best intents - can return multiple for mixed inputs"""
        if not intent_scores:
            return []
        
        # Sort by score (descending)
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Return top intents (can handle multiple intents)
        top_intents = []
        max_score = sorted_intents[0][1]['score']
        
        # Include all intents with score >= 70% of max score
        for intent, score_data in sorted_intents:
            if score_data['score'] >= max_score * 0.7:
                top_intents.append(intent)
        
        return top_intents
    
    def _generate_multi_intent_response(self, intents: List[str], user_input: str) -> str:
        """Generate response when multiple intents are detected"""
        if len(intents) == 1:
            # Single intent - return standard response
            intent_data = self.intent_dictionary[intents[0]]
            return random.choice(intent_data['responses'])
        
        # Multiple intents - combine responses
        responses = []
        
        for intent in intents:
            intent_data = self.intent_dictionary[intent]
            
            # Get a shorter response for multi-intent situations
            full_response = random.choice(intent_data['responses'])
            
            # Extract first sentence or key phrase
            sentences = full_response.split('.')
            if sentences:
                short_response = sentences[0].strip()
                if len(short_response) > 100:
                    # Truncate if too long
                    short_response = short_response[:97] + "..."
                responses.append(short_response)
        
        # Combine responses naturally
        if len(responses) == 2:
            return f"{responses[0]}. {responses[1]}"
        else:
            return f"{responses[0]}. Also, {responses[1]}. And {responses[2]}"
    
    def analyze_and_respond(self, user_input: str, session_id: str = 'default') -> Dict[str, Any]:
        """Main analysis and response generation method"""
        
        # Step 1: Tokenize and clean user input
        tokens = self._tokenize_and_clean(user_input)
        
        # Step 2: Calculate intent scores
        intent_scores = self._calculate_intent_scores(tokens)
        
        # Step 3: Select best intents (can be multiple)
        best_intents = self._select_best_intents(intent_scores)
        
        # Step 4: Generate response
        if best_intents:
            response = self._generate_multi_intent_response(best_intents, user_input)
        else:
            # Fallback response
            response = "मैं अभी सीख रही हूँ! क्या आप मुझसे कोई joke सुनना चाहेंगे या आज का time जानना चाहेंगे? 😊"
        
        # Update session
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = []
        
        self.user_sessions[session_id].append({
            'user_input': user_input,
            'tokens': tokens,
            'intent_scores': intent_scores,
            'detected_intents': best_intents,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'response': response,
            'detected_intents': best_intents,
            'intent_scores': intent_scores,
            'tokens': tokens,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
    
    def demonstrate_mixed_input_processing(self, user_input: str) -> Dict[str, Any]:
        """Demonstrate how mixed input is processed"""
        print(f"\n🔍 Processing: '{user_input}'")
        print("=" * 50)
        
        # Tokenize
        tokens = self._tokenize_and_clean(user_input)
        print(f"📝 Tokens after cleaning: {tokens}")
        
        # Calculate scores
        intent_scores = self._calculate_intent_scores(tokens)
        print(f"\n📊 Intent Scores:")
        for intent, score_data in intent_scores.items():
            print(f"   {intent}: {score_data['score']} (confidence: {score_data['confidence']:.2f})")
            print(f"      Matched keywords: {score_data['matched_keywords']}")
        
        # Select best intents
        best_intents = self._select_best_intents(intent_scores)
        print(f"\n🎯 Selected Intents: {best_intents}")
        
        # Generate response
        response = self._generate_multi_intent_response(best_intents, user_input)
        print(f"\n💬 Generated Response: {response}")
        
        return {
            'input': user_input,
            'tokens': tokens,
            'intent_scores': intent_scores,
            'detected_intents': best_intents,
            'response': response
        }

# Initialize Flask App with CORS
app = Flask(__name__)
CORS(app)

# Initialize Intent Engine
vanie_intent = VANIEIntentEngine()

@app.route('/')
def index():
    """API Documentation"""
    return jsonify({
        'message': 'VANIE Expanded Intent Engine API',
        'version': '2.0.0',
        'intents': list(vanie_intent.intent_dictionary.keys()),
        'features': [
            'Multi-Keyword Detection',
            'Intent Scoring Algorithm',
            'Multi-Intent Handling',
            'Priority-Based Selection',
            'Context-Aware Responses'
        ],
        'endpoints': {
            '/chat': 'POST - Send message and get intent-based response',
            '/analyze': 'POST - Analyze text for intents only',
            '/intents': 'GET - Get all available intents',
            '/demonstrate': 'POST - Demonstrate mixed input processing'
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with intent recognition"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Analyze and generate response
        result = vanie_intent.analyze_and_respond(user_message, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text for intents without generating response"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Text is required',
                'status': 'error'
            }), 400
        
        text = data['text']
        tokens = vanie_intent._tokenize_and_clean(text)
        intent_scores = vanie_intent._calculate_intent_scores(tokens)
        best_intents = vanie_intent._select_best_intents(intent_scores)
        
        return jsonify({
            'text': text,
            'tokens': tokens,
            'intent_scores': intent_scores,
            'detected_intents': best_intents,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Analysis error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/intents', methods=['GET'])
def get_intents():
    """Get all available intents with their keywords"""
    return jsonify({
        'intents': vanie_intent.intent_dictionary,
        'total_intents': len(vanie_intent.intent_dictionary),
        'status': 'success'
    })

@app.route('/demonstrate', methods=['POST'])
def demonstrate():
    """Demonstrate mixed input processing"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Text is required',
                'status': 'error'
            }), 400
        
        text = data['text']
        result = vanie_intent.demonstrate_mixed_input_processing(text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Demonstration error: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("🚀 VANIE Expanded Intent Engine Starting...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 API Documentation: http://localhost:5000")
    print("🎯 Features:")
    print("   ✅ Multi-Keyword Detection")
    print("   ✅ Intent Scoring Algorithm")
    print("   ✅ Multi-Intent Handling")
    print("   ✅ Priority-Based Selection")
    print("   ✅ Context-Aware Responses")
    print("   ✅ Expanded Intent Dictionary")
    
    # Demonstrate mixed input processing
    print("\n" + "="*60)
    print("🧪 DEMONSTRATION: Mixed Input Processing")
    print("="*60)
    
    test_input = "Hello VANIE, kaise ho tum aur tumhe kisne banaya?"
    vanie_intent.demonstrate_mixed_input_processing(test_input)
    
    print("\n" + "="*60)
    print("🌐 Server starting on http://localhost:5000")
    print("📝 Try the /demonstrate endpoint with your own mixed inputs!")
    print("="*60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

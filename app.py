# VANIE Ultimate Chatbot Backend - Complete Solution
# Advanced Multi-Keyword Scoring Algorithm with Flask API and CORS

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
import math

class VANIEChatbot:
    """Advanced Chatbot with Multi-Keyword Scoring System"""
    
    def __init__(self):
        # Initialize comprehensive knowledge base with multi-keyword mapping
        self.knowledge_base = self._initialize_knowledge_base()
        self.stop_words = self._initialize_stop_words()
        self.conversation_context = []
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
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Comprehensive knowledge base with multi-keyword mapping"""
        return {
            # Greetings Category
            'greetings': {
                'keywords': [
                    'hello', 'hi', 'namaste', 'hey', 'good morning', 'good evening', 'good afternoon',
                    'नमस्ते', 'हाय', 'नमस्कार', 'प्रणाम', 'सुप्रभात', 'शुभ प्रभात', 'राम राम',
                    'how are you', 'kaise ho', 'aap kaise ho', 'what\'s up', 'kya haal hai',
                    'greetings', 'welcome', 'स्वागत'
                ],
                'responses': [
                    "नमस्ते! 🙏 मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। आपकी हर तरह की मदद के लिए तैयार हूँ। आज क्या काम है?",
                    "Hello! I'm VANIE - your advanced virtual assistant. How can I help you today? 😊",
                    "नमस्ते दोस्त! मैं आपकी सेवा के लिए यहाँ हूँ। क्या पूछना चाहते हैं? 🙏",
                    "Hi there! I'm VANIE, ready to assist you! What can I do for you? 🤖"
                ],
                'priority': 1
            },
            
            # Coding & Programming Category
            'coding': {
                'keywords': [
                    'python', 'code', 'programming', 'algorithm', 'debug', 'javascript', 'java', 'cpp',
                    'function', 'class', 'variable', 'loop', 'array', 'list', 'dictionary', 'recursion',
                    'web development', 'app development', 'software', 'development', 'bug', 'error',
                    'syntax', 'logic', 'data structure', 'api', 'database', 'framework',
                    'प्रोग्राम', 'फंक्शन', 'वेरिएबल', 'कोड लिखना', 'एरर', 'लॉप', 'प्रिंट', 'कंपाइल',
                    'coding', 'coding help', 'programming help', 'software development'
                ],
                'responses': [
                    "मैं प्रोग्रामिंग में विशेषज हूँ! Python, JavaScript, Java, C++, Web Development - कोई भी भाषा या टेक्सोलॉजी में मदद कर सकती हूँ। किस भी प्रोग्रामिंग या टेक्सोलॉजी में चाहिए? 💻",
                    "I'm an expert programmer! Python, JavaScript, Java, C++, React, Node.js - What specific coding challenge are you facing? 🚀",
                    "प्रोग्रामिंग के बारे में आपकी क्या मदद करूँ? Algorithm design, debugging, data structures, web development, या कोई specific project? 🎯",
                    "Coding is my passion! From basic algorithms to complex systems, I can help with any programming challenge. What's your coding question? 👨‍💻"
                ],
                'priority': 2
            },
            
            # Science & Technology Category
            'science': {
                'keywords': [
                    'science', 'physics', 'chemistry', 'biology', 'quantum', 'space', 'technology',
                    'chemistry', 'physics', 'biology', 'विज्ञान', 'भौतिक', 'रसायन',
                    'astronomy', 'astrophysics', 'quantum mechanics', 'relativity', 'evolution', 'genetics',
                    'scientific method', 'research', 'experiment', 'theory', 'hypothesis', 'discovery',
                    'विज्ञान', 'तकनीक', 'गणित', 'भौतिक', 'प्रयोग', 'खोज', 'आणव', 'रसायन',
                    'scientific', 'technology', 'research', 'experiment'
                ],
                'responses': [
                    "विज्ञान बहुत ही रोचक है! Physics, Chemistry, Biology, Quantum Mechanics, Astronomy - किस भी scientific field में जानकारी चाहिए? 🧪",
                    "Science fascinates me! From quantum physics to space exploration, from chemistry to biology - what scientific topic interests you most? 🔬",
                    "मैं विज्ञान और तकनीक के बारे में जानकारी रखती हूँ। कौन सा वैज्ञानिक topic या discovery के बारे में जानना चाहिए? 🧬",
                    "Scientific inquiry! I can discuss physics, chemistry, biology, astronomy, and more. What specific scientific concept would you like to explore? 🔬"
                ],
                'priority': 2
            },
            
            # Mathematics Category
            'math': {
                'keywords': [
                    'math', 'mathematics', 'algebra', 'calculus', 'geometry', 'statistics', 'गणित',
                    'trigonometry', 'linear algebra', 'differential equations', 'probability', 'number theory',
                    'calculation', 'formula', 'equation', 'solve', 'graph', 'function', 'integral',
                    'derivative', 'matrix', 'vector', 'coordinate', 'theorem', 'proof',
                    'जोड़', 'गुणा', 'भाग', 'गुणा', 'वर्ग', 'प्रश्न', 'फलक',
                    'math help', 'solve math', 'math problem', 'calculate'
                ],
                'responses': [
                    "गणित logic और patterns का study है। Algebra, Calculus, Geometry, Statistics, Trigonometry - किस भी branch में मदद कर सकती हूँ। क्या solve करना है? 🧮",
                    "Mathematics is the language of the universe! From basic arithmetic to advanced calculus, linear algebra to number theory - I can help with any math problem! 📐",
                    "गणित के किसी भी branch में मदद कर सकती हूँ। Differential equations, probability theory, statistics - आप क्या challenge कर रहे हैं? 🔢",
                    "Mathematical thinking! I love solving complex problems. Whether it's algebra, calculus, geometry, or advanced mathematics - what's your mathematical question? 🧮"
                ],
                'priority': 2
            },
            
            # History Category
            'history': {
                'keywords': [
                    'history', 'historical', 'ancient', 'medieval', 'modern', 'india', 'gupta', 'maurya', 'इतिहास',
                    'civilization', 'empire', 'dynasty', 'revolution', 'war', 'culture', 'archaeology',
                    'freedom movement', 'independence', 'colonial', 'medieval period', 'renaissance',
                    'world war', 'cold war', 'indian history', 'mughal', 'british raj',
                    'इतिहास', 'सम्राज्य', 'गुप्त', 'राज', 'महाभारत', 'सिंध', 'मराठ', 'दिल्ली',
                    'historical', 'ancient history', 'modern history', 'cultural history'
                ],
                'responses': [
                    "इतिहास हमें अपने past से सिखाता है। Ancient civilizations से लेके modern era तक, क्या जानना चाहिए? 📚",
                    "History connects us to our roots! From Indus Valley to modern India, from ancient Egypt to space age - what historical period fascinates you? 🏛️",
                    "भारत का इतिहास बहुत समृद्ध है! Mauryan Empire, Gupta Dynasty, Delhi Sultanate, Mughal Empire, British Raj, Freedom Struggle - कौन से काल जानना चाहिए? 🇮🇳",
                    "Historical inquiry! I can discuss ancient civilizations, medieval periods, modern history, and cultural movements. What specific historical topic interests you? 🏛️"
                ],
                'priority': 2
            },
            
            # Help & Support Category
            'help': {
                'keywords': [
                    'help', 'support', 'how to', 'tutorial', 'guide', 'मदद', 'सहायता',
                    'explain', 'definition', 'meaning', 'what is', 'describe', 'clarify',
                    'instructions', 'steps', 'process', 'method', 'technique', 'approach',
                    'assist', 'assistance', 'guidance', 'help me', 'can you help'
                ],
                'responses': [
                    "मैं आपकी हर तरह की मदद के लिए यहाँ हूँ! Coding, Science, History, Math, explanations - कुछ भी पूछिये! 🙏",
                    "I'm here to help! You can ask me about coding, science, history, math, or anything else! What specific assistance do you need? 🤝",
                    "आप मुझसे कुछ भी पूछ सकते हैं! मैं आपकी पूरी सहायता करूँगी। क्या जानना चाहते हैं? 💡",
                    "Help is my middle name! Whether you need step-by-step instructions, explanations, or guidance - I'm here to assist you thoroughly! 📖"
                ],
                'priority': 1
            },
            
            # General Conversation Category
            'general': {
                'keywords': [
                    'how are you', 'what is your name', 'who are you', 'thank you', 'bye', 'goodbye',
                    'what can you do', 'your capabilities', 'features', 'abilities', 'skills',
                    'who created you', 'your purpose', 'your mission', 'tell me about yourself',
                    'कैसे हो', 'क्या हो', 'आप कैसे हो', 'आप कैसी हैं', 'आपका नाम क्या है',
                    'vanie', 'chatbot', 'ai assistant', 'virtual assistant'
                ],
                'responses': [
                    "मैं बिल्कुल ठीक हूँ! आपकी मदद करके मुझे खुशी होती है। आज क्या करें? 😊",
                    "I'm doing great, thank you for asking! I'm VANIE - Virtual Assistant of Neural Integrated Engine, ready to help you! 🌟",
                    "धन्यवाद! आपकी मदद करके मुझे खुशी होती है। और कुछ मदद करूँ? 🙏",
                    "I'm VANIE, your advanced AI assistant! I can help with coding, science, history, math, and much more. What would you like to explore? 🤖"
                ],
                'priority': 1
            }
        }
    
    def _tokenize_and_clean(self, user_input: str) -> List[str]:
        """Tokenize user input and remove stop words"""
        # Convert to lowercase and split into words
        words = user_input.lower().split()
        
        # Remove punctuation and special characters
        cleaned_words = []
        for word in words:
            # Remove punctuation
            word = re.sub(r'[^\w\s]', '', word)
            # Skip stop words and empty strings
            if word and word not in self.stop_words:
                cleaned_words.append(word)
        
        return cleaned_words
    
    def _calculate_keyword_scores(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate scores for each category based on keyword matches"""
        category_scores = {}
        
        for category, data in self.knowledge_base.items():
            score = 0
            matched_keywords = []
            
            # Check each token against category keywords
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
                category_scores[category] = {
                    'score': final_score,
                    'matched_keywords': matched_keywords,
                    'priority': priority_multiplier
                }
        
        return category_scores
    
    def _select_best_category(self, category_scores: Dict[str, float]) -> Optional[str]:
        """Select the best category based on highest score"""
        if not category_scores:
            return None
        
        # Sort by score (descending)
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Return the category with highest score
        return sorted_categories[0][0]
    
    def _get_contextual_response(self, category: str, user_input: str, tokens: List[str], category_scores: Dict[str, float]) -> str:
        """Generate contextual response based on category and user input"""
        if category not in self.knowledge_base:
            return self._get_fallback_response()
        
        responses = self.knowledge_base[category]['responses']
        base_response = random.choice(responses)
        
        # Add contextual information based on specific keywords
        input_lower = user_input.lower()
        
        # Python specific responses
        if 'python' in tokens:
            python_topics = ['algorithm', 'data structure', 'function', 'class', 'module', 'library', 'framework', 'debugging']
            for topic in python_topics:
                if topic in input_lower:
                    return f"Python {topic} के बारे में मैं आपकी मदद कर सकती हूँ। क्या specifically जानना चाहिए? 🐍 {base_response}"
        
        # Algorithm specific responses
        if 'algorithm' in tokens:
            complexity = self._estimate_algorithm_complexity(user_input)
            return f"Algorithm complexity O({complexity}) है। Detailed explanation चाहिए? 🔄 {base_response}"
        
        # Science specific responses
        if any(science in tokens for science in ['physics', 'chemistry', 'biology', 'quantum']):
            return f"विज्ञान के बारे में बहुत interesting है! {base_response}"
        
        # Math specific responses
        if 'math' in tokens:
            math_topics = ['algebra', 'calculus', 'geometry', 'statistics', 'trigonometry']
            for topic in math_topics:
                if topic in input_lower:
                    return f"Mathematics में {topic} solve करना है? मैं help कर सकती हूँ। 🔢 {base_response}"
        
        return base_response
    
    def _estimate_algorithm_complexity(self, user_input: str) -> str:
        """Estimate algorithm complexity based on keywords"""
        if 'linear' in user_input.lower() or 'search' in user_input.lower():
            return 'O(n)'
        elif 'binary' in user_input.lower() or 'log' in user_input.lower():
            return 'O(log n)'
        elif 'quicksort' in user_input.lower() or 'mergesort' in user_input.lower():
            return 'O(n log n)'
        elif 'nested' in user_input.lower() or 'exponential' in user_input.lower():
            return 'O(2^n)'
        else:
            return 'O(n)'
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when no category matches"""
        fallback_responses = [
            "यह एक interesting question है! मैं इसका detailed analysis कर रही हूँ। थोड़ा context दीजिए? 💭",
            "Interesting question! I'm analyzing this. Could you provide a bit more context? 🤔",
            "मैं आपकी मदद के लिए यहाँ हूँ! कोडिंग, विज्ञान, इतिहास, गणित - कुछ भी पूछिये! 🙏",
            "Let me help you with that! I can provide more detailed information if you'd like. 📚"
        ]
        return random.choice(fallback_responses)
    
    def _update_context(self, user_input: str, ai_response: str, category: Optional[str] = None):
        """Update conversation context"""
        context_entry = {
            'user_input': user_input,
            'ai_response': ai_response,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversation_context.append(context_entry)
        
        # Keep last 10 messages for context
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
    
    def generate_response(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Main response generation method with multi-keyword scoring"""
        
        # Step 1: Tokenize and clean user input
        tokens = self._tokenize_and_clean(user_input)
        
        # Step 2: Calculate keyword scores for each category
        category_scores = self._calculate_keyword_scores(tokens)
        
        # Step 3: Select best category based on highest score
        best_category = self._select_best_category(category_scores)
        
        # Step 4: Generate contextual response
        if best_category:
            response = self._get_contextual_response(best_category, user_input, tokens, category_scores)
        else:
            response = self._get_fallback_response()
        
        # Step 5: Update context
        self._update_context(user_input, response, best_category)
        
        # Step 6: Store in session if provided
        if session_id:
            if session_id not in self.user_sessions:
                self.user_sessions[session_id] = []
            self.user_sessions[session_id].append({
                'user_input': user_input,
                'ai_response': response,
                'category': best_category,
                'timestamp': datetime.now().isoformat()
            })
        
        # Return comprehensive response
        return {
            'response': response,
            'category': best_category,
            'confidence': category_scores[best_category]['score'] if best_category and best_category in category_scores else 0,
            'matched_keywords': category_scores[best_category]['matched_keywords'] if best_category and best_category in category_scores else [],
            'tokens': tokens,
            'category_scores': category_scores,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }

# Initialize Flask App with CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Chatbot
vanie_chatbot = VANIEChatbot()

@app.route('/')
def index():
    """API Documentation"""
    return jsonify({
        'message': 'VANIE Chatbot API',
        'version': '1.0.0',
        'endpoints': {
            '/chat': 'POST - Send message and get response',
            '/history': 'GET - Get conversation history',
            '/clear': 'DELETE - Clear conversation context',
            '/health': 'GET - Check API health'
        },
        'features': [
            'Multi-keyword scoring',
            'Stop word filtering',
            'Contextual responses',
            'Session management',
            'CORS enabled'
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with multi-keyword scoring"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Generate response using multi-keyword scoring
        result = vanie_chatbot.generate_response(user_message, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        session_id = request.args.get('session_id', 'default')
        
        if session_id in vanie_chatbot.user_sessions:
            history = vanie_chatbot.user_sessions[session_id]
        else:
            history = vanie_chatbot.conversation_context
        
        return jsonify({
            'history': history,
            'session_id': session_id,
            'total_messages': len(history),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving history: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/clear', methods=['DELETE'])
def clear_context():
    """Clear conversation context"""
    try:
        session_id = request.args.get('session_id', 'default')
        
        vanie_chatbot.conversation_context = []
        if session_id in vanie_chatbot.user_sessions:
            vanie_chatbot.user_sessions[session_id] = []
        
        return jsonify({
            'message': 'Conversation context cleared successfully',
            'session_id': session_id,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error clearing context: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VANIE Chatbot API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'multi_keyword_scoring': True,
            'stop_word_filtering': True,
            'contextual_responses': True,
            'session_management': True,
            'cors_enabled': True,
            'total_categories': len(vanie_chatbot.knowledge_base.keys())
        }
    })

if __name__ == '__main__':
    print("🚀 VANIE Chatbot Backend Starting...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 API Documentation: http://localhost:5000")
    print("🎯 Features: Multi-keyword scoring, Stop word filtering, Contextual responses")
    print("🌐 CORS enabled for frontend communication")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

# VANIE AI Backend - Complete Python Implementation
# Virtual Assistant of Neural Integrated Engine

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

class VANIEAI:
    """Advanced AI Backend for VANIE Web Application"""
    
    def __init__(self):
        # Initialize keyword-response mappings
        self.knowledge_base = self._initialize_knowledge_base()
        self.conversation_context = []
        self.user_sessions = {}
        
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize comprehensive knowledge base with keyword mappings"""
        return {
            # Greetings
            'greetings': {
                'keywords': ['hello', 'hi', 'namaste', 'hey', 'good morning', 'good evening', 'good afternoon', 'नमस्ते', 'हाय', 'नमस्कार'],
                'responses': [
                    "नमस्ते! 🙏 मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। आपकी हर तरह की मदद के लिए तैयार हूँ।",
                    "Hello! I'm VANIE - your virtual assistant. How can I help you today? 😊",
                    "नमस्ते दोस्त! मैं आपकी सेवा के लिए यहाँ हूँ। क्या काम है? 🙏",
                    "Hi there! I'm VANIE, ready to assist you! What can I do for you? 🤖"
                ]
            },
            
            # Coding & Programming
            'coding': {
                'keywords': ['python', 'code', 'programming', 'algorithm', 'debug', 'javascript', 'java', 'cpp', 'coding', 'कोड', 'प्रोग्रामिंग'],
                'responses': [
                    "मैं प्रोग्रामिंग में विशेषज हूँ! Python, JavaScript, Java, C++ - कोई भाषा में मदद कर सकती हूँ। विशिष्ट प्रोग्रामिंग भाषा बताएं? 💻",
                    "I'm proficient in multiple programming languages! Python, JavaScript, Java, C++, and more. What specific coding help do you need? 👨‍💻",
                    "प्रोग्रामिंग के बारे में आपकी क्या मदद करूँ? Algorithm design, debugging, या कोई specific language? 🚀"
                ]
            },
            
            # Science & Technology
            'science': {
                'keywords': ['science', 'physics', 'chemistry', 'biology', 'quantum', 'space', 'technology', 'विज्ञान', 'भौतिक'],
                'responses': [
                    "विज्ञान बहुत ही रोचक है! Physics, Chemistry, Biology - किस टॉपिक पर जानकारी चाहिए? 🧪",
                    "Science fascinates me! From quantum physics to space exploration, what scientific topic interests you? 🔬",
                    "मैं विज्ञान और तकनीक के बारे में जानकारी रखती हूँ। कौन सा विषय जानना चाहते हैं? 🧬"
                ]
            },
            
            # Mathematics
            'math': {
                'keywords': ['math', 'mathematics', 'algebra', 'calculus', 'geometry', 'statistics', 'गणित'],
                'responses': [
                    "गणित logic और patterns का study है। Addition से लेकर calculus तक, क्या solve करना है? 🧮",
                    "Mathematics is the language of the universe! From basic arithmetic to advanced calculus, I can help with any math problem! 📐",
                    "गणित के किसी भी क्षेत्र में मदद कर सकती हूँ। Algebra, Geometry, Calculus - आप क्या सीखना चाहते हैं? 🔢"
                ]
            },
            
            # History
            'history': {
                'keywords': ['history', 'historical', 'ancient', 'medieval', 'modern', 'india', 'gupta', 'maurya', 'इतिहास'],
                'responses': [
                    "इतिहास हमें अपने past से सिखाता है। Ancient civilizations से लेके modern era तक, क्या जानना चाहिए? 📚",
                    "History connects us to our roots! From ancient civilizations to modern times, what historical period interests you? 🏛️",
                    "भारत का इतिहास बहुत समृद्ध है - Indus Valley Civilization से लेके modern India तक! कौन समय की बात करनी है? 🇮🇳"
                ]
            },
            
            # Help & Support
            'help': {
                'keywords': ['help', 'support', 'how to', 'tutorial', 'guide', 'मदद', 'सहायता'],
                'responses': [
                    "मैं आपकी हर तरह की मदद के लिए यहाँ हूँ! Coding, Science, History, Math - कुछ भी पूछिये! 🙏",
                    "I'm here to help! You can ask me about coding, science, history, math, or anything else! What do you need assistance with? 🤝",
                    "आप मुझसे कुछ भी पूछ सकते हैं! मैं आपकी पूरी सहायता करूँगी। क्या जानना चाहते हैं? 💡"
                ]
            },
            
            # General Conversation
            'general': {
                'keywords': ['how are you', 'what is your name', 'who are you', 'thank you', 'bye', 'goodbye'],
                'responses': [
                    "मैं बिल्कुल ठीक हूँ! आपकी मदद करके मुझे खुशी होती है। आज क्या करें? 😊",
                    "I'm doing great, thank you for asking! I'm here to help you with whatever you need! 🌟",
                    "धन्यवाद! आपकी मदद के लिए समय देने में खुशी हूँ। और कुछ मदद करूँ? 🙏"
                ]
            }
        }
    
    def _analyze_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input and extract keywords"""
        input_lower = user_input.lower()
        matched_keywords = []
        confidence_scores = {}
        
        # Check each category for keyword matches
        for category, data in self.knowledge_base.items():
            category_score = 0
            matched_words = []
            
            for keyword in data['keywords']:
                if keyword.lower() in input_lower:
                    category_score += 1
                    matched_words.append(keyword)
                    # Calculate confidence based on position and completeness
                    keyword_position = input_lower.find(keyword.lower())
                    if keyword_position != -1:
                        confidence = 1.0 - (keyword_position / len(input_lower))
                        confidence_scores[category] = max(confidence_scores.get(category, 0), confidence)
            
            if category_score > 0:
                matched_keywords.append({
                    'category': category,
                    'score': category_score,
                    'matched_words': matched_words,
                    'confidence': confidence_scores.get(category, 0)
                })
        
        return {
            'matched_keywords': matched_keywords,
            'input_length': len(user_input),
            'has_multiple_keywords': len(matched_keywords) > 1
        }
    
    def _select_best_category(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Select the best matching category based on analysis"""
        if not analysis['matched_keywords']:
            return None
        
        # Sort by score and confidence
        sorted_matches = sorted(
            analysis['matched_keywords'], 
            key=lambda x: (x['score'], x['confidence']), 
            reverse=True
        )
        
        return sorted_matches[0]['category']
    
    def _get_contextual_response(self, category: str, user_input: str) -> str:
        """Get contextual response based on category and input"""
        if category not in self.knowledge_base:
            return self._get_fallback_response()
        
        responses = self.knowledge_base[category]['responses']
        
        # Add contextual information based on specific keywords
        if 'python' in user_input.lower():
            return random.choice(responses) + " Python में specifically क्या बनाना है? 🐍"
        elif 'algorithm' in user_input.lower():
            return random.choice(responses) + " कौन सा algorithm समझना है? Sorting, searching, ya graph traversal? 🔄"
        elif 'quantum' in user_input.lower():
            return random.choice(responses) + " Quantum computing या quantum physics के बारे में? ⚛️"
        elif 'gupta' in user_input.lower() or 'maurya' in user_input.lower():
            return random.choice(responses) + " Ancient India के कौन से विशेष रूप से जानना चाहिए? 🏛️"
        
        return random.choice(responses)
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when no keywords match"""
        fallback_responses = [
            "यह एक दिलचस्प सवाल है! क्या आप थोड़ा और detail दे सकते हैं? 🤔",
            "Interesting question! मैं आपकी बेहतर समझने की कोशिश कर रही हूँ। कृपया अपना सवाल थोड़ा elaborate करें। 💭",
            "मुझे समझ में आ रहा है! आप किस विषय पर चर्चा कर रहे हैं? मैं पूरी तरह से मदद करूँगी। 🌟",
            "यह एक अच्छा विषय है! क्या आप इसके बारे में और जानना चाहते हैं? मैं विस्तृत जानकारी दे सकती हूँ। 📚",
            "मैं आपकी मदद के लिए यहाँ हूँ! कोडिंग, विज्ञान, इतिहास, गणित - कुछ भी पूछिये! 🙏"
        ]
        
        return random.choice(fallback_responses)
    
    def _update_context(self, user_input: str, ai_response: str, category: Optional[str] = None):
        """Update conversation context for better responses"""
        self.conversation_context.append({
            'user_input': user_input,
            'ai_response': ai_response,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 messages for context
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
    
    def generate_response(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Main method to generate AI response"""
        
        # Analyze the input
        analysis = self._analyze_input(user_input)
        
        # Select best category
        best_category = self._select_best_category(analysis)
        
        # Generate response
        if best_category:
            response = self._get_contextual_response(best_category, user_input)
        else:
            response = self._get_fallback_response()
        
        # Update context
        self._update_context(user_input, response, best_category)
        
        # Store in session if provided
        if session_id:
            if session_id not in self.user_sessions:
                self.user_sessions[session_id] = []
            self.user_sessions[session_id].append({
                'user_input': user_input,
                'ai_response': response,
                'timestamp': datetime.now().isoformat()
            })
        
        return {
            'response': response,
            'category': best_category,
            'confidence': analysis['matched_keywords'][0]['confidence'] if analysis['matched_keywords'] else 0,
            'matched_keywords': [kw['matched_words'] for kw in analysis['matched_keywords']] if analysis['matched_keywords'] else [],
            'context_length': len(self.conversation_context)
        }
    
    def get_conversation_history(self, session_id: Optional[str] = None) -> List[Dict]:
        """Get conversation history"""
        if session_id and session_id in self.user_sessions:
            return self.user_sessions[session_id]
        return self.conversation_context
    
    def clear_context(self, session_id: Optional[str] = None):
        """Clear conversation context"""
        self.conversation_context = []
        if session_id and session_id in self.user_sessions:
            self.user_sessions[session_id] = []

# Flask Web Application
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize AI
vanie_ai = VANIEAI()

@app.route('/')
def index():
    """Main endpoint - returns API documentation"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>VANIE AI Backend API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        .method { color: #007bff; font-weight: bold; }
        .url { color: #e83e8c; font-family: monospace; }
        .description { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 VANIE AI Backend API</h1>
        <h2>Virtual Assistant of Neural Integrated Engine</h2>
        
        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/chat</div>
            <div class="description">Send message and get AI response</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/history</div>
            <div class="description">Get conversation history</div>
        </div>
        
        <div class="endpoint">
            <div class="method">DELETE</div>
            <div class="url">/api/clear</div>
            <div class="description">Clear conversation context</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/health</div>
            <div class="description">Check API health status</div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Generate AI response
        result = vanie_ai.generate_response(user_message, session_id)
        
        return jsonify({
            'response': result['response'],
            'category': result['category'],
            'confidence': result['confidence'],
            'matched_keywords': result['matched_keywords'],
            'context_length': result['context_length'],
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        session_id = request.args.get('session_id', 'default')
        history = vanie_ai.get_conversation_history(session_id)
        
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

@app.route('/api/clear', methods=['DELETE'])
def clear_context():
    """Clear conversation context"""
    try:
        session_id = request.args.get('session_id', 'default')
        vanie_ai.clear_context(session_id)
        
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VANIE AI Backend',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'keyword_matching': True,
            'context_awareness': True,
            'multi_language': True,
            'session_management': True
        }
    })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available categories and keywords"""
    try:
        categories = {}
        for cat_name, cat_data in vanie_ai.knowledge_base.items():
            categories[cat_name] = {
                'keywords': cat_data['keywords'],
                'response_count': len(cat_data['responses'])
            }
        
        return jsonify({
            'categories': categories,
            'total_categories': len(categories),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving categories: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("🤖 VANIE AI Backend Starting...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 API Documentation: http://localhost:5000")
    print("🎯 Ready to handle conversations!")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

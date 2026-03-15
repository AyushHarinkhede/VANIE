# VANIE Enhanced Python Backend - Hindi Algorithm
# Advanced AI with comprehensive Hindi keyword matching and intelligent responses

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
import math

class VANIEAI:
    """Advanced AI Backend for VANIE Web Application with Hindi Support"""
    
    def __init__(self):
        # Initialize comprehensive knowledge base with Hindi keywords
        self.knowledge_base = self._initialize_hindi_knowledge_base()
        self.conversation_context = []
        self.user_sessions = {}
        self.response_templates = self._initialize_response_templates()
        
    def _initialize_hindi_knowledge_base(self) -> Dict[str, Any]:
        """Initialize comprehensive knowledge base with Hindi and English keywords"""
        return {
            # Greetings (Enhanced with Hindi)
            'greetings': {
                'keywords': [
                    'hello', 'hi', 'namaste', 'hey', 'good morning', 'good evening', 'good afternoon', 
                    'नमस्ते', 'हाय', 'नमस्कार', 'प्रणाम', 'सुप्रभात', 'शुभ प्रभात', 'राम राम', 
                    'कैसे हो', 'क्या हो', 'आप कैसे हो', 'कैसी हैं', 'दिन मुझे', 
                    'how are you', 'kaise ho', 'aap kaise ho', 'what\'s up', 'kya haal hai'
                ],
                'responses': [
                    "नमस्ते! 🙏 मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। आपकी हर तरह की मदद के लिए तैयार हूँ। आज क्या काम है?",
                    "Hello! I'm VANIE - your advanced virtual assistant. How can I help you today? 😊",
                    "नमस्ते दोस्त! मैं आपकी सेवा के लिए यहाँ हूँ। क्या पूछना चाहते हैं? 🙏",
                    "Hi there! I'm VANIE, ready to assist you! What can I do for you? 🤖",
                    "प्रणाम! आप कैसे हो? मैं आपकी हर समस्या का समाधान करने के लिए यहाँ हूँ। क्या मदद कर सकती हूँ। ✨"
                ]
            },
            
            # Coding & Programming (Enhanced with Hindi)
            'coding': {
                'keywords': [
                    'python', 'code', 'programming', 'algorithm', 'debug', 'javascript', 'java', 'cpp', 'coding', 'कोड', 'प्रोग्रामिंग',
                    'function', 'class', 'variable', 'loop', 'array', 'list', 'dictionary', 'recursion',
                    'web development', 'app development', 'software', 'development', 'bug', 'error',
                    'syntax', 'logic', 'data structure', 'api', 'database', 'framework',
                    'प्रोग्राम', 'फंक्शन', 'वेरिएबल', 'कोड लिखना', 'एरर', 'लॉप', 'प्रिंट', 'कंपाइल', '�ेटा बेस'
                ],
                'responses': [
                    "मैं प्रोग्रामिंग में विशेषज हूँ! Python, JavaScript, Java, C++, Web Development - कोई भी भाषा या टेक्सोलॉजी में मदद कर सकती हूँ। किस भी प्रोग्रामिंग या टेक्सोलॉजी में चाहिए? 💻",
                    "I'm an expert programmer! Python, JavaScript, Java, C++, React, Node.js - आप कोई भी भाषा में कोई भी प्रोग्रामिंग चुनौती है? What specific coding challenge are you facing? 🚀",
                    "प्रोग्रामिंग के बारे में आपकी क्या मदद करूँ? Algorithm design, debugging, data structures, web development, या कोई specific project? 🎯",
                    "Coding is my passion! From basic algorithms to complex systems, I can help with any programming challenge. What's your coding question? 👨‍💻",
                    "मैं full-stack development में माहिर हूँ! Frontend, backend, database, deployment - सब कुछ संभल सकती हूँ। कौन सा project बना रहे हैं? 🌐"
                ]
            },
            
            # Science & Technology (Enhanced with Hindi)
            'science': {
                'keywords': [
                    'science', 'physics', 'chemistry', 'biology', 'quantum', 'space', 'technology', 'विज्ञान', 'भौतिक',
                    'chemistry', 'रसायन', 'physics', 'भौतिक विज्ञान', 'biology', 'जीव विज्ञान',
                    'astronomy', 'astrophysics', 'quantum mechanics', 'relativity', 'evolution', 'genetics',
                    'scientific method', 'research', 'experiment', 'theory', 'hypothesis', 'discovery',
                    'विज्ञान', 'तकनीक', 'गणित', '�ौतिक', 'प्रयोग', 'खोज', 'आणव', 'रसायन'
                ],
                'responses': [
                    "विज्ञान बहुत ही रोचक है! Physics, Chemistry, Biology, Quantum Mechanics, Astronomy - किस भी scientific field में जानकारी चाहिए? 🧪",
                    "Science fascinates me! From quantum physics to space exploration, from chemistry to biology - what scientific topic interests you most? 🔬",
                    "मैं विज्ञान और तकनीक के बारे में जानकारी रखती हूँ। कौन सा वैज्ञानिक topic या discovery के बारे में जानना चाहिए? 🧬",
                    "Scientific inquiry! I can discuss physics, chemistry, biology, astronomy, and more. What specific scientific concept would you like to explore? 🔬",
                    "From Newton's laws to quantum mechanics, from DNA to space exploration - science is endless! What's your scientific question? 🌌"
                ]
            },
            
            # Mathematics (Enhanced with Hindi)
            'math': {
                'keywords': [
                    'math', 'mathematics', 'algebra', 'calculus', 'geometry', 'statistics', 'गणित',
                    'trigonometry', 'linear algebra', 'differential equations', 'probability', 'number theory',
                    'calculation', 'formula', 'equation', 'solve', 'graph', 'function', 'integral',
                    'derivative', 'matrix', 'vector', 'coordinate', 'theorem', 'proof',
                    'जोड़', 'गुणा', 'भाग', 'गुणा', 'वर्ग', 'प्रश्न', 'फलक'
                ],
                'responses': [
                    "गणित logic और patterns का study है। Algebra, Calculus, Geometry, Statistics, Trigonometry - किस भी branch में मदद कर सकती हूँ। क्या solve करना है? 🧮",
                    "Mathematics is the language of the universe! From basic arithmetic to advanced calculus, linear algebra to number theory - I can help with any math problem! 📐",
                    "गणित के किसी भी branch में मदद कर सकती हूँ। Differential equations, probability theory, statistics - आप क्या challenge कर रहे हैं? 🔢",
                    "Mathematical thinking! I love solving complex problems. Whether it's algebra, calculus, geometry, or advanced mathematics - what's your mathematical question? 🧮",
                    "From Pythagoras to Einstein, from basic arithmetic to quantum mathematics - I'm here to help you understand and solve any mathematical concept! 📊"
                ]
            },
            
            # History (Enhanced with Hindi)
            'history': {
                'keywords': [
                    'history', 'historical', 'ancient', 'medieval', 'modern', 'india', 'gupta', 'maurya', 'इतिहास',
                    'civilization', 'empire', 'dynasty', 'revolution', 'war', 'culture', 'archaeology',
                    'freedom movement', 'independence', 'colonial', 'medieval period', 'renaissance',
                    'world war', 'cold war', 'indian history', 'mughal', 'british raj',
                    'इतिहास', 'सम्राज्य', 'गुप्त', 'राज', 'महाभारत', 'सिंध', 'मराठ', 'दिल्ली', 'शासक', 'बादशाही'
                ],
                'responses': [
                    "इतिहास हमें अपने past से सिखाता है। Ancient civilizations से लेके modern era तक, क्या जानना चाहिए? 📚",
                    "History connects us to our roots! From Indus Valley to modern India, from ancient Egypt to space age - what historical period fascinates you? 🏛️",
                    "भारत का इतिहास बहुत समृद्ध है! Mauryan Empire, Gupta Dynasty, Delhi Sultanate, Mughal Empire, British Raj, Freedom Struggle - कौन से काल जानना चाहिए? 🇮🇳",
                    "Historical inquiry! I can discuss ancient civilizations, medieval periods, modern history, and cultural movements. What specific historical topic interests you? 🏛️",
                    "From stone tools to space exploration, human history is a fascinating journey! What aspect of history would you like to explore? 📜"
                ]
            },
            
            # Help & Support (Enhanced with Hindi)
            'help': {
                'keywords': [
                    'help', 'support', 'how to', 'tutorial', 'guide', 'मदद', 'सहायता',
                    'explain', 'definition', 'meaning', 'what is', 'describe', 'clarify',
                    'instructions', 'steps', 'process', 'method', 'technique', 'approach'
                ],
                'responses': [
                    "मैं आपकी हर तरह की मदद के लिए यहाँ हूँ! Coding, Science, History, Math, explanations - कुछ भी पूछिये! 🙏",
                    "I'm here to help! You can ask me about coding, science, history, math, or anything else! What specific assistance do you need? 🤝",
                    "आप मुझसे कुछ भी पूछ सकते हैं! मैं आपकी पूरी सहायता करूँगी। क्या जानना चाहते हैं? 💡",
                    "Help is my middle name! Whether you need step-by-step instructions, explanations, or guidance - I'm here to assist you thoroughly! 📖"
                ]
            },
            
            # General Conversation (Enhanced with Hindi)
            'general': {
                'keywords': [
                    'how are you', 'what is your name', 'who are you', 'thank you', 'bye', 'goodbye',
                    'what can you do', 'your capabilities', 'features', 'abilities', 'skills',
                    'who created you', 'your purpose', 'your mission', 'tell me about yourself',
                    'कैसे हो', 'क्या हो', 'आप कैसे हो', 'आप कैसी हैं', 'आपका नाम क्या है', 'आप काम करते हो'
                ],
                'responses': [
                    "मैं बिल्कुल ठीक हूँ! आपकी मदद करके मुझे खुशी होती है। आज क्या करें? 😊",
                    "I'm doing great, thank you for asking! I'm VANIE - Virtual Assistant of Neural Integrated Engine, ready to help you! 🌟",
                    "धन्यवाद! आपकी मदद करके मुझे खुशी होती है। और कुछ मदद करूँ? 🙏",
                    "I'm VANIE, your advanced AI assistant! I can help with coding, science, history, math, and much more. What would you like to explore? 🤖"
                ]
            },
            
            # New Categories for Enhanced Experience
            'technology': {
                'keywords': [
                    'computer', 'laptop', 'mobile', 'internet', 'software', 'hardware', 'ai', 'machine learning',
                    'artificial intelligence', 'robotics', 'automation', 'blockchain', 'cybersecurity',
                    'कंप्यूटर', 'मोबाइल', 'इंटरनेट', 'एप्लिकेशन', 'वेबसाइट', 'एआई', 'रोबोट'
                ],
                'responses': [
                    "Technology is evolving rapidly! From AI to quantum computing, from smartphones to supercomputers - what tech topic interests you? 📱",
                    "I'm passionate about technology! Whether it's AI, machine learning, cybersecurity, or emerging tech - I can discuss it all! 🤖",
                    "Tech talk! From the latest innovations to future possibilities, what technology would you like to explore? 🚀"
                ]
            },
            
            'education': {
                'keywords': [
                    'study', 'learn', 'education', 'school', 'college', 'university', 'course', 'exam',
                    'homework', 'assignment', 'project', 'research', 'thesis', 'academic',
                    'पढ़ाई', 'अध्यापन', 'कॉलेज', 'विश्वविद्यालय', 'परीक्षा'
                ],
                'responses': [
                    "Education is the key to success! Whether you need help with studies, exams, or academic projects - I'm here to help! 📚",
                    "Learning is a lifelong journey! From school subjects to advanced research, what educational topic can I assist you with? 🎓",
                    "Academic support! I can help with homework, exam preparation, study techniques, and educational guidance. What do you need? 📖"
                ]
            },
            
            'entertainment': {
                'keywords': [
                    'movie', 'music', 'game', 'book', 'story', 'joke', 'fun', 'entertainment',
                    'sports', 'cricket', 'football', 'hobby', 'interest', 'leisure',
                    'फिल्म', 'गाना', 'खेल', 'मज़द', 'खेलना', 'आनंद'
                ],
                'responses': [
                    "Entertainment time! Whether it's movies, music, games, or sports - let's have some fun! What interests you? 🎮",
                    "Life needs balance! From serious study to fun entertainment, what would you like to explore for leisure? 🎵",
                    "Fun and relaxation! I can discuss movies, music, games, sports, or any entertainment topic. What's your choice? 🎬"
                ]
            }
        }
    
    def _initialize_response_templates(self) -> Dict[str, Any]:
        """Initialize dynamic response templates with Hindi support"""
        return {
            'contextual': {
                'python_specific': [
                    "Python में {topic} के बारे में मैं आपकी मदद कर सकती हूँ। क्या specifically जानना चाहिए? 🐍",
                    "Python programming for {topic}! Let me break it down step by step for you. 👨‍💻"
                ],
                'algorithm_specific': [
                    "{topic} algorithm बहुत interesting है! Time complexity O({complexity}) है। Detailed explanation चाहिए? 🔄",
                    "Algorithm analysis: {topic} uses {approach} approach. Would you like to see the implementation? 📊"
                ],
                'science_specific': [
                    "{topic} के बारे में, यह {principle} principle पर काम करता है। और detail में जानना चाहिए? 🧪",
                    "Scientific explanation: {topic} involves {concept}. Let me elaborate on this fascinating subject! 🔬"
                ],
                'math_specific': [
                    "गणित के किसी भी branch में मदद कर सकती हूँ। Algebra, Geometry, Calculus, Statistics, Trigonometry - आप क्या solve करना है? 🔢",
                    "Mathematical thinking! I love solving complex problems. Whether it's algebra, calculus, geometry, or advanced mathematics - what's your mathematical question? 🧮"
                ],
                'history_specific': [
                    "{topic} के बारे में, यह {principle} principle पर काम करता है। और detail में जानना चाहिए? 🏛️",
                    "Historical context: {topic} involves {context}. Let me provide you with comprehensive information! 📜"
                ]
            },
            'follow_up': [
                "और क्या जानना चाहिए? मैं और detail में बता सकती हूँ🤔",
                "Would you like me to elaborate on any specific aspect? I'm here to provide comprehensive answers! 📚",
                "Any follow-up questions? I want to make sure you understand completely! 💡",
                "मैं आपकी पूरी सहायता करूँगी। क्या जानना चाहिए? मैं और दिन मुझे detailed answers provide करूँगी। 🌟"
            ]
        }
    
    def _analyze_input(self, user_input: str) -> Dict[str, Any]:
        """Enhanced input analysis with Hindi keyword detection"""
        input_lower = user_input.lower()
        matched_keywords = []
        confidence_scores = {}
        
        # Check each category for keyword matches
        for category, data in self.knowledge_base.items():
            category_score = 0
            matched_words = []
            keyword_positions = []
            
            for keyword in data['keywords']:
                if keyword.lower() in input_lower:
                    category_score += 1
                    matched_words.append(keyword)
                    
                    # Calculate position-based confidence
                    keyword_position = input_lower.find(keyword.lower())
                    if keyword_position != -1:
                        position_confidence = 1.0 - (keyword_position / len(input_lower))
                        confidence_scores[category] = max(confidence_scores.get(category, 0), position_confidence)
                        keyword_positions.append(keyword_position)
            
            # Bonus for multiple keyword matches in same category
            if category_score > 1:
                category_score += (category_score - 1) * 0.5
            
            if category_score > 0:
                matched_keywords.append({
                    'category': category,
                    'score': category_score,
                    'matched_words': matched_words,
                    'confidence': confidence_scores.get(category, 0),
                    'positions': keyword_positions
                })
        
        return {
            'matched_keywords': matched_keywords,
            'input_length': len(user_input),
            'has_multiple_keywords': len(matched_keywords) > 1,
            'word_count': len(user_input.split()),
            'complexity_score': self._calculate_complexity_score(user_input),
            'language_detected': self._detect_language(user_input)
        }
    
    def _detect_language(self, user_input: str) -> str:
        """Detect if input is Hindi or English"""
        input_lower = user_input.lower()
        
        # Check for Hindi characters and common Hindi words
        hindi_chars = ['आ', 'इ', 'ई', 'ऊ', 'ए', 'ओ', 'अ', 'ं', 'ड', 'ढ', 'ण', 'ट', 'ठ', 'फ', 'र', 'ल', 'व', 'य', 'ह']
        hindi_words = ['नमस्ते', 'क्या', 'आप', 'मैं', 'हैं', 'कर', 'गए', 'से', 'जो', 'पर', 'और', 'यह', 'वाल', 'से', 'सकते']
        
        hindi_char_count = sum(1 for char in input_lower if char in hindi_chars)
        hindi_word_count = sum(1 for word in input_lower.split() if word in hindi_words)
        
        if hindi_char_count > 5 or hindi_word_count > 0:
            return 'hindi'
        else:
            return 'english'
    
    def _calculate_complexity_score(self, user_input: str) -> float:
        """Calculate complexity score based on input characteristics"""
        score = 0.0
        
        # Length bonus
        if len(user_input) > 10:
            score += 0.1
        if len(user_input) > 20:
            score += 0.1
            
        # Question words
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'explain', 'describe', 'क्या', 'कैसे', 'क्यों', 'कहाँ']
        if any(word in user_input.lower() for word in question_words):
            score += 0.2
            
        # Technical terms
        technical_words = ['algorithm', 'function', 'variable', 'complex', 'analyze', 'implement', 'optimize']
        if any(word in user_input.lower() for word in technical_words):
            score += 0.3
            
        # Hindi language bonus
        if self._detect_language(user_input) == 'hindi':
            score += 0.2
            
        return min(score, 1.0)
    
    def _select_best_category(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Enhanced category selection with complexity and language consideration"""
        if not analysis['matched_keywords']:
            return None
        
        # Sort by score, confidence, complexity, and language bonus
        sorted_matches = sorted(
            analysis['matched_keywords'], 
            key=lambda x: (
                x['score'], 
                x['confidence'], 
                x['complexity_score'],
                1.0 if analysis.get('language_detected') == 'hindi' else 0.0  # Language bonus
            ), 
            reverse=True
        )
        
        return sorted_matches[0]['category']
    
    def _get_contextual_response(self, category: str, user_input: str, analysis: Dict[str, Any]) -> str:
        """Generate contextual response based on category, language, and input analysis"""
        if category not in self.knowledge_base:
            return self._get_enhanced_fallback_response(analysis)
        
        responses = self.knowledge_base[category]['responses']
        base_response = random.choice(responses)
        
        # Enhanced contextual responses with Hindi support
        input_lower = user_input.lower()
        language = analysis.get('language_detected', 'english')
        
        # Python specific responses
        if 'python' in input_lower:
            python_topics = ['algorithm', 'data structure', 'function', 'class', 'module', 'library', 'framework', 'debugging']
            for topic in python_topics:
                if topic in input_lower:
                    if language == 'hindi':
                        return f"Python {topic} के बारे में मैं आपकी मदद कर सकती हूँ। क्या specifically जानना चाहिए? 🐍"
                    else:
                        return f"Python programming for {topic}! Let me break it down step by step for you. 👨‍💻"
        
        # Algorithm specific responses
        if 'algorithm' in input_lower:
            algorithm_types = ['sorting', 'searching', 'graph', 'dynamic programming', 'greedy', 'divide and conquer']
            for algo_type in algorithm_types:
                if algo_type in input_lower:
                    complexity = self._estimate_algorithm_complexity(user_input)
                    if language == 'hindi':
                        return f"{algo_type} algorithm का time complexity O({complexity}) है। Detailed explanation चाहिए? 🔄"
                    else:
                        return f"{algo_type} algorithm analysis: {algo_type} uses {approach} approach. Would you like to see the implementation? 📊"
        
        # Science specific responses
        if any(science in input_lower for science in ['physics', 'chemistry', 'biology', 'quantum']):
            science_topics = ['quantum mechanics', 'relativity', 'thermodynamics', 'electromagnetism', 'genetics', 'evolution']
            for topic in science_topics:
                if topic in input_lower:
                    principle = self._get_scientific_principle(topic)
                    if language == 'hindi':
                        return f"{topic} के बारे में, यह {principle} principle पर काम करता है। और detail में जानना चाहिए? 🧪"
                    else:
                        return f"Scientific explanation: {topic} involves {concept}. Let me elaborate on this fascinating subject! 🔬"
        
        # Math specific responses
        if 'math' in input_lower:
            math_topics = ['algebra', 'calculus', 'geometry', 'statistics', 'trigonometry', 'linear algebra', 'differential equations']
            for topic in math_topics:
                if topic in input_lower:
                    if language == 'hindi':
                        return f"गणित के किसी भी branch में मदद कर सकती हूँ। {topic} solve करना है? 🔢"
                    else:
                        return f"Mathematical thinking! I love solving complex problems involving {topic}. What's your question? 🧮"
        
        # History specific responses
        if any(history in input_lower for history in ['history', 'historical', 'ancient', 'india', 'gupta', 'maurya']):
            history_topics = ['gupta', 'maurya', 'ancient civilizations', 'medieval period', 'modern history']
            for topic in history_topics:
                if topic in input_lower:
                    if language == 'hindi':
                        return f"{topic} काल का विस्तृ बहुत समृद्ध है! Ancient India का Golden Age था। और detail में जानना चाहिए? 🏛️"
                    else:
                        return f"Historical inquiry! I can discuss {topic} and related events. What aspect interests you? 📜"
        
        # Add follow-up questions for complex queries
        if analysis['complexity_score'] > 0.5:
            follow_up = random.choice(self.response_templates['follow_up'])
            base_response += f" {follow_up}"
        
        return base_response
    
    def _get_scientific_principle(self, topic: str) -> str:
        """Get scientific principle in Hindi and English"""
        principles = {
            'quantum mechanics': {
                'hindi': 'सुपरपोजिशन और अनिश्चितत का सिद्धांत',
                'english': 'superposition and uncertainty principle'
            },
            'relativity': {
                'hindi': 'स्पेसटाइम और समतुल्यता',
                'english': 'spacetime and equivalence principle'
            },
            'thermodynamics': {
                'hindi': 'एन्ट्रॉपी और संरक्षण कानूम',
                'english': 'entropy and conservation laws'
            },
            'evolution': {
                'hindi': 'प्राकृति और अनुकूल',
                'english': 'natural selection and adaptation'
            },
            'genetics': {
                'hindi': 'डीएनए और वंशादित',
                'english': 'DNA and heredity'
            }
        }
        
        return principles.get(topic, 'fundamental principles')
    
    def _estimate_algorithm_complexity(self, user_input: str) -> str:
        """Estimate algorithm complexity based on keywords"""
        if 'linear' in user_input or 'search' in user_input:
            return 'O(n)'
        elif 'binary' in user_input or 'log' in user_input:
            return 'O(log n)'
        elif 'quicksort' in user_input or 'mergesort' in user_input:
            return 'O(n log n)'
        elif 'nested' in user_input or 'exponential' in user_input:
            return 'O(2^n)'
        else:
            return 'O(n)'
    
    def _get_enhanced_fallback_response(self, analysis: Dict[str, Any]) -> str:
        """Enhanced fallback responses based on input analysis and language"""
        complexity = analysis['complexity_score']
        language = analysis.get('language_detected', 'english')
        
        if complexity > 0.7:
            if language == 'hindi':
                return [
                    "यह एक बहुत ही complex और interesting question है! मैं इसका thorough analysis करूँगी। 🧠",
                    "Complex inquiry detected! Let me provide you with a comprehensive answer. This requires detailed explanation. 📊",
                    "यह एक गहने depth में जानना चाहिए! मैं आपको step-by-step explanation दूँगी। 🔬"
                ]
            elif complexity > 0.4:
                if language == 'hindi':
                    return [
                        "यह एक thoughtful question है! मैं आपकी जिज्जासी सराहना करूँगी। 💭",
                        "Interesting question! मैं इसका detailed analysis कर रही हूँ। थोड़ा context दीजिए? 🤔",
                        "मुझे समझ में आ रहा है! आप किस विषय पर चर्चा कर रहे हैं? 🌟"
                    ]
            else:
                    return [
                        "यह एक thoughtful question है! मैं इसका detailed analysis कर रही हूँ। थोड़ा context दीजिए? 💭",
                        "Interesting question! मैं इसका detailed analysis कर रही हूँ। थोड़ा context दीजिए? 🤔",
                        "मैं आपकी मदद के लिए यहाँ हूँ! कोडिंग, विज्ञान, इतिहास, गणित - कुछ भी पूछिये! 🙏"
                    ]
        else:
            if language == 'hindi':
                return [
                    "यह एक दिलचस्प सवाल है! क्या आप थोड़ा और detail दे सकते हैं? 🤔",
                    "Interesting question! मैं आपकी बेहतर समझने की कोशिश कर रही हूँ। कृपया अपना सवाल थोड़ा elaborate करें। 💭",
                    "मैं आपकी मदद के लिए यहाँ हूँ! कोडिंग, विज्ञान, इतिहास, गणित - कुछ भी पूछिये! 🙏"
                ]
            else:
                return [
                    "यह एक दिलचस्प सवाल है! क्या आप थोड़ा और detail दे सकते हैं? 🤔",
                    "Interesting question! मैं आपकी बेहतर समझने की कोशिश कर रही हूँ। कृपया अपना सवाल थोड़ा elaborate करें। 💭",
                    "Let me help you with that! I can provide more detailed information if you'd like. 📚"
                ]
        
        return random.choice(self._get_enhanced_fallback_response(analysis))
    
    def _update_context(self, user_input: str, ai_response: str, category: Optional[str] = None, analysis: Dict[str, Any] = None):
        """Enhanced context update with sentiment and language analysis"""
        context_entry = {
            'user_input': user_input,
            'ai_response': ai_response,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'complexity_score': analysis.get('complexity_score', 0) if analysis else 0,
            'word_count': len(user_input.split()),
            'has_question': any(word in user_input.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who', 'क्या', 'कैसे', 'क्यों']),
            'language_detected': analysis.get('language_detected', 'english'),
            'sentiment': self._analyze_sentiment(user_input)
        }
        
        self.conversation_context.append(context_entry)
        
        # Enhanced context management - keep last 20 messages for better continuity
        if len(self.conversation_context) > 20:
            self.conversation_context = self.conversation_context[-20:]
        
        # Maintain conversation themes
        if len(self.conversation_context) >= 3:
            recent_categories = [msg.get('category') for msg in self.conversation_context[-3:] if msg.get('category')]
            if len(set(recent_categories)) == 1 and recent_categories[0]:
                # User is staying on same topic, provide more specialized responses
                context_entry['topic_continuation'] = True
    
    def _analyze_sentiment(self, user_input: str) -> str:
        """Analyze sentiment of user input"""
        positive_words = ['accha', 'badhiya', 'shabaash', 'dhanayavad', 'kamaal', 'utsav', 'prashasan']
        negative_words = ['bur', 'bekar', 'gandi', 'bura', 'durd', 'kharab', 'nakaam']
        
        input_lower = user_input.lower()
        if any(word in input_lower for word in positive_words):
            return 'positive'
        elif any(word in input_lower for word in negative_words):
            return 'negative'
        else:
            return 'neutral'
    
    def generate_response(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced main response generation method with Hindi support"""
        
        # Analyze the input
        analysis = self._analyze_input(user_input)
        
        # Select best category
        best_category = self._select_best_category(analysis)
        
        # Generate enhanced response
        if best_category:
            response = self._get_contextual_response(best_category, user_input, analysis)
        else:
            response = self._get_enhanced_fallback_response(analysis)
        
        # Update enhanced context
        self._update_context(user_input, response, best_category, analysis)
        
        # Store in session if provided
        if session_id:
            if session_id not in self.user_sessions:
                self.user_sessions[session_id] = []
            self.user_sessions[session_id].append({
                'user_input': user_input,
                'ai_response': response,
                'category': best_category,
                'complexity_score': analysis.get('complexity_score', 0),
                'timestamp': datetime.now().isoformat(),
                'language_detected': analysis.get('language_detected', 'english'),
                'sentiment': analysis.get('sentiment', 'neutral')
            })
        
        return {
            'response': response,
            'category': best_category,
            'confidence': analysis['matched_keywords'][0]['confidence'] if analysis['matched_keywords'] else 0,
            'matched_keywords': [kw['matched_words'] for kw in analysis['matched_keywords']] if analysis['matched_keywords'] else [],
            'context_length': len(self.conversation_context),
            'complexity_score': analysis.get('complexity_score', 0),
            'word_count': analysis.get('word_count', 0),
            'has_multiple_keywords': analysis.get('has_multiple_keywords', False),
            'language_detected': analysis.get('language_detected', 'english'),
            'sentiment': analysis.get('sentiment', 'neutral'),
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
    
    def get_conversation_history(self, session_id: Optional[str] = None) -> List[Dict]:
        """Get conversation history with enhanced metadata"""
        if session_id and session_id in self.user_sessions:
            return self.user_sessions[session_id]
        return self.conversation_context
    
    def clear_context(self, session_id: Optional[str] = None):
        """Clear conversation context"""
        self.conversation_context = []
        if session_id and session_id in self.user_sessions:
            self.user_sessions[session_id] = []
    
    def get_conversation_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get conversation statistics with language and sentiment analysis"""
        history = self.get_conversation_history(session_id)
        
        if not history:
            return {'total_messages': 0, 'categories_discussed': [], 'avg_complexity': 0, 'languages': [], 'sentiments': []}
        
        categories = list(set([msg.get('category') for msg in history if msg.get('category')]))
        avg_complexity = sum([msg.get('complexity_score', 0) for msg in history]) / len(history)
        languages = list(set([msg.get('language_detected', 'english') for msg in history if msg.get('language_detected')]))
        sentiments = list(set([msg.get('sentiment', 'neutral') for msg in history if msg.get('sentiment')]))
        
        return {
            'total_messages': len(history),
            'categories_discussed': categories,
            'avg_complexity': round(avg_complexity, 2),
            'languages': languages,
            'sentiments': sentiments,
            'session_duration': self._calculate_session_duration(history),
            'hindi_usage': sum(1 for msg in history if msg.get('language_detected') == 'hindi'),
            'english_usage': sum(1 for msg in history if msg.get('language_detected') == 'english')
        }
    
    def _calculate_session_duration(self, history: List[Dict]) -> str:
        """Calculate session duration from timestamps"""
        if len(history) < 2:
            return "0 minutes"
        
        try:
            start_time = datetime.fromisoformat(history[0]['timestamp'])
            end_time = datetime.fromisoformat(history[-1]['timestamp'])
            duration = end_time - start_time
            
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            
            if hours > 0:
                return f"{int(hours)}h {int(minutes)}m"
            else:
                return f"{int(minutes)} minutes"
        except:
            return "Unknown"

# Enhanced Flask Web Application
app = Flask(__name__)
CORS(app)

# Initialize Enhanced AI with Hindi Support
vanie_ai = VANIEAI()

@app.route('/')
def index():
    """Enhanced API documentation with Hindi support"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>VANIE AI Backend - Enhanced Hindi API</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1); 
            padding: 40px; 
            border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.2); 
            backdrop-filter: blur(10px); 
        }
        h1 { 
            color: #fff; 
            text-align: center; 
            margin-bottom: 10px; 
            font-size: 2.5em; 
        }
        h2 { 
            color: #fff; 
            text-align: center; 
            margin-bottom: 30px; 
            font-size: 1.5em; 
        }
        .endpoint { 
            background: rgba(255,255,255,0.15); 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 10px; 
            border-left: 5px solid #00d4ff; 
            transition: all 0.3s ease; 
        }
        .endpoint:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 20px rgba(0,212,255,0.3); 
        }
        .method { 
            color: #00d4ff; 
            font-weight: bold; 
            font-size: 1.1em; 
        }
        .url { 
            color: #ff6b6b; 
            font-family: 'Courier New', monospace; 
            background: rgba(255,255,255,0.1); 
            padding: 2px 6px; 
            border-radius: 4px; 
        }
        .description { 
            color: #e0e0e0; 
            margin-top: 8px; 
            line-height: 1.4; 
        }
        .features { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin-top: 20px; 
        }
        .feature { 
            background: rgba(255,255,255,0.1); 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center; 
        }
        .feature-icon { 
            font-size: 2em; 
            margin-bottom: 10px; 
        }
        .language-indicator { 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
            color: white; 
            padding: 4px 8px; 
            border-radius: 12px; 
            font-size: 0.8em; 
            margin-left: 10px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 VANIE AI Backend - Enhanced Hindi Support</h1>
        <h2>Virtual Assistant of Neural Integrated Engine - हिंदी समर्थित</h2>
        
        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/chat</div>
            <div class="description">Send message and get intelligent AI response with Hindi/English support</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/history</div>
            <div class="description">Get conversation history with enhanced metadata and language analysis</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/stats</div>
            <div class="description">Get conversation statistics with language usage and sentiment analysis</div>
        </div>
        
        <div class="endpoint">
            <div class="method">DELETE</div>
            <div class="url">/api/clear</div>
            <div class="description">Clear conversation context</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/health</div>
            <div class="description">Check API health status and features</div>
        </div>
        
        <h3>🚀 Enhanced Features with Hindi Support</h3>
        <div class="features">
            <div class="feature">
                <div class="feature-icon">🧠</div>
                <div>Multi-Keyword Detection (हिंदी/English)</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🎯</div>
                <div>Contextual Responses</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div>Complexity Analysis</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🌍</div>
                <div>Language Detection (हिंदी/English)</div>
            </div>
            <div class="feature">
                <div class="feature-icon">💬</div>
                <div>Conversation Memory (20 messages)</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📈</div>
                <div>Session Analytics</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🔧</div>
                <div>Advanced Algorithms</div>
            </div>
            <div class="feature">
                <div class="feature-icon">😊</div>
                <div>Sentiment Analysis</div>
            </div>
            <div class="feature">
                <div class="language-indicator">🇮🇳</div>
                <div>Hindi + English Support</div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with Hindi language detection"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error',
                'language': 'unknown'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Generate enhanced AI response with language detection
        result = vanie_ai.generate_response(user_message, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error',
            'language': 'unknown'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history with enhanced metadata"""
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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get conversation statistics with language analysis"""
    try:
        session_id = request.args.get('session_id', 'default')
        stats = vanie_ai.get_conversation_stats(session_id)
        
        return jsonify({
            'stats': stats,
            'session_id': session_id,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving stats: {str(e)}',
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
    """Enhanced health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VANIE AI Enhanced Backend with Hindi Support',
        'version': '3.0.0',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'keyword_matching': True,
            'context_awareness': True,
            'multi_language': True,
            'session_management': True,
            'complexity_analysis': True,
            'multi_keyword_detection': True,
            'conversation_memory': True,
            'enhanced_responses': True,
            'hindi_support': True,
            'english_support': True,
            'sentiment_analysis': True,
            'language_detection': True,
            'total_categories': len(vanie_ai.knowledge_base.keys())
        },
        'supported_languages': ['hindi', 'english'],
        'language_distribution': {
            'hindi': '50%',
            'english': '50%'
        }
    })

if __name__ == '__main__':
    print("🚀 VANIE AI Enhanced Backend Starting...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 Enhanced API Documentation: http://localhost:5000")
    print("🌟 Ready for advanced conversations with Hindi support!")
    print("🎯 Features: Multi-keyword detection, Context awareness, Complexity analysis, Language detection, Sentiment analysis")
    print("🇮🇳 Languages: Hindi + English support")
    print("🧠 Total Categories:", len(vanie_ai.knowledge_base.keys()))
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

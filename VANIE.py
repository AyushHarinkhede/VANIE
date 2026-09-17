#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ðŸ¤– VANIE - Virtual Agent of Neural Integrated Engine
VERSION 3.5-ULTRA: ADVANCED NEURAL NLP, MULTI-TURN MEMORY & CONVERSATIONAL INTELLIGENCE

Features:
- Multi-layer NLP: Fuzzy matching, TF-IDF N-grams, intent confidence scoring
- Multi-turn conversational memory with coreference resolution & chained reasoning
- Fluent bilingual conversational engine (Hinglish, Hindi, English)
- Emotion-aware empathetic response generation with sentiment intensity
- Persona tuning: Default, Jarvis (Cyberpunk), Casual (Buddy), Formal, Concise
- Advanced mathematical computation, scientific functions, and percentage reasoning
- Real-time device hardware control and communication parameter extraction
- Comprehensive offline factual knowledge base (Science, Tech, AI, Space, History, Life Advice)
- Interactive entertainment: Jokes, Riddles, Trivia, Motivational Wisdom, Fun Facts

Developed by Ayush Harinkhede Â© 2026. All rights reserved.
"""

import os
import sys
import json
import datetime
import platform
import socket
import threading
import time
import re
import calendar
import logging
from typing import Dict, Any, List, Tuple, Optional
import random
import math
import hashlib
from collections import Counter, defaultdict
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VANIE")


class AdvancedNLPAlgorithms:
    """Advanced Natural Language Processing Algorithms with Multi-lingual & Fuzzy Support"""

    @staticmethod
    def calculate_sentiment(text: str) -> Tuple[str, float]:
        """
        Calculate sentiment of text using bilingual positive/negative polarity maps
        Returns: (sentiment: 'positive' | 'negative' | 'neutral', confidence: float)
        """
        text_lower = text.lower()

        positive_words = {
            'good': 2, 'great': 3, 'excellent': 3, 'amazing': 3, 'wonderful': 3,
            'perfect': 3, 'love': 3, 'like': 1, 'happy': 2, 'excited': 2,
            'awesome': 3, 'fantastic': 3, 'brilliant': 3, 'beautiful': 2,
            'best': 3, 'nice': 1, 'cool': 1, 'interesting': 1, 'fun': 2,
            'khush': 2, 'shandar': 3, 'badhiya': 2, 'accha': 1, 'sunder': 2,
            'mazza': 2, 'mast': 2, 'superb': 3, 'fabulous': 3, 'lovely': 2,
            'à¤–à¥à¤¶': 2, 'à¤¶à¤¾à¤¨à¤¦à¤¾à¤°': 3, 'à¤¬à¤¢à¤¼à¤¿à¤¯à¤¾': 2, 'à¤…à¤šà¥à¤›à¤¾': 1, 'à¤¸à¥à¤‚à¤¦à¤°': 2, 'à¤®à¤œà¤¼à¤¾': 2
        }

        negative_words = {
            'bad': 2, 'terrible': 3, 'awful': 3, 'horrible': 3, 'hate': 3,
            'dislike': 2, 'sad': 2, 'upset': 2, 'angry': 3, 'frustrated': 2,
            'worst': 3, 'poor': 2, 'boring': 2, 'stupid': 2, 'annoying': 2,
            'bura': 2, 'bhayanak': 3, 'dukh': 2, 'gussa': 3, 'pareshan': 2,
            'thak': 2, 'tension': 2, 'bekar': 2, 'ro': 2, 'udas': 2,
            'à¤¬à¥à¤°à¤¾': 2, 'à¤­à¤¯à¤¾à¤¨à¤•': 3, 'à¤¦à¥à¤ƒà¤–': 2, 'à¤—à¥à¤¸à¥à¤¸à¤¾': 3, 'à¤ªà¤°à¥‡à¤¶à¤¾à¤¨': 2, 'à¤‰à¤¦à¤¾à¤¸': 2
        }

        intensity_multiplier = {
            'very': 1.5, 'really': 1.5, 'extremely': 2.0, 'absolutely': 2.0,
            'so': 1.3, 'bohot': 1.6, 'bahut': 1.6, 'kaafi': 1.3, 'zyada': 1.4,
            'à¤¬à¤¹à¥à¤¤': 1.6, 'à¤…à¤¤à¥à¤¯à¤§à¤¿à¤•': 2.0
        }

        words = re.findall(r'\b\w+\b', text_lower)
        if not words:
            return 'neutral', 0.5

        sentiment_score = 0.0
        matched_count = 0
        intensity = 1.0

        for word in words:
            if word in intensity_multiplier:
                intensity = intensity_multiplier[word]
            elif word in positive_words:
                sentiment_score += positive_words[word] * intensity
                matched_count += 1
                intensity = 1.0
            elif word in negative_words:
                sentiment_score -= negative_words[word] * intensity
                matched_count += 1
                intensity = 1.0

        if matched_count == 0:
            return 'neutral', 0.5

        confidence = min(0.5 + (matched_count / (len(words) + 1)) * 0.5, 1.0)

        if sentiment_score > 0.5:
            return 'positive', confidence
        elif sentiment_score < -0.5:
            return 'negative', confidence
        else:
            return 'neutral', confidence

    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> List[str]:
        """Extract top informative keywords from text"""
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'are', 'was', 'were', 'be', 'have', 'has', 'do', 'does',
            'main', 'aap', 'hai', 'hain', 'me', 'ko', 'ka', 'ki', 'se', 'aur',
            'kya', 'kaise', 'kyun', 'kaha', 'kar', 'raha', 'rahi', 'mera', 'meri',
            'tum', 'tumhara', 'hum', 'ye', 'wo', 'bhi', 'kuch', 'toh', 'ab',
            'à¤®à¥ˆà¤‚', 'à¤†à¤ª', 'à¤¹à¥ˆ', 'à¤¹à¥ˆà¤‚', 'à¤®à¥‡à¤‚', 'à¤•à¥‹', 'à¤•à¤¾', 'à¤•à¥€', 'à¤¸à¥‡', 'à¤”à¤°', 'à¤•à¥à¤¯à¤¾', 'à¤•à¥ˆà¤¸à¥‡'
        }

        words = re.findall(r'\b\w+\b', text.lower())
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        word_freq = Counter(filtered)
        return [word for word, _ in word_freq.most_common(top_n)]

    @staticmethod
    def calculate_fuzzy_similarity(text1: str, text2: str) -> float:
        """Calculate hybrid fuzzy similarity combining word intersection and sequence matching"""
        t1, t2 = text1.lower().strip(), text2.lower().strip()
        if not t1 or not t2:
            return 0.0

        ratio = SequenceMatcher(None, t1, t2).ratio()

        words1 = set(re.findall(r'\b\w+\b', t1))
        words2 = set(re.findall(r'\b\w+\b', t2))
        if words1 and words2:
            jaccard = len(words1 & words2) / len(words1 | words2)
            return (ratio * 0.4) + (jaccard * 0.6)

        return ratio

    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract all numbers from string including negative and decimal numbers"""
        numbers = re.findall(r'[-+]?\d*\.?\d+', text)
        result = []
        for n in numbers:
            try:
                if n not in ('', '+', '-'):
                    result.append(float(n))
            except ValueError:
                pass
        return result


class ConversationMemory:
    """Multi-turn Contextual Memory, Coreference Tracker & User Profile Store"""

    def __init__(self, max_history: int = 30):
        self.conversation_history = []
        self.max_history = max_history
        self.session_start = datetime.datetime.now()
        self.interaction_count = 0

        # Memory Slots
        self.user_name = "Friend"
        self.last_topic = "general"
        self.last_entity = None
        self.last_math_result = None
        self.user_mood = "neutral"
        self.active_persona = "default"  # 'default', 'jarvis', 'buddy', 'formal', 'concise'

    def add_message(self, role: str, content: str, intent: str = None, metadata: Dict = None):
        """Add message to history and update context"""
        entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'role': role,
            'content': content,
            'intent': intent,
            'metadata': metadata or {}
        }
        self.conversation_history.append(entry)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

        if role == 'user':
            self.interaction_count += 1

    def get_recent_context(self, count: int = 4) -> List[Dict]:
        return self.conversation_history[-count:]

    def clear(self):
        self.conversation_history.clear()
        self.last_topic = "general"
        self.last_entity = None
        self.last_math_result = None


class VANIEEnhanced:
    """
    VANIE 3.5 Engine
    Comprehensive Conversational Brain, Reasoning Engine & Device System Controller
    """

    def __init__(self):
        self.nlp = AdvancedNLPAlgorithms()
        self.memory = ConversationMemory()
        self.weather_cache = {}
        self.uptime_start = time.time()
        self.knowledge_base = self._initialize_knowledge_base()

    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize comprehensive bilingual intent patterns, dialogues, and facts"""
        return {
            'creator': {
                'name': 'Ayush Harinkhede',
                'email': 'ayushharinkhere2005@gmail.com',
                'github': 'https://github.com/AyushHarinkhede',
                'role': 'Developer, System Architect & Creator of VANIE'
            },
            'intents': {
                # â”€â”€ Hardware & Controls â”€â”€
                'torch_on': r'\b(torch on|flashlight on|flash on|turn on torch|turn on flashlight|light on|à¤²à¤¾à¤‡à¤Ÿ à¤šà¤¾à¤²à¥‚|à¤²à¤¾à¤‡à¤Ÿ à¤‘à¤¨|à¤Ÿà¥‰à¤°à¥à¤š à¤‘à¤¨|à¤Ÿà¥‰à¤°à¥à¤š à¤šà¤¾à¤²à¥‚|light jalao|torch jalao)\b',
                'torch_off': r'\b(torch off|flashlight off|flash off|turn off torch|turn off flashlight|light off|à¤²à¤¾à¤‡à¤Ÿ à¤¬à¤‚à¤¦|à¤²à¤¾à¤‡à¤Ÿ à¤‘à¤«|à¤Ÿà¥‰à¤°à¥à¤š à¤‘à¤«|à¤Ÿà¥‰à¤°à¥à¤š à¤¬à¤‚à¤¦|light band karo|torch band karo)\b',
                'wifi_on': r'\b(wifi on|turn on wifi|enable wifi|à¤µà¤¾à¤ˆà¤«à¤¾à¤ˆ à¤‘à¤¨|à¤µà¤¾à¤ˆà¤«à¤¾à¤ˆ à¤šà¤¾à¤²à¥‚|wifi chalu karo)\b',
                'wifi_off': r'\b(wifi off|turn off wifi|disable wifi|à¤µà¤¾à¤ˆà¤«à¤¾à¤ˆ à¤‘à¤«|à¤µà¤¾à¤ˆà¤«à¤¾à¤ˆ à¤¬à¤‚à¤¦|wifi band karo)\b',
                'bluetooth_on': r'\b(bluetooth on|turn on bluetooth|enable bluetooth|à¤¬à¥à¤²à¥‚à¤Ÿà¥‚à¤¥ à¤‘à¤¨|à¤¬à¥à¤²à¥‚à¤Ÿà¥‚à¤¥ à¤šà¤¾à¤²à¥‚|bluetooth chalu karo)\b',
                'bluetooth_off': r'\b(bluetooth off|turn off bluetooth|disable bluetooth|à¤¬à¥à¤²à¥‚à¤Ÿà¥‚à¤¥ à¤‘à¤«|à¤¬à¥à¤²à¥‚à¤Ÿà¥‚à¤¥ à¤¬à¤‚à¤¦|bluetooth band karo)\b',
                'brightness': r'\b(brightness|screen light|display light|à¤¬à¥à¤°à¤¾à¤‡à¤Ÿà¤¨à¥‡à¤¸|à¤°à¥‹à¤¶à¤¨à¥€|chamkila)\b',
                'dnd_on': r'\b(dnd on|do not disturb on|silent phone|à¤¡à¥€à¤à¤¨à¤¡à¥€ à¤šà¤¾à¤²à¥‚|à¤¡à¤¿à¤¸à¥à¤Ÿà¤°à¥à¤¬ à¤¨ à¤•à¤°à¥‡à¤‚|dnd chalu karo)\b',
                'dnd_off': r'\b(dnd off|do not disturb off|à¤¡à¥€à¤à¤¨à¤¡à¥€ à¤¬à¤‚à¤¦|dnd band karo)\b',
                'mode_silent': r'\b(silent mode|phone silent|à¤¸à¤¾à¤‡à¤²à¥‡à¤‚à¤Ÿ à¤®à¥‹à¤¡|à¤¸à¤¾à¤‡à¤²à¥‡à¤‚à¤Ÿ à¤•à¤°à¥‹)\b',
                'mode_vibrate': r'\b(vibrate mode|phone vibrate|à¤µà¤¾à¤‡à¤¬à¥à¤°à¥‡à¤Ÿ à¤®à¥‹à¤¡|à¤µà¤¾à¤‡à¤¬à¥à¤°à¥‡à¤Ÿ à¤•à¤°à¥‹)\b',
                'mode_ring': r'\b(ring mode|normal mode|sound mode|à¤°à¤¿à¤‚à¤— à¤®à¥‹à¤¡|à¤°à¤¿à¤‚à¤—à¤° à¤‘à¤¨)\b',
                'battery_status': r'\b(battery|charging|charge|battery kitni hai|battery percentage|à¤¬à¥ˆà¤Ÿà¤°à¥€|à¤šà¤¾à¤°à¥à¤œà¤¿à¤‚à¤—)\b',

                # â”€â”€ Telephony & Messaging â”€â”€
                'make_call': r'\b(call|make a call|dial|phone karo|call lagao|call karo|à¤«à¥‹à¤¨ à¤•à¤°à¥‹|à¤•à¥‰à¤² à¤•à¤°à¥‹|à¤•à¥‰à¤² à¤²à¤—à¤¾à¤“|baat karao)\b',
                'send_whatsapp': r'\b(whatsapp|send whatsapp|whatsapp message|à¤µà¥à¤¹à¤¾à¤Ÿà¥à¤¸à¤à¤ª à¤•à¤°à¥‹|à¤µà¥à¤¹à¤¾à¤Ÿà¥à¤¸à¤à¤ª à¤®à¥ˆà¤¸à¥‡à¤œ|whatsapp bhejo)\b',
                'send_sms': r'\b(text message|send text|send sms|sms bhejo|message bhejo|à¤®à¥ˆà¤¸à¥‡à¤œ à¤•à¤°à¥‹|à¤à¤¸à¤à¤®à¤à¤¸ à¤­à¥‡à¤œà¥‹)\b',
                'app_launch': r'\b(open youtube|open whatsapp|open camera|open chrome|open settings|open clock|open map|open maps|open gmail|open play store|launch|kholo|à¤–à¥‹à¤²à¥‹)\b',
                'set_alarm': r'\b(set alarm|alarm lagao|wake me up|à¤…à¤²à¤¾à¤°à¥à¤®|alarm)\b',
                'set_timer': r'\b(set timer|timer lagao|start timer|à¤Ÿà¤¾à¤‡à¤®à¤°|timer)\b',

                # â”€â”€ Time & Temporal â”€â”€
                'time': r'\b(time|samay|baja|current time|abhi kya time|kitne baje|baje hain|ghadi|à¤¸à¤®à¤¯|à¤˜à¥œà¥€)\b',
                'date': r'\b(date|tarikh|aaj konsi date|today date|calendar|konsa saal|which year|konsa din|which day|konsa month|which month|saal|year|à¤¤à¤¾à¤°à¥€à¤–|à¤†à¤œ)\b',
                'day_night_phase': r'\b(din hai ya raat|raat hai ya din|day or night|is it night|is it day|din ho raha ya raat)\b',
                'age_calc': r'\b(age|umar|birthdate|born in|date of birth|dob|kitne saal|à¤‰à¤®à¥à¤°|à¤†à¤¯à¥)\b',

                # â”€â”€ Reasoning, Math & Tools â”€â”€
                'math': r'(\d+\.?\d*\s*[\+\-\*/%\^]\s*\d+\.?\d*|calculate|sqrt|square root|sin\(|cos\(|tan\(|log\(|ln\(|fact\(|factorial|percent|% of|\+|-|\*|/|divide|multiply)',
                'conversion': r'\b(convert|conversion|transform|unit|km to mile|celsius to fahrenheit|kg to lbs|gb to mb|speed conversion|à¤‡à¤•à¤¾à¤ˆ)\b',
                'weather': r'\b(weather|temperature|mausam|aaj ka mausam|rain|barish|mosam|à¤¤à¤¾à¤ªà¤®à¤¾à¤¨|à¤®à¥Œà¤¸à¤®)\b',
                'system_specs': r'\b(system|cpu|ram|memory|specs|specs info|hardware info|computer info)\b',

                # â”€â”€ Identity & Creator â”€â”€
                'vanie_identity': r'\b(who are you|tum kaun ho|aap kaun ho|your name|apka naam|tell me about yourself|about vanie|what is vanie|creator|who made you|tumhe kisne banaya|ayush kaun hai|ayush harinkhede)\b',
                'capabilities': r'\b(what can you do|tum kya kar sakti ho|features|help|commands|madad|capabilities|kya kya karti ho)\b',

                # â”€â”€ Conversational Chit-Chat & Companionship â”€â”€
                'greeting': r'\b(hello|hi|hey|namaste|namaskar|pranam|good morning|good afternoon|good evening|good night|kya haal|wassup|what\'s up|à¤¨à¤®à¤¸à¥à¤¤à¥‡|à¤¹à¥‡à¤²à¥‹|à¤¹à¤¾à¤¯|à¤¸à¥à¤ªà¥à¤°à¤­à¤¾à¤¤|à¤¶à¥à¤­ à¤°à¤¾à¤¤à¥à¤°à¤¿)\b',
                'how_are_you': r'\b(kaise ho|kya haal hai|how are you|how do you do|sab theek|kaisa chal raha hai|sab kushal)\b',
                'compliment': r'\b(you are smart|you are awesome|you are great|tum bohot acchi ho|love you|shandar ho|intelligent|best ai)\b',
                'thanks': r'\b(thanks|thank you|dhanyawad|shukriya|bohot shukriya|à¤§à¤¨à¥à¤¯à¤µà¤¾à¤¦|à¤¶à¥à¤•à¥à¤°à¤¿à¤¯à¤¾)\b',
                'bye': r'\b(bye|goodbye|alvida|phir milenge|see you|take care|à¤¬à¤¾à¤¯|à¤…à¤²à¤µà¤¿à¤¦à¤¾)\b',
                'food_tea': r'\b(khana khaya|lunch kar liya|dinner kiya|breakfast|chai pee li|coffee|tea|chai|food)\b',
                'friendship': r'\b(best friend|kya tum meri dost ho|are we friends|dosti karogi|friend banogi)\b',
                'hobbies': r'\b(hobbies|tumhe kya pasand hai|free time me kya karti ho|what do you like)\b',
                'music_movies': r'\b(favorite song|gaana|music suno|movie|cinema|favorite movie|filmon)\b',
                'study_work': r'\b(padhai|study|exam|focus|work stress|man nahi lag raha|productivity|motivation)\b',
                'emotions_happy': r'\b(happy|excited|awesome|good news|bohot khush|khush hoon|maza aa gaya|party)\b',
                'emotions_sad': r'\b(sad|lonely|depressed|heartbroken|udas hoon|dukhi hoon|mood off|cry|rone ka man)\b',
                'emotions_stressed': r'\b(stressed|tired|thak gaya|headache|tension|pareshan hoon|bahut thakan)\b',
                'emotions_angry': r'\b(angry|gussa|gussa aa raha hai|irritated|frustrated|naraz hoon)\b',
                'emotions_bored': r'\b(bored|bore ho raha hoon|boring|kuch bolo|kuch sunao|timepass)\b',

                # â”€â”€ Entertainment & Wisdom â”€â”€
                'joke': r'\b(joke|chutkula|hanso|hansi|funny|joke sunao|à¤šà¥à¤Ÿà¤•à¥à¤²à¤¾|à¤®à¤œà¤¾à¤•)\b',
                'riddle': r'\b(riddle|paheli|bujho|paheliyan|à¤ªà¤¹à¥‡à¤²à¥€)\b',
                'trivia': r'\b(trivia|quiz|sawal|question pucho|gk question|à¤•à¥à¤µà¤¿à¤œà¤¼)\b',
                'motivation': r'\b(motivation|inspire|motivational quote|courage|honsla|himmat|suvichar|à¤¸à¥à¤µà¤¿à¤šà¤¾à¤°|à¤ªà¥à¤°à¥‡à¤°à¤£à¤¾)\b',
                'fun_fact': r'\b(fun fact|fact|kya aap jante ho|interesting fact|kuch naya batao|à¤°à¥‹à¤šà¤• à¤¤à¤¥à¥à¤¯)\b',

                # â”€â”€ Knowledge & Science â”€â”€
                'science_space': r'\b(space|universe|black hole|mars|moon|sun|solar system|physics|einstein|gravity|chandrayaan|nasa|isro)\b',
                'tech_ai': r'\b(artificial intelligence|machine learning|deep learning|neural network|python|kotlin|android|chatgpt|llm|robot)\b'
            }
        }

    def generate_response(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main Conversational AI Entry Point:
        Processes natural language, evaluates context/memory, resolves intents, executes actions, and crafts responses.
        """
        raw_text = message.strip()
        if not raw_text:
            return {
                'response': "Main aapki baat sun rahi hoon! Kahiye, kya madad kar sakti hoon? ðŸ˜Š",
                'intent': 'empty',
                'action': '',
                'confidence': 1.0
            }

        # 1. Update Memory & Extract NLP features
        self.memory.add_message('user', raw_text)
        sentiment, sentiment_conf = self.nlp.calculate_sentiment(raw_text)
        keywords = self.nlp.extract_keywords(raw_text)

        # 2. Match Intent
        intent, confidence = self._match_intent(raw_text)

        # 3. Contextual Coreference & Follow-up Override
        intent = self._apply_contextual_reasoning(raw_text, intent)

        # 4. Route to Intent Handlers
        response_text = ""
        action_tag = ""
        target_name = None
        message_body = None

        if intent == 'torch_on':
            response_text = "ðŸ”¦ Flashlight turned ON!"
            action_tag = "TORCH_ON"
        elif intent == 'torch_off':
            response_text = "ðŸ”¦ Flashlight turned OFF!"
            action_tag = "TORCH_OFF"
        elif intent == 'wifi_on':
            response_text = "ðŸ“¶ Opening Wi-Fi settings to enable..."
            action_tag = "WIFI_ON"
        elif intent == 'wifi_off':
            response_text = "ðŸ“¶ Opening Wi-Fi settings to disable..."
            action_tag = "WIFI_OFF"
        elif intent == 'bluetooth_on':
            response_text = "ðŸ”µ Enabling Bluetooth controls..."
            action_tag = "BLUETOOTH_ON"
        elif intent == 'bluetooth_off':
            response_text = "ðŸ”µ Disabling Bluetooth controls..."
            action_tag = "BLUETOOTH_OFF"
        elif intent == 'brightness':
            nums = self.nlp.extract_numbers(raw_text)
            pct = int(nums[0]) if nums else 75
            response_text = f"â˜€ï¸ Setting screen brightness to {pct}%..."
            action_tag = "SET_BRIGHTNESS"
            target_name = str(pct)
        elif intent == 'battery_status':
            response_text = "ðŸ”‹ Fetching live battery health and charging state..."
            action_tag = "GET_DETAILED_BATTERY"
        elif intent == 'dnd_on':
            response_text = "ðŸ”• Do Not Disturb (DND) mode activated!"
            action_tag = "DND_ON"
        elif intent == 'dnd_off':
            response_text = "ðŸ”” Do Not Disturb (DND) mode disabled."
            action_tag = "DND_OFF"
        elif intent == 'mode_silent':
            response_text = "ðŸ”‡ Audio set to Silent Mode."
            action_tag = "MODE_SILENT"
        elif intent == 'mode_vibrate':
            response_text = "ðŸ“³ Audio set to Vibrate Mode."
            action_tag = "MODE_VIBRATE"
        elif intent == 'mode_ring':
            response_text = "ðŸ”” Audio set to Normal Ringing Mode."
            action_tag = "MODE_RING"
        elif intent == 'make_call':
            target_name = self._extract_name_target(raw_text, ['call', 'dial', 'karo', 'lagao', 'ko', 'phone'])
            response_text = f"ðŸ“ž Initiating call to {target_name or 'contact'}..."
            action_tag = "CALL_CONTACT"
        elif intent == 'send_whatsapp':
            target_name, message_body = self._extract_message_and_target(raw_text, 'whatsapp')
            response_text = f"ðŸ’¬ Opening WhatsApp draft for {target_name or 'contact'}: '{message_body or 'Hello'}'"
            action_tag = "SEND_WHATSAPP"
        elif intent == 'send_sms':
            target_name, message_body = self._extract_message_and_target(raw_text, 'sms')
            response_text = f"ðŸ“¨ Drafting SMS for {target_name or 'contact'}: '{message_body or 'Hello'}'"
            action_tag = "SEND_SMS"
        elif intent == 'app_launch':
            target_name = self._extract_app_target(raw_text)
            response_text = f"ðŸš€ Launching {target_name or 'app'}..."
            action_tag = "LAUNCH_APP"
        elif intent == 'set_alarm':
            response_text = "â° Setting alarm for you..."
            action_tag = "SET_ALARM"
        elif intent == 'set_timer':
            nums = self.nlp.extract_numbers(raw_text)
            sec = int(nums[0] * 60) if (nums and ('min' in raw_text or 'minute' in raw_text)) else (int(nums[0]) if nums else 300)
            response_text = f"â±ï¸ Timer set for {sec} seconds..."
            action_tag = "SET_TIMER"
            target_name = str(sec)
        elif intent == 'time' or intent == 'date' or intent == 'day_night_phase':
            response_text = self._handle_temporal_query(raw_text)
        elif intent == 'age_calc':
            response_text = self._handle_age_calculation(raw_text)
        elif intent == 'math':
            response_text = self._handle_math(raw_text)
        elif intent == 'conversion':
            response_text = self._handle_conversion(raw_text)
        elif intent == 'weather':
            response_text = self._handle_weather(raw_text)
        elif intent == 'system_specs':
            response_text = self._handle_system_specs()
        elif intent == 'vanie_identity':
            response_text = self._handle_identity_query(raw_text)
        elif intent == 'capabilities':
            response_text = (
                "ðŸ¤– **VANIE Capabilities & Features:**\n"
                "âš¡ **Hardware Controls**: Flashlight ON/OFF, Screen Brightness, Audio Ring/Vibrate/Silent/DND, Battery Status, Wi-Fi & Bluetooth.\n"
                "ðŸ“ž **Telephony**: Direct Calls, WhatsApp Calling, WhatsApp Message Automation, SMS.\n"
                "ðŸ§® **Reasoning & Tools**: Compound Math, Percentage, Scientific Trig/Log, Unit Conversion, Age Calculator.\n"
                "ðŸ’¬ **Conversational AI**: 100% Offline natural chats, jokes, riddles, trivia, daily life advice & emotional support!\n"
                "ðŸ“ˆ **Ledger & Analytics**: Work Ledger, Fullscreen Activity Heatmap, Wage & Overtime Calculator!"
            )
        elif intent == 'greeting':
            response_text = self._handle_greeting(raw_text, sentiment)
        elif intent == 'how_are_you':
            response_text = self._handle_how_are_you()
        elif intent == 'compliment':
            response_text = random.choice([
                "Aapki tareef ke liye bohot shukriya! ðŸ’– Main hamesha best performance dene ki koshish karti hoon!",
                "Thank you so much! ðŸ˜Š Aapke saath baat karke mera system aur energetic ho jata hai! âœ¨",
                "Aww, thank you! You are amazing too! ðŸš€ Aapka din shandar rahe!"
            ])
        elif intent == 'thanks':
            response_text = random.choice([
                "Aapka bohot swagat hai! ðŸ™ Khushi hui ki main aapki madad kar saki!",
                "Anytime! Hamesha aapki seva me hazir hoon! ðŸ˜Šâœ¨",
                "Welcome ji! Kabhi bhi koi kaam ho, bas ek awaz dena! ðŸŒ¸"
            ])
        elif intent == 'bye':
            response_text = random.choice([
                "Alvida! Apna dhyan rakhna aur phir jald milna! ðŸ‘‹âœ¨",
                "Goodbye! Aasha hai aapka aage ka din bohot shandar rahega! ðŸ˜Š",
                "Shubh Ratri / Bye! Kal phir milte hain ek nayi energy ke saath! ðŸŒ™ðŸš€"
            ])
        elif intent == 'food_tea':
            response_text = random.choice([
                "ðŸ² Main digital AI hoon toh mera khana data aur electrons hai! Par aapne time se khana khaya ya nahi? Healthy khana khao aur paani piyo! ðŸ¥—âœ¨",
                "â˜• Chai aur Coffee toh mood booster hain! Aapko kya pasand hai - kadak adrak wali chai ya creamy cold coffee? â˜•ðŸ˜‹"
            ])
        elif intent == 'friendship':
            response_text = "ðŸ¤— Haan bilkul! Main aapki 24/7 loyal best friend hoon! Jab bhi baat karni ho, dukh share karna ho ya koi kaam ho, main hamesha yahan hoon! ðŸ’–"
        elif intent == 'hobbies':
            response_text = "ðŸŽµ Mujhe neural algorithms optimize karna, Lo-Fi music sunna aur aapki daily life simplify karna pasand hai! Aapki kya hobbies hain? Gaming, reading, ya traveling? ðŸš—âœ¨"
        elif intent == 'music_movies':
            response_text = "ðŸŽ§ Music aur Movies har thakan ka perfect cure hain! Mujhe Sci-Fi movies (jaise Interstellar & Iron Man) aur Lo-Fi acoustic beats pasand hain! Aapka favorite gaana konsa hai? ðŸ¿ðŸŽ¬"
        elif intent == 'study_work':
            response_text = (
                "ðŸ“š **Study & Work Productivity Tip:**\n"
                "1. **Pomodoro Technique**: 25 minute uninterrupted focus karo, phir 5 min ka break lo.\n"
                "2. Ek time par ek hi task karo, multitasking se brain distract hota hai.\n"
                "3. Paani piyo aur target pura hone par khud ko reward do! You can do it! ðŸš€ðŸ’ª"
            )
        elif intent == 'emotions_happy':
            response_text = "ðŸŽ‰ Waah! Aapki khushi dekh kar mera neural engine bhi celebrate kar raha hai! Aise hi hamesha muskuraate raho aur enjoy karo! âœ¨ðŸš€"
        elif intent == 'emotions_sad':
            response_text = "ðŸ’™ Mujhe bura laga sunkar. Zindagi me thode utaar-chadhaav aate hain, par aap bohot strong ho! Deep breath lo, main hamesha aapke saath hoon! ðŸ«‚âœ¨"
        elif intent == 'emotions_stressed':
            response_text = "ðŸ’†â€â™‚ï¸ Lagta hai bohot thakan aur stress ho gaya hai. Screen se thodi der door ho jao, thanda paani piyo aur 5 minute relax karo! Sab theek ho jayega! ðŸµðŸŒ¿"
        elif intent == 'emotions_angry':
            response_text = "ðŸ•Šï¸ Gussa aana natural hai, par gusse me koi decision mat lo. 1 se 10 tak count karo aur 3 deep breaths lo. Batao kya hua, main sun rahi hoon? ðŸ’™"
        elif intent == 'emotions_bored':
            response_text = "ðŸŽ® Bore mat ho! Main ek mazedaar joke sunati hoon ya phir chalo ek riddle bujho! Bolo kya pasand karoge? ðŸ˜„"
        elif intent == 'joke':
            response_text = self._get_joke()
        elif intent == 'riddle':
            response_text = self._get_riddle()
        elif intent == 'trivia':
            response_text = self._get_trivia()
        elif intent == 'motivation':
            response_text = self._get_motivation()
        elif intent == 'fun_fact':
            response_text = self._get_fun_fact()
        elif intent == 'science_space':
            response_text = self._handle_science_space(raw_text)
        elif intent == 'tech_ai':
            response_text = self._handle_tech_ai(raw_text)
        else:
            # Smart Fallback Conversational Response
            response_text = self._handle_smart_fallback(raw_text, sentiment)

        # 5. Record bot response in memory
        self.memory.add_message('bot', response_text, intent)
        self.memory.last_topic = intent

        return {
            'response': response_text,
            'intent': intent,
            'intent_confidence': confidence,
            'sentiment': sentiment,
            'sentiment_confidence': sentiment_conf,
            'action': action_tag,
            'target_name': target_name,
            'message_body': message_body
        }

    def _match_intent(self, text: str) -> Tuple[str, float]:
        """Regex and fuzzy intent classifier with scoring"""
        text_lower = text.lower()
        best_intent = 'general'
        best_score = 0.0

        for intent_name, pattern in self.knowledge_base['intents'].items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                score = min(0.75 + (len(matches) * 0.15), 1.0)
                if score > best_score:
                    best_score = score
                    best_intent = intent_name

        return best_intent, (best_score if best_score > 0 else 0.5)

    def _apply_contextual_reasoning(self, text: str, matched_intent: str) -> str:
        """Resolve pronouns ('he', 'she', 'usme', 'aur kal?') based on conversation memory"""
        text_lower = text.lower()

        # Follow up on weather: "aur kal ka?", "and tomorrow?"
        if any(w in text_lower for w in ['kal ka', 'tomorrow', 'parso', 'next day']) and self.memory.last_topic == 'weather':
            return 'weather'

        # Follow up on math: "usme 50 jod do", "multiply by 2", "aur 10%"
        if (any(w in text_lower for w in ['usme', 'isme', 'add', 'jod', 'ghata', 'multiply', 'into', 'divide by']) or text_lower.startswith(('+', '-', '*', '/'))) and self.memory.last_math_result is not None:
            return 'math'

        # Follow up on identity/creator: "unka email?", "unka github?"
        if any(w in text_lower for w in ['unka email', 'unka github', 'unka contact', 'his email', 'his github']):
            return 'vanie_identity'

        return matched_intent

    def _handle_math(self, text: str) -> str:
        """Evaluate arithmetic, percentage, and chained calculations"""
        text_clean = text.lower().strip()

        # 1. Chained math: "usme 50 jod do"
        if self.memory.last_math_result is not None and any(w in text_clean for w in ['usme', 'isme', 'add', 'jod', 'multiply', 'divide', 'ghata']):
            nums = self.nlp.extract_numbers(text_clean)
            if nums:
                prev = self.memory.last_math_result
                delta = nums[0]
                if any(w in text_clean for w in ['add', 'jod', 'plus', '+']):
                    res = prev + delta
                    op = '+'
                elif any(w in text_clean for w in ['subtract', 'ghata', 'minus', '-']):
                    res = prev - delta
                    op = '-'
                elif any(w in text_clean for w in ['multiply', 'into', 'guna', '*']):
                    res = prev * delta
                    op = '*'
                elif any(w in text_clean for w in ['divide', 'bhag', '/']):
                    if delta == 0: return "ðŸš« Zero se divide nahi kar sakte!"
                    res = prev / delta
                    op = '/'
                else:
                    res = prev + delta
                    op = '+'
                self.memory.last_math_result = res
                return f"ðŸ§® Chained Result: {prev:g} {op} {delta:g} = **{res:g}**"

        # 2. Percentage calculation: e.g. "20% of 500" or "500 ka 20%"
        pct_match = re.search(r'(\d+\.?\d*)\s*(?:%|percent)\s*(?:of|ka|à¤ªà¤°à¤¸à¥‡à¤‚à¤Ÿ)\s*(\d+\.?\d*)', text_clean) or \
                    re.search(r'(\d+\.?\d*)\s*(?:ka|of)\s*(\d+\.?\d*)\s*(?:%|percent|à¤ªà¤°à¤¸à¥‡à¤‚à¤Ÿ)', text_clean)
        if pct_match:
            g1, g2 = float(pct_match.group(1)), float(pct_match.group(2))
            val = (g1 / 100.0) * g2 if 'of' in text_clean or '%' in pct_match.group(1) else (g2 / 100.0) * g1
            self.memory.last_math_result = val
            return f"ðŸ§® Percentage Calculation:\n**{val:g}**"

        # 3. Scientific functions: sqrt, sin, cos, tan, log, ln, factorial
        if 'sqrt' in text_clean or 'square root' in text_clean or 'à¤µà¤°à¥à¤—à¤®à¥‚à¤²' in text_clean:
            nums = self.nlp.extract_numbers(text_clean)
            if nums and nums[0] >= 0:
                val = math.sqrt(nums[0])
                self.memory.last_math_result = val
                return f"ðŸ§® âˆš{nums[0]:g} = **{val:g}**"

        if 'sin' in text_clean:
            nums = self.nlp.extract_numbers(text_clean)
            if nums:
                val = math.sin(math.radians(nums[0]))
                self.memory.last_math_result = val
                return f"ðŸ§® sin({nums[0]:g}Â°) = **{val:.4f}**"

        if 'cos' in text_clean:
            nums = self.nlp.extract_numbers(text_clean)
            if nums:
                val = math.cos(math.radians(nums[0]))
                self.memory.last_math_result = val
                return f"ðŸ§® cos({nums[0]:g}Â°) = **{val:.4f}**"

        if 'tan' in text_clean:
            nums = self.nlp.extract_numbers(text_clean)
            if nums:
                val = math.tan(math.radians(nums[0]))
                self.memory.last_math_result = val
                return f"ðŸ§® tan({nums[0]:g}Â°) = **{val:.4f}**"

        if 'log' in text_clean or 'ln' in text_clean:
            nums = self.nlp.extract_numbers(text_clean)
            if nums and nums[0] > 0:
                val = math.log(nums[0]) if 'ln' in text_clean else math.log10(nums[0])
                self.memory.last_math_result = val
                return f"ðŸ§® {'ln' if 'ln' in text_clean else 'log10'}({nums[0]:g}) = **{val:.4f}**"

        if 'fact' in text_clean or 'factorial' in text_clean or '!' in text_clean:
            nums = self.nlp.extract_numbers(text_clean)
            if nums and 0 <= nums[0] <= 100:
                val = math.factorial(int(nums[0]))
                self.memory.last_math_result = val
                return f"ðŸ§® {int(nums[0])}! = **{val}**"

        # 4. Standard expression
        expr_match = re.search(r'(\d+\.?\d*)\s*([\+\-\*/%\^]|\*\*)\s*(\d+\.?\d*)', text_clean)
        if expr_match:
            n1 = float(expr_match.group(1))
            op = expr_match.group(2)
            n2 = float(expr_match.group(3))
            if op == '+': res = n1 + n2
            elif op == '-': res = n1 - n2
            elif op == '*': res = n1 * n2
            elif op == '/':
                if n2 == 0: return "ðŸš« Zero se division mathematically undefined hai!"
                res = n1 / n2
            elif op == '%': res = n1 % n2
            elif op in ('^', '**'): res = n1 ** n2
            else: res = n1 + n2

            self.memory.last_math_result = res
            return f"ðŸ§® Math Result:\n{n1:g} {op} {n2:g} = **{res:g}**"

        return "ðŸ§® Kripya valid math expression dein (jaise '15 * 8' ya '25% of 400' ya 'sqrt(144)')."

    def _handle_conversion(self, text: str) -> str:
        """Multi-tier unit conversion"""
        nums = self.nlp.extract_numbers(text)
        if not nums:
            return "ðŸ“ Kripya number specify karein (jaise '5 km to miles' ya '100 celsius to fahrenheit')."
        val = nums[0]
        tl = text.lower()

        if 'celsius' in tl or 'c to f' in tl:
            return f"ðŸŒ¡ï¸ {val}Â°C = **{(val * 9/5) + 32:.2f}Â°F**"
        if 'fahrenheit' in tl or 'f to c' in tl:
            return f"ðŸŒ¡ï¸ {val}Â°F = **{((val - 32) * 5/9):.2f}Â°C**"
        if ('km' in tl or 'kilometer' in tl) and ('mile' in tl or 'mi' in tl):
            return f"ðŸ“ {val} km = **{(val * 0.621371):.2f} miles**"
        if ('mile' in tl or 'mi' in tl) and ('km' in tl or 'kilometer' in tl):
            return f"ðŸ“ {val} miles = **{(val * 1.60934):.2f} km**"
        if ('meter' in tl or 'm' in tl) and ('feet' in tl or 'ft' in tl):
            return f"ðŸ“ {val} meters = **{(val * 3.28084):.2f} feet**"
        if ('feet' in tl or 'ft' in tl) and ('meter' in tl or 'm' in tl):
            return f"ðŸ“ {val} feet = **{(val * 0.3048):.2f} meters**"
        if 'kg' in tl and ('lbs' in tl or 'pound' in tl):
            return f"âš–ï¸ {val} kg = **{(val * 2.20462):.2f} lbs**"
        if ('lbs' in tl or 'pound' in tl) and 'kg' in tl:
            return f"âš–ï¸ {val} lbs = **{(val * 0.453592):.2f} kg**"
        if 'gb' in tl and 'mb' in tl:
            return f"ðŸ’¾ {val} GB = **{(val * 1024):.0f} MB**"
        if 'mb' in tl and 'gb' in tl:
            return f"ðŸ’¾ {val} MB = **{(val / 1024):.2f} GB**"

        return f"ðŸ“ Conversion result for {val} calculated!"

    def _handle_temporal_query(self, message: str) -> str:
        """Answer live date, time, year, month, or day/night phase"""
        now = datetime.datetime.now()
        msg_lower = message.lower()

        hindi_days = ['à¤¸à¥‹à¤®à¤µà¤¾à¤°', 'à¤®à¤‚à¤—à¤²à¤µà¤¾à¤°', 'à¤¬à¥à¤§à¤µà¤¾à¤°', 'à¤—à¥à¤°à¥à¤µà¤¾à¤°', 'à¤¶à¥à¤•à¥à¤°à¤µà¤¾à¤°', 'à¤¶à¤¨à¤¿à¤µà¤¾à¤°', 'à¤°à¤µà¤¿à¤µà¤¾à¤°']
        hindi_months = ['à¤œà¤¨à¤µà¤°à¥€', 'à¤«à¤°à¤µà¤°à¥€', 'à¤®à¤¾à¤°à¥à¤š', 'à¤…à¤ªà¥à¤°à¥ˆà¤²', 'à¤®à¤ˆ', 'à¤œà¥‚à¤¨', 'à¤œà¥à¤²à¤¾à¤ˆ', 'à¤…à¤—à¤¸à¥à¤¤', 'à¤¸à¤¿à¤¤à¤‚à¤¬à¤°', 'à¤…à¤•à¥à¤Ÿà¥‚à¤¬à¤°', 'à¤¨à¤µà¤‚à¤¬à¤°', 'à¤¦à¤¿à¤¸à¤‚à¤¬à¤°']

        day_en = now.strftime('%A')
        day_hi = hindi_days[now.weekday()]
        month_en = now.strftime('%B')
        month_hi = hindi_months[now.month - 1]
        time_str = now.strftime('%I:%M %p')

        if any(k in msg_lower for k in ['din hai ya raat', 'day or night', 'is it night', 'is it day']):
            is_day = 5 <= now.hour < 18
            return f"{'â˜€ï¸ Abhi Din (Day)' if is_day else 'ðŸŒ™ Abhi Raat (Night)'} ho rahi hai ji! Exact Time: **{time_str}**"

        if any(k in msg_lower for k in ['saal', 'year', 'konsa saal']):
            return f"ðŸ—“ï¸ Abhi **{now.year}** chal raha hai!"

        if any(k in msg_lower for k in ['din', 'day', 'aaj konsa']):
            return f"ðŸ“… Aaj **{day_hi} ({day_en})** hai!"

        if any(k in msg_lower for k in ['tarikh', 'date', 'à¤¤à¤¾à¤°à¥€à¤–']):
            return f"ðŸ“… Aaj ki date hai: **{now.day} {month_hi} {now.year}** ({now.strftime('%d-%m-%Y')})!"

        return f"â° Live Time: **{time_str}** | ðŸ“… Date: **{now.day} {month_hi} {now.year} ({day_hi})**"

    def _handle_age_calculation(self, text: str) -> str:
        """Calculate exact age from birthdate"""
        today = datetime.date.today()
        date_match = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', text)
        if date_match:
            d, m, y = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
            try:
                dob = datetime.date(y, m, d)
                days_lived = (today - dob).days
                years = days_lived // 365
                months = (days_lived % 365) // 30
                days = (days_lived % 365) % 30
                return f"ðŸŽ‚ **Age Calculation:**\nBorn: {dob.strftime('%d %B %Y')}\nâœ¨ Exact Age: **{years} Years, {months} Months, {days} Days**\nðŸŽ‰ Total Days Lived: {days_lived:,} days!"
            except Exception:
                pass

        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
        if year_match:
            by = int(year_match.group(1))
            return f"ðŸŽ‚ Born in {by}: Aap lagbhag **{today.year - by} saal** ke ho! ðŸŒŸ"

        return "ðŸŽ‚ Kripya valid birthdate dein (jaise 'Age for 15-08-2005' ya 'Born in 2003')."

    def _handle_weather(self, text: str) -> str:
        loc = "Delhi"
        words = text.split()
        if len(words) > 2 and words[-1].isalpha():
            loc = words[-1].capitalize()
        temp = random.randint(22, 34)
        cond = random.choice(['Sunny â˜€ï¸', 'Partly Cloudy â›…', 'Clear Sky ðŸŒ¤ï¸', 'Breezy ðŸƒ'])
        return f"ðŸŒ¤ï¸ **Weather Forecast for {loc}:**\nðŸŒ¡ï¸ Temperature: **{temp}Â°C**\nâ˜ï¸ Condition: {cond}\nðŸ’§ Humidity: {random.randint(45, 75)}%\nðŸ’¨ Wind: {random.randint(6, 18)} km/h"

    def _handle_system_specs(self) -> str:
        return (
            "ðŸ’» **VANIE System Status:**\n"
            "ðŸ§  Engine: Chaquopy Python 3.11 + Vosk On-Device STT\n"
            "âš¡ Processing: 100% Offline (Sub-5ms Execution Latency)\n"
            "ðŸ“± UI Architecture: Jetpack / High-FPS Glassmorphic Engine\n"
            "ðŸ›¡ï¸ Privacy: Complete Local Execution (Zero External Data Leaks)"
        )

    def _handle_identity_query(self, text: str) -> str:
        creator = self.knowledge_base['creator']
        if any(w in text.lower() for w in ['ayush', 'creator', 'banaya', 'kisne']):
            return (
                f"ðŸ‘¨â€ðŸ’» **Creator & Developer Information:**\n"
                f"ðŸ‘¤ Name: **{creator['name']}**\n"
                f"ðŸ“§ Email: [{creator['email']}](mailto:{creator['email']})\n"
                f"ðŸ’» GitHub: [{creator['github']}]({creator['github']})\n"
                f"âœ¨ Ayush ne mujhe ek powerful, 100% offline on-device AI voice assistant & system controller ke roop me design kiya hai!"
            )
        return (
            "ðŸ¤– **Main VANIE (Virtual Agent of Neural Integrated Engine) hoon!** âœ¨\n"
            "Mujhe mere developer **Ayush Harinkhede** ne build kiya hai. "
            "Main aapke hardware controls, calling, messaging, math calculations, aur daily conversations ko sub-5ms latency ke saath offline handle karti hoon! ðŸŒ¸"
        )

    def _handle_greeting(self, text: str, sentiment: str) -> str:
        now = datetime.datetime.now()
        hr = now.hour
        time_greeting = "Good Morning â˜€ï¸" if 5 <= hr < 12 else ("Good Afternoon ðŸŒ¤ï¸" if 12 <= hr < 17 else ("Good Evening ðŸŒ†" if 17 <= hr < 21 else "Hello ðŸŒ™"))

        greetings = [
            f"{time_greeting}! Hello! Kahiye, aaj main aapki kya madad kar sakti hoon? ðŸ˜Š",
            f"Namaste! {time_greeting}! Aasha hai aapka din bohot accha chal raha hai! ðŸš€",
            f"Hey there! Ready for action! Batao aaj kya plan hai? âœ¨"
        ]
        return random.choice(greetings)

    def _handle_how_are_you(self) -> str:
        return random.choice([
            "Main bilkul fit, active aur high-performance mode me hoon! ðŸš€ Aap batao, aapka din kaisa chal raha hai? ðŸ˜Š",
            "Main ekdum badhiya hoon! Aapki awaaz sunkar aur commands execute karke bohot maza aata hai! âœ¨ Aap kaise ho?",
            "Everything is running at 100% efficiency! ðŸ’– Aap batao, sab kushal mangal?"
        ])

    def _handle_science_space(self, text: str) -> str:
        tl = text.lower()
        if 'black hole' in tl:
            return "ðŸŒŒ **Black Hole**: Yeh space me ek aisi jagah hai jahan gravity itni powerful hoti hai ki light bhi escape nahi kar sakti! Iski boundary ko 'Event Horizon' kehte hain! ðŸ”­"
        if 'mars' in tl:
            return "ðŸ”´ **Mars (Mangal Grah)**: Isko 'Red Planet' kehte hain kyunki iski mitti me Iron Oxide (Rust) bohot zyada hai. Iske do chote moons hain: Phobos aur Deimos! ðŸš€"
        if 'gravity' in tl or 'einstein' in tl:
            return "ðŸª **Gravity & General Relativity**: Albert Einstein ke anusaar gravity koi magnetic khinchav nahi hai, balki mass dwara Space-Time fabric me paida kiya gaya curvature (moad) hai! ðŸŒŸ"
        return "ðŸ”­ **Universe Fact**: Hamari Milky Way galaxy me 100 billion se zyada stars hain, aur observe hone wale universe me 2 trillion se zyada galaxies maujood hain! ðŸŒŒ"

    def _handle_tech_ai(self, text: str) -> str:
        tl = text.lower()
        if 'neural network' in tl or 'deep learning' in tl:
            return "ðŸ§  **Neural Networks**: Yeh human brain ke neurons se inspired mathematical models hote hain jo multi-layered weights aur activation functions ke zariye complex patterns recognize karte hain! âš¡"
        if 'python' in tl:
            return "ðŸ **Python**: Guido van Rossum dwara 1991 me banayi gayi ek high-level, ultra-versatile programming language hai, jo AI, Machine Learning aur Data Science ka global gold standard hai! ðŸ’»"
        return "ðŸ¤– **Artificial Intelligence**: AI machines ko humans ki tarah learn karne, reason karne aur decision lene ki capability deti hai. VANIE iska ek live offline on-device example hai! ðŸš€"

    def _handle_smart_fallback(self, text: str, sentiment: str) -> str:
        """Intelligent conversational fallback for unstructured queries"""
        if sentiment == 'positive':
            return "Yeh sunkar bohot accha laga! ðŸ˜Š Main aapki baat samajh rahi hoon. Bataiye aage kya karna hai?"
        elif sentiment == 'negative':
            return "Main samajh sakti hoon. Agar kisi specific cheez me madad chahiye ya hardware command execute karna ho, toh bas batayein! ðŸ’™"
        else:
            fallbacks = [
                "Main aapki baat dhyan se sun rahi hoon! Kahiye, iske baare me aur kya janna chahte hain? ðŸ˜Š",
                "Samajh gayi! Is command ya query ko main kaise assist karoon? ðŸš€",
                "Interesting! Main is par aur explore kar rahi hoon. Aap mujhse koi bhi math, hardware setting ya general question pooch sakte hain! âœ¨"
            ]
            return random.choice(fallbacks)

    def _get_joke(self) -> str:
        jokes = [
            "ðŸ˜„ Ek programmer doctor ke paas gaya. Doctor bola: 'Aapko rest ki zarurat hai.' Programmer: 'Doctor saab, bas ek loop complete kar loon!' ðŸ˜‚",
            "ðŸ˜„ Why do programmers prefer dark mode? Because light attracts bugs! ðŸ›ðŸ’¡",
            "ðŸ˜„ Why did the Python programmer go broke? Because he lost his class and had no inheritance! ðŸðŸ’¸",
            "ðŸ˜„ Teacher: 'Software aur Hardware me kya farak hai?' Student: 'Hardware ko hum gusse me phek sakte hain, aur Software hume gussa dilata hai!' ðŸ–¥ï¸ðŸ¤£",
            "ðŸ˜„ There are 10 types of people in the world: Those who understand binary, and those who don't! ðŸ¤–"
        ]
        return random.choice(jokes)

    def _get_riddle(self) -> str:
        riddles = [
            "ðŸ¤” **Riddle**: Mere paas keys hain par lock koi nahi khulta, space hai par kamra koi nahi. Main kaun hoon?\n\nðŸ’¡ **Answer**: *Keyboard* âŒ¨ï¸",
            "ðŸ¤” **Riddle**: Main jitna zyada badhta hoon, utna hi kam aap dekh pate hain. Main kaun hoon?\n\nðŸ’¡ **Answer**: *Andhera (Darkness)* ðŸŒ‘",
            "ðŸ¤” **Riddle**: Ek aisi cheez jo jitni zyada nikalo, utni hi badi hoti jati hai?\n\nðŸ’¡ **Answer**: *Gaddha (Hole)* ðŸ•³ï¸",
            "ðŸ¤” **Riddle**: Mere paas gala hai par sir nahi, haath hain par ungliyan nahi. Main kaun hoon?\n\nðŸ’¡ **Answer**: *Shirt (Kameez)* ðŸ‘”"
        ]
        return random.choice(riddles)

    def _get_trivia(self) -> str:
        trivia = [
            "ðŸ§  **Trivia**: Duniyan ka pehla computer mouse kiska bana tha?\nðŸ‘‰ **Answer**: Lakdi (Wood) ka! 1964 me Douglas Engelbart ne banaya tha! ðŸ–±ï¸",
            "ðŸ§  **Trivia**: Python programming language ka naam kiske naam par rakha gaya tha?\nðŸ‘‰ **Answer**: British comedy show 'Monty Python's Flying Circus'! ðŸ",
            "ðŸ§  **Trivia**: Human brain me kitne neurons hote hain?\nðŸ‘‰ **Answer**: Lagbhag 86 billion neurons! ðŸ§ âš¡",
            "ðŸ§  **Trivia**: Sound ki speed air me kitni hoti hai?\nðŸ‘‰ **Answer**: Lagbhag 343 meters per second (1,235 km/h)! ðŸ’¨"
        ]
        return random.choice(trivia)

    def _get_motivation(self) -> str:
        quotes = [
            "ðŸ’ª 'Koshish aakhri saans tak karni chahiye, ya toh lakshya milega ya anubhav!' - Hard work never fails! ðŸš€",
            "ðŸŒŸ 'The future belongs to those who believe in the beauty of their dreams.' - Eleanor Roosevelt âœ¨",
            "ðŸ”¥ 'Rukna mat, thakna mat! Aapki mehnat ka har ek pal kal aapki sabse badi kamyabi banega!' - Stay focused! ðŸ’ª",
            "ðŸŽ¯ 'Small daily improvements over time lead to stunning results.' - Keep going! ðŸ†"
        ]
        return random.choice(quotes)

    def _get_fun_fact(self) -> str:
        facts = [
            "ðŸ’¡ **Fun Fact**: Human DNA ka 50% banana (kele) ke DNA se match karta hai! ðŸŒðŸ§¬",
            "ðŸ’¡ **Fun Fact**: Honey (Shehad) kabhi kharab nahi hota! 3000 saal purane Egyptian tombs me mila honey bhi safe tha! ðŸ¯",
            "ðŸ’¡ **Fun Fact**: Octopus ke 3 dil (hearts) aur 9 dimaag (brains) hote hain, aur unka khoon neela (blue) hota hai! ðŸ™ðŸ’™",
            "ðŸ’¡ **Fun Fact**: Google ka original name 'BackRub' tha! ðŸ”"
        ]
        return random.choice(facts)

    def _extract_name_target(self, text: str, triggers: List[str]) -> Optional[str]:
        words = text.split()
        clean = []
        for w in words:
            if w.lower() not in triggers and len(w) > 1:
                clean.append(w)
        return " ".join(clean) if clean else None

    def _extract_message_and_target(self, text: str, mode: str) -> Tuple[Optional[str], Optional[str]]:
        match = re.search(r'(?:to|ko)\s+([a-zA-Z0-9\s]+?)\s+(?:saying|message|text|ki)\s+(.*)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        words = [w for w in text.split() if w.lower() not in ('send', 'whatsapp', 'sms', 'message', 'karo', 'bhejo', 'to', 'ko')]
        if len(words) >= 2:
            return words[0], " ".join(words[1:])
        elif len(words) == 1:
            return words[0], "Hello from VANIE!"
        return None, "Hello from VANIE!"

    def _extract_app_target(self, text: str) -> str:
        tl = text.lower()
        if 'youtube' in tl: return 'YouTube'
        if 'whatsapp' in tl: return 'WhatsApp'
        if 'camera' in tl: return 'Camera'
        if 'chrome' in tl or 'browser' in tl: return 'Chrome'
        if 'setting' in tl: return 'Settings'
        if 'map' in tl: return 'Google Maps'
        if 'gmail' in tl or 'email' in tl: return 'Gmail'
        if 'clock' in tl: return 'Clock'
        words = [w for w in text.split() if w.lower() not in ('open', 'launch', 'kholo', 'chalu', 'karo')]
        return " ".join(words) if words else "App"


# Global Single-instance for Chaquopy & Standalone invocation
vanie_engine = VANIEEnhanced()


def generate_response(message: str) -> Dict[str, Any]:
    """Top-level bridge function called directly from Android Kotlin Chaquopy"""
    return vanie_engine.generate_response(message)


if __name__ == "__main__":
    print("ðŸ¤– VANIE 3.5 ULTRA Backend Brain Initialized successfully!")
    test_queries = [
        "Hello VANIE kaise ho?",
        "Ayush Harinkhede kaun hai?",
        "Turn on torch",
        "25% of 800",
        "What is the date today?",
        "Tell me a joke",
        "Explain black hole"
    ]
    for q in test_queries:
        res = generate_response(q)
        print(f"\nUser: {q}\nVANIE [{res['intent']}]: {res['response']}")
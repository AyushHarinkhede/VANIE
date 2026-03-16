
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import requests
import hashlib

# Try to import NLP libraries - fallback to basic if not available
try:
    import spacy
    SPACY_AVAILABLE = True
    # Load small English model for semantic understanding
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
        SPACY_AVAILABLE = False
        nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    print("⚠️ spaCy not installed. Run: pip install spacy")

# Try to import sentence transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    # Load a lightweight model for semantic understanding
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    sentence_model = None
    print("⚠️ Sentence Transformers not installed. Run: pip install sentence-transformers")

class VANIEKnowledgeBase:
    """Complete knowledge base with intents, keywords, and responses"""
    
    @staticmethod
    def get_intents():
        return {
            # 1. Greetings & Small Talk Intent
            'greeting': {
                'keywords': [
                    'hi', 'hello', 'hey', 'hey there', 'good morning', 'good afternoon', 'good evening',
                    'good night', 'greetings', 'welcome', 'what\'s up', 'whats up', 'sup', 'yo',
                    'how are you', 'howdy', 'how do you do', 'nice to meet you', 'pleased to meet you',
                    'नमस्ते', 'नमस्कार', 'प्रणाम', 'राम राम', 'हाय', 'हेलो', 'हे',
                    'कैसे हो', 'कैसी हो', 'कैसी हैं', 'क्या हाल है', 'क्या हाल चाल',
                    'सुप्रभात', 'शुभ प्रभात', 'शुभ रात्रि', 'आप कैसे हो',
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
                'priority': 1
            },
            
            # 2. Identity & Creator Intent
            'identity': {
                'keywords': [
                    'who are you', 'what are you', 'what is your name', 'your name', 'tell me about yourself',
                    'introduce yourself', 'what is vanie', 'what does vanie stand for',
                    'who made you', 'who created you', 'who is your creator', 'who is your owner',
                    'who developed you', 'who programmed you', 'who built you', 'your creator',
                    'your developer', 'your owner', 'your maker', 'your father', 'your boss',
                    'तुम कौन हो', 'तुम क्या हो', 'तुम्हारा नाम क्या है', 'तुम्हारा परिचय',
                    'तुम कौन हो वैनी', 'वैनी कौन है', 'वैनी क्या है',
                    'तुम्हें किसने बनाया', 'तुम्हारा निर्माता कौन है', 'तुम्हारा creator कौन है',
                    'किसने बनाया', 'किसने बनाया वैनी', 'तुम्हारा malik कौन है',
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
                'priority': 3
            },
            
            # 3. Capabilities & Usefulness Intent
            'capabilities': {
                'keywords': [
                    'what can you do', 'what do you do', 'your capabilities', 'your features',
                    'what are your abilities', 'what are your skills', 'how can you help',
                    'help me', 'assist me', 'what can you assist with', 'your functions',
                    'what are you good at', 'what do you specialize in', 'your purpose',
                    'how can you be useful', 'what services do you provide', 'your utilities',
                    'तुम क्या कर सकते हो', 'तुम क्या करते हो', 'तुम्हारी capabilities क्या हैं',
                    'तुम कैसे मदद कर सकते हो', 'तुम क्या काम कर सकते हो',
                    'तुम्हारी features क्या हैं', 'तुम्हारे skills क्या हैं',
                    'मुझे मदद करो', 'मेरी मदद करो', 'तुम मेरी कैसे मदद कर सकते हो',
                    'तुम्हारा purpose क्या है', 'तुम कैसे useful हो सकते हो',
                    'tum kya kar sakte ho', 'tum kya karte ho', 'tumhari capabilities kya hain',
                    'help me', 'assist me', 'tum meri kaise help kar sakte ho',
                    'what can you do', 'your features', 'your skills'
                ],
                'responses': [
                    "मैं आपकी कई तरह से मदद कर सकती हूँ! 🌟\n\n💬 **Conversations**: Natural और friendly बातचीत\n❓ **Questions Answering**: Science, History, Math, Coding में सवाल\n🔧 **Problem Solving**: Complex problems का solution\n📚 **Learning**: New topics सिखाना\n💡 **Ideas**: Creative suggestions देना\n⏰ **Real-time Info**: Time, date, weather updates\n🎯 **Personalization**: आपकी preferences याद रखना\n\nक्या आप कुछ specific जानना चाहते हैं?",
                    "I can help you in many ways! 🚀\n\n🤖 **AI Assistant**: Answer questions and have conversations\n📚 **Knowledge Base**: Science, History, Math, Coding, and more\n🔧 **Problem Solver**: Help with homework and complex problems\n💬 **Friendly Chat**: Natural and engaging conversations\n⏰ **Real-time Info**: Current time, date, and weather\n🎯 **Remember You**: Personalized experience\n\nWhat would you like help with?",
                    "मेरे पास कई amazing capabilities हैं! ✨\n\n🧠 **Intelligent Chat**: Natural conversations with context\n📖 **Knowledge Expert**: Multiple subjects में deep knowledge\n🔍 **Problem Solver**: Step-by-step solutions\n💡 **Creative Helper**: Ideas and suggestions\n⏰ **Live Information**: Real-time updates\n🎭 **Entertainment**: Jokes and fun facts\n\nआप किस क्षेत्र में मदद चाहते हैं?",
                    "I'm designed to be your comprehensive assistant! 🌈\n\n💬 **Chat Naturally**: Like talking to a friend\n📚 **Answer Questions**: From simple to complex\n🔧 **Solve Problems**: Math, coding, and logic puzzles\n📊 **Analyze & Explain**: Break down complex topics\n⏰ **Real-time Data**: Time, weather, and more\n🎯 **Remember You**: Personalized experience\n\nHow can I assist you today?"
                ],
                'priority': 2
            },
            
            # 4. Entertainment & Mood Intent
            'entertainment': {
                'keywords': [
                    'bore', 'boring', 'bored', 'tell me a joke', 'joke', 'jokes', 'funny',
                    'entertain me', 'make me laugh', 'cheer me up', 'sad', 'feeling sad',
                    'depressed', 'unhappy', 'feeling down', 'mood off', 'not feeling good',
                    'stress', 'stressed', 'tired', 'exhausted', 'need fun', 'fun time',
                    'play', 'game', 'entertainment', 'amuse', 'distract', 'lighten mood',
                    'बोर हो रहा हूँ', 'बोरिंग', 'बोर हो गया', 'जोक सुनाओ', 'जोक्स',
                    'मज़ाक', 'मज़ाकिया', 'हसाओ', 'मुझे हसाओ', 'दुखी हूँ', 'उदास हूँ',
                    'परेशान हूँ', 'तनाव में हूँ', 'थक गया', 'थकी हूँ', 'मज़ा करो',
                    'आनंद', 'खुश', 'मूड ऑफ', 'अच्छा नहीं लग रहा',
                    'bore ho raha hu', 'boring', 'joke sunao', 'funny',
                    'sad', 'feeling sad', 'entertain me', 'make me laugh',
                    'mood off', 'stress', 'tired', 'need fun'
                ],
                'responses': [
                    "मैं समझ सकती हूँ कि आप bored महसूस कर रहे हैं! चलिए मज़ा करते हैं 😄\n\nयह लो एक joke: \"Why don't scientists trust atoms? Because they make up everything! 😄\"\n\nया शायद आप कोई interesting fact जानना चाहेंगे? या मैं आपको कोई fun activity suggest कर सकती हूँ!",
                    "I can see you need some entertainment! Let me brighten your day! 🌟\n\nHere's a joke for you: \"प्रोग्रामर का घर क्यों छोटा होता है? क्योंकि वो space को respect करते हैं! 🏠💻\"\n\nWant another joke, or would you prefer a fun fact to cheer you up?",
                    "Feeling down? Let me turn that frown upside down! 😊\n\n**Joke Time**: \"Why did scarecrow win an award? Because he was outstanding in his field! 🌾\"\n\n**Fun Fact**: Did you know that octopuses have three hearts and blue blood? 🐙\n\nHow about we talk about something fun instead?",
                    "I'm here to cheer you up! 🎉\n\nLet me tell you something funny: \"Mathematics की सबसे बड़ी problem क्या है? Problem solving! 😂\"\n\nOr if you prefer, I can tell you about amazing space facts, cool science discoveries, or we can plan something fun! What sounds good to you?"
                ],
                'priority': 1
            },
            
            # 5. Farewells Intent
            'goodbye': {
                'keywords': [
                    'bye', 'goodbye', 'good bye', 'see you', 'see ya', 'later', 'farewell',
                    'take care', 'have a good day', 'have a good night', 'sweet dreams',
                    'talk to you later', 'catch you later', 'until next time', 'so long',
                    'good night', 'good evening', 'good afternoon', 'peace out', 'ciao',
                    'बाय', 'गुडबाय', 'अलविदा', 'फिर मिलेंगे', 'बाद में मिलते हैं',
                    'अभी बात करते हैं', 'चलो बाद में मिलते हैं', 'ताता',
                    'फिर मिलना', 'जल्दी', 'शुभ रात्रि', 'अपना ख्याल रखना',
                    'धन्यवाद', 'धन्यवाद', 'सुस्रीक्षल', 'अपना ध्यान रखना',
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
                'priority': 1
            },
            
            # Domain-specific intents
            'web_development': {
                'keywords': [
                    'javascript', 'html', 'css', 'react', 'next.js', 'nodejs', 'frontend', 'backend', 'web dev', 'website', 'web app',
                    'python', 'code', 'programming', 'algorithm', 'debug', 'java', 'cpp',
                    'function', 'class', 'variable', 'loop', 'array', 'list', 'dictionary', 'recursion',
                    'sorting', 'searching', 'bubble sort', 'quick sort', 'merge sort', 'binary search', 'linear search',
                    'graph', 'tree', 'bfs', 'dfs', 'dijkstra', 'shortest path', 'dynamic programming',
                    'fibonacci', 'knapsack', 'lcs', 'gcd', 'lcm', 'prime', 'factorial', 'power', 'hash',
                    'data structure', 'complexity', 'big o', 'time complexity', 'space complexity',
                    'web development', 'app development', 'software', 'development', 'bug', 'error',
                    'syntax', 'logic', 'api', 'database', 'framework',
                    'design', 'ui', 'ux', 'interface', 'user interface', 'user experience', 'layout',
                    'responsive', 'mobile', 'desktop', 'testing', 'deployment', 'version control',
                    'git', 'github', 'css framework', 'bootstrap', 'tailwind', 'material design',
                    'javascript framework', 'typescript', 'webpack', 'npm', 'package manager',
                    'database design', 'sql', 'nosql', 'mongodb', 'mysql', 'postgresql',
                    'rest api', 'graphql', 'microservices', 'serverless', 'cloud computing',
                    'docker', 'kubernetes', 'devops', 'ci/cd', 'automation', 'testing',
                    'unit testing', 'integration testing', 'e2e testing', 'jest', 'cypress',
                    'performance', 'optimization', 'security', 'authentication', 'authorization',
                    'frontend performance', 'backend performance', 'caching', 'cdn', 'load balancing',
                    'web security', 'xss', 'csrf', 'sql injection', 'owasp', 'security best practices',
                    'mobile development', 'react native', 'flutter', 'ios', 'android', 'cross platform',
                    'progressive web app', 'pwa', 'service worker', 'offline', 'push notifications',
                    'web components', 'custom elements', 'shadow dom', 'lit element', 'polymer',
                    'css preprocessors', 'sass', 'scss', 'less', 'postcss', 'css modules',
                    'javascript es6', 'es6 features', 'arrow functions', 'async await', 'promises',
                    'node.js', 'express', 'koa', 'fastify', 'middleware', 'routing',
                    'database orm', 'sequelize', 'mongoose', 'prisma', 'typeorm', 'sqlalchemy',
                    'frontend tools', 'babel', 'eslint', 'prettier', 'webpack', 'vite', 'parcel',
                    'state management', 'redux', 'mobx', 'vuex', 'context api', 'hooks',
                    'styling', 'css-in-js', 'styled components', 'emotion', 'jss', 'aphrodite',
                    'animation', 'transitions', 'css animations', 'javascript animations', 'gsap',
                    'accessibility', 'a11y', 'wcag', 'screen readers', 'aria labels', 'semantic html',
                    'seo', 'search engine optimization', 'meta tags', 'open graph', 'structured data',
                    'web analytics', 'google analytics', 'mixpanel', 'segment', 'tracking',
                    'monitoring', 'logging', 'error tracking', 'sentry', 'logrocket', 'fullstory',
                    'api testing', 'postman', 'insomnia', 'swagger', 'openapi', 'api documentation',
                    'code quality', 'code review', 'linting', 'formatting', 'best practices',
                    'architecture', 'mvc', 'mvp', 'mvvm', 'clean architecture', 'design patterns',
                    'solid principles', 'dry', 'kiss', 'yagni', 'technical debt', 'refactoring',
                    'agile', 'scrum', 'kanban', 'project management', 'sprints', 'user stories',
                    'wireframing', 'prototyping', 'mockups', 'figma', 'sketch', 'adobe xd',
                    'color theory', 'typography', 'visual hierarchy', 'grid systems', 'layout design',
                    'user research', 'user testing', 'usability testing', 'a/b testing', 'analytics',
                    'design systems', 'component libraries', 'design tokens', 'brand guidelines',
                    'responsive design', 'mobile first', 'breakpoints', 'media queries', 'flexbox',
                    'css grid', 'layout systems', 'positioning', 'floats', 'box model',
                    'javascript libraries', 'jquery', 'lodash', 'moment', 'axios', 'fetch',
                    'build tools', 'gulp', 'grunt', 'webpack', 'rollup', 'esbuild',
                    'package managers', 'npm', 'yarn', 'pnpm', 'bower', 'dependency management',
                    'version control', 'git', 'github', 'gitlab', 'bitbucket', 'pull requests',
                    'collaboration', 'code review', 'pair programming', 'team workflow',
                    'continuous integration', 'continuous deployment', 'jenkins', 'github actions',
                    'cloud platforms', 'aws', 'azure', 'google cloud', 'heroku', 'vercel', 'netlify',
                    'serverless functions', 'aws lambda', 'cloud functions', 'azure functions',
                    'static site generators', 'gatsby', 'next.js', 'nuxt.js', 'jekyll', 'hugo',
                    'headless cms', 'strapi', 'contentful', 'sanity', 'ghost', 'wordpress headless',
                    'e-commerce', 'shopify', 'magento', 'woocommerce', 'payment integration',
                    'websockets', 'real-time', 'socket.io', 'signalr', 'pusher', 'firebase realtime',
                    'web assembly', 'wasm', 'rust', 'c++', 'performance critical applications',
                    'machine learning', 'tensorflow.js', 'brain.js', 'ml5.js', 'web ml',
                    'computer vision', 'opencv.js', 'face detection', 'image processing',
                    'audio processing', 'web audio api', 'speech recognition', 'text to speech',
                    'web bluetooth', 'web usb', 'web nfc', 'device apis', 'hardware integration',
                    'pwa features', 'offline support', 'caching', 'background sync', 'push api',
                    'web monetization', 'payment request api', 'digital goods', 'subscriptions',
                    'web standards', 'w3c', 'whatwg', 'ecmascript', 'html5', 'css3',
                    'browser compatibility', 'cross browser', 'polyfills', 'shims', 'feature detection',
                    'performance metrics', 'core web vitals', 'lighthouse', 'page speed insights',
                    'web development tools', 'chrome devtools', 'firefox devtools', 'debugging',
                    'code editors', 'vscode', 'sublime', 'atom', 'vim', 'emacs', 'ide',
                    'terminal', 'command line', 'bash', 'zsh', 'powershell', 'shell scripting',
                    'webgl', 'three.js', 'babylon.js', '3d graphics', 'webgl2', 'canvas',
                    'svg', 'vector graphics', 'd3.js', 'chart.js', 'data visualization',
                    'web components', 'custom elements', 'shadow dom', 'html templates',
                    'css architecture', 'bem', 'smacss', 'oocss', 'atomic css', 'utility first',
                    'javascript patterns', 'module pattern', 'observer pattern', 'factory pattern',
                    'functional programming', 'imperative programming', 'object oriented programming',
                    'type systems', 'typescript', 'flow', 'type checking', 'interfaces',
                    'error handling', 'try catch', 'error boundaries', 'graceful degradation',
                    'internationalization', 'i18n', 'localization', 'l10n', 'multi language',
                    'web accessibility', 'a11y', 'screen readers', 'keyboard navigation',
                    'progressive enhancement', 'feature detection', 'fallbacks',
                    'web performance', 'lazy loading', 'code splitting', 'tree shaking',
                    'caching strategies', 'browser cache', 'cdn cache', 'service worker cache',
                    'security headers', 'csp', 'hsts', 'cors', 'authentication', 'oauth',
                    'api design', 'restful', 'graphql', 'api versioning', 'documentation',
                    'database design', 'normalization', 'indexing', 'query optimization',
                    'nosql databases', 'document stores', 'key-value stores', 'graph databases',
                    'cloud architecture', 'microservices', 'serverless', 'containers',
                    'devops practices', 'infrastructure as code', 'monitoring', 'alerting',
                    'testing strategies', 'tdd', 'bdd', 'test pyramid', 'mocking', 'stubbing',
                    'frontend frameworks', 'react', 'vue', 'angular', 'svelte', 'solid',
                    'backend frameworks', 'express', 'django', 'rails', 'spring', 'laravel',
                    'mobile frameworks', 'react native', 'flutter', 'ionic', 'cordova',
                    'desktop apps', 'electron', 'tauri', 'nw.js', 'web technologies',
                    'game development', 'phaser', 'three.js', 'babylon.js', 'webgl games',
                    'ai integration', 'openai api', 'chatgpt', 'gpt-4', 'machine learning',
                    'blockchain', 'web3', 'ethereum', 'smart contracts', 'dapps',
                    'ar/vr', 'webxr', 'augmented reality', 'virtual reality', 'immersive web',
                    'iot', 'internet of things', 'web things', 'device integration',
                    'web standards compliance', 'html validation', 'css validation', 'accessibility testing',
                    'code optimization', 'minification', 'compression', 'bundling',
                    'development workflow', 'hot reload', 'live preview', 'development server',
                    'package management', 'dependencies', 'security updates', 'vulnerability scanning',
                    'documentation', 'jsdoc', 'typedoc', 'api docs', 'readme', 'wiki',
                    'collaboration tools', 'slack', 'discord', 'teams', 'communication',
                    'project management', 'jira', 'trello', 'asana', 'task tracking',
                    'time tracking', 'productivity', 'focus', 'deep work', 'pomodoro',
                    'learning resources', 'tutorials', 'courses', 'documentation', 'books',
                    'community', 'stackoverflow', 'github', 'meetups', 'conferences',
                    'career development', 'portfolio', 'resume', 'interview preparation',
                    'freelancing', 'client management', 'pricing', 'contracts', 'proposals',
                    'open source', 'contributing', 'maintaining', 'licensing', 'community',
                    'web ethics', 'privacy', 'data protection', 'user rights', 'responsible design'
                ],
                'responses': [
                    "मैं प्रोग्रामिंग और वेब डेवलपमेंट में विशेषज्ञ हूँ! JavaScript, React, Next.js, Python, Algorithms, Data Structures - कोई भी algorithm या data structure में मदद कर सकती हूँ! कौन सा algorithm सीखना चाहिए? या कोई specific programming challenge है? 💻🎨",
                    "I'm an expert in algorithms and programming! Sorting, searching, graph algorithms, dynamic programming, tree traversals - I can implement and explain any algorithm! Which algorithm do you need help with? Are you working on a specific project or learning for interviews? 🚀🎯",
                    "प्रोग्रामिंग algorithms के बारे में आपकी क्या मदद करूँ? Sorting algorithms (bubble, quick, merge), searching (binary, linear), graph algorithms (BFS, DFS, Dijkstra), dynamic programming, tree traversals - कौन सा algorithm चाहिए? क्या आप complexity analysis भी चाहिए? 🎨💻",
                    "Algorithms are my specialty! From basic sorting to complex graph algorithms, from dynamic programming to tree structures - I can implement any algorithm with time complexity analysis! What algorithm challenge are you facing? Is this for learning, interview preparation, or a real project? 👨‍💻🎨",
                    "मैं algorithms और data structures में expert हूँ! Time complexity analysis, space optimization, sorting algorithms, graph theory, dynamic programming, tree structures - क्या algorithm implement करना है? क्या आप optimization techniques भी जानना चाहिए? 🌟",
                    "I can help with any algorithm! Whether it's sorting (bubble sort, quick sort, merge sort), searching (binary search), graph algorithms (Dijkstra, BFS, DFS), dynamic programming (Fibonacci, knapsack), or mathematical algorithms - I've got you covered! What do you need? Want me to explain the algorithm step by step or just provide the code? 🎯",
                    "प्रोग्रामिंग algorithms में मदद कर सकती हूँ! Algorithm implementation, complexity analysis, optimization techniques, problem-solving approaches, data structures - आप क्या algorithm सीखना चाहते हैं? क्या मुझे बताओं समझाना चाहिए या step-by-step explanation चाहिए? 💡",
                    "From sorting algorithms to graph traversals, from dynamic programming to mathematical computations - I can implement and explain any algorithm with proper complexity analysis! What's your algorithm question? Are you preparing for technical interviews or working on something specific? Want me to show you examples? 🚀"
                ],
                'priority': 2
            },
            
            'science': {
                'keywords': [
                    'science', 'physics', 'chemistry', 'biology', 'quantum', 'space', 'technology',
                    'chemistry', 'physics', 'biology', 'विज्ञान', 'भौतिक', 'रसायन',
                    'astronomy', 'astrophysics', 'quantum mechanics', 'relativity', 'evolution', 'genetics',
                    'scientific method', 'research', 'experiment', 'theory', 'hypothesis', 'discovery',
                    'विज्ञान', 'तकनीक', 'गणित', 'भौतिक', 'प्रयोग', 'खोज',
                    'scientific', 'technology', 'research', 'experiment'
                ],
                'responses': [
                    "विज्ञान बहुत ही रोचक है! Physics, Chemistry, Biology, Quantum Mechanics, Astronomy - किस भी scientific field में जानकारी चाहिए? क्या कोई specific scientific concept explore करना चाहिए? 🧪",
                    "Science fascinates me! From quantum physics to molecular biology, from astronomy to environmental science - what's your scientific interest? Are you studying for exams, doing research, or just curious? 🔬",
                    "भारती का इतिहास और विज्ञान बहुत समृद्ध है! Ancient civilizations से लेके modern science तक, क्या खास discovery explore करना चाहिए? क्या कोई scientific era interest करते हैं? 🇮🇳",
                    "Scientific inquiry! I can discuss physics, chemistry, biology, astronomy, and more. What specific scientific concept would you like to explore? Want to know the theory behind it or practical applications? 🔬",
                    "मैं scientific research और discovery में passionate हूँ! Latest discoveries, breakthrough technologies, scientific theories, experimental methods - आप क्या scientific topic discuss करना चाहिए? क्या आप कोई research paper पढ़ना चाहिए? 🧪",
                    "Let's explore the scientific world together! Whether it's fundamental physics, cutting-edge biology, space exploration, or environmental science - I can provide detailed explanations and real-world examples! What scientific mystery fascinates you most? 🌟"
                ],
                'priority': 2
            },
            
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
                    "गणित logic और patterns का study है। Algebra, Calculus, Geometry, Statistics, Trigonometry - किस भी branch में मदद कर सकती हूँ। क्या solve करना है? क्या कोई mathematical problem face कर रहे हैं? 🧮",
                    "Mathematics is the language of the universe! From basic arithmetic to advanced calculus, linear algebra to number theory - I can help with any math problem! Are you studying for exams, working on a project, or just curious about a concept? 📐",
                    "गणित के किसी भी branch में मदद कर सकती हूँ। Differential equations, probability theory, statistics - आप क्या mathematical challenge कर रहे हैं? क्या step-by-step solution चाहिए? 🔢",
                    "Mathematical thinking! I love solving complex problems. Whether it's algebra, calculus, geometry, or advanced mathematics - what's your mathematical question? Want me to show you the method or just the answer? 🧮",
                    "मैं mathematical problem solving में expert हूँ! Complex equations, calculus problems, statistical analysis, mathematical proofs - आप क्या mathematical concept समझनना चाहिए? क्या अभ्यास करना चाहिए? 🌟",
                    "Let's solve your math problems! Whether it's basic arithmetic, advanced calculus, linear algebra, or number theory - I can provide step-by-step solutions and explanations! What's your mathematical challenge? Need help with homework, exam preparation, or just curious about a concept? 📈"
                    "From algebra to calculus, from geometry to statistics, from basic arithmetic to advanced mathematics - I can help with any mathematical problem! Need help with homework, exam preparation, or just curious about a concept? 🌟"
                ],
                'priority': 2
            },
            
            'history': {
                'keywords': [
                    'history', 'historical', 'ancient', 'medieval', 'modern', 'india', 'gupta', 'maurya',
                    'civilization', 'empire', 'dynasty', 'revolution', 'war', 'culture', 'archaeology',
                    'freedom movement', 'independence', 'colonial', 'medieval period', 'renaissance',
                    'world war', 'cold war', 'indian history', 'mughal', 'british raj',
                    'इतिहास', 'सम्राज्य', 'गुप्त', 'राज', 'महाभारत', 'सिंध', 'मराठ',
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
            
            'health_fitness': {
                'keywords': [
                    'health', 'fitness', 'exercise', 'workout', 'gym', 'diet', 'nutrition', 'weight loss',
                    'yoga', 'meditation', 'mental health', 'stress', 'anxiety', 'depression', 'wellness',
                    'healthy lifestyle', 'sleep', 'hydration', 'vitamins', 'supplements', 'muscle building',
                    'cardio', 'strength training', 'flexibility', 'balance', 'endurance', 'recovery',
                    'स्वास्थ्य', 'व्यायाम', 'योग', 'ध्यान', 'मानसिक स्वास्थ्य', 'पोषण', 'आहार',
                    'health tips', 'fitness routine', 'healthy habits', 'mental wellness', 'physical therapy'
                ],
                'responses': [
                    "स्वास्थ्य सबसे महत्वपूर्ण है! Yoga, meditation, exercise, nutrition, mental health - किस aspect में मदद चाहिए? 🏃‍♀️",
                    "Health and fitness are essential! From workout routines to nutrition plans, mental wellness to physical therapy - what health topic interests you? 💪",
                    "मैं health और fitness के बारे में expert हूँ! Exercise science, nutrition, yoga, meditation, mental health awareness - आप क्या health goal बनाना चाहते हैं? 🧘‍♀️",
                    "Wellness is my priority! Whether it's physical fitness, mental health, nutrition, or lifestyle changes - I can help you achieve your health goals! What's your health question? 🌟"
                ],
                'priority': 2
            },
            
            'entertainment': {
                'keywords': [
                    'movies', 'music', 'songs', 'games', 'sports', 'cricket', 'football', 'bollywood', 'hollywood',
                    'tv shows', 'web series', 'netflix', 'amazon prime', 'disney', 'youtube', 'entertainment',
                    'celebrities', 'actors', 'actresses', 'directors', 'films', 'cinema', 'theatre',
                    'books', 'novels', 'reading', 'literature', 'poetry', 'art', 'painting', 'dance',
                    'फिल्म', 'गाने', 'संगीत', 'खेल', 'क्रिकेट', 'फुटबॉल', 'मनोरंजन', 'कला',
                    'entertainment news', 'movie reviews', 'music recommendations', 'game reviews', 'sports updates'
                ],
                'responses': [
                    "मनोरंजन के लिए बहुत सारे options हैं! Movies, music, games, sports, books, art - किस entertainment medium में interest है? 🎬",
                    "Entertainment galore! From Bollywood to Hollywood, cricket to football, music to movies - what's your entertainment preference? 🎵",
                    "मैं entertainment के बारे में जानकारी रखती हूँ! Latest movies, trending music, sports updates, book recommendations - आप क्या entertainment news चाहिए? 🎮",
                    "Let's talk entertainment! Whether it's movies, music, games, sports, or cultural events - I can discuss all forms of entertainment! What's your favorite? 🌟"
                ],
                'priority': 2
            },
            
            'travel_tourism': {
                'keywords': [
                    'travel', 'tourism', 'vacation', 'holiday', 'trip', 'destination', 'tourist', 'explore',
                    'india travel', 'international travel', 'beaches', 'mountains', 'cities', 'heritage sites',
                    'hotels', 'flights', 'booking', 'itinerary', 'travel guide', 'sightseeing', 'adventure',
                    'backpacking', 'luxury travel', 'budget travel', 'travel tips', 'solo travel', 'family vacation',
                    'यात्रा', 'पर्यटन', 'ुट्टी', 'घूमने', 'भ्रमण', 'पर्यटक स्थल', 'दर्शनीय स्थल',
                    'travel destinations', 'best places to visit', 'travel recommendations', 'tourist attractions'
                ],
                'responses': [
                    "यात्रा करना बहुत ही अनुभव है! India और international destinations, beaches, mountains, heritage sites - कहाँ घूमना चाहिए? ✈️",
                    "Travel enthusiast? From exotic beaches to majestic mountains, from cultural heritage to modern cities - what's your dream destination? 🌍",
                    "मैं travel और tourism की expert हूँ! Travel planning, destination recommendations, itinerary suggestions, budget tips - आप किस type की trip plan करना चाहते हैं? 🗺️",
                    "Adventure awaits! Whether it's solo backpacking, family vacations, luxury travel, or budget trips - I can help plan your perfect journey! Where do you want to explore? 🧳"
                ],
                'priority': 2
            },
            
            'food_cuisine': {
                'keywords': [
                    'food', 'cuisine', 'cooking', 'recipes', 'dishes', 'restaurants', 'eating', 'meal',
                    'indian food', 'chinese food', 'italian food', 'mexican food', 'japanese food', 'thai food',
                    'street food', 'home cooking', 'baking', 'desserts', 'beverages', 'drinks', 'coffee',
                    'vegetarian', 'vegan', 'non-vegetarian', 'healthy food', 'junk food', 'diet food',
                    'खाना', 'भोजन', 'रेसिपी', 'खाना बनाना', 'रेस्टोरेंट', 'व्यंजन',
                    'food recipes', 'cooking tips', 'meal planning', 'nutrition advice', 'culinary arts'
                ],
                'responses': [
                    "खाना life का अहम हिस्सा है! Indian, Chinese, Italian, Mexican, Japanese cuisine - किस type का food चाहिए? 🍽️",
                    "Food lover's paradise! From traditional recipes to international cuisines, from street food to fine dining - what's your culinary preference? 🍴",
                    "मैं cooking और cuisine की expert हूँ! Recipe suggestions, cooking techniques, food pairings, nutritional information - आप क्या dish बनाना सीखना चाहिए? 👨‍🍳",
                    "Let's talk food! Whether it's home cooking, restaurant recommendations, dietary advice, or culinary experiments - I can satisfy your food cravings! What's on your menu? 🌟"
                ],
                'priority': 2
            },
            
            'relationships': {
                'keywords': [
                    'love', 'relationship', 'dating', 'marriage', 'friendship', 'family', 'parents', 'siblings',
                    'romance', 'partner', 'boyfriend', 'girlfriend', 'husband', 'wife', 'couple', 'together',
                    'breakup', 'divorce', 'heartbreak', 'moving on', 'single', 'alone', 'lonely',
                    'communication', 'trust', 'honesty', 'commitment', 'intimacy', 'emotions', 'feelings',
                    'प्यार', 'रिश्ता', 'शादी', 'दोस्ती', 'परिवार', 'माता-पिता', 'भाई-बहन',
                    'relationship advice', 'love tips', 'dating advice', 'marriage counseling', 'family issues'
                ],
                'responses': [
                    "रिश्ते और emotions बहुत नाजुक होते हैं! Love, friendship, family relationships, dating, marriage - किस relationship topic पर बात करनी है? ❤️",
                    "Relationships are complex and beautiful! From love and dating to marriage and family dynamics - what relationship aspect would you like to discuss? 💕",
                    "मैं relationships के बारे में समझदारी रखती हूँ! Communication tips, emotional support, relationship advice, family guidance - आप क्या relationship issue face कर रहे हैं? 🤗",
                    "Let's talk relationships! Whether it's romantic love, friendship, family bonds, or self-love - I can provide thoughtful guidance and support. What's on your heart? 🌟"
                ],
                'priority': 2
            },
            
            'career_jobs': {
                'keywords': [
                    'career', 'job', 'work', 'employment', 'profession', 'business', 'startup', 'entrepreneur',
                    'interview', 'resume', 'cv', 'skills', 'qualification', 'education', 'training',
                    'salary', 'promotion', 'raise', 'bonus', 'benefits', 'workplace', 'office',
                    'remote work', 'work from home', 'freelancing', 'part-time', 'full-time', 'internship',
                    'करियर', 'नौकरी', 'व्यवसाय', 'रोजगार', 'इंटरव्यू', 'बिजनेस', 'स्टार्टअप',
                    'career advice', 'job search', 'professional development', 'networking', 'leadership'
                ],
                'responses': [
                    "करियर growth बहुत important है! Job search, interviews, skill development, entrepreneurship, professional growth - किस career aspect में guidance चाहिए? 💼",
                    "Career matters! From job hunting to professional development, from entrepreneurship to leadership skills - what's your career question? 🚀",
                    "मैं career guidance में expert हूँ! Resume building, interview preparation, skill assessment, career planning - आप क्या career goal achieve करना चाहते हैं? 📈",
                    "Let's build your career! Whether it's finding the right job, preparing for interviews, developing skills, or starting a business - I can help you succeed professionally! What's your career goal? 🌟"
                ],
                'priority': 2
            },
            
            'spirituality_mindfulness': {
                'keywords': [
                    'spirituality', 'meditation', 'mindfulness', 'yoga', 'zen', 'peace', 'calm', 'relax',
                    'consciousness', 'awareness', 'enlightenment', 'wisdom', 'philosophy', 'life purpose',
                    'stress relief', 'anxiety management', 'mental peace', 'emotional balance', 'self-care',
                    'chakras', 'energy', 'healing', 'positive thinking', 'gratitude', 'affirmations',
                    'आध्यात्मिकता', 'ध्यान', 'मेडिटेशन', 'शांति', 'शांत', 'जीवन का उद्देश्य',
                    'spiritual growth', 'inner peace', 'self-discovery', 'personal transformation', 'mindfulness practices'
                ],
                'responses': [
                    "आध्यात्मिकता inner peace देती है! Meditation, mindfulness, yoga, philosophy, life purpose - किस spiritual path पर जाना चाहिए? 🧘‍♀️",
                    "Spiritual journey awaits! From meditation techniques to philosophical insights, from mindfulness practices to inner peace - what spiritual aspect interests you? 🕉️",
                    "मैं spirituality और mindfulness की guide हूँ! Meditation techniques, stress management, emotional healing, personal growth - आप क्या spiritual practice अपनाना चाहिए? 🌸",
                    "Let's explore your inner world! Whether it's meditation, mindfulness, spiritual growth, or finding life purpose - I can guide you on your spiritual journey. What's your spiritual question? 🌟"
                ],
                'priority': 2
            },
            
            'technology_future': {
                'keywords': [
                    'technology', 'tech', 'innovation', 'future', 'artificial intelligence', 'ai', 'machine learning',
                    'robotics', 'automation', 'blockchain', 'cryptocurrency', 'metaverse', 'virtual reality',
                    'space technology', 'quantum computing', 'biotechnology', 'nanotechnology', 'genetics',
                    'internet', 'social media', 'smartphones', 'apps', 'software', 'hardware', 'gadgets',
                    'तकनीक', 'भविष्य', 'भविष्यविज्ञान', 'कृत्रिम बुद्धिधि', 'रोबोटिक्स', 'ऑटोमेशन',
                    'tech trends', 'future predictions', 'emerging technologies', 'digital transformation', 'tech news'
                ],
                'responses': [
                    "Technology future बहुत exciting है! AI, robotics, blockchain, quantum computing, space tech - किस technology trend में interest है? 🤖",
                    "Tech enthusiast! From AI and machine learning to blockchain and quantum computing, from robotics to space technology - what's your tech interest? 🚀",
                    "मैं technology और innovation की expert हूँ! Latest tech trends, future predictions, emerging technologies, digital transformation - आप क्या tech topic explore करना चाहिए? 💡",
                    "Future is now! Whether it's artificial intelligence, quantum computing, biotechnology, or space exploration - I can discuss cutting-edge technologies! What tech fascinates you? 🌟"
                ],
                'priority': 2
            },
            
            'realtime': {
                'keywords': [
                    'time', 'date', 'weather', 'temperature', 'samay', 'samay kya hai',
                    'aaj ka samay', 'aaj ki tarikh', 'mausam', 'mausam kaisa hai',
                    'current time', 'what time', 'what date', 'today', 'abhi'
                ],
                'responses': [
                    "Real-time information: Let me check that for you!",
                    "अभी मैं आपके लिए real-time information check करती हूँ!",
                    "Let me get current information for you!"
                ],
                'priority': 3
            },
            
            'education_learning': {
                'keywords': [
                    'education', 'learning', 'study', 'school', 'college', 'university', 'students',
                    'teaching', 'teacher', 'professor', 'courses', 'subjects', 'exams', 'results',
                    'homework', 'assignment', 'project', 'research', 'thesis', 'phd', 'scholarship',
                    'online learning', 'e-learning', 'distance education', 'skill development', 'training',
                    'शिक्षा', 'अध्ययन', 'पढ़ाई', 'स्कूल', 'कॉलेज', 'विश्वविद्यालय', 'विद्यार्थी',
                    'learning tips', 'study techniques', 'exam preparation', 'academic help', 'career guidance'
                ],
                'responses': [
                    "शिक्षा सबसे important है! School, college, university, online courses, skill development - किस education topic में मदद चाहिए? ",
                    "Education is the key to success! From school subjects to university courses, from online learning to skill development - what's your educational query? ",
                    "मैं education और learning की expert हूँ! Study techniques, exam preparation, career guidance, academic support - आप क्या learning goal achieve करना चाहिए? ",
                    "Let's enhance your knowledge! Whether it's academic subjects, skill development, career guidance, or learning techniques - I can help you excel! What's your learning goal? "
                ],
                'priority': 2
            },
            
            'finance_money': {
                'keywords': [
                    'finance', 'money', 'investment', 'savings', 'banking', 'stocks', 'mutual funds',
                    'crypto', 'bitcoin', 'ethereum', 'trading', 'shares', 'portfolio', 'wealth',
                    'budget', 'expenses', 'income', 'salary', 'tax', 'insurance', 'loan', 'emi',
                    'financial planning', 'retirement', 'pension', 'wealth management', 'financial literacy',
                    'वित्त', 'पैसा', 'निवेश', 'बचत', 'बैंकिंग', 'शेयर', 'म्यूचुअल फंड',
                    'money management', 'investment advice', 'financial tips', 'saving strategies', 'tax planning'
                ],
                'responses': [
                    "वित्त management बहुत जरूरी है! Investment, savings, banking, crypto, financial planning - किस finance topic में guidance चाहिए? ",
                    "Finance matters! From investment strategies to budget planning, from crypto trading to wealth management - what's your financial question? ",
                    "मैं finance और money management की expert हूँ! Investment options, savings strategies, tax planning, retirement planning - आप क्या financial goal achieve करना चाहिए? ",
                    "Let's build your wealth! Whether it's investment planning, budget management, crypto trading, or financial literacy - I can help you grow your money! What's your financial goal? "
                ],
                'priority': 2
            },
            
            'environment_nature': {
                'keywords': [
                    'environment', 'nature', 'climate', 'weather', 'pollution', 'global warming', 'sustainability',
                    'eco-friendly', 'green energy', 'renewable energy', 'solar', 'wind', 'electric vehicles',
                    'conservation', 'wildlife', 'animals', 'plants', 'forests', 'oceans', 'rivers',
                    'environmental protection', 'carbon footprint', 'recycling', 'waste management',
                    'पर्यावरण', 'प्रकृति', 'जलवायु', 'मौसम', 'प्रदूषण', 'जंगल',
                    'climate action', 'green living', 'environmental awareness', 'nature conservation', 'sustainable living'
                ],
                'responses': [
                    "पर्यावरण संरक्षण हमारा duty है! Climate change, renewable energy, wildlife conservation, sustainable living - किस environmental issue पर बात करनी है? ",
                    "Environment matters! From climate action to wildlife conservation, from renewable energy to sustainable living - what's your environmental concern? ",
                    "मैं environment और nature की protector हूँ! Climate solutions, green energy, conservation efforts, sustainable practices - आप क्या environmental initiative अपनाना चाहिए? ",
                    "Let's protect our planet! Whether it's climate action, wildlife conservation, renewable energy, or sustainable living - I can help you make a difference! What's your environmental goal? "
                ],
                'priority': 2
            },
            
            'fashion_style': {
                'keywords': [
                    'fashion', 'style', 'clothing', 'outfit', 'dress', 'wearing', 'trends', 'designer',
                    'makeup', 'beauty', 'skincare', 'hair', 'accessories', 'jewelry', 'shoes', 'bags',
                    'fashion tips', 'style advice', 'personal styling', 'wardrobe', 'shopping',
                    'traditional wear', 'ethnic wear', 'western wear', 'casual', 'formal', 'party wear',
                    'फैशन', 'स्टाइल', 'कपड़े', 'पहनावा', 'मेकअप', 'ज्वेलरी', 'सौंदर्य',
                    'beauty tips', 'style guide', 'fashion trends', 'personal care', 'grooming', 'appearance'
                ],
                'responses': [
                    "फैशन और style self-expression है! Outfit ideas, fashion trends, beauty tips, personal styling - किस fashion aspect में मदद चाहिए? ",
                    "Fashion forward! From outfit coordination to beauty routines, from style tips to personal grooming - what's your fashion query? ",
                    "मैं fashion और beauty की expert हूँ! Style advice, outfit suggestions, beauty tips, personal care - आप क्या style statement बनाना चाहिए? ",
                    "Let's style you up! Whether it's fashion trends, outfit coordination, beauty routines, or personal styling - I can help you look your best! What's your fashion question? "
                ],
                'priority': 2
            },
            
            'hobbies_interests': {
                'keywords': [
                    'hobbies', 'interests', 'passion', 'leisure', 'free time', 'activities', 'pastime',
                    'photography', 'gardening', 'cooking', 'baking', 'painting', 'drawing', 'sketching',
                    'music', 'dance', 'singing', 'playing instruments', 'writing', 'reading', 'blogging',
                    'sports', 'fitness', 'gaming', 'travel', 'collecting', 'crafts', 'diy projects',
                    'शौक', 'रुचि', 'अभिरुचि', 'खाली समय', 'पसंद',
                    'hobby ideas', 'new hobbies', 'creative hobbies', 'relaxing hobbies', 'skill-building hobbies'
                ],
                'responses': [
                    "Hobbies life को enjoyable बनाते हैं! Photography, gardening, cooking, painting, music, writing - किस hobby explore करना चाहिए? क्या कोई new hobby try करना चाहिए? 🎨",
                    "Hobby enthusiast! From creative pursuits to relaxing activities, from skill-building hobbies to leisure interests - what's your hobby interest? Are you looking for something new or want to improve existing skills? 🎯",
                    "मैं hobbies और interests की expert हूँ! Hobby suggestions, skill development, creative ideas, leisure activities - आप क्या new hobby try करना चाहिए? क्या मुझे beginner guide चाहिए? 🌟",
                    "Let's explore your passions! Whether it's creative hobbies, relaxing activities, skill-building pursuits, or leisure interests - I can help you find your perfect hobby! What's your interest? Want suggestions based on your personality? 🌟"
                ],
                'priority': 2
            },
            
            'daily_life_routine': {
                'keywords': [
                    'daily routine', 'morning routine', 'evening routine', 'lifestyle', 'habits', 'schedule',
                    'time management', 'productivity', 'organization', 'planning', 'daily schedule',
                    'morning habits', 'evening habits', 'work routine', 'study routine', 'exercise routine',
                    'sleep schedule', 'meal timing', 'break time', 'weekend plans', 'daily goals',
                    'दैनिक दिनचर्या', 'सुबह की दिनचर्या', 'शाम की दिनचर्या', 'आदतें', 'समय प्रबंधन',
                    'routine tips', 'lifestyle advice', 'daily planning', 'habit formation', 'productivity hacks'
                ],
                'responses': [
                    "Daily routine life को organized बनाता है! Morning routine, evening routine, time management, productivity - किस routine aspect improve करना चाहिए? क्या आपका current routine effective है? ⏰",
                    "Routine matters! From morning rituals to evening wind-down, from time management to productivity hacks - what's your routine question? Are you looking to build new habits or optimize existing ones? 📅",
                    "मैं daily routine और lifestyle की expert हूँ! Habit formation, time management, productivity tips, lifestyle optimization - आप क्या daily routine improve करना चाहिए? क्या specific challenge है? 🌟",
                    "Let's design your perfect day! Whether it's morning routines, evening rituals, productivity systems, or habit formation - I can help you create a lifestyle that works for you! What's your daily challenge? Want personalized routine suggestions? 🌟"
                ],
                'priority': 2
            },
            
            'personal_development': {
                'keywords': [
                    'personal development', 'self improvement', 'growth', 'learning', 'skills', 'confidence',
                    'motivation', 'inspiration', 'goal setting', 'success', 'achievement', 'progress',
                    'self help', 'self growth', 'mindset', 'positive thinking', 'self discipline', 'focus',
                    'leadership', 'communication skills', 'social skills', 'emotional intelligence', 'resilience',
                    'व्यक्तिगत विकास', 'आत्म-सुधार', 'विकास', 'सीखना', 'कौशल', 'आत्मविश्वास',
                    'growth mindset', 'personal growth', 'skill development', 'life coaching', 'self motivation'
                ],
                'responses': [
                    "Personal development life को better बनाता है! Self improvement, skill development, confidence building, goal setting - किस personal growth area में मदद चाहिए? क्या आपके development goals हैं? 🚀",
                    "Growth mindset! From skill acquisition to confidence building, from goal setting to achievement tracking - what's your personal development journey? Are you looking for specific strategies or general guidance? 🌱",
                    "मैं personal development की coach हूँ! Self improvement techniques, motivation strategies, skill building, confidence enhancement - आप क्या personal growth achieve करना चाहिए? क्या specific challenge है? 🌟",
                    "Let's unlock your potential! Whether it's skill development, confidence building, goal achievement, or mindset transformation - I can guide your personal growth journey! What's your development goal? Want personalized growth strategies? 🌟"
                ],
                'priority': 2
            },
            
            'social_culture': {
                'keywords': [
                    'social', 'culture', 'society', 'community', 'traditions', 'customs', 'values',
                    'festivals', 'celebrations', 'social events', 'gatherings', 'parties', 'socializing',
                    'cultural diversity', 'traditions', 'heritage', 'social norms', 'etiquette', 'manners',
                    'social issues', 'current affairs', 'news', 'trends', 'social media', 'influencers',
                    'सामाजिक', 'संस्कृति', 'समाज', 'समुदाय', 'परंपरा', 'रीति-रिवाज', 'त्योहार',
                    'cultural awareness', 'social responsibility', 'community service', 'social engagement'
                ],
                'responses': [
                    "Social culture हमें connected रखता है! Festivals, traditions, community events, social norms - किस cultural aspect explore करना चाहिए? क्या कोई festival celebrate करना है? 🎉",
                    "Cultural explorer! From traditional festivals to modern social trends, from community values to social etiquette - what's your cultural curiosity? Are you learning about different cultures or exploring your own? 🌍",
                    "मैं social culture की expert हूँ! Cultural traditions, social norms, festival celebrations, community values - आप क्या cultural topic explore करना चाहिए? क्या कोई specific tradition जानना है? 🌟",
                    "Let's explore cultures together! Whether it's traditional festivals, social customs, community values, or modern trends - I can provide insights into diverse cultural perspectives! What cultural aspect interests you? Want to learn about specific traditions? 🌟"
                ],
                'priority': 2
            },
            
            'motivation_inspiration': {
                'keywords': [
                    'motivation', 'inspiration', 'encourage', 'motivate', 'inspire', 'positive', 'uplift',
                    'success stories', 'achievements', 'role models', 'heroes', 'legends', 'icons',
                    'quotes', 'wisdom', 'life lessons', 'experiences', 'journey', 'struggles',
                    'overcome challenges', 'resilience', 'perseverance', 'determination', 'willpower',
                    'प्रेरणा', 'प्रोत्साहन', 'सकारात्मक', 'ऊर्जा', 'उत्साह', 'प्रेरित',
                    'inspirational stories', 'motivational quotes', 'success tips', 'life advice', 'encouragement'
                ],
                'responses': [
                    "Motivation success की key है! Success stories, inspirational quotes, life lessons, achievement tips - किस motivational boost चाहिए? क्या आपको encourage करना चाहिए? 💪",
                    "Inspiration station! From success stories to motivational quotes, from life lessons to achievement tips - what's your motivation need? Are you facing challenges or seeking inspiration? 🌟",
                    "मैं motivation और inspiration की source हूँ! Success stories, motivational quotes, life wisdom, achievement guidance - आप क्या motivational support चाहिए? क्या specific challenge है? 🌟",
                    "Let's fuel your motivation! Whether it's success stories, inspirational quotes, life lessons, or achievement strategies - I can provide the encouragement you need! What's your motivation goal? Need specific inspiration for your journey? 🌟"
                ],
                'priority': 2
            },
            
            'philosophy_thinking': {
                'keywords': [
                    'philosophy', 'thinking', 'thought', 'mind', 'consciousness', 'reality', 'existence',
                    'meaning', 'purpose', 'wisdom', 'knowledge', 'truth', 'perception', 'awareness',
                    'ethics', 'morality', 'values', 'principles', 'virtue', 'character', 'integrity',
                    'logic', 'reasoning', 'critical thinking', 'analysis', 'debate', 'argumentation',
                    'metaphysics', 'epistemology', 'ontology', 'philosophical questions', 'deep thinking',
                    'दर्शन', 'विचार', 'मन', 'चेतना', 'वास्तविकता', 'अस्तित्व', 'ज्ञान',
                    'philosophical inquiry', 'deep questions', 'life philosophy', 'existential questions', 'wisdom seeking'
                ],
                'responses': [
                    "Philosophy mind को expand करता है! Deep thinking, consciousness, reality, existence, meaning of life - किस philosophical topic explore करना चाहिए? क्या कोई deep question discuss करना है? 🧠",
                    "Philosophical journey! From ancient wisdom to modern thought, from existential questions to ethical dilemmas - what philosophical concept interests you? Are you seeking answers or exploring questions? 🤔",
                    "मैं philosophy और deep thinking की explorer हूँ! Consciousness studies, reality questions, ethical dilemmas, life meaning - आप क्या philosophical inquiry करना चाहिए? क्या कोजी specific philosophical problem है? 🌟",
                    "Let's explore the depths of thought! Whether it's consciousness, reality, ethics, or the meaning of existence - I can engage in profound philosophical discussions! What's your philosophical question? Want to explore different perspectives? 🌟"
                ],
                'priority': 2
            },
            
            'creativity_imagination': {
                'keywords': [
                    'creativity', 'creative', 'imagination', 'innovative', 'innovation', 'ideas', 'inspiration',
                    'artistic', 'art', 'design', 'creative thinking', 'brainstorming', 'ideation',
                    'originality', 'uniqueness', 'inventive', 'ingenuity', 'resourcefulness', 'cleverness',
                    'creative process', 'imagination power', 'visual thinking', 'abstract thinking', 'concepts',
                    'artistic expression', 'creative writing', 'music composition', 'visual arts', 'performing arts',
                    'रचनात्मकता', 'कल्पना', 'नवाचार', 'विचार', 'कलात्मक', 'आविष्कार',
                    'creative problem solving', 'innovative solutions', 'artistic vision', 'imagination exercises'
                ],
                'responses': [
                    "Creativity imagination की power है! Creative thinking, innovation, artistic expression, brainstorming - किस creative aspect explore करना चाहिए? क्या कोई creative project करना है? 🎨",
                    "Creative explorer! From artistic expression to innovative thinking, from imagination power to creative problem-solving - what's your creative interest? Are you looking for inspiration or techniques? 🎭",
                    "मैं creativity और imagination की muse हूँ! Artistic techniques, creative thinking exercises, innovation strategies, ideation methods - आप क्या creative skill develop करना चाहिए? क्या artistic challenge है? 🌟",
                    "Let's unleash your creativity! Whether it's artistic expression, innovative thinking, creative problem-solving, or imagination exercises - I can help you tap into your creative potential! What's your creative goal? Want specific techniques? 🌟"
                ],
                'priority': 2
            },
            
            'problem_solving': {
                'keywords': [
                    'problem solving', 'solve problems', 'challenges', 'solutions', 'troubleshooting', 'fix issues',
                    'analytical thinking', 'logical reasoning', 'critical analysis', 'decision making', 'choices',
                    'strategy', 'planning', 'approach', 'methodology', 'framework', 'systematic thinking',
                    'obstacles', 'barriers', 'difficulties', 'complications', 'issues', 'challenges',
                    'solutions', 'answers', 'resolutions', 'fixes', 'remedies', 'cures', 'strategies',
                    'समस्या समाधान', 'समस्या', 'चुनौतियां', 'समाधान', 'विश्लेषण', 'तर्क',
                    'problem solving techniques', 'decision making skills', 'critical thinking exercises', 'solution strategies'
                ],
                'responses': [
                    "Problem solving life की skill है! Challenges, obstacles, analytical thinking, decision making - किस problem solve करना चाहिए? क्या कोई specific challenge है? 🧩",
                    "Problem solver! From analytical thinking to creative solutions, from decision making to strategic planning - what's your problem-solving challenge? Are you facing a specific issue or learning techniques? 🎯",
                    "मैं problem solving की expert हूँ! Analytical methods, strategic thinking, solution frameworks, decision processes - आप क्या problem overcome करना चाहिए? क्या specific obstacle है? 🌟",
                    "Let's solve your problems! Whether it's analytical challenges, creative obstacles, decision dilemmas, or strategic issues - I can help you find effective solutions! What's your problem? Want systematic approach or creative solutions? 🌟"
                ],
                'priority': 2
            },
            
            'learning_curiosity': {
                'keywords': [
                    'learning', 'curiosity', 'discover', 'explore', 'knowledge', 'understanding', 'comprehension',
                    'study', 'research', 'investigate', 'examine', 'analyze', 'inquire', 'question',
                    'curious mind', 'inquisitive', 'explorer', 'discoverer', 'knowledge seeker', 'lifelong learning',
                    'intellectual curiosity', 'desire to learn', 'knowledge acquisition', 'skill development',
                    'new ideas', 'concepts', 'theories', 'principles', 'foundations', 'fundamentals',
                    'सीखना', 'जिज्ञासा', 'खोज', 'अन्वेषण', 'ज्ञान', 'समझ', 'अध्ययन',
                    'curiosity driven', 'knowledge exploration', 'intellectual growth', 'learning journey'
                ],
                'responses': [
                    "Curiosity learning की engine है! Knowledge exploration, discovery, intellectual growth, understanding - किस topic explore करना चाहिए? क्या आपकी curiosity guide करे? 🔍",
                    "Curious explorer! From knowledge discovery to intellectual growth, from learning techniques to understanding complex concepts - what sparks your curiosity? Are you exploring new fields or deepening existing knowledge? 🧐",
                    "मैं curiosity और learning की facilitator हूँ! Knowledge exploration methods, learning strategies, intellectual development, understanding techniques - आप क्या discover करना चाहिए? क्या specific curiosity है? 🌟",
                    "Let's satisfy your curiosity! Whether it's exploring new knowledge, understanding complex concepts, developing learning strategies, or intellectual growth - I can guide your learning journey! What's your curiosity? Want structured learning or exploratory discovery? 🌟"
                ],
                'priority': 2
            },
            
            'wisdom_insight': {
                'keywords': [
                    'wisdom', 'insight', 'understanding', 'deep knowledge', 'profound', 'meaningful', 'enlightenment',
                    'life wisdom', 'experience', 'lessons learned', 'life lessons', 'practical wisdom', 'street smarts',
                    'intuitive understanding', 'deep insight', 'perception', 'awareness', 'consciousness', 'mindfulness',
                    'philosophical wisdom', 'ancient wisdom', 'modern insights', 'timeless truths', 'universal principles',
                    'personal growth', 'self awareness', 'emotional intelligence', 'social wisdom', 'interpersonal skills',
                    'ज्ञान', 'अंतर्दृष्टि', 'समझ', 'गहरा ज्ञान', 'जीवन ज्ञान', 'अनुभव',
                    'wisdom sharing', 'insight development', 'deep understanding', 'meaningful conversations'
                ],
                'responses': [
                    "Wisdom life का guide है! Deep understanding, life lessons, meaningful insights, practical wisdom - किस wisdom explore करना चाहिए? क्या life experience share करना है? 🌟",
                    "Wisdom seeker! From life lessons to deep insights, from practical wisdom to philosophical understanding - what wisdom are you seeking? Are you looking for guidance or sharing your own insights? 🧘",
                    "मैं wisdom और insight की repository हूँ! Life wisdom, deep understanding, meaningful conversations, practical insights - आप क्या wisdom discover करना चाहिए? क्या specific insight चाहिए? 🌟",
                    "Let's explore wisdom together! Whether it's life lessons, deep insights, practical wisdom, or philosophical understanding - I can provide meaningful perspectives and guidance! What wisdom are you seeking? Want to share experiences or gain insights? 🌟"
                ],
                'priority': 2
            },
            
            'brain_teasers_puzzles': {
                'keywords': [
                    'brain teasers', 'puzzles', 'riddles', 'mind games', 'mental challenges', 'iq tests',
                    'logical puzzles', 'math puzzles', 'word puzzles', 'pattern recognition', 'problem solving games',
                    'mental exercise', 'brain training', 'cognitive challenges', 'thinking games', 'intelligence tests',
                    'riddles', 'enigmas', 'mysteries', 'brain gym', 'mental workout', 'cognitive fitness',
                    'logic games', 'reasoning puzzles', 'analytical challenges', 'creative thinking puzzles',
                    'दिमागी पहेलियां', 'पहेलियां', 'बुद्धिमान', 'मानसिक चुनौतियां', 'र्क',
                    'puzzle solving', 'brain exercises', 'mental stimulation', 'cognitive development'
                ],
                'responses': [
                    "Brain teasers mind को sharp बनाते हैं! Puzzles, riddles, logical challenges, mental exercises - किस mental challenge try करना चाहिए? क्या brain exercise चाहिए? 🧩",
                    "Mental gymnast! From brain teasers to logic puzzles, from riddles to cognitive challenges - what's your mental workout preference? Are you looking for fun challenges or brain training? 🧠",
                    "मैं brain teasers और puzzles की champion हूँ! Logic puzzles, math challenges, word games, pattern recognition - आप क्या mental exercise try करना चाहिए? क्या difficulty level prefer करते हैं? 🌟",
                    "Let's exercise your brain! Whether it's logic puzzles, brain teasers, riddles, or cognitive challenges - I can provide stimulating mental exercises! What's your preferred challenge type? Want beginner or expert level? 🌟"
                ],
                'priority': 2
            },
            
            'emotional_support': {
                'keywords': [
                    'emotional support', 'feelings', 'emotions', 'sad', 'happy', 'angry', 'frustrated', 'worried',
                    'comfort', 'understanding', 'empathy', 'compassion', 'kindness', 'care', 'support system',
                    'mental health', 'wellbeing', 'stress', 'anxiety', 'depression', 'loneliness', 'isolation',
                    'coping mechanisms', 'emotional regulation', 'self care', 'healing', 'recovery', 'resilience',
                    'emotional intelligence', 'self awareness', 'mindfulness', 'meditation', 'relaxation',
                    'भावनात्मक समर्थन', 'भावनाएं', 'दुखी', 'खुश', 'ुस्सा', 'िंतित',
                    'emotional help', 'feeling better', 'emotional wellness', 'mental peace', 'stress relief'
                ],
                'responses': [
                    "Emotional support का समय हमेशा है! Feelings, emotions, stress, anxiety, depression - आप कैसा महसूस कर रहे हैं? क्या आपको emotional support चाहिए? 🤗",
                    "I'm here for emotional support! Whether you're feeling sad, anxious, frustrated, or just need someone to talk to - I'm here to listen with empathy and understanding. What's on your heart today? Need comfort or guidance? 💕",
                    "मैं आपकी emotional support system हूँ! Stress management, anxiety relief, emotional healing, coping strategies - आप किस emotional challenge face कर रहे हैं? क्या आपको कोई talk करना है? 🌟",
                    "Let's talk about your feelings! Whether you need emotional support, stress relief, anxiety management, or just a caring ear - I'm here to provide compassionate understanding and practical help. How are you feeling right now? Want to share what's bothering you? 🌟"
                ],
                'priority': 2
            },
            
            'user_behavior_analysis': {
                'keywords': [
                    'behavior', 'habits', 'patterns', 'routine', 'lifestyle', 'choices', 'decisions',
                    'psychology', 'human behavior', 'behavioral patterns', 'personality traits', 'character',
                    'self awareness', 'self reflection', 'personal growth', 'behavior change', 'habit formation',
                    'motivation', 'discipline', 'consistency', 'willpower', 'self control', 'focus',
                    'user experience', 'interaction patterns', 'communication style', 'social behavior',
                    'व्यवहार', 'आदतें', 'पैटर्न', 'व्यक्तित्व', 'चरित्र', 'विकास',
                    'behavioral analysis', 'personal insights', 'self understanding', 'habit tracking'
                ],
                'responses': [
                    "User behavior analysis में मदद कर सकती हूँ! Habits, patterns, lifestyle choices, behavior change - आप किस behavior aspect understand करना चाहिए? क्या कोई habit change करना है? 🧐",
                    "Behavior analyst! From habit patterns to lifestyle choices, from decision making to personal growth - what behavioral aspect interests you? Are you looking to understand your patterns or make positive changes? 🎯",
                    "मैं user behavior की observer हूँ! Behavior patterns, habit formation, lifestyle analysis, personal insights - आप क्या behavior explore करना चाहिए? क्या specific behavior pattern analyze करना है? 🌟",
                    "Let's understand your behavior patterns! Whether it's habit analysis, lifestyle choices, decision patterns, or personal growth - I can provide insights and guidance for positive behavioral changes. What behavior would you like to explore? Want to understand your patterns better? 🌟"
                ],
                'priority': 2
            },
            
            'social_interaction': {
                'keywords': [
                    'social', 'interaction', 'communication', 'conversation', 'friends', 'family', 'relationships',
                    'social skills', 'people skills', 'interpersonal', 'communication style', 'social anxiety',
                    'making friends', 'building relationships', 'networking', 'social confidence', 'shyness',
                    'social behavior', 'group dynamics', 'teamwork', 'collaboration', 'conflict resolution',
                    'empathy', 'active listening', 'social awareness', 'cultural sensitivity', 'inclusivity',
                    'सामाजिक', 'बातचीत', 'दोस्ती', 'परिवार', 'रिश्ते', 'संवाद',
                    'social help', 'communication advice', 'relationship building', 'social confidence'
                ],
                'responses': [
                    "Social interaction life को connected बनाता है! Communication, relationships, social skills, confidence - आप किस social aspect improve करना चाहिए? क्या social anxiety है? 🤝",
                    "Social connector! From communication skills to relationship building, from social confidence to conflict resolution - what's your social interaction goal? Are you looking to make friends or improve existing relationships? 👥",
                    "मैं social interaction की guide हूँ! Communication techniques, social confidence, relationship building, conflict resolution - आप क्या social skill develop करना चाहिए? क्या specific social challenge है? 🌟",
                    "Let's enhance your social skills! Whether it's communication improvement, relationship building, social confidence, or conflict resolution - I can help you develop better interpersonal abilities! What's your social goal? Want specific communication techniques? 🌟"
                ],
                'priority': 2
            },
            
            'user_experience_feedback': {
                'keywords': [
                    'feedback', 'experience', 'satisfaction', 'improvement', 'suggestions', 'opinions',
                    'user feedback', 'customer experience', 'service quality', 'better service', 'improvement',
                    'what do you think', 'how am I doing', 'your opinion', 'suggestions for improvement',
                    'rate my service', 'performance review', 'quality assessment', 'service evaluation',
                    'helpful', 'not helpful', 'good service', 'bad service', 'experience sharing',
                    'प्रतिक्रिया', 'अनुभव', 'संतुष्टि', 'सुधार', 'सुझाव', 'राय',
                    'service feedback', 'user satisfaction', 'improvement suggestions', 'experience sharing'
                ],
                'responses': [
                    "User feedback मुझे improve करने में मदद करता है! Experience, satisfaction, suggestions, improvement - आपका experience कैसा रहा? क्या improvements चाहिए? 📝",
                    "Feedback seeker! I value your experience and suggestions! Whether it's positive feedback or areas for improvement - your opinion matters to me. How am I doing? What can I do better? ⭐",
                    "मैं user feedback से सीखती हूँ! Service quality, user experience, improvement suggestions, satisfaction - आपकी क्या राय है? क्या मैं बेहर service provide कर सकती हूँ? 🌟",
                    "I appreciate your feedback! Whether you're satisfied with my service or have suggestions for improvement - your experience helps me grow. How was our interaction? What would make it even better? Want to share your thoughts? 🌟"
                ],
                'priority': 2
            },
            
            'personalized_guidance': {
                'keywords': [
                    'personalized', 'custom', 'tailored', 'individual', 'specific', 'personal',
                    'guidance', 'advice', 'recommendations', 'suggestions', 'personal plan', 'custom help',
                    'individual needs', 'specific situation', 'personal circumstances', 'unique challenges',
                    'personal coaching', 'life coaching', 'personal development', 'customized support',
                    'one-on-one', 'personal attention', 'individual approach', 'tailored solutions',
                    'व्यक्तिगत', 'अनुकूल', 'विशिष्ट', 'व्यक्तिगत मार्गदर्शन',
                    'personal help', 'custom advice', 'individual guidance', 'personalized support'
                ],
                'responses': [
                    "Personalized guidance आपके लिए है! Individual needs, specific situation, personal challenges, custom solutions - आपकी क्या specific requirement है? क्या personalized advice चाहिए? 🎯",
                    "Personal guide! I provide tailored guidance based on your individual needs and specific circumstances. What's your unique situation? Let me create a personalized plan just for you! 🌟",
                    "मैं personalized guidance provide करती हूँ! Individual assessment, custom solutions, personal coaching, tailored advice - आपका कौन सा specific challenge है? क्या आपकी unique needs हैं? 🌟",
                    "Let's create your personalized plan! Whether it's individual challenges, specific circumstances, unique goals, or custom solutions - I can provide tailored guidance just for you. What's your specific situation? Want personalized recommendations? 🌟"
                ],
                'priority': 2
            },
            
            'user_psychology': {
                'keywords': [
                    'psychology', 'mental state', 'user psychology', 'behavioral psychology', 'cognitive psychology',
                    'thought patterns', 'mental models', 'cognitive biases', 'psychological insights',
                    'user mindset', 'thinking patterns', 'mental frameworks', 'psychological profile',
                    'personality analysis', 'character traits', 'behavioral tendencies', 'psychological assessment',
                    'emotional state', 'mood analysis', 'mental wellbeing', 'psychological health',
                    'cognitive processes', 'decision making psychology', 'motivation psychology', 'learning psychology',
                    'मनोविज्ञान', 'मानसिक स्थिति', 'विचार पैटर्न', 'व्यवहारिक मनोविज्ञान',
                    'psychological help', 'mental health insights', 'behavioral understanding', 'cognitive patterns'
                ],
                'responses': [
                    "User psychology को समझना important है! Mental state, thought patterns, cognitive biases, behavioral insights - आप किस psychological aspect explore करना चाहिए? क्या mental clarity चाहिए? 🧠",
                    "Psychology explorer! From cognitive patterns to behavioral insights, from mental models to decision psychology - what psychological aspect interests you? Are you looking to understand yourself better or learn about human psychology? 🧐",
                    "मैं user psychology की student हूँ! Mental state analysis, thought patterns, cognitive biases, behavioral tendencies - आप क्या psychological insight चाहिए? क्या specific mental pattern understand करना है? 🌟",
                    "Let's explore your psychology! Whether it's thought patterns, cognitive biases, behavioral tendencies, or mental models - I can provide psychological insights and understanding. What's your psychological question? Want to understand your thinking patterns better? 🌟"
                ],
                'priority': 2
            },
        }
    
    @staticmethod
    def get_stop_words():
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
            'jab', 'tab', 'yah', 'vah', 'ye', 'vo', 'hamara', 'tumhara', 'iska',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'which', 'who',
            }

# ========================================
# SECTION 3: ADVANCED ALGORITHMS
# ========================================
class VANIEAlgorithms:
    """Advanced algorithms for various computational tasks"""
    
    def __init__(self):
        self.cache = {}
        self.complexity_cache = {}
    
    # Sorting Algorithms
    def bubble_sort(self, arr: List[int]) -> List[int]:
        """Bubble Sort Algorithm - O(n²)"""
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr
    
    def quick_sort(self, arr: List[int]) -> List[int]:
        """Quick Sort Algorithm - O(n log n) average"""
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return self.quick_sort(left) + middle + self.quick_sort(right)
    
    def merge_sort(self, arr: List[int]) -> List[int]:
        """Merge Sort Algorithm - O(n log n)"""
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid])
        right = self.merge_sort(arr[mid:])
        
        return self.merge(left, right)
    
    def merge(self, left: List[int], right: List[int]) -> List[int]:
        """Helper function for merge sort"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    # Searching Algorithms
    def binary_search(self, arr: List[int], target: int) -> int:
        """Binary Search Algorithm - O(log n)"""
        left, right = 0, len(arr) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1
    
    def linear_search(self, arr: List[int], target: int) -> int:
        """Linear Search Algorithm - O(n)"""
        for i, val in enumerate(arr):
            if val == target:
                return i
        return -1
    
    # Graph Algorithms
    def dijkstra(self, graph: Dict[str, Dict[str, int]], start: str, end: str) -> Dict:
        """Dijkstra's Algorithm - Shortest Path"""
        import heapq
        
        distances = {node: float('infinity') for node in graph}
        distances[start] = 0
        previous = {node: None for node in graph}
        
        pq = [(0, start)]
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node == end:
                break
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        path = []
        current = end
        while current:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return {
            'distance': distances[end],
            'path': path,
            'distances': distances
        }
    
    def bfs(self, graph: Dict[str, List[str]], start: str) -> Dict:
        """Breadth-First Search"""
        from collections import deque
        
        visited = set()
        queue = deque([start])
        visited.add(start)
        order = []
        
        while queue:
            node = queue.popleft()
            order.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return {'traversal_order': order, 'visited': list(visited)}
    
    def dfs(self, graph: Dict[str, List[str]], start: str) -> Dict:
        """Depth-First Search"""
        visited = set()
        order = []
        
        def dfs_recursive(node):
            visited.add(node)
            order.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs_recursive(neighbor)
        
        dfs_recursive(start)
        return {'traversal_order': order, 'visited': list(visited)}
    
    # Dynamic Programming
    def fibonacci(self, n: int, memo: Dict = None) -> int:
        """Fibonacci with Memoization - O(n)"""
        if memo is None:
            memo = {}
        
        if n in memo:
            return memo[n]
        if n <= 1:
            return n
        
        memo[n] = self.fibonacci(n-1, memo) + self.fibonacci(n-2, memo)
        return memo[n]
    
    def knapsack_01(self, weights: List[int], values: List[int], capacity: int) -> int:
        """0/1 Knapsack Problem - Dynamic Programming"""
        n = len(weights)
        dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(capacity + 1):
                if weights[i-1] <= w:
                    dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], dp[i-1][w])
                else:
                    dp[i][w] = dp[i-1][w]
        
        return dp[n][capacity]
    
    def longest_common_subsequence(self, text1: str, text2: str) -> str:
        """Longest Common Subsequence - Dynamic Programming"""
        m, n = len(text1), len(text2)
        dp = [["" for _ in range(n+1)] for _ in range(m+1)]
        
        for i in range(m+1):
            for j in range(n+1):
                if i == 0 or j == 0:
                    dp[i][j] = ""
                elif text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + text1[i-1]
                else:
                    dp[i][j] = dp[i-1][j] if len(dp[i-1][j]) > len(dp[i][j-1]) else dp[i][j-1]
        
        return dp[m][n]
    
    # Mathematical Algorithms
    def gcd(self, a: int, b: int) -> int:
        """Greatest Common Divisor - Euclidean Algorithm"""
        while b:
            a, b = b, a % b
        return a
    
    def lcm(self, a: int, b: int) -> int:
        """Least Common Multiple"""
        return abs(a * b) // self.gcd(a, b)
    
    def is_prime(self, n: int) -> bool:
        """Prime Number Check - Optimized"""
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        
        i = 5
        w = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += w
            w = 6 - w
        
        return True
    
    def prime_factors(self, n: int) -> List[int]:
        """Prime Factorization"""
        factors = []
        
        # Handle 2 separately
        while n % 2 == 0:
            factors.append(2)
            n = n // 2
        
        # Check odd numbers up to sqrt(n)
        i = 3
        while i * i <= n:
            while n % i == 0:
                factors.append(i)
                n = n // i
            i += 2
        
        # If remaining n is a prime > 2
        if n > 2:
            factors.append(n)
        
        return factors
    
    # String Algorithms
    def is_palindrome(self, s: str) -> bool:
        """Palindrome Check"""
        s = ''.join(c.lower() for c in s if c.isalnum())
        return s == s[::-1]
    
    def reverse_string(self, s: str) -> str:
        """String Reversal"""
        return s[::-1]
    
    def find_substring(self, text: str, pattern: str) -> int:
        """Find Substring Index (Naive Approach)"""
        for i in range(len(text) - len(pattern) + 1):
            if text[i:i+len(pattern)] == pattern:
                return i
        return -1
    
    # Tree Algorithms
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right
    
    def inorder_traversal(self, root: TreeNode) -> List[int]:
        """Inorder Tree Traversal"""
        result = []
        
        def inorder(node):
            if node:
                inorder(node.left)
                result.append(node.val)
                inorder(node.right)
        
        inorder(root)
        return result
    
    def preorder_traversal(self, root: TreeNode) -> List[int]:
        """Preorder Tree Traversal"""
        result = []
        
        def preorder(node):
            if node:
                result.append(node.val)
                preorder(node.left)
                preorder(node.right)
        
        preorder(root)
        return result
    
    def postorder_traversal(self, root: TreeNode) -> List[int]:
        """Postorder Tree Traversal"""
        result = []
        
        def postorder(node):
            if node:
                postorder(node.left)
                postorder(node.right)
                result.append(node.val)
        
        postorder(root)
        return result
    
    # Machine Learning Algorithms (Basic)
    def linear_regression_predict(self, x: float, slope: float, intercept: float) -> float:
        """Simple Linear Regression Prediction"""
        return slope * x + intercept
    
    def euclidean_distance(self, point1: List[float], point2: List[float]) -> float:
        """Euclidean Distance Calculation"""
        return sum((a - b) ** 2 for a, b in zip(point1, point2)) ** 0.5
    
    def manhattan_distance(self, point1: List[float], point2: List[float]) -> float:
        """Manhattan Distance Calculation"""
        return sum(abs(a - b) for a, b in zip(point1, point2))
    
    # Hashing Algorithms
    def hash_string(self, s: str) -> int:
        """Simple String Hash Function"""
        hash_val = 0
        for char in s:
            hash_val = (hash_val * 31 + ord(char)) % 2**32
        return hash_val
    
    def check_sum(self, data: str) -> str:
        """Simple Checksum Calculation"""
        return hashlib.md5(data.encode()).hexdigest()
    
    # Utility Algorithms
    def factorial(self, n: int) -> int:
        """Factorial Calculation"""
        if n <= 1:
            return 1
        return n * self.factorial(n - 1)
    
    def power(self, base: int, exponent: int) -> int:
        """Power Calculation with Exponentiation by Squaring"""
        if exponent == 0:
            return 1
        elif exponent < 0:
            return 1 / self.power(base, -exponent)
        elif exponent % 2 == 0:
            half = self.power(base, exponent // 2)
            return half * half
        else:
            return base * self.power(base, exponent - 1)
    
    def absolute_value(self, n: int) -> int:
        """Absolute Value"""
        return -n if n < 0 else n
    
    # Algorithm Complexity Analysis
    def get_time_complexity(self, algorithm_name: str) -> str:
        """Get Time Complexity of Common Algorithms"""
        complexities = {
            'bubble_sort': 'O(n²)',
            'quick_sort': 'O(n log n) average, O(n²) worst',
            'merge_sort': 'O(n log n)',
            'binary_search': 'O(log n)',
            'linear_search': 'O(n)',
            'dijkstra': 'O((V + E) log V)',
            'bfs': 'O(V + E)',
            'dfs': 'O(V + E)',
            'fibonacci': 'O(2^n) naive, O(n) with memoization',
            'knapsack': 'O(nW)',
            'lcs': 'O(mn)',
            'gcd': 'O(log min(a,b))',
            'is_prime': 'O(√n)',
            'factorial': 'O(n)',
            'power': 'O(log n)'
        }
        return complexities.get(algorithm_name, 'Unknown')
    
    def explain_algorithm(self, algorithm_name: str) -> str:
        """Get Explanation of Algorithm"""
        explanations = {
            'bubble_sort': 'Bubble Sort repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order.',
            'quick_sort': 'Quick Sort picks a pivot element and partitions the array around it, then recursively sorts the sub-arrays.',
            'merge_sort': 'Merge Sort divides the array into two halves, recursively sorts them, and then merges the sorted halves.',
            'binary_search': 'Binary Search searches for a target value in a sorted array by repeatedly dividing the search interval in half.',
            'dijkstra': "Dijkstra's algorithm finds the shortest path between nodes in a weighted graph.",
            'fibonacci': 'Fibonacci sequence where each number is the sum of the two preceding ones.',
            'knapsack': 'The 0/1 Knapsack problem maximizes the total value of items that can fit in a knapsack of fixed capacity.',
            'lcs': 'Longest Common Subsequence finds the longest subsequence common to all sequences in a set of sequences.'
        }
        return explanations.get(algorithm_name, 'Algorithm explanation not available.')

# ========================================
# SECTION 4: ADVANCED NLP CORE ALGORITHM
# ========================================
class VANIEAI:
    """Complete AI Core with Multi-Keyword Scoring, Memory, Emotion Analysis, and NLP"""
    
    def __init__(self):
        # Initialize knowledge base
        self.intents = VANIEKnowledgeBase.get_intents()
        self.stop_words = VANIEKnowledgeBase.get_stop_words()
        
        # Initialize algorithms
        self.algorithms = VANIEAlgorithms()
        
        # Session management
        self.user_sessions = {}
        
        # Emotion words for sentiment analysis
        self.positive_words = [
            'happy', 'excited', 'amazing', 'wonderful', 'fantastic', 'great', 'awesome', 'love',
            'beautiful', 'excellent', 'perfect', 'brilliant', 'outstanding', 'superb',
            'खुश', 'अच्छा', 'बहुत अच्छा', 'शानदार', 'कमाल', 'जबरदस्त', 'उत्कृष्ट',
            'delighted', 'pleased', 'thrilled', 'ecstatic', 'joyful', 'cheerful'
        ]
        
        self.negative_words = [
            'sad', 'angry', 'frustrated', 'disappointed', 'worried', 'anxious', 'depressed',
            'upset', 'annoyed', 'irritated', 'stressed', 'tired', 'exhausted',
            'दुखी', 'गुस्सा', 'नाराज', 'चिंतित', 'परेशान', 'थका हुआ', 'उदास',
            'miserable', 'hopeless', 'helpless', 'lonely', 'confused', 'lost'
        ]
        
        # Semantic intent patterns
        self.intent_patterns = {
            "question": ["what", "how", "why", "when", "where", "which", "who", "can you", "could you"],
            "request": ["help", "assist", "show", "tell", "explain", "describe", "find"],
            "clarification": ["what do you mean", "clarify", "explain more", "what about"],
            "greeting": ["hi", "hello", "hey", "good morning", "good evening"],
            "farewell": ["bye", "goodbye", "see you", "take care"],
            "thanks": ["thank", "thanks", "appreciate", "helpful"]
        }
        
        # Identity and creator patterns
        self.identity_patterns = [
            "who are you", "what are you", "what is your name", "introduce yourself",
            "who made you", "who created you", "your creator", "your developer"
        ]
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if SENTENCE_TRANSFORMERS_AVAILABLE and sentence_model:
            try:
                # Generate embeddings
                embeddings = sentence_model.encode([text1, text2])
                # Calculate cosine similarity
                similarity = util.cos_sim(embeddings[0], embeddings[1])
                return float(similarity[0])
            except:
                pass
        
        # Fallback to keyword overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
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
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis using word matching"""
        text_lower = text.lower()
        
        positive_score = sum(1 for word in self.positive_words if word in text_lower)
        negative_score = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return {'emotion': 'happy', 'confidence': min(positive_score / 5, 1.0)}
        elif negative_score > positive_score:
            return {'emotion': 'sad', 'confidence': min(negative_score / 5, 1.0)}
        else:
            return {'emotion': 'neutral', 'confidence': 0.5}
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities using spaCy or fallback method"""
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(text)
                entities = [ent.text.lower() for ent in doc.ents]
                # Also extract important noun chunks
                chunks = [chunk.text.lower() for chunk in doc.noun_chunks]
                return list(set(entities + chunks))
            except:
                pass
        
        # Fallback: extract potential entities (capitalized words, technical terms)
        words = text.lower().split()
        entities = []
        for word in words:
            if len(word) > 3 and word.isalpha():
                entities.append(word)
        return entities
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract user name from text"""
        text_lower = text.lower()
        
        # Patterns for name extraction
        patterns = [
            r'my name is (\w+)',
            r'mera naam (\w+)',
            r'call me (\w+)',
            r'i am (\w+)',
            r'mein hoon (\w+)',
            r'mujhe (\w+) bulao'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).capitalize()
                return name
        
        return None
    
    def _detect_intent_semantically(self, text: str) -> Tuple[str, float]:
        """Detect intent using semantic understanding"""
        text_lower = text.lower()
        best_intent = "unknown"
        best_score = 0.0
        
        # Check pattern-based intents first
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return intent, 0.8  # High confidence for pattern matches
        
        # Use semantic similarity for complex inputs
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(text)
                # Analyze sentence structure and keywords
                for token in doc:
                    if token.pos_ in ["VERB", "NOUN", "PROPN"]:
                        # Check semantic similarity with intent keywords
                        for intent, data in self.intents.items():
                            for keyword in data["keywords"]:
                                similarity = self._semantic_similarity(token.text.lower(), keyword)
                                if similarity > best_score:
                                    best_score = similarity
                                    best_intent = intent
            except:
                pass
        
        return best_intent, best_score
    
    def _get_real_time_info(self, text: str) -> Optional[str]:
        """Get real-time information"""
        text_lower = text.lower()
        
        # Time queries
        if any(word in text_lower for word in ['time', 'samay', 'samay kya hai', 'current time']):
            now = datetime.now()
            return f"अभी समय है: {now.strftime('%I:%M %p')} | Current time: {now.strftime('%I:%M %p')} ⏰"
        
        # Date queries
        if any(word in text_lower for word in ['date', 'tarikh', 'aaj ki tarikh', 'today']):
            now = datetime.now()
            return f"आज की तारीख है: {now.strftime('%d %B %Y')} | Today's date: {now.strftime('%d %B %Y')} 📅"
        
        # Weather queries (basic response)
        if any(word in text_lower for word in ['weather', 'mausam', 'mausam kaisa hai', 'temperature']):
            return "मैं weather API से connect कर सकती हूँ, लेकिन अभी basic response दे रही हूँ। Weather check के लिए location बताएं! 🌤️"
        
        return None
    
    def _get_joke(self) -> str:
        """Get a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "प्रोग्रामर का घर क्यों छोटा होता है? क्योंकि वो space को respect करते हैं! 🏠💻",
            "Why did scarecrow win an award? Because he was outstanding in his field! 🌾",
            "Mathematics की सबसे बड़ी problem क्या है? Problem solving! 😂",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚😄"
        ]
        return random.choice(jokes)
    
    def _calculate_intent_scores(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate scores for each intent based on keyword matches"""
        intent_scores = {}
        
        for intent, data in self.intents.items():
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
    
    def _generate_multi_intent_response(self, intents: List[str], user_input: str, session_data: Dict) -> str:
        """Generate response when multiple intents are detected"""
        if len(intents) == 1:
            # Single intent - return standard response
            intent_data = self.intents[intents[0]]
            base_response = random.choice(intent_data['responses'])
            
            # Add personalization if user name is known
            if session_data.get('name'):
                if session_data['name'] not in base_response:
                    base_response = f"{session_data['name']}, {base_response}"
            
            return base_response
        
        # Multiple intents - combine responses
        responses = []
        
        for intent in intents:
            intent_data = self.intents[intent]
            
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
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context"""
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                'name': None,
                'emotion_history': [],
                'conversation_count': 0,
                'last_activity': datetime.now(),
                'preferences': {},
                'history': deque(maxlen=5)
            }
        return self.user_sessions[session_id]
    
    def _update_session_context(self, session_id: str, user_input: str, emotion: Dict[str, Any]):
        """Update session context"""
        context = self._get_session_context(session_id)
        
        # Extract and store name
        name = self._extract_name(user_input)
        if name and not context['name']:
            context['name'] = name
        
        # Update emotion history
        context['emotion_history'].append({
            'emotion': emotion['emotion'],
            'confidence': emotion['confidence'],
            'timestamp': datetime.now()
        })
        
        # Keep only last 10 emotions
        if len(context['emotion_history']) > 10:
            context['emotion_history'] = context['emotion_history'][-10:]
        
        # Update conversation count
        context['conversation_count'] += 1
        context['last_activity'] = datetime.now()
    
    def _check_context_reference(self, text: str, session_id: str) -> Optional[str]:
        """Check if user is referring to previous context"""
        if session_id not in self.user_sessions:
            return None
        
        history = self.user_sessions[session_id].get("history", [])
        if not history:
            return None
        
        # Check for reference words
        reference_words = ["that", "it", "the other one", "more about", "what about", "tell me more"]
        text_lower = text.lower()
        
        for word in reference_words:
            if word in text_lower:
                # Find most recent relevant topic
                for past_interaction in reversed(history):
                    if "domain" in past_interaction:
                        return past_interaction["domain"]
        
        return None
    
    def _get_smart_fallback(self) -> str:
        """Get smart fallback response"""
        fallback_responses = [
            "मैं अभी seekh rahi hu, par kya aap mujhse koi joke sunna chahenge ya aaj ka time janna chahenge? 😊",
            "I'm still learning! Would you like to hear a joke, check current time, or maybe talk about something I know well? 🤔",
            "मैं अभी इस topic के बारे में ज्यादा नहीं जानती, लेकिन मैं आपको हसा सकती हूँ या time बता सकती हूँ! 😄",
            "Let me help you with that! I can provide more detailed information if you'd like. 📚"
        ]
        return random.choice(fallback_responses)
    
    def generate_response(self, user_input: str, session_id: str = 'default') -> Dict[str, Any]:
        """Main response generation method with all advanced features"""
        
        # Check for identity questions first
        text_lower = user_input.lower()
        for pattern in self.identity_patterns:
            if pattern in text_lower:
                response = "मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। मुझे **Ayush Harinkhede** ने develop और create किया है। वे एक talented developer हैं जिन्होंने मुझे आपकी मदद करने के लिए बनाया है। 🤖✨"
                self._update_session_context(session_id, user_input, {'emotion': 'neutral', 'confidence': 0.9})
                return {
                    'response': response,
                    'intent': 'identity',
                    'domain': 'identity',
                    'confidence': 0.9,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
        
        # Check for context references
        context_domain = self._check_context_reference(user_input, session_id)
        if context_domain:
            # User is referring to previous topic
            intent_data = self.intents.get(context_domain, self.intents['greeting'])
            response = random.choice(intent_data['responses'])
            self._update_session_context(session_id, user_input, {'emotion': 'neutral', 'confidence': 0.8})
            return {
                'response': response,
                'intent': 'context_reference',
                'domain': context_domain,
                'confidence': 0.8,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 1: Analyze sentiment/emotion
        emotion = self._analyze_sentiment(user_input)
        
        # Step 2: Update session context
        self._update_session_context(session_id, user_input, emotion)
        
        # Step 3: Check for real-time information requests
        realtime_info = self._get_real_time_info(user_input)
        if realtime_info:
            return {
                'response': realtime_info,
                'category': 'realtime',
                'emotion': emotion,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 4: Check for joke requests
        if any(word in user_input.lower() for word in ['joke', 'jokes', 'funny', 'hasi', 'majak']):
            joke = self._get_joke()
            return {
                'response': joke,
                'category': 'entertainment',
                'emotion': emotion,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 5: Tokenize and calculate intent scores
        tokens = self._tokenize_and_clean(user_input)
        intent_scores = self._calculate_intent_scores(tokens)
        
        # Step 6: Select best intents
        best_intents = self._select_best_intents(intent_scores)
        
        # Step 7: Generate response
        if best_intents:
            session_data = self._get_session_context(session_id)
            response = self._generate_multi_intent_response(best_intents, user_input, session_data)
        else:
            # Smart fallback
            response = self._get_smart_fallback()
        
        return {
            'response': response,
            'detected_intents': best_intents,
            'intent_scores': intent_scores,
            'tokens': tokens,
            'emotion': emotion,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })

# ========================================
# SECTION3: ADVANCED NLP CORE ALGORITHM
# ========================================
class VANIEAI:
    """Complete AI Core with Multi-Keyword Scoring, Memory, Emotion Analysis, and NLP"""
    
    def __init__(self):
        # Initialize knowledge base
        self.intents = VANIEKnowledgeBase.get_intents()
        self.stop_words = VANIEKnowledgeBase.get_stop_words()
        
        # Session management
        self.user_sessions = {}
        
        # Emotion words for sentiment analysis
        self.positive_words = [
            'happy', 'excited', 'amazing', 'wonderful', 'fantastic', 'great', 'awesome', 'love',
            'beautiful', 'excellent', 'perfect', 'brilliant', 'outstanding', 'superb',
            'खुश', 'अच्छा', 'बहुत अच्छा', 'शानदार', 'कमाल', 'जबरदस्त', 'उत्कृष्ट',
            'delighted', 'pleased', 'thrilled', 'ecstatic', 'joyful', 'cheerful'
        ]
        
        self.negative_words = [
            'sad', 'angry', 'frustrated', 'disappointed', 'worried', 'anxious', 'depressed',
            'upset', 'annoyed', 'irritated', 'stressed', 'tired', 'exhausted',
            'दुखी', 'गुस्सा', 'नाराज', 'चिंतित', 'परेशान', 'थका हुआ', 'उदास',
            'miserable', 'hopeless', 'helpless', 'lonely', 'confused', 'lost'
        ]
        
        # Semantic intent patterns
        self.intent_patterns = {
            "question": ["what", "how", "why", "when", "where", "which", "who", "can you", "could you"],
            "request": ["help", "assist", "show", "tell", "explain", "describe", "find"],
            "clarification": ["what do you mean", "clarify", "explain more", "what about"],
            "greeting": ["hi", "hello", "hey", "good morning", "good evening"],
            "farewell": ["bye", "goodbye", "see you", "take care"],
            "thanks": ["thank", "thanks", "appreciate", "helpful"]
        }
        
        # Identity and creator patterns
        self.identity_patterns = [
            "who are you", "what are you", "what is your name", "introduce yourself",
            "who made you", "who created you", "your creator", "your developer"
        ]
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if SENTENCE_TRANSFORMERS_AVAILABLE and sentence_model:
            try:
                # Generate embeddings
                embeddings = sentence_model.encode([text1, text2])
                # Calculate cosine similarity
                similarity = util.cos_sim(embeddings[0], embeddings[1])
                return float(similarity[0])
            except:
                pass
        
        # Fallback to keyword overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
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
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis using word matching"""
        text_lower = text.lower()
        
        positive_score = sum(1 for word in self.positive_words if word in text_lower)
        negative_score = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return {'emotion': 'happy', 'confidence': min(positive_score / 5, 1.0)}
        elif negative_score > positive_score:
            return {'emotion': 'sad', 'confidence': min(negative_score / 5, 1.0)}
        else:
            return {'emotion': 'neutral', 'confidence': 0.5}
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities using spaCy or fallback method"""
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(text)
                entities = [ent.text.lower() for ent in doc.ents]
                # Also extract important noun chunks
                chunks = [chunk.text.lower() for chunk in doc.noun_chunks]
                return list(set(entities + chunks))
            except:
                pass
        
        # Fallback: extract potential entities (capitalized words, technical terms)
        words = text.lower().split()
        entities = []
        for word in words:
            if len(word) > 3 and word.isalpha():
                entities.append(word)
        return entities
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract user name from text"""
        text_lower = text.lower()
        
        # Patterns for name extraction
        patterns = [
            r'my name is (\w+)',
            r'mera naam (\w+)',
            r'call me (\w+)',
            r'i am (\w+)',
            r'mein hoon (\w+)',
            r'mujhe (\w+) bulao'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).capitalize()
                return name
        
        return None
    
    def _detect_intent_semantically(self, text: str) -> Tuple[str, float]:
        """Detect intent using semantic understanding"""
        text_lower = text.lower()
        best_intent = "unknown"
        best_score = 0.0
        
        # Check pattern-based intents first
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return intent, 0.8  # High confidence for pattern matches
        
        # Use semantic similarity for complex inputs
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(text)
                # Analyze sentence structure and keywords
                for token in doc:
                    if token.pos_ in ["VERB", "NOUN", "PROPN"]:
                        # Check semantic similarity with intent keywords
                        for intent, data in self.intents.items():
                            for keyword in data["keywords"]:
                                similarity = self._semantic_similarity(token.text.lower(), keyword)
                                if similarity > best_score:
                                    best_score = similarity
                                    best_intent = intent
            except:
                pass
        
        return best_intent, best_score
    
    def _get_real_time_info(self, text: str) -> Optional[str]:
        """Get real-time information"""
        text_lower = text.lower()
        
        # Time queries
        if any(word in text_lower for word in ['time', 'samay', 'samay kya hai', 'current time']):
            now = datetime.now()
            return f"अभी समय है: {now.strftime('%I:%M %p')} | Current time: {now.strftime('%I:%M %p')} ⏰"
        
        # Date queries
        if any(word in text_lower for word in ['date', 'tarikh', 'aaj ki tarikh', 'today']):
            now = datetime.now()
            return f"आज की तारीख है: {now.strftime('%d %B %Y')} | Today's date: {now.strftime('%d %B %Y')} 📅"
        
        # Weather queries (basic response)
        if any(word in text_lower for word in ['weather', 'mausam', 'mausam kaisa hai', 'temperature']):
            return "मैं weather API से connect कर सकती हूँ, लेकिन अभी basic response दे रही हूँ। Weather check के लिए location बताएं! 🌤️"
        
        return None
    
    def _get_joke(self) -> str:
        """Get a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "प्रोग्रामर का घर क्यों छोटा होता है? क्योंकि वो space को respect करते हैं! 🏠💻",
            "Why did scarecrow win an award? Because he was outstanding in his field! 🌾",
            "Mathematics की सबसे बड़ी problem क्या है? Problem solving! 😂",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚😄"
        ]
        return random.choice(jokes)
    
    def _calculate_intent_scores(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate scores for each intent based on keyword matches"""
        intent_scores = {}
        
        for intent, data in self.intents.items():
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
    
    def _generate_multi_intent_response(self, intents: List[str], user_input: str, session_data: Dict) -> str:
        """Generate response when multiple intents are detected"""
        if len(intents) == 1:
            # Single intent - return standard response
            intent_data = self.intents[intents[0]]
            base_response = random.choice(intent_data['responses'])
            
            # Add personalization if user name is known
            if session_data.get('name'):
                if session_data['name'] not in base_response:
                    base_response = f"{session_data['name']}, {base_response}"
            
            return base_response
        
        # Multiple intents - combine responses
        responses = []
        
        for intent in intents:
            intent_data = self.intents[intent]
            
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
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context"""
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                'name': None,
                'emotion_history': [],
                'conversation_count': 0,
                'last_activity': datetime.now(),
                'preferences': {},
                'history': deque(maxlen=5)
            }
        return self.user_sessions[session_id]
    
    def _update_session_context(self, session_id: str, user_input: str, emotion: Dict[str, Any]):
        """Update session context"""
        context = self._get_session_context(session_id)
        
        # Extract and store name
        name = self._extract_name(user_input)
        if name and not context['name']:
            context['name'] = name
        
        # Update emotion history
        context['emotion_history'].append({
            'emotion': emotion['emotion'],
            'confidence': emotion['confidence'],
            'timestamp': datetime.now()
        })
        
        # Keep only last 10 emotions
        if len(context['emotion_history']) > 10:
            context['emotion_history'] = context['emotion_history'][-10:]
        
        # Update conversation count
        context['conversation_count'] += 1
        context['last_activity'] = datetime.now()
    
    def _check_context_reference(self, text: str, session_id: str) -> Optional[str]:
        """Check if user is referring to previous context"""
        if session_id not in self.user_sessions:
            return None
        
        history = self.user_sessions[session_id].get("history", [])
        if not history:
            return None
        
        # Check for reference words
        reference_words = ["that", "it", "the other one", "more about", "what about", "tell me more"]
        text_lower = text.lower()
        
        for word in reference_words:
            if word in text_lower:
                # Find most recent relevant topic
                for past_interaction in reversed(history):
                    if "domain" in past_interaction:
                        return past_interaction["domain"]
        
        return None
    
    def _get_smart_fallback(self) -> str:
        """Get smart fallback response"""
        fallback_responses = [
            "मैं अभी seekh rahi hu, par kya aap mujhse koi joke sunna chahenge ya aaj ka time janna chahenge? 😊",
            "I'm still learning! Would you like to hear a joke, check current time, or maybe talk about something I know well? 🤔",
            "मैं अभी इस topic के बारे में ज्यादा नहीं जानती, लेकिन मैं आपको हसा सकती हूँ या time बता सकती हूँ! 😄",
            "Let me help you with that! I can provide more detailed information if you'd like. 📚"
        ]
        return random.choice(fallback_responses)
    
    def generate_response(self, user_input: str, session_id: str = 'default') -> Dict[str, Any]:
        """Main response generation method with all advanced features"""
        
        # Check for identity questions first
        text_lower = user_input.lower()
        for pattern in self.identity_patterns:
            if pattern in text_lower:
                response = "मैं VANIE हूँ - Virtual Assistant of Neural Integrated Engine। मुझे **Ayush Harinkhede** ने develop और create किया है। वे एक talented developer हैं जिन्होंने मुझे आपकी मदद करने के लिए बनाया है। 🤖✨"
                self._update_session_context(session_id, user_input, {'emotion': 'neutral', 'confidence': 0.9})
                return {
                    'response': response,
                    'intent': 'identity',
                    'domain': 'identity',
                    'confidence': 0.9,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
        
        # Check for context references
        context_domain = self._check_context_reference(user_input, session_id)
        if context_domain:
            # User is referring to previous topic
            intent_data = self.intents.get(context_domain, self.intents['greeting'])
            response = random.choice(intent_data['responses'])
            self._update_session_context(session_id, user_input, {'emotion': 'neutral', 'confidence': 0.8})
            return {
                'response': response,
                'intent': 'context_reference',
                'domain': context_domain,
                'confidence': 0.8,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 1: Analyze sentiment/emotion
        emotion = self._analyze_sentiment(user_input)
        
        # Step 2: Update session context
        self._update_session_context(session_id, user_input, emotion)
        
        # Step 3: Check for real-time information requests
        realtime_info = self._get_real_time_info(user_input)
        if realtime_info:
            return {
                'response': realtime_info,
                'category': 'realtime',
                'emotion': emotion,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 4: Check for joke requests
        if any(word in user_input.lower() for word in ['joke', 'jokes', 'funny', 'hasi', 'majak']):
            joke = self._get_joke()
            return {
                'response': joke,
                'category': 'entertainment',
                'emotion': emotion,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        # Step 5: Tokenize and calculate intent scores
        tokens = self._tokenize_and_clean(user_input)
        intent_scores = self._calculate_intent_scores(tokens)
        
        # Step 6: Select best intents
        best_intents = self._select_best_intents(intent_scores)
        
        # Step 7: Generate response
        if best_intents:
            session_data = self._get_session_context(session_id)
            response = self._generate_multi_intent_response(best_intents, user_input, session_data)
        else:
            # Smart fallback
            response = self._get_smart_fallback()
        
        return {
            'response': response,
            'detected_intents': best_intents,
            'intent_scores': intent_scores,
            'tokens': tokens,
            'emotion': emotion,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }

# ========================================
# SECTION 4: FLASK API SERVER
# ========================================
# Initialize Flask App with CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize AI
vanie_ai = VANIEAI()
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

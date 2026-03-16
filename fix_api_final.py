# Fix API by removing broken section and adding new one
import re

# Read the file
with open('VANIE.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove broken section from "Enhanced API Endpoints" to "Run Server"
pattern = r'# Enhanced API Endpoints.*?# 5\. Run Server'
content = re.sub(pattern, '# 5. Run Server', content, flags=re.DOTALL)

# Add new API section before "Run Server"
new_api = '''# Enhanced API Endpoints
@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced Chat API with better error handling"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request format',
                'message': 'Please provide JSON data',
                'status': 'error'
            }), 400
        
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({
                'error': 'No message provided',
                'message': 'Please provide a message to chat',
                'status': 'error'
            }), 400
        
        result = vanie_ai.process_message(user_message, session_id)
        
        response_data = {
            'response': result.get('response', 'Sorry, I could not process your message.'),
            'metadata': {
                'detected_intents': result.get('detected_intents', []),
                'intent_scores': result.get('intent_scores', {}),
                'emotion': result.get('emotion', {}),
                'session_id': result.get('session_id', session_id),
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'status': result.get('status', 'success')
            },
            'vanie_info': {
                'name': 'VANIE - Virtual Assistant of Neural Integrated Engine',
                'version': '2.0',
                'capabilities': ['Natural conversation', 'Algorithm help', 'Programming assistance']
            },
            'status': 'success'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': f'An error occurred: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VANIE AI Backend',
        'version': '2.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get frontend configuration"""
    try:
        config = vanie_ai.get_frontend_config()
        return jsonify({
            'config': config,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get configuration',
            'message': str(e),
            'status': 'error'
        }), 500

# Legacy endpoint for backward compatibility
@app.route('/chat', methods=['POST'])
def chat_legacy():
    """Legacy chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"response": "Please say something!"})
        
        result = vanie_ai.process_message(user_message)
        return jsonify({"response": result.get('response', 'No response available')})
        
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

'''

# Insert new API section
content = content.replace('# 5. Run Server', new_api + '\n\n# 5. Run Server')

# Write back to file
with open('VANIE.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("API section fixed successfully!")

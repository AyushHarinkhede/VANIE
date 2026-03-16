# Fix the broken API section
import sys
import os

# Read the file
with open('VANIE.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the broken API section
broken_start = "# Enhanced API Endpoints"
broken_end = "# 5. Run Server"

# New API section
new_api_section = """# Enhanced API Endpoints
@app.route('/api/chat', methods=['POST'])
def chat():
    \"\"\"Enhanced Chat API with better error handling and response structure\"\"\"
    try:
        data = request.get_json()
        
        # Validate request data
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
        
        # Process message with VANIE AI
        result = vanie_ai.process_message(user_message, session_id)
        
        # Enhanced response structure
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
                'capabilities': [
                    'Natural conversation',
                    'Algorithm help',
                    'Programming assistance',
                    'Real-time information',
                    'Multi-language support',
                    'Emotional intelligence'
                ]
            },
            'status': 'success'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        # Enhanced error handling
        return jsonify({
            'error': 'Internal server error',
            'message': f'An error occurred while processing your request: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    \"\"\"Health check endpoint\"\"\"
    return jsonify({
        'status': 'healthy',
        'service': 'VANIE AI Backend',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'running'
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    \"\"\"Get frontend configuration\"\"\"
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

@app.route('/api/search-suggestions', methods=['GET'])
def get_search_suggestions():
    \"\"\"Get search suggestions for frontend\"\"\"
    try:
        suggestions = vanie_ai.get_search_suggestions_data()
        return jsonify({
            'suggestions': suggestions,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get search suggestions',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    \"\"\"Get enhanced knowledge base\"\"\"
    try:
        knowledge = vanie_ai.get_enhanced_knowledge()
        return jsonify({
            'knowledge': knowledge,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get knowledge base',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/responses', methods=['GET'])
def get_responses():
    \"\"\"Get enhanced response templates\"\"\"
    try:
        responses = vanie_ai.get_enhanced_responses()
        return jsonify({
            'responses': responses,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get response templates',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session_data(session_id):
    \"\"\"Get session data for context\"\"\"
    try:
        session_data = vanie_ai.get_session_context(session_id)
        return jsonify({
            'session_id': session_id,
            'data': session_data,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get session data',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    \"\"\"Clear session data\"\"\"
    try:
        vanie_ai.clear_session(session_id)
        return jsonify({
            'message': f'Session {session_id} cleared successfully',
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to clear session',
            'message': str(e),
            'status': 'error'
        }), 500

# Legacy endpoint for backward compatibility
@app.route('/chat', methods=['POST'])
def chat_legacy():
    \"\"\"Legacy chat endpoint for backward compatibility\"\"\"
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"response": "Please say something!"})
        
        result = vanie_ai.process_message(user_message)
        return jsonify({"response": result.get('response', 'No response available')})
        
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint',
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), 500

# 5. Run Server"""

# Replace the broken section
content = content.replace(broken_start + "\n" + content.split(broken_start)[1].split(broken_end)[0], new_api_section)

# Write back to file
with open('VANIE.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("API section fixed successfully!")

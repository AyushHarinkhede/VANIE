# Fix backend response structure
import sys
import os

# Read the file
with open('VANIE.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the generate_response method to return proper structure
old_response = """        return {
            'response': response,
            'detected_intents': best_intents,
            'intent_scores': intent_scores,
            'tokens': tokens,
            'emotion': emotion,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }"""

new_response = """        return {
            'response': response,
            'metadata': {
                'detected_intents': best_intents,
                'intent_scores': intent_scores,
                'emotion': emotion,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            },
            'vanie_info': {
                'name': 'VANIE - Virtual Assistant of Neural Integrated Engine',
                'version': '2.0',
                'capabilities': ['Natural conversation', 'Algorithm help', 'Programming assistance', 'Multi-language support']
            },
            'status': 'success'
        }"""

# Replace the response structure
content = content.replace(old_response, new_response)

# Write back to file
with open('VANIE.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Backend response structure fixed successfully!")

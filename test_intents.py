# Simple test to check if algorithm keywords are in intents
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check if we can import and access intents
try:
    from VANIE import VANIEKnowledgeBase
    intents = VANIEKnowledgeBase.get_intents()
    
    print("Available intents:", list(intents.keys()))
    print()
    
    # Check web_development intent
    if 'web_development' in intents:
        web_dev_keywords = intents['web_development']['keywords']
        print(f'web_development intent found with {len(web_dev_keywords)} keywords')
        print('Sample keywords:', web_dev_keywords[:10])
        print()
        
        # Test if algorithm keywords are present
        algorithm_keywords = ['bubble sort', 'quick sort', 'binary search', 'dijkstra', 'fibonacci', 'prime number']
        print('Testing algorithm keywords in web_development intent:')
        for keyword in algorithm_keywords:
            if keyword in web_dev_keywords:
                print(f'✓ {keyword} - FOUND in web_development intent')
            else:
                print(f'✗ {keyword} - NOT found in web_development intent')
    else:
        print('web_development intent not found')
        
    print()
    # Check for any algorithm-related intents
    algorithm_intents = [intent for intent in intents.keys() if 'algorithm' in intent.lower()]
    print('Algorithm-related intents:', algorithm_intents)
    
except Exception as e:
    print(f'Error: {e}')
    print('This indicates the VANIE.py file may have syntax errors or import issues')

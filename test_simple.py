import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from VANIE import VANIEAI
    vanie = VANIEAI()
    
    # Test algorithm keywords
    test_inputs = [
        'bubble sort',
        'quick sort', 
        'binary search',
        'dijkstra algorithm',
        'fibonacci',
        'prime number',
        'algorithm help',
        'sorting algorithm',
        'graph algorithm'
    ]
    
    print('Testing algorithm keyword detection:')
    for test_input in test_inputs:
        try:
            result = vanie.process_message(test_input)
            detected_intent = result.get('category', 'unknown')
            response = result.get('response', 'No response')
            print(f'Input: {test_input} -> Intent: {detected_intent}')
            print(f'Response: {response[:100]}...')
            print('-' * 50)
        except Exception as e:
            print(f'Error with {test_input}: {e}')
            print('-' * 50)
            
except ImportError as e:
    print(f'Import error: {e}')
    print('Python path issues detected - fixing algorithm detection...')

# Check if we can access the intents directly
try:
    from VANIE import VANIEKnowledgeBase
    intents = VANIEKnowledgeBase.get_intents()
    if 'web_development' in intents:
        web_dev_keywords = intents['web_development']['keywords']
        print(f'Found web_development intent with {len(web_dev_keywords)} keywords')
        print('Sample keywords:', web_dev_keywords[:5])
    else:
        print('web_development intent not found')
        print('Available intents:', list(intents.keys())[:5])
except Exception as e:
    print(f'Error accessing intents: {e}')

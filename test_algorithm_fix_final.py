# Test script to verify algorithm detection fix
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from VANIE import VANIEAI
    
    # Initialize VANIE
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
    
    print('Testing algorithm keyword detection after fix:')
    print('=' * 60)
    
    for test_input in test_inputs:
        try:
            # Test tokenization
            tokens = vanie._tokenize_and_clean(test_input)
            
            # Test intent scoring
            scores = vanie._calculate_intent_scores(tokens)
            
            # Test full response
            result = vanie.process_message(test_input)
            detected_intent = result.get('category', 'unknown')
            response = result.get('response', 'No response')
            
            print(f'Input: "{test_input}"')
            print(f'Tokens: {tokens}')
            print(f'Intents detected: {list(scores.keys())}')
            print(f'Best intent: {detected_intent}')
            print(f'Response preview: {response[:80]}...')
            print('-' * 60)
            
        except Exception as e:
            print(f'Error with "{test_input}": {e}')
            print('-' * 60)
    
    print('\nTest completed! Check if algorithm keywords are now properly detected.')
    
except ImportError as e:
    print(f'Import error: {e}')
    print('This indicates VANIE.py may have syntax errors.')
except Exception as e:
    print(f'Unexpected error: {e}')
    import traceback
    traceback.print_exc()

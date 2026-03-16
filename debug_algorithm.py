# Test to check algorithm detection issue
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from VANIE import VANIEKnowledgeBase
    
    # Get web_development intent
    intents = VANIEKnowledgeBase.get_intents()
    
    if 'web_development' in intents:
        web_dev_keywords = intents['web_development']['keywords']
        print(f'web_development intent found with {len(web_dev_keywords)} keywords')
        
        # Test algorithm keywords
        algorithm_keywords = ['bubble sort', 'quick sort', 'binary search', 'dijkstra', 'fibonacci', 'prime number']
        print(f'Testing algorithm keywords:')
        
        found_count = 0
        for keyword in algorithm_keywords:
            if keyword in web_dev_keywords:
                found_count += 1
                print(f'✓ {keyword} - FOUND in keywords list')
            else:
                print(f'✗ {keyword} - NOT FOUND in keywords list')
        
        print(f'Algorithm keywords found: {found_count}/{len(algorithm_keywords)}')
        
        # Test tokenization
        from VANIE import VANIEAI
        vanie = VANIEAI()
        
        print(f'\nTesting tokenization:')
        test_input = 'bubble sort'
        tokens = vanie._tokenize_and_clean(test_input)
        print(f'Input: "{test_input}" -> Tokens: {tokens}')
        
        # Test intent scoring
        scores = vanie._calculate_intent_scores(tokens)
        print(f'Intent scores: {list(scores.keys())}')
        
        if 'web_development' in scores:
            print(f'web_development score: {scores["web_development"]}')
        else:
            print('web_development not detected!')
            
    else:
        print('web_development intent not found!')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

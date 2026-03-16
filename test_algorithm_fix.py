# Test algorithm detection in VANIE
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import and test
try:
    from VANIE import VANIEKnowledgeBase
    
    # Get web_development intent
    intents = VANIEKnowledgeBase.get_intents()
    
    if 'web_development' in intents:
        web_dev_keywords = intents['web_development']['keywords']
        print(f'✅ web_development intent found with {len(web_dev_keywords)} keywords')
        
        # Test algorithm keywords
        algorithm_keywords = ['bubble sort', 'quick sort', 'binary search', 'dijkstra', 'fibonacci', 'prime number']
        print(f'Testing algorithm keywords:')
        
        found_count = 0
        for keyword in algorithm_keywords:
            if keyword in web_dev_keywords:
                found_count += 1
                print(f'✓ {keyword} - FOUND')
            else:
                print(f'✗ {keyword} - NOT FOUND')
        
        print(f'Algorithm keywords found: {found_count}/{len(algorithm_keywords)}')
        
        if found_count == 0:
            print('❌ No algorithm keywords found in web_development intent!')
            print('This is the problem - algorithm keywords are not in the intent keywords list!')
            print('Available keywords in web_development intent:', web_dev_keywords[:10])
    else:
        print('✅ Algorithm keywords are properly integrated in web_development intent!')
    else:
        print('❌ web_development intent not found!')
        print('Available intents:', list(intents.keys())[:10])
        
except Exception as e:
    print(f'Error: {e}')
    print('This indicates VANIE.py has syntax errors or import issues')
    
print('\nTesting algorithm detection by keyword matching manually:')
# Test if algorithm keywords are in the web_development intent keywords
manual_test_keywords = ['bubble sort', 'quick sort', 'binary search', 'dijkstra', 'fibonacci', 'prime number']

try:
    if 'web_development' in intents:
        web_dev_keywords = intents['web_development']['keywords']
        print(f'Manual test of algorithm keywords:')
        for keyword in manual_test_keywords:
            if keyword.lower() in [kw.lower() for kw in web_dev_keywords]:
                print(f'✅ {keyword} - FOUND by manual check')
            else:
                print(f'✗ {keyword} - NOT FOUND by manual check')
except:
    print('Could not perform manual check')

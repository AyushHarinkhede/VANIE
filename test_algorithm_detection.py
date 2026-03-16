#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

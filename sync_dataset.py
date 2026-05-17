#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_dataset.py
Extracts intent patterns, sentiment words, jokes, riddles, quotes, trivia, and facts
from VANIE_ENHANCED.py and writes them to app/src/main/assets/vanie_dataset.json
for seamless offline Kotlin synchronization.
"""

import os
import json
import re
import sys
from VANIE_ENHANCED import VANIEEnhanced, AdvancedNLPAlgorithms

def export_dataset():
    engine = VANIEEnhanced()
    kb = engine.knowledge_base
    
    positive_words = {
        'good': 2, 'great': 3, 'excellent': 3, 'amazing': 3, 'wonderful': 3,
        'perfect': 3, 'love': 2, 'like': 1, 'happy': 2, 'excited': 2,
        'awesome': 3, 'fantastic': 3, 'brilliant': 3, 'beautiful': 2,
        'best': 3, 'nice': 1, 'cool': 1, 'interesting': 1, 'fun': 1,
        'खुश': 2, 'शानदार': 3, 'बढ़िया': 2, 'अच्छा': 1, 'सुंदर': 2
    }
    
    negative_words = {
        'bad': 2, 'terrible': 3, 'awful': 3, 'horrible': 3, 'hate': 3,
        'dislike': 2, 'sad': 2, 'upset': 2, 'angry': 2, 'frustrated': 2,
        'worst': 3, 'poor': 2, 'boring': 1, 'stupid': 2, 'annoying': 2,
        'बुरा': 2, 'भयानक': 3, 'दुःख': 2, 'गुस्सा': 2, 'परेशान': 2
    }

    dataset = {
        "version": kb['vanie_info']['version'],
        "name": "VANIE - Virtual Agent of Neural Integrated Engine",
        "intents": kb['intent_patterns'],
        "jokes": engine.jokes,
        "riddles": engine.riddles,
        "quotes": engine.motivational_quotes,
        "facts": engine.fun_facts,
        "trivia": engine.trivia_questions,
        "sentiment": {
            "positive": positive_words,
            "negative": negative_words
        }
    }

    output_dir = os.path.join("app", "src", "main", "assets")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "vanie_dataset.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully exported VANIE NLP dataset to {output_path}")
    print(f"📊 Total intents: {len(kb['intent_patterns'])}")
    print(f"😄 Jokes: {len(engine.jokes)}, 🤔 Riddles: {len(engine.riddles)}")

if __name__ == "__main__":
    export_dataset()

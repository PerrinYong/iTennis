#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate questions.json format"""

import json
import sys

try:
    with open('aiteni-core/config/questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"✅ JSON is valid!")
    print(f"   Total questions: {len(questions)}")
    
    # Count by tier
    basic_count = sum(1 for q in questions if q.get('question_tier') == 'basic')
    advanced_count = sum(1 for q in questions if q.get('question_tier') == 'advanced')
    
    print(f"   Basic questions: {basic_count}")
    print(f"   Advanced questions: {advanced_count}")
    
    # Check for A0 options
    a0_count = 0
    for q in questions:
        for opt in q.get('options', []):
            if opt['id'].endswith('_A0'):
                a0_count += 1
    
    print(f"   Questions with A0 option: {a0_count}")
    
    sys.exit(0)
    
except json.JSONDecodeError as e:
    print(f"❌ JSON格式错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 验证失败: {e}")
    sys.exit(1)

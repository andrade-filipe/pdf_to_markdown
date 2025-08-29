#!/usr/bin/env python3
"""Teste simples de detecção de títulos"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter.steps.markdown_conversion_step import MarkdownConversionStep

def test_simple():
    step = MarkdownConversionStep()
    
    test_cases = [
        "Abstract",
        "Introduction", 
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
        "References",
        "Bibliography",
        "Appendix"
    ]
    
    print("🔍 TESTE SIMPLES DE DETECÇÃO DE TÍTULOS")
    print("=" * 50)
    
    for case in test_cases:
        result = step._is_title(case)
        status = "✅ TÍTULO" if result else "❌ NÃO É TÍTULO"
        print(f"{status}: '{case}'")

if __name__ == "__main__":
    test_simple()

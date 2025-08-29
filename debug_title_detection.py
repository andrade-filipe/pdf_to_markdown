#!/usr/bin/env python3
"""Debug da detecção de títulos"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter.steps.markdown_conversion_step import MarkdownConversionStep

def debug_title_detection():
    step = MarkdownConversionStep()
    
    test_cases = ["Methods", "Results"]
    
    print("🔍 DEBUG DETECÇÃO DE TÍTULOS")
    print("=" * 50)
    
    for case in test_cases:
        print(f"\n📝 Testando: '{case}'")
        
        # Verificar se está na lista de seções acadêmicas
        academic_sections = {
            'abstract', 'introduction', 'methods', 'method', 'materials', 'results', 'result', 'discussion', 
            'conclusion', 'conclusions', 'references', 'bibliography', 'appendix', 
            'appendices', 'acknowledgments', 'acknowledgements', 'summary', 'background',
            'literature review', 'methodology', 'analysis', 'evaluation', 'assessment'
        }
        
        print(f"   Está em academic_sections? {case.lower() in academic_sections}")
        print(f"   academic_sections contém: {academic_sections}")
        
        # Testar a função diretamente
        result = step._is_title(case)
        print(f"   Resultado final: {result}")

if __name__ == "__main__":
    debug_title_detection()

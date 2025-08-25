#!/usr/bin/env python3
import fitz

def debug_raw_text(pdf_path):
    """Debuga o texto bruto do PDF"""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for i in range(len(doc)):
            page = doc[i]
            full_text += page.get_text()
        doc.close()
        
        print(f"\n🔍 Texto bruto de {pdf_path}")
        
        # Procurar por padrões BR no texto bruto
        lines = full_text.split('\n')
        
        for i, line in enumerate(lines):
            if '_BR_' in line:
                print(f"Linha {i+1}: '{line}'")
                # Mostrar contexto
                start = max(0, i-2)
                end = min(len(lines), i+3)
                for j in range(start, end):
                    if j == i:
                        print(f"  >>> {j+1}: '{lines[j]}'")
                    else:
                        print(f"     {j+1}: '{lines[j]}'")
                print()
        
        return full_text
        
    except Exception as e:
        print(f"Erro: {e}")
        return ""

# Testar com um PDF que não está sendo detectado
debug_raw_text("/home/andrade/Documentos/quantum/pdf/quantum-dominio.pdf")

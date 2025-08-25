#!/usr/bin/env python3
import fitz
import os

def check_pdf_pages(pdf_path):
    """Verifica as páginas de um PDF e extrai o texto"""
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"\n📄 {os.path.basename(pdf_path)}")
        print(f"Total de páginas: {total_pages}")
        
        full_text = ""
        for i in range(total_pages):
            page = doc[i]
            page_text = page.get_text()
            full_text += f"\n--- PÁGINA {i+1} ---\n"
            full_text += page_text
            print(f"  Página {i+1}: {len(page_text)} caracteres")
        
        doc.close()
        
        print(f"Texto total extraído: {len(full_text)} caracteres")
        
        # Verificar se há padrões de regras de negócio
        business_rules = []
        lines = full_text.split('\n')
        for line in lines:
            if '_BR_' in line and '(' in line and ')' in line and '[' in line and ']' in line:
                business_rules.append(line.strip())
        
        print(f"Regras de negócio encontradas: {len(business_rules)}")
        if business_rules:
            print("Primeiras 5 regras:")
            for i, rule in enumerate(business_rules[:5]):
                print(f"  {i+1}. {rule}")
        
        return full_text, business_rules
        
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")
        return "", []

# Verificar todos os PDFs Quantum
quantum_pdf_dir = "/home/andrade/Documentos/quantum/pdf"
pdf_files = [f for f in os.listdir(quantum_pdf_dir) if f.endswith('.pdf')]

for pdf_file in sorted(pdf_files):
    pdf_path = os.path.join(quantum_pdf_dir, pdf_file)
    check_pdf_pages(pdf_path)

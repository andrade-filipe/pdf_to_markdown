#!/usr/bin/env python3
import fitz
import os
import re

def check_pdf_patterns(pdf_path):
    """Verifica diferentes padrões nos PDFs"""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for i in range(len(doc)):
            page = doc[i]
            full_text += page.get_text()
        doc.close()
        
        print(f"\n📄 {os.path.basename(pdf_path)}")
        print(f"Texto total: {len(full_text)} caracteres")
        
        # Verificar diferentes padrões
        patterns = {
            'BR_pattern': r'[A-Za-z_]+_BR_\d+',
            'class_pattern': r'class\s+[A-Za-z_]+',
            'method_pattern': r'public\s+[A-Za-z_<>\[\]]+\s+[A-Za-z_]+\s*\(',
            'property_pattern': r'public\s+[A-Za-z_<>\[\]]+\s+[A-Za-z_]+\s*\{',
            'interface_pattern': r'interface\s+[A-Za-z_]+',
            'table_pattern': r'\|.*\|.*\|.*\|',
            'code_block': r'```[\s\S]*?```',
            'function_pattern': r'def\s+[A-Za-z_]+',
            'variable_pattern': r'var\s+[A-Za-z_]+',
            'const_pattern': r'const\s+[A-Za-z_]+',
            'enum_pattern': r'enum\s+[A-Za-z_]+',
            'struct_pattern': r'struct\s+[A-Za-z_]+'
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                print(f"  {pattern_name}: {len(matches)} encontrados")
                if len(matches) <= 5:
                    for match in matches:
                        print(f"    - {match}")
                else:
                    print(f"    - Primeiros 5: {matches[:5]}")
        
        # Verificar se há seções específicas
        sections = [
            'Resultado Regra de Negócio',
            'Diagrama Regra de Negócio', 
            'Sumário de Regras',
            'Detalhamento do Código',
            'Regras de Negócio',
            'Business Rules',
            'Code Details',
            'Implementation',
            'Architecture',
            'Design Patterns'
        ]
        
        print("  Seções encontradas:")
        for section in sections:
            if section in full_text:
                print(f"    ✓ {section}")
        
        # Verificar estrutura de tabelas
        lines = full_text.split('\n')
        table_lines = [line for line in lines if '|' in line and line.count('|') >= 3]
        if table_lines:
            print(f"  Linhas de tabela: {len(table_lines)}")
            print(f"    Primeiras 3: {table_lines[:3]}")
        
        return full_text
        
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")
        return ""

# Verificar todos os PDFs Quantum
quantum_pdf_dir = "/home/andrade/Documentos/quantum/pdf"
pdf_files = [f for f in os.listdir(quantum_pdf_dir) if f.endswith('.pdf')]

for pdf_file in sorted(pdf_files):
    pdf_path = os.path.join(quantum_pdf_dir, pdf_file)
    check_pdf_patterns(pdf_path)

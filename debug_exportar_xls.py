#!/usr/bin/env python3
import fitz
import re
import os

def debug_exportar_xls():
    """Debuga especificamente o PDF exportar-xls"""
    pdf_path = "/home/andrade/Documentos/quantum/pdf/quantum-exportar-xls.pdf"
    
    print("🔍 DEBUGANDO quantum-exportar-xls.pdf")
    print("=" * 60)
    
    # 1. Extração bruta do PDF
    print("\n1️⃣ EXTRAÇÃO BRUTA DO PDF:")
    doc = fitz.open(pdf_path)
    raw_text = ""
    
    for i in range(len(doc)):
        page = doc[i]
        page_text = page.get_text()
        raw_text += f"\n--- PÁGINA {i+1} ---\n"
        raw_text += page_text
        print(f"  Página {i+1}: {len(page_text)} caracteres")
    
    doc.close()
    print(f"  Total: {len(raw_text)} caracteres")
    
    # 2. Verificar seções importantes
    print("\n2️⃣ SEÇÕES IMPORTANTES ENCONTRADAS:")
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
        'Design Patterns',
        'Excel',
        'Export',
        'XLS',
        'XLSX',
        'Configuração',
        'Configuracoes'
    ]
    
    for section in sections:
        if section in raw_text:
            print(f"  ✓ {section}")
        else:
            print(f"  ✗ {section}")
    
    # 3. Verificar padrões BR
    print("\n3️⃣ PADRÕES BR ENCONTRADOS:")
    br_pattern = r'([A-Za-z_]*)_BR_(\d+)'
    br_matches = re.findall(br_pattern, raw_text)
    
    print(f"  Total de padrões BR: {len(br_matches)}")
    if br_matches:
        print("  Primeiros 10 padrões:")
        for i, (class_name, br_id) in enumerate(br_matches[:10]):
            print(f"    {i+1}. {class_name}_BR_{br_id}")
    
    # 4. Verificar tabelas
    print("\n4️⃣ TABELAS ENCONTRADAS:")
    lines = raw_text.split('\n')
    table_lines = [line for line in lines if '|' in line and line.count('|') >= 3]
    print(f"  Linhas de tabela: {len(table_lines)}")
    if table_lines:
        print("  Primeiras 5 linhas de tabela:")
        for i, line in enumerate(table_lines[:5]):
            print(f"    {i+1}. {line}")
    
    # 5. Verificar código
    print("\n5️⃣ CÓDIGO ENCONTRADO:")
    code_patterns = [
        r'class\s+[A-Za-z_]+',
        r'public\s+[A-Za-z_<>\[\]]+\s+[A-Za-z_]+\s*\(',
        r'interface\s+[A-Za-z_]+',
        r'def\s+[A-Za-z_]+',
        r'var\s+[A-Za-z_]+',
        r'const\s+[A-Za-z_]+',
        r'enum\s+[A-Za-z_]+',
        r'struct\s+[A-Za-z_]+'
    ]
    
    for pattern_name, pattern in zip(['class', 'method', 'interface', 'function', 'variable', 'const', 'enum', 'struct'], code_patterns):
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        if matches:
            print(f"  {pattern_name}: {len(matches)} encontrados")
            if len(matches) <= 5:
                for match in matches:
                    print(f"    - {match}")
            else:
                print(f"    - Primeiros 5: {matches[:5]}")
    
    # 6. Verificar palavras-chave específicas do Excel
    print("\n6️⃣ PALAVRAS-CHAVE EXCEL:")
    excel_keywords = [
        'Excel', 'XLS', 'XLSX', 'Export', 'Exportar', 'Planilha', 'Sheet',
        'Workbook', 'Worksheet', 'Cell', 'Range', 'Formula', 'Fórmula',
        'Configuração', 'Configuracoes', 'Template', 'Modelo'
    ]
    
    for keyword in excel_keywords:
        count = raw_text.count(keyword)
        if count > 0:
            print(f"  {keyword}: {count} ocorrências")
    
    # 7. Mostrar amostra do texto
    print("\n7️⃣ AMOSTRA DO TEXTO (primeiros 2000 caracteres):")
    print("-" * 40)
    print(raw_text[:2000])
    print("-" * 40)
    
    return raw_text

if __name__ == "__main__":
    debug_exportar_xls()

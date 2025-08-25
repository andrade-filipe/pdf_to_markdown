#!/usr/bin/env python3
import fitz
import re

def debug_code_section():
    """Debuga especificamente a seção de código do PDF exportar-xls"""
    pdf_path = "/home/andrade/Documentos/quantum/pdf/quantum-exportar-xls.pdf"
    
    print("🔍 DEBUGANDO SEÇÃO DE CÓDIGO - quantum-exportar-xls.pdf")
    print("=" * 60)
    
    # Extrair texto
    doc = fitz.open(pdf_path)
    raw_text = ""
    for i in range(len(doc)):
        page = doc[i]
        raw_text += page.get_text()
    doc.close()
    
    lines = raw_text.split('\n')
    print(f"Total de linhas: {len(lines)}")
    
    # Encontrar a seção "Detalhamento do Código"
    code_section_start = -1
    for i, line in enumerate(lines):
        if 'Detalhamento do Código' in line:
            code_section_start = i
            print(f"\n📍 Seção 'Detalhamento do Código' encontrada na linha {i+1}")
            print(f"   Linha: '{line}'")
            break
    
    if code_section_start == -1:
        print("❌ Seção 'Detalhamento do Código' não encontrada!")
        return
    
    # Mostrar contexto ao redor da seção
    print(f"\n📋 CONTEXTO AO REDOR DA SEÇÃO (linhas {code_section_start-5} a {code_section_start+20}):")
    print("-" * 60)
    
    start = max(0, code_section_start - 5)
    end = min(len(lines), code_section_start + 20)
    
    for i in range(start, end):
        marker = ">>> " if i == code_section_start else "    "
        print(f"{marker}{i+1:4d}: '{lines[i]}'")
    
    # Procurar por conteúdo após a seção
    print(f"\n🔍 PROCURANDO CONTEÚDO APÓS A SEÇÃO:")
    print("-" * 60)
    
    content_found = False
    for i in range(code_section_start + 1, min(len(lines), code_section_start + 50)):
        line = lines[i].strip()
        if line:
            print(f"   {i+1:4d}: '{line}'")
            content_found = True
        elif content_found:
            # Se encontrou conteúdo e agora tem linha vazia, pode ser fim da seção
            print(f"   {i+1:4d}: (linha vazia - possível fim da seção)")
            break
    
    if not content_found:
        print("   ❌ Nenhum conteúdo encontrado após a seção!")
    
    # Verificar se há outras seções próximas
    print(f"\n🔍 OUTRAS SEÇÕES PRÓXIMAS:")
    print("-" * 60)
    
    for i in range(code_section_start - 10, min(len(lines), code_section_start + 50)):
        line = lines[i].strip()
        if any(section in line for section in ['Resultado Regra de Negócio', 'Diagrama Regra de Negócio', 'Sumário de Regras', 'Regras de Negócio']):
            print(f"   {i+1:4d}: '{line}'")
    
    # Verificar se há conteúdo relacionado ao Excel
    print(f"\n🔍 CONTEÚDO RELACIONADO AO EXCEL:")
    print("-" * 60)
    
    excel_content = []
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in ['Excel', 'Export', 'XLS', 'Template', 'Configuração']):
            excel_content.append((i+1, line.strip()))
    
    if excel_content:
        print(f"Encontradas {len(excel_content)} linhas com conteúdo Excel:")
        for line_num, content in excel_content[:10]:  # Mostrar apenas as primeiras 10
            print(f"   {line_num:4d}: '{content}'")
        if len(excel_content) > 10:
            print(f"   ... e mais {len(excel_content) - 10} linhas")
    else:
        print("   ❌ Nenhum conteúdo relacionado ao Excel encontrado!")

if __name__ == "__main__":
    debug_code_section()

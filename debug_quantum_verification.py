#!/usr/bin/env python3
"""
Script para verificar se todas as informações dos PDFs Quantum estão presentes nos Markdowns
"""

import os
import fitz
import re
from pathlib import Path

def extract_pdf_content(pdf_path):
    """Extrai todo o conteúdo de um PDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Erro ao extrair PDF {pdf_path}: {e}")
        return ""

def read_markdown_content(md_path):
    """Lê o conteúdo de um arquivo Markdown"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler Markdown {md_path}: {e}")
        return ""

def check_keywords_in_content(content, keywords, content_name):
    """Verifica se palavras-chave estão presentes no conteúdo"""
    found_keywords = []
    missing_keywords = []
    
    for keyword in keywords:
        if keyword.lower() in content.lower():
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    print(f"\n📋 {content_name}:")
    print(f"✅ Encontradas ({len(found_keywords)}): {', '.join(found_keywords)}")
    if missing_keywords:
        print(f"❌ Faltando ({len(missing_keywords)}): {', '.join(missing_keywords)}")
    
    return found_keywords, missing_keywords

def check_br_patterns(content, content_name):
    """Verifica padrões de regras de negócio"""
    br_pattern = r'[A-Za-z_]*_BR_\d+'
    br_matches = re.findall(br_pattern, content)
    
    print(f"\n🔍 {content_name} - Padrões BR encontrados: {len(br_matches)}")
    if br_matches:
        unique_brs = list(set(br_matches))
        print(f"   Regras únicas: {len(unique_brs)}")
        print(f"   Exemplos: {', '.join(unique_brs[:10])}")
    
    return br_matches

def check_sections(content, content_name):
    """Verifica seções importantes"""
    sections = [
        'Resultado Regra de Negócio',
        'Diagrama Regra de Negócio', 
        'Sumário de Regras',
        'Detalhamento do Código',
        'Regras de Negócio'
    ]
    
    found_sections = []
    for section in sections:
        if section in content:
            found_sections.append(section)
    
    print(f"\n📑 {content_name} - Seções encontradas: {len(found_sections)}")
    for section in found_sections:
        print(f"   ✅ {section}")
    
    return found_sections

def check_content_length(pdf_content, md_content, pdf_name):
    """Verifica o tamanho do conteúdo"""
    pdf_chars = len(pdf_content)
    md_chars = len(md_content)
    
    print(f"\n📊 {pdf_name}:")
    print(f"   PDF: {pdf_chars:,} caracteres")
    print(f"   Markdown: {md_chars:,} caracteres")
    
    if md_chars > 0:
        ratio = (md_chars / pdf_chars) * 100
        print(f"   Proporção: {ratio:.1f}%")
        if ratio < 10:
            print(f"   ⚠️  ATENÇÃO: Proporção muito baixa!")
    
    return pdf_chars, md_chars

def main():
    pdf_dir = "/home/andrade/Documentos/quantum/pdf"
    md_dir = "/home/andrade/Documentos/quantum/markdown"
    
    # Palavras-chave específicas para cada PDF
    keywords_by_pdf = {
        'quantum-authentication': ['authentication', 'token', 'login', 'auth', 'security', 'middleware'],
        'quantum-controle-acesso': ['acesso', 'controle', 'permissão', 'authorization', 'role'],
        'quantum-dominio': ['domínio', 'domain', 'entidade', 'entity', 'repository'],
        'quantum-email': ['email', 'mail', 'send', 'queue', 'notification'],
        'quantum-exportar-xls': ['excel', 'export', 'xls', 'template', 'configuração', 'matriz'],
        'quantum-sinc-api': ['api', 'sinc', 'controller', 'service', 'endpoint'],
        'quantum-sinc-client': ['client', 'sinc', 'dto', 'map', 'repository']
    }
    
    # Palavras-chave gerais para todos os PDFs
    general_keywords = [
        'responsável', 'configurar', 'gerar', 'processar', 'validar',
        'interface', 'classe', 'método', 'construtor', 'propriedade',
        'repository', 'service', 'controller', 'dto', 'entity'
    ]
    
    print("🔍 VERIFICAÇÃO COMPLETA DOS PDFs QUANTUM")
    print("=" * 60)
    
    total_issues = 0
    
    for pdf_file in os.listdir(pdf_dir):
        if not pdf_file.endswith('.pdf'):
            continue
            
        pdf_name = pdf_file.replace('.pdf', '')
        pdf_path = os.path.join(pdf_dir, pdf_file)
        md_path = os.path.join(md_dir, f"{pdf_name}.md")
        
        print(f"\n{'='*60}")
        print(f"📄 VERIFICANDO: {pdf_name}")
        print(f"{'='*60}")
        
        # Verificar se arquivos existem
        if not os.path.exists(pdf_path):
            print(f"❌ PDF não encontrado: {pdf_path}")
            continue
            
        if not os.path.exists(md_path):
            print(f"❌ Markdown não encontrado: {md_path}")
            total_issues += 1
            continue
        
        # Extrair conteúdo
        pdf_content = extract_pdf_content(pdf_path)
        md_content = read_markdown_content(md_path)
        
        if not pdf_content:
            print(f"❌ Não foi possível extrair conteúdo do PDF")
            total_issues += 1
            continue
            
        if not md_content:
            print(f"❌ Markdown está vazio")
            total_issues += 1
            continue
        
        # Verificações básicas
        pdf_chars, md_chars = check_content_length(pdf_content, md_content, pdf_name)
        
        # Verificar seções
        sections = check_sections(md_content, "Markdown")
        
        # Verificar padrões BR
        pdf_brs = check_br_patterns(pdf_content, "PDF")
        md_brs = check_br_patterns(md_content, "Markdown")
        
        # Verificar palavras-chave específicas
        specific_keywords = keywords_by_pdf.get(pdf_name, [])
        if specific_keywords:
            pdf_found, pdf_missing = check_keywords_in_content(pdf_content, specific_keywords, "PDF")
            md_found, md_missing = check_keywords_in_content(md_content, specific_keywords, "Markdown")
            
            if md_missing:
                print(f"⚠️  Palavras-chave específicas faltando no Markdown: {', '.join(md_missing)}")
                total_issues += len(md_missing)
        
        # Verificar palavras-chave gerais
        pdf_found, pdf_missing = check_keywords_in_content(pdf_content, general_keywords, "PDF (gerais)")
        md_found, md_missing = check_keywords_in_content(md_content, general_keywords, "Markdown (gerais)")
        
        # Verificar se há tabela de regras
        if '| ID | Nome | Impacto |' in md_content:
            print(f"✅ Tabela de regras de negócio presente")
        else:
            print(f"❌ Tabela de regras de negócio ausente")
            total_issues += 1
        
        # Verificar se há detalhamento do código
        if 'Detalhamento do Código' in md_content:
            # Verificar se há conteúdo após a seção
            code_section_start = md_content.find('## Detalhamento do Código')
            if code_section_start != -1:
                # Procurar próxima seção ou fim do arquivo
                next_section = md_content.find('##', code_section_start + 25)
                if next_section != -1:
                    code_content = md_content[code_section_start + 25:next_section].strip()
                else:
                    code_content = md_content[code_section_start + 25:].strip()
                
                if len(code_content) > 100:
                    print(f"✅ Seção de código com conteúdo: {len(code_content)} caracteres")
                else:
                    print(f"⚠️  Seção de código com pouco conteúdo: {len(code_content)} caracteres")
                    total_issues += 1
            else:
                print(f"❌ Seção de código sem conteúdo")
                total_issues += 1
        else:
            print(f"❌ Seção de detalhamento do código ausente")
            total_issues += 1
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"Total de problemas encontrados: {total_issues}")
    
    if total_issues == 0:
        print(f"🎉 TODOS OS PDFs ESTÃO COMPLETOS!")
    else:
        print(f"⚠️  {total_issues} problemas precisam ser corrigidos")

if __name__ == "__main__":
    main()

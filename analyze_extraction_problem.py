#!/usr/bin/env python3
"""
Script para analisar o problema de extração de texto
"""

import os
import sys
from pathlib import Path
import fitz
import re

def analyze_extraction_problem():
    """Analisa detalhadamente o problema de extração de texto"""
    
    # Arquivo para testar
    pdf_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/Mount St. Helens and Catastrophism.pdf"
    
    print("🔍 ANÁLISE DETALHADA DO PROBLEMA DE EXTRAÇÃO")
    print("="*60)
    
    doc = fitz.open(pdf_path)
    
    print(f"\n📄 ARQUIVO: {Path(pdf_path).name}")
    print(f"📊 PÁGINAS: {len(doc)}")
    print("-" * 40)
    
    total_chars = 0
    total_words = 0
    
    # Analisar cada página individualmente
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        print(f"\n📄 PÁGINA {page_num + 1}:")
        
        # Método 1: Extração simples
        simple_text = page.get_text()
        simple_chars = len(simple_text)
        simple_words = len(re.findall(r'\b\w+\b', simple_text.lower()))
        
        print(f"   Método 1 (simples): {simple_chars:,} chars, {simple_words:,} palavras")
        
        # Método 2: Extração com dict
        dict_text = ""
        try:
            blocks = page.get_text("dict")
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            dict_text += span['text'] + " "
        except:
            dict_text = "Erro na extração dict"
        
        dict_chars = len(dict_text)
        dict_words = len(re.findall(r'\b\w+\b', dict_text.lower()))
        
        print(f"   Método 2 (dict): {dict_chars:,} chars, {dict_words:,} palavras")
        
        # Método 3: Extração com HTML
        html_text = ""
        try:
            html_raw = page.get_text("html")
            html_text = re.sub(r'<[^>]+>', '', html_raw)
        except:
            html_text = "Erro na extração HTML"
        
        html_chars = len(html_text)
        html_words = len(re.findall(r'\b\w+\b', html_text.lower()))
        
        print(f"   Método 3 (HTML): {html_chars:,} chars, {html_words:,} palavras")
        
        # Mostrar amostra do melhor método
        best_method = "simple"
        best_text = simple_text
        best_chars = simple_chars
        
        if dict_chars > simple_chars:
            best_method = "dict"
            best_text = dict_text
            best_chars = dict_chars
        
        if html_chars > best_chars:
            best_method = "HTML"
            best_text = html_text
            best_chars = html_chars
        
        print(f"   🎯 Melhor método: {best_method}")
        print(f"   📝 Amostra (primeiros 200 chars):")
        print(f"      {best_text[:200]}...")
        
        # Analisar qualidade do texto
        analyze_text_quality(best_text, f"Página {page_num + 1}")
        
        total_chars += best_chars
        total_words += dict_words  # Usar dict_words como base
    
    doc.close()
    
    print(f"\n📊 RESUMO DA EXTRAÇÃO:")
    print(f"   Total de caracteres: {total_chars:,}")
    print(f"   Total de palavras: {total_words:,}")
    
    # Comparar com a conversão final
    final_md_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown/Mount St. Helens and Catastrophism.md"
    
    if Path(final_md_path).exists():
        with open(final_md_path, 'r', encoding='utf-8') as f:
            final_content = f.read()
        
        final_chars = len(final_content)
        final_words = len(re.findall(r'\b\w+\b', final_content.lower()))
        
        print(f"\n📈 COMPARAÇÃO COM CONVERSÃO FINAL:")
        print(f"   Extração: {total_chars:,} chars, {total_words:,} palavras")
        print(f"   Conversão final: {final_chars:,} chars, {final_words:,} palavras")
        print(f"   Perda na conversão: {(total_chars - final_chars):+,} chars ({(total_chars - final_chars)/total_chars*100:.1f}%)")
        print(f"   Perda de palavras: {(total_words - final_words):+,} palavras ({(total_words - final_words)/total_words*100:.1f}%)")

def analyze_text_quality(text, label):
    """Analisa a qualidade do texto extraído"""
    
    # Detectar problemas comuns
    issues = []
    
    # Verificar se há muitas quebras de linha
    lines = text.split('\n')
    if len(lines) > len(text) / 50:  # Muitas linhas para o tamanho do texto
        issues.append("Muitas quebras de linha")
    
    # Verificar se há palavras juntas sem espaço
    words_together = len(re.findall(r'[a-z][A-Z]', text))
    if words_together > len(text) / 100:
        issues.append(f"Muitas palavras juntas ({words_together})")
    
    # Verificar se há caracteres estranhos
    strange_chars = sum(1 for char in text if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
    if strange_chars > len(text) * 0.1:
        issues.append(f"Muitos caracteres estranhos ({strange_chars})")
    
    # Verificar se há frases quebradas
    sentences = re.split(r'[.!?]', text)
    broken_sentences = sum(1 for s in sentences if len(s.strip()) < 10 and len(s.strip()) > 0)
    if broken_sentences > len(sentences) * 0.2:
        issues.append("Muitas frases quebradas")
    
    if issues:
        print(f"   ⚠️ Problemas detectados: {', '.join(issues)}")
    else:
        print(f"   ✅ Qualidade do texto boa")

def analyze_specific_page():
    """Analisa uma página específica em detalhes"""
    
    pdf_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/Mount St. Helens and Catastrophism.pdf"
    
    print(f"\n🔍 ANÁLISE DETALHADA DA PÁGINA 3 (mais conteúdo)")
    print("="*60)
    
    doc = fitz.open(pdf_path)
    page = doc[2]  # Página 3 (índice 2)
    
    # Extrair usando dict para análise detalhada
    blocks = page.get_text("dict")
    
    print(f"📊 ESTRUTURA DA PÁGINA:")
    print(f"   Total de blocos: {len(blocks.get('blocks', []))}")
    
    block_count = 0
    text_accumulator = ""
    
    for block in blocks.get("blocks", []):
        block_count += 1
        
        if block.get("type") == 0:  # texto
            print(f"\n   📝 BLOCO {block_count} (texto):")
            
            for line in block.get("lines", []):
                line_text = ""
                for span in line["spans"]:
                    text = span['text']
                    size = span['size']
                    font = span['font']
                    
                    line_text += text
                    
                    if len(text.strip()) > 0:
                        print(f"      '{text}' (fonte: {font}, tamanho: {size})")
                
                text_accumulator += line_text + "\n"
        
        elif block.get("type") == 1:  # imagem
            print(f"\n   🖼️ BLOCO {block_count} (imagem)")
    
    doc.close()
    
    print(f"\n📝 TEXTO COMPLETO DA PÁGINA 3:")
    print("-" * 40)
    print(text_accumulator)
    print("-" * 40)

def propose_extraction_improvements():
    """Propõe melhorias para a extração de texto"""
    
    print(f"\n💡 PROPOSTA DE MELHORIAS PARA EXTRAÇÃO")
    print("="*60)
    
    print(f"\n🎯 PROBLEMAS IDENTIFICADOS:")
    print("1. Extração básica não preserva estrutura de parágrafos")
    print("2. Palavras ficam juntas sem espaços")
    print("3. Frases são quebradas desnecessariamente")
    print("4. Caracteres especiais não são tratados adequadamente")
    
    print(f"\n🔧 MELHORIAS PROPOSTAS:")
    print("1. Melhorar o algoritmo de junção de palavras")
    print("2. Implementar detecção inteligente de frases")
    print("3. Adicionar tratamento de caracteres especiais")
    print("4. Implementar preservação de estrutura de parágrafos")
    print("5. Adicionar fallback para diferentes métodos de extração")
    
    print(f"\n📋 PLANO DE IMPLEMENTAÇÃO:")
    print("1. Modificar TextExtractionStep para usar método dict como padrão")
    print("2. Implementar algoritmo de junção inteligente de spans")
    print("3. Adicionar limpeza de caracteres especiais")
    print("4. Testar com casos problemáticos específicos")
    print("5. Validar melhorias em conjunto completo")

def main():
    """Função principal"""
    print("🔬 ANÁLISE DO PROBLEMA DE EXTRAÇÃO DE TEXTO")
    print("="*60)
    
    # Análises
    analyze_extraction_problem()
    analyze_specific_page()
    propose_extraction_improvements()
    
    print(f"\n🎉 ANÁLISE CONCLUÍDA!")
    print("Próximo passo: Implementar melhorias na extração")

if __name__ == "__main__":
    main()

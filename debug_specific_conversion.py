#!/usr/bin/env python3
"""
Script para debug específico da conversão problemática
"""

import os
import sys
from pathlib import Path
import fitz
import re

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from converter.pipeline import ConversionPipeline

def analyze_pdf_detailed(pdf_path):
    """Análise detalhada do PDF"""
    print(f"🔍 ANÁLISE DETALHADA DO PDF: {Path(pdf_path).name}")
    print("="*60)
    
    doc = fitz.open(pdf_path)
    
    total_chars = 0
    total_words = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        text_dict = page.get_text("dict")
        
        chars = len(text)
        words = len(re.findall(r'\b\w+\b', text.lower()))
        
        total_chars += chars
        total_words += words
        
        print(f"\n📄 PÁGINA {page_num + 1}:")
        print(f"   Caracteres: {chars}")
        print(f"   Palavras: {words}")
        print(f"   Primeiros 200 chars: {text[:200]}...")
        
        # Analisar estrutura de blocos
        blocks = text_dict.get("blocks", [])
        text_blocks = 0
        image_blocks = 0
        
        for block in blocks:
            if block.get("type") == 0:  # texto
                text_blocks += 1
            elif block.get("type") == 1:  # imagem
                image_blocks += 1
        
        print(f"   Blocos de texto: {text_blocks}")
        print(f"   Blocos de imagem: {image_blocks}")
    
    total_pages = len(doc)
    doc.close()
    
    print(f"\n📊 RESUMO DO PDF:")
    print(f"   Total de páginas: {total_pages}")
    print(f"   Total de caracteres: {total_chars:,}")
    print(f"   Total de palavras: {total_words:,}")
    
    return total_chars, total_words

def analyze_markdown_detailed(markdown_path):
    """Análise detalhada do Markdown"""
    print(f"\n📝 ANÁLISE DETALHADA DO MARKDOWN: {Path(markdown_path).name}")
    print("="*60)
    
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    total_chars = len(content)
    total_words = len(re.findall(r'\b\w+\b', content.lower()))
    
    # Contar elementos
    titles = len([line for line in lines if line.strip().startswith('#')])
    empty_lines = len([line for line in lines if line.strip() == ''])
    non_empty_lines = len([line for line in lines if line.strip() != ''])
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   Total de caracteres: {total_chars:,}")
    print(f"   Total de palavras: {total_words:,}")
    print(f"   Total de linhas: {len(lines)}")
    print(f"   Linhas não vazias: {non_empty_lines}")
    print(f"   Linhas vazias: {empty_lines}")
    print(f"   Títulos: {titles}")
    print(f"   Taxa de linhas vazias: {empty_lines/len(lines)*100:.1f}%")
    
    # Mostrar amostra do conteúdo
    print(f"\n📄 AMOSTRA DO CONTEÚDO (primeiros 500 chars):")
    print("-" * 40)
    print(content[:500])
    print("-" * 40)
    
    # Problemas identificados
    issues = []
    
    if empty_lines > len(lines) * 0.3:
        issues.append("Muitas linhas vazias (>30%)")
    
    if titles < 3:
        issues.append("Poucos títulos (<3)")
    
    if total_words < 1000:
        issues.append("Muito pouco conteúdo (<1000 palavras)")
    
    # Caracteres estranhos
    strange_chars = sum(1 for char in content if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
    if strange_chars > len(content) * 0.05:
        issues.append(f"Muitos caracteres estranhos ({strange_chars})")
    
    if issues:
        print(f"\n⚠️ PROBLEMAS IDENTIFICADOS:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print(f"\n✅ Nenhum problema identificado")
    
    return total_chars, total_words, issues

def test_conversion_methods(pdf_path, output_dir):
    """Testa diferentes métodos de conversão"""
    print(f"\n🧪 TESTANDO DIFERENTES MÉTODOS DE CONVERSÃO")
    print("="*60)
    
    pipeline = ConversionPipeline(output_dir)
    
    # Forçar diferentes métodos
    methods = ['current', 'intelligent', 'structured', 'compact', 'clean', 'academic', 'minimal']
    
    results = {}
    
    for method in methods:
        print(f"\n🔬 Testando método: {method}")
        
        try:
            # Modificar temporariamente o método no pipeline
            # (Isso requer acesso aos dados internos do pipeline)
            
            # Por enquanto, vamos apenas converter normalmente
            output_path = pipeline.convert(pdf_path)
            
            # Analisar resultado
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chars = len(content)
            words = len(re.findall(r'\b\w+\b', content.lower()))
            lines = len(content.split('\n'))
            
            results[method] = {
                'chars': chars,
                'words': words,
                'lines': lines,
                'quality_score': _calculate_quality_score(content)
            }
            
            print(f"   Caracteres: {chars:,}")
            print(f"   Palavras: {words:,}")
            print(f"   Linhas: {lines}")
            print(f"   Score: {results[method]['quality_score']:.2f}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results[method] = None
    
    return results

def _calculate_quality_score(content):
    """Calcula um score de qualidade para o conteúdo"""
    lines = content.split('\n')
    
    score = 0
    
    # Pontos por títulos
    titles = len([line for line in lines if line.strip().startswith('#')])
    score += titles * 2
    
    # Pontos por conteúdo
    words = len(re.findall(r'\b\w+\b', content.lower()))
    if words > 500:
        score += 10
    elif words > 100:
        score += 5
    else:
        score += 1
    
    # Penalidade por linhas vazias excessivas
    empty_lines = len([line for line in lines if line.strip() == ''])
    empty_ratio = empty_lines / len(lines) if lines else 0
    
    if empty_ratio > 0.3:
        score -= 5
    elif empty_ratio > 0.2:
        score -= 2
    
    return score

def suggest_improvements(pdf_chars, pdf_words, md_chars, md_words, issues):
    """Sugere melhorias baseadas na análise"""
    print(f"\n💡 SUGESTÕES DE MELHORIA")
    print("="*60)
    
    # Calcular taxas de preservação
    char_preservation = md_chars / pdf_chars if pdf_chars > 0 else 0
    word_preservation = md_words / pdf_words if pdf_words > 0 else 0
    
    print(f"📉 TAXAS DE PRESERVAÇÃO:")
    print(f"   Caracteres: {char_preservation:.2%}")
    print(f"   Palavras: {word_preservation:.2%}")
    
    suggestions = []
    
    if char_preservation < 0.5:
        suggestions.append("• A perda de conteúdo é significativa (>50%). Verificar se o PDF tem texto extraível ou se há problemas de OCR")
    
    if word_preservation < 0.5:
        suggestions.append("• A perda de palavras é significativa. Considerar uso de OCR ou métodos alternativos de extração")
    
    if "Muitas linhas vazias" in issues:
        suggestions.append("• Implementar algoritmo para reduzir quebras de linha desnecessárias")
        suggestions.append("• Melhorar lógica de agrupamento de parágrafos")
    
    if "Poucos títulos" in issues:
        suggestions.append("• Implementar detecção automática de títulos baseada em tamanho de fonte")
        suggestions.append("• Adicionar padrões de reconhecimento de cabeçalhos")
    
    if "Muitos caracteres estranhos" in issues:
        suggestions.append("• Melhorar algoritmo de limpeza de caracteres")
        suggestions.append("• Implementar detecção e substituição de caracteres corrompidos")
    
    if not suggestions:
        suggestions.append("• A conversão parece estar funcionando bem!")
    
    for suggestion in suggestions:
        print(suggestion)

def main():
    """Função principal"""
    # Arquivo problemático
    pdf_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/Mount St. Helens and Catastrophism.pdf"
    markdown_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown/Mount St. Helens and Catastrophism.md"
    output_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF não encontrado: {pdf_path}")
        return
    
    if not Path(markdown_path).exists():
        print(f"❌ Markdown não encontrado: {markdown_path}")
        return
    
    # Análises
    pdf_chars, pdf_words = analyze_pdf_detailed(pdf_path)
    md_chars, md_words, issues = analyze_markdown_detailed(markdown_path)
    
    # Sugestões
    suggest_improvements(pdf_chars, pdf_words, md_chars, md_words, issues)

if __name__ == "__main__":
    main()

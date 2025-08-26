#!/usr/bin/env python3
"""
Análise e conversão direta dos 5 piores casos
"""

import os
import json
import fitz
import re
from pathlib import Path
from collections import defaultdict
from converter.pipeline import ConversionPipeline

# Configurações
PDF_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
MARKDOWN_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"

# Os 5 piores casos identificados
WORST_CASES = [
    "181014cronologia_ap.pdf",  # Score: 3/10 - Preservação: 305.8%
    "Shoreline Transgressive Terraces.pdf",  # Score: 4/10 - Preservação: 101.1%
    "Biostratigraphic Continuity and Earth History.pdf",  # Score: 4/10 - Preservação: 106.2%
    "coming-to-grips-with-genesis-ch6.pdf",  # Score: 4/10 - Preservação: 96.0%
    "Dark Matter and Dark Energy.pdf"  # Score: 4/10 - Preservação: 100.0%
]

def analyze_pdf_structure_detailed(pdf_path):
    """Análise detalhada da estrutura do PDF"""
    doc = fitz.open(pdf_path)
    
    analysis = {
        'total_pages': len(doc),
        'page_analysis': [],
        'text_blocks': [],
        'font_analysis': defaultdict(int),
        'line_analysis': {'total_lines': 0, 'empty_lines': 0, 'avg_line_length': 0},
        'total_chars': 0,
        'total_words': 0
    }
    
    total_lines = 0
    empty_lines = 0
    line_lengths = []
    all_text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")
        
        page_analysis = {
            'page': page_num + 1,
            'blocks': len(blocks['blocks']),
            'text_blocks': 0,
            'image_blocks': 0,
            'text_content': '',
            'lines': []
        }
        
        for block in blocks['blocks']:
            if 'lines' in block:  # Text block
                page_analysis['text_blocks'] += 1
                
                for line in block['lines']:
                    line_text = ''
                    for span in line['spans']:
                        text = span['text'].strip()
                        if text:
                            line_text += text + ' '
                            analysis['font_analysis'][span['font']] += 1
                    
                    line_text = line_text.strip()
                    page_analysis['lines'].append({
                        'text': line_text,
                        'length': len(line_text),
                        'is_empty': len(line_text) == 0
                    })
                    
                    if line_text:
                        page_analysis['text_content'] += line_text + '\n'
                        all_text += line_text + ' '
                        total_lines += 1
                        line_lengths.append(len(line_text))
                    else:
                        empty_lines += 1
                        
            elif 'width' in block and 'height' in block:  # Image block
                page_analysis['image_blocks'] += 1
        
        analysis['page_analysis'].append(page_analysis)
    
    # Calcular estatísticas de texto
    analysis['total_chars'] = len(all_text)
    analysis['total_words'] = len(all_text.split())
    
    analysis['line_analysis'] = {
        'total_lines': total_lines,
        'empty_lines': empty_lines,
        'avg_line_length': sum(line_lengths) / len(line_lengths) if line_lengths else 0,
        'line_density': total_lines / (total_lines + empty_lines) if (total_lines + empty_lines) > 0 else 0
    }
    
    doc.close()
    return analysis

def analyze_markdown_quality_detailed(md_path):
    """Análise detalhada da qualidade do Markdown"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return {'error': 'Arquivo não encontrado'}
    
    lines = content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    analysis = {
        'total_lines': len(lines),
        'non_empty_lines': len(non_empty_lines),
        'empty_lines': len(lines) - len(non_empty_lines),
        'content_density': len(non_empty_lines) / len(lines) if lines else 0,
        'avg_line_length': sum(len(line) for line in non_empty_lines) / len(non_empty_lines) if non_empty_lines else 0,
        'total_chars': len(content),
        'total_words': len(content.split()),
        
        # Análise de estrutura
        'headers': len(re.findall(r'^#{1,6}\s', content, re.MULTILINE)),
        'paragraphs': len(re.findall(r'\n\n', content)),
        'lists': len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE)),
        
        # Problemas detectados
        'problems': []
    }
    
    # Detectar problemas específicos
    if analysis['content_density'] < 0.3:
        analysis['problems'].append(f"Baixa densidade de conteúdo: {analysis['content_density']:.2%}")
    
    if analysis['content_density'] > 0.9:
        analysis['problems'].append(f"Densidade muito alta (possível problema): {analysis['content_density']:.2%}")
    
    # Verificar repetições excessivas
    lines_text = ' '.join(non_empty_lines)
    words = lines_text.split()
    if len(words) > 100:  # Só analisar se houver conteúdo suficiente
        word_freq = defaultdict(int)
        for word in words:
            word_freq[word.lower()] += 1
        
        repeated_words = [(word, count) for word, count in word_freq.items() if count > 20]
        if repeated_words:
            analysis['problems'].append(f"Palavras muito repetidas: {len(repeated_words)} (máx: {max(count for _, count in repeated_words)})")
    
    # Verificar quebras de linha excessivas
    consecutive_empty = 0
    max_empty = 0
    for line in lines:
        if not line.strip():
            consecutive_empty += 1
            max_empty = max(max_empty, consecutive_empty)
        else:
            consecutive_empty = 0
    
    if max_empty > 3:
        analysis['problems'].append(f"Muitas linhas vazias consecutivas: {max_empty}")
    
    # Verificar preservação excessiva (>100% pode indicar duplicação)
    if 'total_chars' in analysis and analysis['total_chars'] > 0:
        char_density = len(lines_text) / analysis['total_chars']
        if char_density > 1.5:
            analysis['problems'].append(f"Possível duplicação de conteúdo: densidade de caracteres {char_density:.2f}")
    
    return analysis

def main():
    print("🔍 ANÁLISE E CONVERSÃO DIRETA DOS 5 PIORES CASOS")
    print("=" * 60)
    
    # Criar pipeline
    pipeline = ConversionPipeline(str(Path(MARKDOWN_DIR)))
    
    results = {}
    
    for pdf_name in WORST_CASES:
        print(f"\n📄 ANALISANDO: {pdf_name}")
        print("-" * 40)
        
        pdf_path = Path(PDF_DIR) / pdf_name
        md_path = Path(MARKDOWN_DIR) / f"{pdf_name.replace('.pdf', '.md')}"
        
        if not pdf_path.exists():
            print(f"❌ PDF não encontrado: {pdf_path}")
            continue
        
        # 1. Análise do PDF original
        print("📊 Analisando estrutura do PDF...")
        pdf_analysis = analyze_pdf_structure_detailed(pdf_path)
        
        print(f"   📄 Páginas: {pdf_analysis['total_pages']}")
        print(f"   📝 Linhas totais: {pdf_analysis['line_analysis']['total_lines']}")
        print(f"   📊 Linhas vazias: {pdf_analysis['line_analysis']['empty_lines']}")
        print(f"   📈 Densidade: {pdf_analysis['line_analysis']['line_density']:.3f}")
        print(f"   📏 Comprimento médio: {pdf_analysis['line_analysis']['avg_line_length']:.1f}")
        print(f"   🔢 Caracteres: {pdf_analysis['total_chars']:,}")
        print(f"   📚 Palavras: {pdf_analysis['total_words']:,}")
        
        # 2. Conversão para Markdown (sobrescrevendo)
        print("\n🔄 Convertendo para Markdown...")
        try:
            output_filename = f"{pdf_name.replace('.pdf', '.md')}"
            output_path = pipeline.convert(str(pdf_path), output_filename)
            print(f"   ✅ Conversão concluída: {output_path}")
            
            # 3. Análise do Markdown convertido
            print("\n📝 Analisando Markdown convertido...")
            md_analysis = analyze_markdown_quality_detailed(output_path)
            
            if 'error' not in md_analysis:
                print(f"   📊 Linhas totais: {md_analysis['total_lines']}")
                print(f"   📝 Linhas com conteúdo: {md_analysis['non_empty_lines']}")
                print(f"   📈 Densidade: {md_analysis['content_density']:.3f}")
                print(f"   📏 Comprimento médio: {md_analysis['avg_line_length']:.1f}")
                print(f"   🔢 Caracteres: {md_analysis['total_chars']:,}")
                print(f"   📚 Palavras: {md_analysis['total_words']:,}")
                print(f"   🏷️ Headers: {md_analysis['headers']}")
                print(f"   📋 Listas: {md_analysis['lists']}")
                
                # Calcular preservação
                char_preservation = md_analysis['total_chars'] / pdf_analysis['total_chars'] * 100
                word_preservation = md_analysis['total_words'] / pdf_analysis['total_words'] * 100
                
                print(f"   📈 Preservação de caracteres: {char_preservation:.1f}%")
                print(f"   📚 Preservação de palavras: {word_preservation:.1f}%")
                
                if md_analysis['problems']:
                    print(f"   ⚠️ Problemas detectados:")
                    for problem in md_analysis['problems']:
                        print(f"      - {problem}")
                
                # 4. Análise do Markdown original (se existir)
                if md_path.exists():
                    print("\n📄 Analisando Markdown original...")
                    original_analysis = analyze_markdown_quality_detailed(md_path)
                    
                    if 'error' not in original_analysis:
                        print(f"   📈 Densidade original: {original_analysis['content_density']:.3f}")
                        print(f"   📊 Linhas originais: {original_analysis['non_empty_lines']}")
                        
                        improvement = md_analysis['content_density'] - original_analysis['content_density']
                        print(f"   🔄 Mudança na densidade: {improvement:+.3f}")
                        
                        if improvement > 0.1:
                            print(f"   🚀 MELHORIA SIGNIFICATIVA DETECTADA!")
                
                results[pdf_name] = {
                    'pdf': pdf_analysis,
                    'markdown': md_analysis,
                    'char_preservation': char_preservation,
                    'word_preservation': word_preservation
                }
            else:
                print(f"   ❌ Erro: {md_analysis['error']}")
                
        except Exception as e:
            print(f"   ❌ Erro na conversão: {e}")
    
    # 5. Análise geral dos problemas
    print("\n🎯 ANÁLISE GERAL DOS PROBLEMAS")
    print("=" * 60)
    
    if results:
        common_issues = defaultdict(int)
        preservation_stats = []
        
        for pdf_name, result in results.items():
            if 'markdown' in result:
                for problem in result['markdown']['problems']:
                    common_issues[problem] += 1
                
                preservation_stats.append({
                    'file': pdf_name,
                    'char_preservation': result['char_preservation'],
                    'word_preservation': result['word_preservation'],
                    'density': result['markdown']['content_density']
                })
        
        print("📊 Problemas mais comuns:")
        for problem, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {problem}: {count} arquivos")
        
        print("\n📈 Estatísticas de preservação:")
        for stat in preservation_stats:
            status = "⚠️ ALTO" if stat['char_preservation'] > 120 else "✅ NORMAL" if stat['char_preservation'] >= 80 else "❌ BAIXO"
            print(f"   {stat['file']}: {stat['char_preservation']:.1f}% chars, {stat['word_preservation']:.1f}% palavras, densidade {stat['density']:.3f} {status}")
    
    # Salvar análise detalhada
    output_file = "worst_cases_direct_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análise salva em: {output_file}")
    print("\n📁 Arquivos convertidos estão em:")
    print(f"   {MARKDOWN_DIR}")
    
    return results

if __name__ == "__main__":
    main()

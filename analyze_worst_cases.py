#!/usr/bin/env python3
"""
Análise detalhada dos 5 piores casos da validação
"""

import os
import json
import fitz
import re
from pathlib import Path
from collections import defaultdict

# Configurações
PDF_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
MARKDOWN_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
TEMP_DIR = "/tmp/validate_all_improvements"

# Os 5 piores casos identificados
WORST_CASES = [
    "181014cronologia_ap.pdf",  # Score: 3/10
    "Shoreline Transgressive Terraces.pdf",  # Score: 4/10
    "Biostratigraphic Continuity and Earth History.pdf",  # Score: 4/10
    "coming-to-grips-with-genesis-ch6.pdf",  # Score: 4/10
    "Dark Matter and Dark Energy.pdf"  # Score: 4/10
]

def analyze_pdf_structure_detailed(pdf_path):
    """Análise detalhada da estrutura do PDF"""
    doc = fitz.open(pdf_path)
    
    analysis = {
        'total_pages': len(doc),
        'page_analysis': [],
        'text_blocks': [],
        'font_analysis': defaultdict(int),
        'line_analysis': {'total_lines': 0, 'empty_lines': 0, 'avg_line_length': 0}
    }
    
    total_lines = 0
    empty_lines = 0
    line_lengths = []
    
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
                        total_lines += 1
                        line_lengths.append(len(line_text))
                    else:
                        empty_lines += 1
                        
            elif 'width' in block and 'height' in block:  # Image block
                page_analysis['image_blocks'] += 1
        
        analysis['page_analysis'].append(page_analysis)
    
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
    
    # Verificar repetições excessivas
    lines_text = ' '.join(non_empty_lines)
    words = lines_text.split()
    if len(words) > 100:  # Só analisar se houver conteúdo suficiente
        word_freq = defaultdict(int)
        for word in words:
            word_freq[word.lower()] += 1
        
        repeated_words = [(word, count) for word, count in word_freq.items() if count > 10]
        if repeated_words:
            analysis['problems'].append(f"Palavras muito repetidas: {len(repeated_words)}")
    
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
    
    return analysis

def compare_pdf_markdown(pdf_analysis, md_analysis):
    """Comparação detalhada entre PDF e Markdown"""
    comparison = {
        'content_preservation': {
            'pdf_lines': pdf_analysis['line_analysis']['total_lines'],
            'md_lines': md_analysis['non_empty_lines'],
            'preservation_rate': md_analysis['non_empty_lines'] / pdf_analysis['line_analysis']['total_lines'] * 100 if pdf_analysis['line_analysis']['total_lines'] > 0 else 0
        },
        'density_comparison': {
            'pdf_density': pdf_analysis['line_analysis']['line_density'],
            'md_density': md_analysis['content_density'],
            'density_loss': pdf_analysis['line_analysis']['line_density'] - md_analysis['content_density']
        },
        'structure_analysis': {
            'pdf_avg_line_length': pdf_analysis['line_analysis']['avg_line_length'],
            'md_avg_line_length': md_analysis['avg_line_length'],
            'line_length_change': md_analysis['avg_line_length'] - pdf_analysis['line_analysis']['avg_line_length']
        }
    }
    
    return comparison

def main():
    print("🔍 ANÁLISE DETALHADA DOS 5 PIORES CASOS")
    print("=" * 60)
    
    results = {}
    
    for pdf_name in WORST_CASES:
        print(f"\n📄 ANALISANDO: {pdf_name}")
        print("-" * 40)
        
        pdf_path = Path(PDF_DIR) / pdf_name
        md_path = Path(MARKDOWN_DIR) / f"{pdf_name.replace('.pdf', '.md')}"
        improved_md_path = Path(TEMP_DIR) / f"improved_{pdf_name.replace('.pdf', '.md')}"
        
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
        
        # 2. Análise do Markdown melhorado
        print("\n📝 Analisando Markdown melhorado...")
        if improved_md_path.exists():
            md_analysis = analyze_markdown_quality_detailed(improved_md_path)
            
            if 'error' not in md_analysis:
                print(f"   📊 Linhas totais: {md_analysis['total_lines']}")
                print(f"   📝 Linhas com conteúdo: {md_analysis['non_empty_lines']}")
                print(f"   📈 Densidade: {md_analysis['content_density']:.3f}")
                print(f"   📏 Comprimento médio: {md_analysis['avg_line_length']:.1f}")
                print(f"   🏷️ Headers: {md_analysis['headers']}")
                print(f"   📋 Listas: {md_analysis['lists']}")
                
                if md_analysis['problems']:
                    print(f"   ⚠️ Problemas detectados:")
                    for problem in md_analysis['problems']:
                        print(f"      - {problem}")
                
                # 3. Comparação
                comparison = compare_pdf_markdown(pdf_analysis, md_analysis)
                print(f"\n📊 COMPARAÇÃO:")
                print(f"   📈 Taxa de preservação: {comparison['content_preservation']['preservation_rate']:.1f}%")
                print(f"   📉 Perda de densidade: {comparison['density_comparison']['density_loss']:.3f}")
                print(f"   📏 Mudança no comprimento: {comparison['structure_analysis']['line_length_change']:.1f}")
                
                results[pdf_name] = {
                    'pdf': pdf_analysis,
                    'markdown': md_analysis,
                    'comparison': comparison
                }
            else:
                print(f"   ❌ Erro: {md_analysis['error']}")
        else:
            print(f"   ❌ Markdown melhorado não encontrado: {improved_md_path}")
        
        # 4. Análise do Markdown original (se existir)
        if md_path.exists():
            print("\n📄 Analisando Markdown original...")
            original_analysis = analyze_markdown_quality_detailed(md_path)
            
            if 'error' not in original_analysis:
                print(f"   📈 Densidade original: {original_analysis['content_density']:.3f}")
                print(f"   📊 Linhas originais: {original_analysis['non_empty_lines']}")
                
                if pdf_name in results and 'markdown' in results[pdf_name]:
                    improvement = original_analysis['content_density'] - results[pdf_name]['markdown']['content_density']
                    print(f"   🔄 Mudança na densidade: {improvement:+.3f}")
    
    # 5. Análise geral dos problemas
    print("\n🎯 ANÁLISE GERAL DOS PROBLEMAS")
    print("=" * 60)
    
    common_issues = defaultdict(int)
    for pdf_name, result in results.items():
        if 'markdown' in result:
            for problem in result['markdown']['problems']:
                common_issues[problem] += 1
    
    print("📊 Problemas mais comuns:")
    for problem, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {problem}: {count} arquivos")
    
    # Salvar análise detalhada
    output_file = "worst_cases_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análise salva em: {output_file}")
    
    return results

if __name__ == "__main__":
    main()

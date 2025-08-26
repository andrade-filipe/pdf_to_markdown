#!/usr/bin/env python3
"""
Processamento Debug Simplificado de todos os 44 PDFs
"""

import os
import json
import time as time_module
from pathlib import Path
from datetime import datetime
from converter.pipeline import ConversionPipeline

# Configurações
PDF_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
MARKDOWN_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
DEBUG_OUTPUT_DIR = Path("debug_analysis")

# Criar diretório de debug
DEBUG_OUTPUT_DIR.mkdir(exist_ok=True)

def get_all_pdfs():
    """Obtém todos os PDFs do diretório"""
    pdf_files = list(Path(PDF_DIR).glob("*.pdf"))
    return sorted(pdf_files)

def analyze_extracted_data(raw_text):
    """Análise básica dos dados extraídos"""
    analysis = {
        'raw_text_length': len(raw_text),
        'text_lines': len(raw_text.split('\n')),
        'text_words': len(raw_text.split()),
        'issues': []
    }
    
    lines = raw_text.split('\n')
    
    # Problemas básicos
    empty_lines = len([l for l in lines if not l.strip()])
    empty_line_ratio = empty_lines / len(lines) if lines else 0
    if empty_line_ratio > 0.3:
        analysis['issues'].append(f"Muitas linhas vazias: {empty_line_ratio:.1%}")
    
    short_lines = len([l for l in lines if len(l.strip()) < 5 and l.strip()])
    if short_lines > len(lines) * 0.2:
        analysis['issues'].append(f"Muitas linhas curtas: {short_lines}")
    
    words = raw_text.split()
    word_freq = {}
    for word in words:
        word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
    
    max_repetitions = max(word_freq.values()) if word_freq else 0
    if max_repetitions > 100:
        analysis['issues'].append(f"Palavra muito repetida: {max_repetitions}x")
    
    if len(raw_text) < 1000:
        analysis['issues'].append(f"Texto muito pequeno: {len(raw_text)} chars")
    
    return analysis

def analyze_markdown_output(content):
    """Análise básica do output Markdown"""
    analysis = {
        'total_length': len(content),
        'total_lines': len(content.split('\n')),
        'content_lines': len([l for l in content.split('\n') if l.strip()]),
        'headers': len([l for l in content.split('\n') if l.strip().startswith('#')]),
        'issues': []
    }
    
    if analysis['headers'] == 0:
        analysis['issues'].append("Nenhum cabeçalho Markdown")
    
    density = analysis['content_lines'] / analysis['total_lines'] if analysis['total_lines'] > 0 else 0
    if density < 0.3:
        analysis['issues'].append(f"Baixa densidade: {density:.1%}")
    
    seen_lines = set()
    repeated_lines = 0
    for line in content.split('\n'):
        if line.strip():
            normalized = line.strip().lower()
            if normalized in seen_lines:
                repeated_lines += 1
            else:
                seen_lines.add(normalized)
    
    if repeated_lines > analysis['content_lines'] * 0.1:
        analysis['issues'].append(f"Linhas repetidas: {repeated_lines}")
    
    return analysis

def main():
    print("🔍 PROCESSAMENTO DEBUG SIMPLIFICADO - TODOS OS 44 PDFs")
    print("=" * 70)
    
    # Obter todos os PDFs
    pdf_files = get_all_pdfs()
    print(f"📚 Encontrados {len(pdf_files)} arquivos PDF")
    
    # Criar pipeline
    pipeline = ConversionPipeline(str(Path(MARKDOWN_DIR)))
    
    # Resultados
    all_results = []
    successful = 0
    failed = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        pdf_name = pdf_path.name
        print(f"\n📄 [{i}/{len(pdf_files)}] PROCESSANDO: {pdf_name}")
        
        try:
            # Converter PDF
            start_time = time_module.time()
            
            output_filename = f"{pdf_name.replace('.pdf', '.md')}"
            output_path = pipeline.convert(str(pdf_path), output_filename)
            
            conversion_time = time_module.time() - start_time
            
            print(f"   ✅ Conversão: {conversion_time:.2f}s")
            
            # Dados da conversão
            ocr_applied = pipeline.current_data.get('ocr_applied', False)
            ocr_pages = pipeline.current_data.get('ocr_pages_processed', 0)
            
            # Análise dados extraídos
            print("   🔍 Analisando dados extraídos...")
            raw_text = pipeline.current_data.get('raw_text', '')
            extracted_analysis = analyze_extracted_data(raw_text)
            
            print(f"      Texto: {extracted_analysis['raw_text_length']:,} chars")
            print(f"      Problemas extração: {len(extracted_analysis['issues'])}")
            
            # Análise Markdown
            print("   📝 Analisando Markdown...")
            with open(output_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            markdown_analysis = analyze_markdown_output(markdown_content)
            
            print(f"      Markdown: {markdown_analysis['total_length']:,} chars")
            print(f"      Problemas markdown: {len(markdown_analysis['issues'])}")
            
            # Calcular score
            extracted_score = max(0, 100 - len(extracted_analysis['issues']) * 25)
            markdown_score = max(0, 100 - len(markdown_analysis['issues']) * 25)
            total_score = (extracted_score + markdown_score) / 2
            
            # Status
            if total_score >= 80:
                status = "🏆 EXCELENTE"
            elif total_score >= 60:
                status = "✅ BOM"
            elif total_score >= 40:
                status = "⚠️ MODERADO"
            else:
                status = "❌ PROBLEMÁTICO"
            
            print(f"   🎯 Score: {total_score:.1f}/100 - {status}")
            
            # Adicionar resultado
            all_results.append({
                'pdf_name': pdf_name,
                'score': total_score,
                'extracted_issues': len(extracted_analysis['issues']),
                'markdown_issues': len(markdown_analysis['issues']),
                'ocr_applied': ocr_applied,
                'ocr_pages': ocr_pages,
                'conversion_time': conversion_time,
                'text_length': extracted_analysis['raw_text_length'],
                'markdown_length': markdown_analysis['total_length'],
                'extracted_problems': extracted_analysis['issues'],
                'markdown_problems': markdown_analysis['issues']
            })
            
            successful += 1
            
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            failed += 1
            
            all_results.append({
                'pdf_name': pdf_name,
                'score': 0,
                'error': str(e)
            })
    
    # Gerar relatório
    print(f"\n📊 RESUMO FINAL:")
    print(f"   PDFs processados: {len(pdf_files)}")
    print(f"   Conversões bem-sucedidas: {successful}")
    print(f"   Falhas: {failed}")
    
    if successful > 0:
        successful_scores = [r['score'] for r in all_results if r['score'] > 0]
        avg_score = sum(successful_scores) / len(successful_scores)
        
        excellent_count = len([r for r in all_results if r['score'] >= 80])
        good_count = len([r for r in all_results if 60 <= r['score'] < 80])
        moderate_count = len([r for r in all_results if 40 <= r['score'] < 60])
        poor_count = len([r for r in all_results if 0 < r['score'] < 40])
        
        print(f"   Score médio: {avg_score:.1f}/100")
        print(f"   Excelente: {excellent_count}")
        print(f"   Bom: {good_count}")
        print(f"   Moderado: {moderate_count}")
        print(f"   Problemático: {poor_count}")
        
        # Análise de problemas
        print(f"\n🔍 ANÁLISE DE PROBLEMAS:")
        
        # Problemas mais frequentes na extração
        all_extracted_problems = []
        for result in all_results:
            if 'extracted_problems' in result:
                all_extracted_problems.extend(result['extracted_problems'])
        
        from collections import Counter
        extracted_counter = Counter(all_extracted_problems)
        print(f"   Problemas na extração:")
        for problem, count in extracted_counter.most_common(3):
            print(f"     - {problem}: {count}x")
        
        # Problemas mais frequentes no Markdown
        all_markdown_problems = []
        for result in all_results:
            if 'markdown_problems' in result:
                all_markdown_problems.extend(result['markdown_problems'])
        
        markdown_counter = Counter(all_markdown_problems)
        print(f"   Problemas no Markdown:")
        for problem, count in markdown_counter.most_common(3):
            print(f"     - {problem}: {count}x")
    
    # Salvar resultados
    json_path = DEBUG_OUTPUT_DIR / "debug_simple_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {json_path}")

if __name__ == "__main__":
    main()

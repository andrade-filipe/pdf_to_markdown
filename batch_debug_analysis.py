#!/usr/bin/env python3
"""
Script de Debug e Análise em Lote - PDF to Markdown Converter
Analisa todos os 44 PDFs da pasta de referências e gera relatório detalhado
"""

import os
import sys
import json
import time
from pathlib import Path
from collections import defaultdict
import fitz  # PyMuPDF
import re
from datetime import datetime

# Adicionar o diretório atual ao path para importar o converter
sys.path.append(str(Path(__file__).parent))

from converter.pipeline import ConversionPipeline

# Configurações
PDF_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
MARKDOWN_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
OUTPUT_REPORT = "batch_analysis_report.json"

def analyze_pdf_structure(pdf_path):
    """Análise detalhada da estrutura do PDF"""
    try:
        doc = fitz.open(pdf_path)
        
        analysis = {
            'file_size_mb': os.path.getsize(pdf_path) / (1024 * 1024),
            'total_pages': len(doc),
            'total_words': 0,
            'total_images': 0,
            'text_blocks': 0,
            'font_info': defaultdict(int),
            'page_details': [],
            'potential_issues': [],
            'metadata': doc.metadata
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extrair texto com informações de fonte
            text_dict = page.get_text("dict")
            text_blocks = text_dict.get("blocks", [])
            
            page_words = 0
            page_images = 0
            page_fonts = defaultdict(int)
            
            for block in text_blocks:
                if block.get("type") == 0:  # texto
                    analysis['text_blocks'] += 1
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            font_name = span.get("font", "unknown")
                            font_size = span.get("size", 0)
                            
                            # Contar palavras
                            words = re.findall(r'\b\w+\b', text.lower())
                            page_words += len(words)
                            
                            # Registrar fonte
                            font_key = f"{font_name}_{font_size}"
                            page_fonts[font_key] += len(text)
                            
                            # Detectar potenciais títulos
                            if font_size > 12 and len(text.strip()) < 100:
                                analysis['potential_issues'].append(f"Página {page_num + 1}: Possível título: '{text.strip()}'")
                
                elif block.get("type") == 1:  # imagem
                    page_images += 1
            
            # Imagens da página
            images = page.get_images()
            page_images += len(images)
            
            page_detail = {
                'page': page_num + 1,
                'words': page_words,
                'images': page_images,
                'fonts': dict(page_fonts),
                'text_sample': page.get_text()[:300] + "..." if len(page.get_text()) > 300 else page.get_text()
            }
            
            analysis['page_details'].append(page_detail)
            analysis['total_words'] += page_words
            analysis['total_images'] += page_images
            
            # Atualizar font_info global
            for font, count in page_fonts.items():
                analysis['font_info'][font] += count
        
        doc.close()
        
        # Detectar problemas baseados no conteúdo
        if analysis['total_words'] < 100:
            analysis['potential_issues'].append("PDF com muito pouco texto")
        
        if analysis['total_pages'] > 50 and analysis['total_words'] < 5000:
            analysis['potential_issues'].append("PDF longo mas com pouco texto (possível problema de OCR)")
        
        return analysis
        
    except Exception as e:
        return {'error': str(e)}

def analyze_markdown_quality(markdown_path):
    """Análise detalhada da qualidade do Markdown"""
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        analysis = {
            'file_size_kb': os.path.getsize(markdown_path) / 1024,
            'total_lines': len(lines),
            'total_words': len(re.findall(r'\b\w+\b', content.lower())),
            'titles': {
                'h1': len([line for line in lines if line.strip().startswith('# ')]),
                'h2': len([line for line in lines if line.strip().startswith('## ')]),
                'h3': len([line for line in lines if line.strip().startswith('### ')]),
                'h4+': len([line for line in lines if line.strip().startswith('#### ')]),
            },
            'lists': {
                'unordered': len([line for line in lines if re.match(r'^\s*[-•*]\s', line)]),
                'ordered': len([line for line in lines if re.match(r'^\s*\d+\.\s', line)]),
            },
            'images': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)),
            'tables': len(re.findall(r'\|.*\|', content)),
            'code_blocks': len(re.findall(r'```[\w]*\n.*?\n```', content, re.DOTALL)),
            'links': len(re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)),
            'emphasis': {
                'bold': len(re.findall(r'\*\*([^*]+)\*\*', content)),
                'italic': len(re.findall(r'\*([^*]+)\*', content)),
                'code_inline': len(re.findall(r'`([^`]+)`', content)),
            },
            'quality_issues': [],
            'structure_score': 0
        }
        
        # Calcular score de estrutura
        structure_score = 0
        
        # Pontos por títulos bem estruturados
        if analysis['titles']['h1'] > 0:
            structure_score += 10
        if analysis['titles']['h2'] > 0:
            structure_score += 5
        if analysis['titles']['h2'] > 3:
            structure_score += 5
        
        # Pontos por listas
        if analysis['lists']['unordered'] > 0:
            structure_score += 3
        if analysis['lists']['ordered'] > 0:
            structure_score += 2
        
        # Pontos por imagens
        if analysis['images'] > 0:
            structure_score += 2
        
        # Pontos por tabelas
        if analysis['tables'] > 0:
            structure_score += 5
        
        # Pontos por formatação
        if analysis['emphasis']['bold'] > 0:
            structure_score += 1
        if analysis['emphasis']['italic'] > 0:
            structure_score += 1
        
        analysis['structure_score'] = structure_score
        
        # Detectar problemas
        if analysis['total_words'] < 50:
            analysis['quality_issues'].append("Muito pouco conteúdo")
        
        if analysis['titles']['h1'] == 0:
            analysis['quality_issues'].append("Sem títulos principais (H1)")
        
        # Verificar se há muitas quebras de linha desnecessárias
        empty_lines = len([line for line in lines if line.strip() == ''])
        if empty_lines > len(lines) * 0.3:
            analysis['quality_issues'].append("Muitas linhas vazias")
        
        # Verificar caracteres estranhos
        strange_chars = sum(1 for char in content if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
        if strange_chars > len(content) * 0.05:
            analysis['quality_issues'].append(f"Caracteres estranhos detectados ({strange_chars})")
        
        return analysis
        
    except Exception as e:
        return {'error': str(e)}

def compare_conversion_quality(pdf_analysis, markdown_analysis):
    """Compara a qualidade entre PDF original e Markdown convertido"""
    comparison = {
        'content_preservation': 0,
        'structure_improvement': 0,
        'overall_quality': 0,
        'issues': []
    }
    
    # Preservação de conteúdo
    pdf_words = pdf_analysis.get('total_words', 0)
    md_words = markdown_analysis.get('total_words', 0)
    
    if pdf_words > 0:
        content_ratio = md_words / pdf_words
        if content_ratio > 0.8:
            comparison['content_preservation'] = 10
        elif content_ratio > 0.6:
            comparison['content_preservation'] = 7
        elif content_ratio > 0.4:
            comparison['content_preservation'] = 4
        else:
            comparison['content_preservation'] = 1
            comparison['issues'].append(f"Perda significativa de conteúdo ({content_ratio:.2%})")
    
    # Melhoria de estrutura
    structure_score = markdown_analysis.get('structure_score', 0)
    if structure_score > 20:
        comparison['structure_improvement'] = 10
    elif structure_score > 15:
        comparison['structure_improvement'] = 8
    elif structure_score > 10:
        comparison['structure_improvement'] = 6
    elif structure_score > 5:
        comparison['structure_improvement'] = 4
    else:
        comparison['structure_improvement'] = 2
        comparison['issues'].append("Estrutura Markdown pobre")
    
    # Qualidade geral
    comparison['overall_quality'] = (comparison['content_preservation'] + comparison['structure_improvement']) / 2
    
    return comparison

def process_single_file(pdf_path, markdown_path, pipeline):
    """Processa um único arquivo PDF e analisa a conversão"""
    pdf_name = Path(pdf_path).name
    print(f"🔍 Analisando: {pdf_name}")
    
    result = {
        'pdf_name': pdf_name,
        'pdf_path': str(pdf_path),
        'markdown_path': str(markdown_path),
        'pdf_analysis': {},
        'markdown_analysis': {},
        'conversion_comparison': {},
        'processing_time': 0,
        'status': 'pending'
    }
    
    start_time = time.time()
    
    try:
        # 1. Analisar PDF original
        result['pdf_analysis'] = analyze_pdf_structure(pdf_path)
        
        # 2. Verificar se Markdown existe
        if not markdown_path.exists():
            print(f"  ⚠️  Markdown não encontrado, convertendo...")
            try:
                output_path = pipeline.convert(str(pdf_path))
                result['markdown_path'] = str(output_path)
            except Exception as e:
                result['status'] = 'conversion_error'
                result['error'] = str(e)
                return result
        
        # 3. Analisar Markdown convertido
        result['markdown_analysis'] = analyze_markdown_quality(markdown_path)
        
        # 4. Comparar qualidade
        result['conversion_comparison'] = compare_conversion_quality(
            result['pdf_analysis'], 
            result['markdown_analysis']
        )
        
        result['processing_time'] = time.time() - start_time
        result['status'] = 'success'
        
        print(f"  ✅ Concluído em {result['processing_time']:.2f}s")
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        result['processing_time'] = time.time() - start_time
        print(f"  ❌ Erro: {e}")
    
    return result

def generate_summary_report(all_results):
    """Gera relatório resumido de todos os resultados"""
    summary = {
        'total_files': len(all_results),
        'successful': len([r for r in all_results if r['status'] == 'success']),
        'errors': len([r for r in all_results if r['status'] == 'error']),
        'conversion_errors': len([r for r in all_results if r['status'] == 'conversion_error']),
        'average_quality': 0,
        'best_files': [],
        'worst_files': [],
        'common_issues': defaultdict(int),
        'size_distribution': {
            'small': 0,    # < 1MB
            'medium': 0,   # 1-10MB
            'large': 0     # > 10MB
        },
        'quality_distribution': {
            'excellent': 0,  # 9-10
            'good': 0,       # 7-8
            'fair': 0,       # 5-6
            'poor': 0        # < 5
        }
    }
    
    successful_results = [r for r in all_results if r['status'] == 'success']
    
    if successful_results:
        # Média de qualidade
        qualities = [r['conversion_comparison']['overall_quality'] for r in successful_results]
        summary['average_quality'] = sum(qualities) / len(qualities)
        
        # Melhores e piores arquivos
        best_worst = sorted(successful_results, 
                          key=lambda x: x['conversion_comparison']['overall_quality'], 
                          reverse=True)
        summary['best_files'] = [r['pdf_name'] for r in best_worst[:5]]
        summary['worst_files'] = [r['pdf_name'] for r in best_worst[-5:]]
        
        # Distribuição de qualidade
        for quality in qualities:
            if quality >= 9:
                summary['quality_distribution']['excellent'] += 1
            elif quality >= 7:
                summary['quality_distribution']['good'] += 1
            elif quality >= 5:
                summary['quality_distribution']['fair'] += 1
            else:
                summary['quality_distribution']['poor'] += 1
        
        # Distribuição de tamanho
        for result in successful_results:
            size_mb = result['pdf_analysis']['file_size_mb']
            if size_mb < 1:
                summary['size_distribution']['small'] += 1
            elif size_mb < 10:
                summary['size_distribution']['medium'] += 1
            else:
                summary['size_distribution']['large'] += 1
    
    # Problemas comuns
    for result in all_results:
        if result['status'] == 'success':
            for issue in result['conversion_comparison']['issues']:
                summary['common_issues'][issue] += 1
    
    return summary

def main():
    """Função principal"""
    print("🚀 INICIANDO ANÁLISE EM LOTE DE PDFs")
    print(f"📁 PDFs: {PDF_DIR}")
    print(f"📁 Markdown: {MARKDOWN_DIR}")
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Verificar diretórios
    pdf_dir = Path(PDF_DIR)
    markdown_dir = Path(MARKDOWN_DIR)
    
    if not pdf_dir.exists():
        print(f"❌ Diretório de PDFs não encontrado: {pdf_dir}")
        return
    
    if not markdown_dir.exists():
        print(f"❌ Diretório de Markdown não encontrado: {markdown_dir}")
        return
    
    # Listar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📊 Encontrados {len(pdf_files)} arquivos PDF")
    
    if not pdf_files:
        print("❌ Nenhum arquivo PDF encontrado")
        return
    
    # Criar pipeline
    pipeline = ConversionPipeline(str(markdown_dir))
    
    # Processar cada arquivo
    all_results = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] ", end="")
        
        # Determinar caminho do Markdown correspondente
        markdown_name = pdf_path.stem + ".md"
        markdown_path = markdown_dir / markdown_name
        
        # Processar arquivo
        result = process_single_file(pdf_path, markdown_path, pipeline)
        all_results.append(result)
    
    # Gerar relatório resumido
    print(f"\n{'='*80}")
    print("📋 GERANDO RELATÓRIO RESUMO")
    
    summary = generate_summary_report(all_results)
    
    # Exibir resumo
    print(f"\n📊 RESUMO DA ANÁLISE:")
    print(f"   Total de arquivos: {summary['total_files']}")
    print(f"   Sucessos: {summary['successful']}")
    print(f"   Erros: {summary['errors']}")
    print(f"   Erros de conversão: {summary['conversion_errors']}")
    print(f"   Qualidade média: {summary['average_quality']:.2f}/10")
    
    if summary['successful'] > 0:
        print(f"\n🏆 MELHORES CONVERSÕES:")
        for i, filename in enumerate(summary['best_files'], 1):
            print(f"   {i}. {filename}")
        
        print(f"\n⚠️  PIORES CONVERSÕES:")
        for i, filename in enumerate(summary['worst_files'], 1):
            print(f"   {i}. {filename}")
        
        print(f"\n📈 DISTRIBUIÇÃO DE QUALIDADE:")
        print(f"   Excelente (9-10): {summary['quality_distribution']['excellent']}")
        print(f"   Boa (7-8): {summary['quality_distribution']['good']}")
        print(f"   Regular (5-6): {summary['quality_distribution']['fair']}")
        print(f"   Pobre (<5): {summary['quality_distribution']['poor']}")
        
        print(f"\n📏 DISTRIBUIÇÃO DE TAMANHO:")
        print(f"   Pequeno (<1MB): {summary['size_distribution']['small']}")
        print(f"   Médio (1-10MB): {summary['size_distribution']['medium']}")
        print(f"   Grande (>10MB): {summary['size_distribution']['large']}")
    
    if summary['common_issues']:
        print(f"\n🚨 PROBLEMAS MAIS COMUNS:")
        for issue, count in sorted(summary['common_issues'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {issue}: {count} arquivos")
    
    # Salvar relatório completo
    full_report = {
        'summary': summary,
        'detailed_results': all_results,
        'timestamp': datetime.now().isoformat(),
        'pdf_directory': PDF_DIR,
        'markdown_directory': MARKDOWN_DIR
    }
    
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório completo salvo em: {OUTPUT_REPORT}")
    print(f"⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 ANÁLISE CONCLUÍDA!")

if __name__ == "__main__":
    main()

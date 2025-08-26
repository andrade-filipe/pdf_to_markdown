#!/usr/bin/env python3
"""
Script para validar todas as melhorias implementadas em todos os 44 PDFs
"""

import os
import sys
from pathlib import Path
import fitz
import re
import time
import json
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from converter.pipeline import ConversionPipeline

def validate_all_improvements():
    """Valida todas as melhorias em todos os 44 PDFs"""
    
    # Diretórios
    pdf_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
    original_md_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    test_output_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    
    print("🔬 VALIDAÇÃO COMPLETA DE TODAS AS MELHORIAS")
    print("="*60)
    print("✅ Conflito de processamento corrigido")
    print("✅ Métrica de densidade adicionada")
    print("✅ Extração de texto melhorada")
    print("✅ Otimização de parágrafos implementada")
    print("="*60)
    
    # Criar diretório de teste
    test_dir = Path(test_output_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Buscar todos os PDFs
    pdf_files = list(Path(pdf_dir).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ Nenhum PDF encontrado em {pdf_dir}")
        return False
    
    print(f"\n📄 ENCONTRADOS {len(pdf_files)} ARQUIVOS PDF")
    print("-" * 40)
    
    # Criar pipeline com melhorias
    pipeline = ConversionPipeline(str(test_dir))
    
    # Resultados
    results = []
    successful_conversions = 0
    failed_conversions = 0
    total_start_time = time.time()
    
    print(f"\n🚀 INICIANDO VALIDAÇÃO DE TODOS OS ARQUIVOS")
    print("-" * 40)
    
    for i, pdf_path in enumerate(pdf_files, 1):
        pdf_name = pdf_path.name
        original_md_path = Path(original_md_dir) / (pdf_name.replace('.pdf', '.md'))
        
        print(f"\n[{i:2d}/{len(pdf_files)}] Testando: {pdf_name}")
        
        try:
            # 1. Análise do PDF original
            pdf_info = analyze_pdf(pdf_path)
            
            # 2. Conversão com melhorias
            conversion_start = time.time()
            improved_md_path = pipeline.convert(str(pdf_path), f"improved_{pdf_name.replace('.pdf', '.md')}")
            conversion_time = time.time() - conversion_start
            
            # 3. Análise do resultado melhorado
            improved_info = analyze_markdown(improved_md_path)
            
            # 4. Calcular preservação em relação ao PDF original
            improved_char_preservation = improved_info['total_chars'] / pdf_info['total_chars'] * 100
            improved_word_preservation = improved_info['total_words'] / pdf_info['total_words'] * 100
            improved_info['preservation_rate'] = improved_char_preservation
            
            # 5. Comparação com conversão original (se existir)
            comparison_info = {}
            if original_md_path.exists():
                original_info = analyze_markdown(original_md_path)
                comparison_info = compare_conversions(improved_info, original_info, pdf_info)
            
            # 6. Avaliação da qualidade
            quality_score = evaluate_quality(improved_info, comparison_info)
            
            # 6. Coletar resultado
            result = {
                'filename': pdf_name,
                'pdf_info': pdf_info,
                'improved_info': improved_info,
                'comparison_info': comparison_info,
                'quality_score': quality_score,
                'conversion_time': conversion_time,
                'success': True
            }
            
            results.append(result)
            successful_conversions += 1
            
            # Exibir resumo
            print(f"   ✅ Conversão: {conversion_time:.2f}s")
            print(f"   📊 Preservação: {improved_info['preservation_rate']:.1f}%")
            print(f"   📈 Densidade: {improved_info['density']:.3f}")
            print(f"   🎯 Score: {quality_score}/10")
            
            if comparison_info:
                improvement = comparison_info.get('density_improvement', 0)
                if improvement > 0:
                    print(f"   🚀 Melhoria na densidade: {improvement:+.3f}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            failed_conversions += 1
            
            result = {
                'filename': pdf_name,
                'error': str(e),
                'success': False
            }
            results.append(result)
    
    total_time = time.time() - total_start_time
    
    # Gerar relatório completo
    generate_comprehensive_report(results, total_time, successful_conversions, failed_conversions, test_output_dir)
    
    return successful_conversions, failed_conversions

def analyze_pdf(pdf_path):
    """Analisa um PDF individual"""
    doc = fitz.open(pdf_path)
    
    # Extrair informações básicas
    total_chars = 0
    total_words = 0
    total_pages = len(doc)
    
    for page in doc:
        text = page.get_text()
        total_chars += len(text)
        total_words += len(re.findall(r'\b\w+\b', text.lower()))
    
    doc.close()
    
    return {
        'total_chars': total_chars,
        'total_words': total_words,
        'total_pages': total_pages,
        'avg_chars_per_page': total_chars / total_pages if total_pages > 0 else 0,
        'avg_words_per_page': total_words / total_pages if total_pages > 0 else 0
    }

def analyze_markdown(md_path):
    """Analisa um arquivo Markdown"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    words = re.findall(r'\b\w+\b', content.lower())
    
    # Calcular métricas
    total_lines = len(lines)
    empty_lines = len([line for line in lines if line.strip() == ''])
    content_lines = total_lines - empty_lines
    density = 1 - (empty_lines / total_lines) if total_lines > 0 else 0
    
    # Análise de qualidade do texto
    sample_text = content[:2000]  # Primeiros 2000 caracteres para análise
    words_together = len(re.findall(r'[a-z][A-Z]', sample_text))
    sentences = re.split(r'[.!?]', sample_text)
    broken_sentences = sum(1 for s in sentences if len(s.strip()) < 10 and len(s.strip()) > 0)
    
    # Parágrafos
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
    
    # Títulos
    titles = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    
    return {
        'total_chars': len(content),
        'total_words': len(words),
        'total_lines': total_lines,
        'empty_lines': empty_lines,
        'content_lines': content_lines,
        'density': density,
        'words_together': words_together,
        'broken_sentences': broken_sentences,
        'paragraphs_count': len(paragraphs),
        'avg_paragraph_length': avg_paragraph_length,
        'titles_count': len(titles),
        'preservation_rate': 0  # Será calculado na comparação
    }

def compare_conversions(improved_info, original_info, pdf_info):
    """Compara conversões melhorada vs original"""
    
    # Calcular taxas de preservação
    improved_char_preservation = improved_info['total_chars'] / pdf_info['total_chars'] * 100
    improved_word_preservation = improved_info['total_words'] / pdf_info['total_words'] * 100
    original_char_preservation = original_info['total_chars'] / pdf_info['total_chars'] * 100
    original_word_preservation = original_info['total_words'] / pdf_info['total_words'] * 100
    
    # Melhorias
    char_improvement = improved_char_preservation - original_char_preservation
    word_improvement = improved_word_preservation - original_word_preservation
    density_improvement = improved_info['density'] - original_info['density']
    
    # Redução de linhas vazias
    original_empty_rate = original_info['empty_lines'] / original_info['total_lines'] if original_info['total_lines'] > 0 else 0
    improved_empty_rate = improved_info['empty_lines'] / improved_info['total_lines'] if improved_info['total_lines'] > 0 else 0
    empty_line_improvement = original_empty_rate - improved_empty_rate
    
    # Melhoria na qualidade do texto
    text_quality_improvement = 0
    if original_info['words_together'] > improved_info['words_together']:
        text_quality_improvement += 1
    if original_info['broken_sentences'] > improved_info['broken_sentences']:
        text_quality_improvement += 1
    
    return {
        'improved_char_preservation': improved_char_preservation,
        'improved_word_preservation': improved_word_preservation,
        'original_char_preservation': original_char_preservation,
        'original_word_preservation': original_word_preservation,
        'char_improvement': char_improvement,
        'word_improvement': word_improvement,
        'density_improvement': density_improvement,
        'empty_line_improvement': empty_line_improvement * 100,  # Em percentual
        'text_quality_improvement': text_quality_improvement
    }

def evaluate_quality(improved_info, comparison_info):
    """Avalia a qualidade da conversão melhorada"""
    score = 0
    
    # Pontuação baseada na densidade
    if improved_info['density'] > 0.9:
        score += 3
    elif improved_info['density'] > 0.8:
        score += 2
    elif improved_info['density'] > 0.7:
        score += 1
    
    # Pontuação baseada na qualidade do texto
    if improved_info['words_together'] < 5:
        score += 2
    elif improved_info['words_together'] < 10:
        score += 1
    
    if improved_info['broken_sentences'] < 5:
        score += 2
    elif improved_info['broken_sentences'] < 10:
        score += 1
    
    # Pontuação baseada na estrutura
    if improved_info['avg_paragraph_length'] > 100:
        score += 1
    
    if improved_info['titles_count'] > 3:
        score += 1
    
    # Pontuação baseada em melhorias (se comparável)
    if comparison_info:
        if comparison_info.get('density_improvement', 0) > 0.05:
            score += 1
        if comparison_info.get('text_quality_improvement', 0) > 0:
            score += 1
    
    return min(score, 10)  # Máximo 10 pontos

def generate_comprehensive_report(results, total_time, successful_conversions, failed_conversions, output_dir):
    """Gera relatório abrangente dos resultados"""
    
    print(f"\n📊 RELATÓRIO COMPREENSIVO DE VALIDAÇÃO")
    print("="*60)
    
    # Estatísticas gerais
    total_files = len(results)
    success_rate = successful_conversions / total_files * 100
    
    print(f"📈 ESTATÍSTICAS GERAIS:")
    print(f"   Total de arquivos testados: {total_files}")
    print(f"   Conversões bem-sucedidas: {successful_conversions}")
    print(f"   Conversões falharam: {failed_conversions}")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    print(f"   Tempo total: {total_time:.2f}s")
    print(f"   Tempo médio por arquivo: {total_time/total_files:.2f}s")
    
    # Filtrar conversões bem-sucedidas
    successful_results = [r for r in results if r['success']]
    
    if not successful_results:
        print("❌ Nenhuma conversão bem-sucedida para análise")
        return
    
    # Análise de qualidade
    quality_scores = [r['quality_score'] for r in successful_results]
    avg_quality = sum(quality_scores) / len(quality_scores)
    
    densities = [r['improved_info']['density'] for r in successful_results]
    avg_density = sum(densities) / len(densities)
    
    conversion_times = [r['conversion_time'] for r in successful_results]
    avg_conversion_time = sum(conversion_times) / len(conversion_times)
    
    print(f"\n🎯 ANÁLISE DE QUALIDADE:")
    print(f"   Score médio de qualidade: {avg_quality:.2f}/10")
    print(f"   Densidade média: {avg_density:.3f}")
    print(f"   Tempo médio de conversão: {avg_conversion_time:.2f}s")
    
    # Análise de melhorias (se houver comparações)
    comparisons = [r for r in successful_results if r['comparison_info']]
    
    if comparisons:
        density_improvements = [r['comparison_info']['density_improvement'] for r in comparisons]
        avg_density_improvement = sum(density_improvements) / len(density_improvements)
        
        improved_files = sum(1 for r in comparisons if r['comparison_info']['density_improvement'] > 0)
        improvement_rate = improved_files / len(comparisons) * 100
        
        print(f"\n🚀 ANÁLISE DE MELHORIAS:")
        print(f"   Arquivos com melhorias na densidade: {improved_files}/{len(comparisons)}")
        print(f"   Taxa de melhoria: {improvement_rate:.1f}%")
        print(f"   Melhoria média na densidade: {avg_density_improvement:+.3f}")
    
    # Melhores e piores casos
    print(f"\n🏆 MELHORES CASOS (Top 5):")
    successful_results.sort(key=lambda x: x['quality_score'], reverse=True)
    for i, result in enumerate(successful_results[:5]):
        print(f"   {i+1}. {result['filename']} - Score: {result['quality_score']}/10")
    
    print(f"\n⚠️ PIORES CASOS (Bottom 5):")
    for i, result in enumerate(successful_results[-5:]):
        print(f"   {i+1}. {result['filename']} - Score: {result['quality_score']}/10")
    
    # Casos problemáticos (se houver)
    failed_results = [r for r in results if not r['success']]
    if failed_results:
        print(f"\n❌ CASOS PROBLEMÁTICOS:")
        for result in failed_results:
            print(f"   - {result['filename']}: {result['error']}")
    
    # Salvar relatório JSON
    report_path = Path(output_dir) / "validation_report.json"
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files': total_files,
            'successful_conversions': successful_conversions,
            'failed_conversions': failed_conversions,
            'success_rate': success_rate,
            'total_time': total_time,
            'avg_conversion_time': total_time/total_files if total_files > 0 else 0,
            'avg_quality_score': avg_quality,
            'avg_density': avg_density
        },
        'results': results
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {report_path}")
    
    # Avaliação final
    print(f"\n🎯 AVALIAÇÃO FINAL:")
    if success_rate >= 95 and avg_quality >= 7:
        print("🏆 EXCELENTE: Melhorias validadas com sucesso!")
        print("✅ Sistema pronto para uso em produção")
    elif success_rate >= 90 and avg_quality >= 6:
        print("👍 BOM: Melhorias funcionando bem")
        print("✅ Sistema funcional com pequenos ajustes")
    elif success_rate >= 80:
        print("⚠️ MODERADO: Alguns problemas identificados")
        print("🔧 Requer ajustes antes do uso em produção")
    else:
        print("❌ PROBLEMÁTICO: Muitas falhas")
        print("🔧 Requer revisão significativa")

def main():
    """Função principal"""
    print("🔬 VALIDAÇÃO COMPLETA DE MELHORIAS - PDF TO MARKDOWN CONVERTER")
    print("="*60)
    
    # Executar validação
    successful, failed = validate_all_improvements()
    
    if successful > 0:
        print(f"\n✅ VALIDAÇÃO CONCLUÍDA!")
        print(f"Sucessos: {successful}, Falhas: {failed}")
    else:
        print(f"\n❌ VALIDAÇÃO FALHOU!")
        print("Nenhuma conversão bem-sucedida")

if __name__ == "__main__":
    main()

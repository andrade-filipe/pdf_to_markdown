#!/usr/bin/env python3
"""
Script para analisar os resultados do batch_analysis_report.json
"""

import json
from pathlib import Path

def load_report():
    """Carrega o relatório de análise"""
    with open('batch_analysis_report.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_worst_conversions(report):
    """Analisa as piores conversões para identificar problemas"""
    print("🔍 ANÁLISE DAS PIORES CONVERSÕES")
    print("="*50)
    
    worst_files = report['summary']['worst_files']
    detailed_results = {r['pdf_name']: r for r in report['detailed_results']}
    
    for filename in worst_files:
        if filename in detailed_results:
            result = detailed_results[filename]
            print(f"\n📄 {filename}")
            print(f"   Qualidade: {result['conversion_comparison']['overall_quality']:.2f}/10")
            print(f"   Preservação: {result['conversion_comparison']['content_preservation']}/10")
            print(f"   Estrutura: {result['conversion_comparison']['structure_improvement']}/10")
            
            if result['conversion_comparison']['issues']:
                print(f"   Problemas: {', '.join(result['conversion_comparison']['issues'])}")
            
            # Informações do PDF
            pdf_analysis = result['pdf_analysis']
            print(f"   PDF: {pdf_analysis['total_pages']} páginas, {pdf_analysis['total_words']} palavras")
            
            # Informações do Markdown
            md_analysis = result['markdown_analysis']
            print(f"   Markdown: {md_analysis['total_words']} palavras, {md_analysis['structure_score']} pontos de estrutura")
            
            if md_analysis['quality_issues']:
                print(f"   Issues Markdown: {', '.join(md_analysis['quality_issues'])}")

def analyze_common_issues(report):
    """Analisa os problemas mais comuns"""
    print("\n🚨 PROBLEMAS MAIS COMUNS")
    print("="*50)
    
    common_issues = report['summary']['common_issues']
    
    if common_issues:
        for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / report['summary']['total_files']) * 100
            print(f"   {issue}: {count} arquivos ({percentage:.1f}%)")
    else:
        print("   Nenhum problema comum identificado!")

def analyze_quality_distribution(report):
    """Analisa a distribuição de qualidade"""
    print("\n📈 ANÁLISE DE QUALIDADE")
    print("="*50)
    
    dist = report['summary']['quality_distribution']
    total = report['summary']['total_files']
    
    print(f"   Total de arquivos: {total}")
    print(f"   Excelente (9-10): {dist['excellent']} ({dist['excellent']/total*100:.1f}%)")
    print(f"   Boa (7-8): {dist['good']} ({dist['good']/total*100:.1f}%)")
    print(f"   Regular (5-6): {dist['fair']} ({dist['fair']/total*100:.1f}%)")
    print(f"   Pobre (<5): {dist['poor']} ({dist['poor']/total*100:.1f}%)")
    print(f"   Qualidade média: {report['summary']['average_quality']:.2f}/10")

def find_specific_problems(report):
    """Encontra problemas específicos nos arquivos"""
    print("\n🔍 PROBLEMAS ESPECÍFICOS IDENTIFICADOS")
    print("="*50)
    
    detailed_results = report['detailed_results']
    
    # Problemas de preservação de conteúdo
    content_loss = [r for r in detailed_results 
                   if r['conversion_comparison']['content_preservation'] < 5]
    
    if content_loss:
        print(f"\n📉 PERDA SIGNIFICATIVA DE CONTEÚDO ({len(content_loss)} arquivos):")
        for result in content_loss:
            issues = result['conversion_comparison']['issues']
            content_issues = [i for i in issues if 'Perda significativa' in i]
            if content_issues:
                print(f"   {result['pdf_name']}: {content_issues[0]}")
    
    # Problemas de estrutura
    structure_problems = [r for r in detailed_results 
                         if r['conversion_comparison']['structure_improvement'] < 4]
    
    if structure_problems:
        print(f"\n🏗️ PROBLEMAS DE ESTRUTURA ({len(structure_problems)} arquivos):")
        for result in structure_problems:
            print(f"   {result['pdf_name']}: Score {result['conversion_comparison']['structure_improvement']}/10")
    
    # Caracteres estranhos
    strange_chars = [r for r in detailed_results 
                    if 'Caracteres estranhos' in ' '.join(r['markdown_analysis']['quality_issues'])]
    
    if strange_chars:
        print(f"\n🔤 CARACTERES ESTRANHOS ({len(strange_chars)} arquivos):")
        for result in strange_chars:
            print(f"   {result['pdf_name']}")

def analyze_performance(report):
    """Analisa performance e tempos de processamento"""
    print("\n⚡ ANÁLISE DE PERFORMANCE")
    print("="*50)
    
    detailed_results = report['detailed_results']
    
    # Tempos de processamento
    times = [r['processing_time'] for r in detailed_results]
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"   Tempo médio: {avg_time:.2f}s")
    print(f"   Tempo máximo: {max_time:.2f}s")
    print(f"   Tempo mínimo: {min_time:.2f}s")
    
    # Arquivos mais lentos
    slow_files = sorted(detailed_results, key=lambda x: x['processing_time'], reverse=True)[:5]
    print(f"\n🐌 ARQUIVOS MAIS LENTOS:")
    for result in slow_files:
        print(f"   {result['pdf_name']}: {result['processing_time']:.2f}s")

def main():
    """Função principal"""
    print("📊 ANÁLISE DETALHADA DOS RESULTADOS")
    print("="*60)
    
    # Carregar relatório
    try:
        report = load_report()
    except FileNotFoundError:
        print("❌ Arquivo batch_analysis_report.json não encontrado!")
        print("Execute primeiro: python3 batch_debug_analysis.py")
        return
    
    # Análises
    analyze_quality_distribution(report)
    analyze_common_issues(report)
    analyze_worst_conversions(report)
    find_specific_problems(report)
    analyze_performance(report)
    
    print(f"\n🎉 ANÁLISE CONCLUÍDA!")
    print(f"📁 Relatório completo: batch_analysis_report.json")

if __name__ == "__main__":
    main()

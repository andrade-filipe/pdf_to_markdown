#!/usr/bin/env python3
"""Processamento dos 44 PDFs com análise crítica da fidelidade"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter.pipeline import ConversionPipeline

def analyze_fidelity(pdf_path, md_content):
    """Analisa a fidelidade do conteúdo Markdown em relação ao PDF original"""
    
    # Métricas de fidelidade
    fidelity_metrics = {
        'total_chars': len(md_content),
        'total_lines': len(md_content.split('\n')),
        'headers_count': len([line for line in md_content.split('\n') if line.startswith('#')]),
        'issues': [],
        'fidelity_score': 0
    }
    
    # Problemas críticos que afetam fidelidade
    critical_issues = []
    
    # 1. Verificar duplicações excessivas
    lines = md_content.split('\n')
    seen_lines = set()
    duplicates = 0
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and line_stripped in seen_lines:
            duplicates += 1
        seen_lines.add(line_stripped)
    
    duplicate_percentage = (duplicates / len(lines)) * 100 if lines else 0
    if duplicate_percentage > 10:
        critical_issues.append(f"Duplicações excessivas: {duplicate_percentage:.1f}%")
        fidelity_metrics['fidelity_score'] -= 20
    
    # 2. Verificar metadados incorretamente marcados como headers
    academic_metadata_headers = 0
    academic_patterns = [
        'Proceedings', 'Volume', 'Article', 'Print Reference', 'DOI:', 
        'Available at:', 'Follow this and additional works', 'CedarCommons repository',
        'Recommended Citation', 'Browse the contents', 'University', 'College',
        'Copyright', 'All Rights Reserved', 'Journal Policies', 'Editorial Board',
        'Assistant Editor:', 'Editor:', 'About the', 'Founded in', 'BSG membership',
        'Occas. Papers', 'www.', 'Email:', 'USA', 'Center for Origins',
        'Weatherford, TX', 'Dayton, TN', 'Tallahassee, FL', 'Joseph Francis',
        'Margaret Helder', 'Georg Huber', 'Richard Sternberg', 'Todd Charles Wood',
        'Kurt P. Wise', 'Roger Sanders', 'N. Doran'
    ]
    
    for line in lines:
        if line.startswith('#'):
            for pattern in academic_patterns:
                if pattern in line:
                    academic_metadata_headers += 1
                    break
    
    if academic_metadata_headers > 5:
        critical_issues.append(f"Muitos metadados como headers: {academic_metadata_headers}")
        fidelity_metrics['fidelity_score'] -= 15
    
    # 3. Verificar conteúdo muito pequeno (possível falha na extração)
    if len(md_content) < 5000:  # Menos de 5KB
        critical_issues.append(f"Conteúdo muito pequeno: {len(md_content)} chars")
        fidelity_metrics['fidelity_score'] -= 30
    
    # 4. Verificar fragmentação excessiva (muitas linhas vazias)
    empty_lines = len([line for line in lines if not line.strip()])
    empty_percentage = (empty_lines / len(lines)) * 100 if lines else 0
    if empty_percentage > 30:
        critical_issues.append(f"Muitas linhas vazias: {empty_percentage:.1f}%")
        fidelity_metrics['fidelity_score'] -= 10
    
    # 5. Verificar estrutura hierárquica
    headers = [line for line in lines if line.startswith('#')]
    if len(headers) == 0:
        critical_issues.append("Sem estrutura hierárquica detectada")
        fidelity_metrics['fidelity_score'] -= 15
    elif len(headers) > len(lines) * 0.3:
        critical_issues.append("Estrutura hierárquica excessiva")
        fidelity_metrics['fidelity_score'] -= 10
    
    # 6. Verificar palavras-chave acadêmicas importantes
    academic_keywords = ['abstract', 'introduction', 'method', 'results', 'discussion', 'conclusion', 'references']
    found_keywords = []
    for keyword in academic_keywords:
        if keyword in md_content.lower():
            found_keywords.append(keyword)
    
    if len(found_keywords) < 3:
        critical_issues.append(f"Poucas seções acadêmicas encontradas: {found_keywords}")
        fidelity_metrics['fidelity_score'] -= 10
    
    # Calcular score de fidelidade (base 100)
    fidelity_metrics['fidelity_score'] += 100
    fidelity_metrics['fidelity_score'] = max(0, fidelity_metrics['fidelity_score'])
    
    # Determinar status
    if fidelity_metrics['fidelity_score'] >= 95:
        status = "EXCELENTE"
    elif fidelity_metrics['fidelity_score'] >= 85:
        status = "BOM"
    elif fidelity_metrics['fidelity_score'] >= 70:
        status = "REGULAR"
    else:
        status = "POBRE"
    
    fidelity_metrics['status'] = status
    fidelity_metrics['critical_issues'] = critical_issues
    
    return fidelity_metrics

def process_all_pdfs_critical():
    """Processa todos os 44 PDFs com análise crítica"""
    
    # Diretórios
    pdf_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/"
    output_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    
    # Listar todos os PDFs
    pdf_files = list(Path(pdf_dir).glob("*.pdf"))
    pdf_files.sort()
    
    print(f"🎯 PROCESSAMENTO CRÍTICO DOS {len(pdf_files)} PDFs")
    print(f"📊 Padrão de qualidade: 95% de fidelidade")
    print("=" * 80)
    
    # Criar pipeline
    pipeline = ConversionPipeline(output_dir)
    
    # Estatísticas
    total_stats = {
        'processed': 0,
        'excellent': 0,
        'good': 0,
        'regular': 0,
        'poor': 0,
        'total_fidelity_score': 0,
        'failures': 0,
        'results': {}
    }
    
    start_time = time.time()
    
    for i, pdf_path in enumerate(pdf_files, 1):
        pdf_name = pdf_path.name
        print(f"\n[{i}/{len(pdf_files)}] 🔍 ANÁLISE CRÍTICA: {pdf_name}")
        
        try:
            # Executar conversão
            result = pipeline.convert(str(pdf_path))
            
            if result and 'markdown_content' in result:
                markdown_content = result['markdown_content']
                
                # Análise crítica de fidelidade
                fidelity_metrics = analyze_fidelity(pdf_path, markdown_content)
                
                # Exibir resultados
                print(f"  📊 Fidelidade: {fidelity_metrics['fidelity_score']:.1f}% - {fidelity_metrics['status']}")
                print(f"  📏 Tamanho: {fidelity_metrics['total_chars']:,} chars")
                print(f"  📋 Linhas: {fidelity_metrics['total_lines']}")
                print(f"  🏷️  Headers: {fidelity_metrics['headers_count']}")
                
                if fidelity_metrics['critical_issues']:
                    print(f"  ⚠️  Problemas críticos:")
                    for issue in fidelity_metrics['critical_issues']:
                        print(f"     - {issue}")
                else:
                    print(f"  ✅ Sem problemas críticos detectados")
                
                # Salvar resultado
                output_file = os.path.join(output_dir, pdf_name.replace('.pdf', '.md'))
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                # Acumular estatísticas
                total_stats['processed'] += 1
                total_stats['total_fidelity_score'] += fidelity_metrics['fidelity_score']
                
                if fidelity_metrics['status'] == "EXCELENTE":
                    total_stats['excellent'] += 1
                elif fidelity_metrics['status'] == "BOM":
                    total_stats['good'] += 1
                elif fidelity_metrics['status'] == "REGULAR":
                    total_stats['regular'] += 1
                else:
                    total_stats['poor'] += 1
                
                total_stats['results'][pdf_name] = fidelity_metrics
                
                print(f"  💾 Arquivo salvo: {output_file}")
                
            else:
                print(f"  ❌ Falha na conversão")
                total_stats['failures'] += 1
                
        except Exception as e:
            print(f"  ❌ ERRO: {str(e)}")
            total_stats['failures'] += 1
    
    # Estatísticas finais
    elapsed_time = time.time() - start_time
    
    print(f"\n" + "=" * 80)
    print(f"🎯 RESULTADOS DA ANÁLISE CRÍTICA")
    print(f"=" * 80)
    print(f"📁 Total processado: {total_stats['processed']}/{len(pdf_files)}")
    print(f"⏱️  Tempo total: {elapsed_time:.1f} segundos")
    print(f"📊 Tempo médio: {elapsed_time/len(pdf_files):.1f} segundos/arquivo")
    
    if total_stats['processed'] > 0:
        avg_fidelity = total_stats['total_fidelity_score'] / total_stats['processed']
        print(f"🎯 Fidelidade média: {avg_fidelity:.1f}%")
    
    print(f"\n📈 DISTRIBUIÇÃO DE QUALIDADE:")
    print(f"  🎉 EXCELENTE (≥95%): {total_stats['excellent']} arquivos")
    print(f"  👍 BOM (85-94%): {total_stats['good']} arquivos")
    print(f"  ⚠️  REGULAR (70-84%): {total_stats['regular']} arquivos")
    print(f"  ❌ POBRE (<70%): {total_stats['poor']} arquivos")
    print(f"  💥 FALHAS: {total_stats['failures']} arquivos")
    
    # Avaliação geral
    print(f"\n🎯 AVALIAÇÃO GERAL:")
    if avg_fidelity >= 95:
        print(f"  🎉 EXCELENTE! Sistema atingiu o padrão de 95% de fidelidade!")
    elif avg_fidelity >= 85:
        print(f"  👍 BOM! Sistema próximo do padrão desejado.")
    elif avg_fidelity >= 70:
        print(f"  ⚠️  REGULAR. Melhorias necessárias para atingir 95%.")
    else:
        print(f"  ❌ POBRE. Revisão completa necessária.")
    
    # Salvar relatório detalhado
    report_file = f"relatorio_fidelidade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(total_stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório detalhado salvo: {report_file}")
    print(f"📂 Verifique os arquivos em: {output_dir}")

if __name__ == "__main__":
    process_all_pdfs_critical()

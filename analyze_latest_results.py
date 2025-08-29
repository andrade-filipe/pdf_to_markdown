#!/usr/bin/env python3
"""Análise dos resultados mais recentes das conversões"""

import os
import re
from pathlib import Path

def analyze_markdown_files():
    """Analisa os arquivos Markdown gerados mais recentemente"""
    
    output_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    
    # Listar arquivos mais recentes
    md_files = list(Path(output_dir).glob("*.md"))
    md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"Analisando {len(md_files)} arquivos Markdown...")
    print("=" * 80)
    
    total_stats = {
        'total_files': len(md_files),
        'total_lines': 0,
        'total_headers': 0,
        'total_duplicates': 0,
        'academic_metadata_headers': 0,
        'files_with_issues': []
    }
    
    # Padrões para detectar metadados acadêmicos
    academic_patterns = [
        'Proceedings', 'Volume', 'Article', 'Print Reference', 'DOI:', 
        'Available at:', 'Follow this and additional works', 'CedarCommons repository',
        'Recommended Citation', 'Browse the contents', 'University', 'College',
        'Copyright', 'All Rights Reserved', 'Journal Policies', 'Editorial Board'
    ]
    
    for i, md_file in enumerate(md_files[:10], 1):  # Analisar apenas os 10 mais recentes
        print(f"\n[{i}] Analisando: {md_file.name}")
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            headers = [line for line in lines if line.startswith('#')]
            
            # Estatísticas básicas
            file_stats = {
                'lines': len(lines),
                'headers': len(headers),
                'size_chars': len(content),
                'duplicate_lines': 0,
                'academic_metadata_headers': 0,
                'issues': []
            }
            
            # Verificar duplicações
            seen_lines = set()
            for line in lines:
                line_stripped = line.strip()
                if line_stripped and line_stripped in seen_lines:
                    file_stats['duplicate_lines'] += 1
                seen_lines.add(line_stripped)
            
            # Verificar metadados acadêmicos marcados como headers
            for header in headers:
                for pattern in academic_patterns:
                    if pattern in header:
                        file_stats['academic_metadata_headers'] += 1
                        break
            
            # Detectar problemas específicos
            if file_stats['academic_metadata_headers'] > 0:
                file_stats['issues'].append(f"Metadados acadêmicos como headers: {file_stats['academic_metadata_headers']}")
            
            if file_stats['duplicate_lines'] > len(lines) * 0.1:  # Mais de 10% duplicadas
                file_stats['issues'].append(f"Muitas duplicações: {file_stats['duplicate_lines']} ({file_stats['duplicate_lines']/len(lines)*100:.1f}%)")
            
            if len(headers) == 0:
                file_stats['issues'].append("Sem headers detectados")
            
            if len(content) < 1000:
                file_stats['issues'].append("Conteúdo muito pequeno")
            
            # Exibir estatísticas
            print(f"  📊 Linhas: {file_stats['lines']}")
            print(f"  📋 Headers: {file_stats['headers']}")
            print(f"  📏 Tamanho: {file_stats['size_chars']:,} chars")
            print(f"  🔄 Duplicações: {file_stats['duplicate_lines']} ({file_stats['duplicate_lines']/len(lines)*100:.1f}%)")
            print(f"  ⚠️  Metadados como headers: {file_stats['academic_metadata_headers']}")
            
            if file_stats['issues']:
                print(f"  ❌ Problemas:")
                for issue in file_stats['issues']:
                    print(f"     - {issue}")
                total_stats['files_with_issues'].append(md_file.name)
            else:
                print(f"  ✅ Sem problemas detectados")
            
            # Acumular estatísticas totais
            total_stats['total_lines'] += file_stats['lines']
            total_stats['total_headers'] += file_stats['headers']
            total_stats['total_duplicates'] += file_stats['duplicate_lines']
            total_stats['academic_metadata_headers'] += file_stats['academic_metadata_headers']
            
        except Exception as e:
            print(f"  ❌ ERRO ao analisar: {str(e)}")
    
    # Estatísticas finais
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS GERAIS")
    print("=" * 80)
    print(f"📁 Arquivos analisados: {total_stats['total_files']}")
    print(f"📊 Total de linhas: {total_stats['total_lines']:,}")
    print(f"📋 Total de headers: {total_stats['total_headers']}")
    print(f"🔄 Total de duplicações: {total_stats['total_duplicates']} ({(total_stats['total_duplicates']/total_stats['total_lines'])*100:.1f}%)")
    print(f"⚠️  Metadados como headers: {total_stats['academic_metadata_headers']}")
    print(f"❌ Arquivos com problemas: {len(total_stats['files_with_issues'])}")
    
    if total_stats['files_with_issues']:
        print(f"\n📝 Arquivos com problemas:")
        for file_name in total_stats['files_with_issues']:
            print(f"  - {file_name}")
    
    # Avaliação geral
    print(f"\n🎯 AVALIAÇÃO GERAL:")
    if len(total_stats['files_with_issues']) == 0:
        print("  🎉 EXCELENTE! Todos os arquivos estão sem problemas.")
    elif len(total_stats['files_with_issues']) < total_stats['total_files'] * 0.3:
        print("  👍 BOM! Menos de 30% dos arquivos têm problemas.")
    elif len(total_stats['files_with_issues']) < total_stats['total_files'] * 0.7:
        print("  ⚠️  REGULAR. Entre 30-70% dos arquivos têm problemas.")
    else:
        print("  ❌ PROBLEMÁTICO. Mais de 70% dos arquivos têm problemas.")
    
    print(f"\n📈 Taxa de duplicação média: {(total_stats['total_duplicates']/total_stats['total_lines'])*100:.1f}%")
    print(f"📋 Headers por arquivo: {total_stats['total_headers']/min(10, total_stats['total_files']):.1f}")
    print(f"📊 Linhas por arquivo: {total_stats['total_lines']/min(10, total_stats['total_files']):.1f}")

if __name__ == "__main__":
    analyze_markdown_files()


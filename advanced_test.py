#!/usr/bin/env python3
"""Script avançado para testar múltiplos PDFs e gerar estatísticas detalhadas"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def advanced_test():
    """Testa múltiplos PDFs e gera relatório detalhado"""
    
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    output_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown")
    
    # Listar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📚 Encontrados {len(pdf_files)} arquivos PDF para testar")
    
    results = []
    successful = 0
    failed = 0
    
    # Testar os primeiros 20 PDFs para validação de robustez
    for i, pdf_file in enumerate(pdf_files[:20], 1):
        print(f"\n🔄 [{i}/{min(20, len(pdf_files))}] Testando: {pdf_file.name}")
        
        try:
            # Executar conversão via CLI
            cmd = [
                '/usr/bin/python3', 'main.py', 
                str(pdf_file), 
                '-d', str(output_dir),
                '-v'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Ler o arquivo gerado
                output_file = output_dir / f"{pdf_file.stem}.md"
                if output_file.exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extrair estatísticas da saída
                    stats = extract_stats_from_output(result.stdout)
                    
                    # Estatísticas do arquivo
                    lines = len(content.split('\n'))
                    chars = len(content)
                    size_kb = len(content.encode('utf-8')) / 1024
                    
                    file_result = {
                        'file': pdf_file.name,
                        'size_pdf_mb': pdf_file.stat().st_size / (1024 * 1024),
                        'method': stats.get('method_chosen', 'unknown'),
                        'lines': lines,
                        'chars': chars,
                        'size_kb': size_kb,
                        'pages': stats.get('total_pages', 0),
                        'text_blocks': stats.get('text_blocks', 0),
                        'tables': stats.get('tables', 0),
                        'images': stats.get('images', 0),
                        'font_info_entries': stats.get('font_info_entries', 0),
                        'raw_text_length': stats.get('raw_text_length', 0),
                        'cleaned_text_length': stats.get('cleaned_text_length', 0),
                        'markdown_length': stats.get('markdown_length', 0),
                        'success': True
                    }
                    
                    results.append(file_result)
                    successful += 1
                    
                    print(f"✅ {pdf_file.name}: {lines} linhas, {size_kb:.1f}KB, método: {file_result['method']}")
                else:
                    print(f"❌ Erro: arquivo não gerado para {pdf_file.name}")
                    failed += 1
            else:
                print(f"❌ Erro na conversão: {result.stderr}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Erro ao processar {pdf_file.name}: {e}")
            failed += 1
    
    # Gerar relatório detalhado
    generate_detailed_report(results, successful, failed)


def extract_stats_from_output(output: str) -> dict:
    """Extrai estatísticas da saída do comando"""
    stats = {}
    
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        
        # Extrair método escolhido
        if 'Método escolhido:' in line:
            method = line.split(': ')[1].strip()
            stats['method_chosen'] = method
        
        # Extrair outras estatísticas
        if line.startswith('   - '):
            parts = line[5:].split(': ')
            if len(parts) == 2:
                key = parts[0].lower().replace(' ', '_').replace('-', '_')
                value = parts[1]
                
                # Converter valores numéricos
                try:
                    if ',' in value:
                        value = int(value.replace(',', ''))
                    else:
                        value = int(value)
                except ValueError:
                    pass
                
                stats[key] = value
    
    return stats


def generate_detailed_report(results: list, successful: int, failed: int):
    """Gera relatório detalhado dos testes"""
    
    print(f"\n📊 RELATÓRIO DETALHADO")
    print(f"=" * 60)
    
    # Estatísticas gerais
    print(f"📁 Total de arquivos: {successful + failed}")
    print(f"✅ Sucessos: {successful}")
    print(f"❌ Falhas: {failed}")
    print(f"📈 Taxa de sucesso: {(successful/(successful+failed)*100):.1f}%")
    
    if not results:
        print("❌ Nenhum arquivo foi processado com sucesso")
        return
    
    # Métodos utilizados
    method_counts = {}
    for result in results:
        method = result['method']
        method_counts[method] = method_counts.get(method, 0) + 1
    
    print(f"\n🎯 Métodos utilizados:")
    for method, count in method_counts.items():
        percentage = (count / len(results)) * 100
        print(f"   {method}: {count} arquivos ({percentage:.1f}%)")
    
    # Estatísticas de tamanho
    total_lines = sum(r['lines'] for r in results)
    total_chars = sum(r['chars'] for r in results)
    total_size_kb = sum(r['size_kb'] for r in results)
    total_pdf_size_mb = sum(r['size_pdf_mb'] for r in results)
    
    print(f"\n📏 Estatísticas de tamanho:")
    print(f"   Total de linhas: {total_lines:,}")
    print(f"   Total de caracteres: {total_chars:,}")
    print(f"   Tamanho total Markdown: {total_size_kb:.1f}KB")
    print(f"   Tamanho total PDF: {total_pdf_size_mb:.1f}MB")
    print(f"   Média de linhas por arquivo: {total_lines/len(results):.1f}")
    print(f"   Média de caracteres por arquivo: {total_chars/len(results):.1f}")
    
    # Estatísticas de extração
    total_pages = sum(r['pages'] for r in results)
    total_text_blocks = sum(r['text_blocks'] for r in results)
    total_tables = sum(r['tables'] for r in results)
    total_images = sum(r['images'] for r in results)
    
    print(f"\n📄 Estatísticas de extração:")
    print(f"   Total de páginas: {total_pages}")
    print(f"   Total de blocos de texto: {total_text_blocks}")
    print(f"   Total de tabelas: {total_tables}")
    print(f"   Total de imagens: {total_images}")
    print(f"   Média de páginas por arquivo: {total_pages/len(results):.1f}")
    
    # Top 5 arquivos por tamanho
    print(f"\n📋 Top 5 arquivos por número de linhas:")
    sorted_by_lines = sorted(results, key=lambda x: x['lines'], reverse=True)
    for i, result in enumerate(sorted_by_lines[:5], 1):
        print(f"   {i}. {result['file']}: {result['lines']} linhas ({result['method']})")
    
    # Salvar relatório em JSON
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files': successful + failed,
            'successful': successful,
            'failed': failed,
            'success_rate': successful/(successful+failed)*100
        },
        'methods': method_counts,
        'statistics': {
            'total_lines': total_lines,
            'total_chars': total_chars,
            'total_size_kb': total_size_kb,
            'total_pdf_size_mb': total_pdf_size_mb,
            'total_pages': total_pages,
            'total_text_blocks': total_text_blocks,
            'total_tables': total_tables,
            'total_images': total_images
        },
        'results': results
    }
    
    report_file = Path("test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {report_file}")


if __name__ == "__main__":
    advanced_test()

#!/usr/bin/env python3
"""Script para testar todos os métodos de conversão em múltiplos PDFs"""

import os
import sys
import subprocess
from pathlib import Path


def test_all_methods():
    """Testa todos os métodos de conversão em múltiplos PDFs"""
    
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    output_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown")
    
    # Listar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📚 Encontrados {len(pdf_files)} arquivos PDF para testar")
    
    results = []
    
    for i, pdf_file in enumerate(pdf_files[:5], 1):  # Testar apenas os primeiros 5
        print(f"\n🔄 [{i}/{min(5, len(pdf_files))}] Testando: {pdf_file.name}")
        
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
                    
                    # Extrair método usado da saída
                    method = 'unknown'
                    if 'Método escolhido:' in result.stdout:
                        method_line = [line for line in result.stdout.split('\n') if 'Método escolhido:' in line][0]
                        method = method_line.split(': ')[1].strip()
                    
                    # Estatísticas
                    lines = len(content.split('\n'))
                    chars = len(content)
                    
                    results.append({
                        'file': pdf_file.name,
                        'method': method,
                        'lines': lines,
                        'chars': chars,
                        'size_kb': len(content.encode('utf-8')) / 1024,
                        'stats': {
                            'lines': lines,
                            'chars': chars,
                            'method': method
                        }
                    })
                    
                    print(f"✅ {pdf_file.name}: {lines} linhas, método: {method}")
                else:
                    print(f"❌ Erro: arquivo não gerado para {pdf_file.name}")
            else:
                print(f"❌ Erro na conversão: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao processar {pdf_file.name}: {e}")
    
    # Relatório final
    print(f"\n📊 RELATÓRIO FINAL")
    print(f"=" * 50)
    
    total_files = len(results)
    if total_files == 0:
        print("❌ Nenhum arquivo foi processado com sucesso")
        return
        
    method_counts = {}
    total_lines = 0
    total_chars = 0
    
    for result in results:
        method = result['method']
        method_counts[method] = method_counts.get(method, 0) + 1
        total_lines += result['lines']
        total_chars += result['chars']
    
    print(f"📁 Total de arquivos processados: {total_files}")
    print(f"📝 Total de linhas: {total_lines:,}")
    print(f"📄 Total de caracteres: {total_chars:,}")
    print(f"📊 Média de linhas por arquivo: {total_lines/total_files:.1f}")
    
    print(f"\n🎯 Métodos utilizados:")
    for method, count in method_counts.items():
        percentage = (count / total_files) * 100
        print(f"   {method}: {count} arquivos ({percentage:.1f}%)")
    
    print(f"\n📋 Detalhes por arquivo:")
    for result in results:
        print(f"   {result['file']}: {result['lines']} linhas ({result['method']})")


if __name__ == "__main__":
    test_all_methods()

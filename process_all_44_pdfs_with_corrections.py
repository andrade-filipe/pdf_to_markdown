#!/usr/bin/env python3
"""Processa todos os 44 PDFs com as correções implementadas"""

import sys
import os
import time
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter.pipeline import ConversionPipeline

def process_all_pdfs():
    """Processa todos os PDFs na pasta de referências"""
    
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/")
    output_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    
    # Listar todos os PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    total_files = len(pdf_files)
    
    print(f"Processando {total_files} arquivos PDF...")
    print(f"Diretório de entrada: {pdf_dir}")
    print(f"Diretório de saída: {output_dir}")
    print("-" * 80)
    
    # Criar pipeline
    pipeline = ConversionPipeline(output_dir)
    
    # Estatísticas
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    # Processar cada arquivo
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{total_files}] Processando: {pdf_path.name}")
        
        try:
            # Executar conversão
            result = pipeline.convert(str(pdf_path))
            
            if result:
                success_count += 1
                print(f"  ✅ Conversão concluída com sucesso")
                
                # Análise rápida do resultado
                if 'markdown_content' in result:
                    content = result['markdown_content']
                    lines = content.split('\n')
                    headers = [line for line in lines if line.startswith('#')]
                    
                    print(f"  📊 Linhas: {len(lines)}, Headers: {len(headers)}, Tamanho: {len(content)} chars")
                    
                    # Verificar duplicações
                    duplicate_lines = 0
                    seen_lines = set()
                    for line in lines:
                        line_stripped = line.strip()
                        if line_stripped and line_stripped in seen_lines:
                            duplicate_lines += 1
                        seen_lines.add(line_stripped)
                    
                    duplicate_percentage = (duplicate_lines / len(lines)) * 100 if lines else 0
                    print(f"  🔍 Duplicações: {duplicate_lines} ({duplicate_percentage:.1f}%)")
                    
                    # Verificar metadados acadêmicos incorretamente marcados como headers
                    academic_metadata_headers = 0
                    academic_patterns = [
                        'Proceedings', 'Volume', 'Article', 'Print Reference', 'DOI:', 
                        'Available at:', 'Follow this and additional works', 'CedarCommons repository',
                        'Recommended Citation', 'Browse the contents'
                    ]
                    
                    for header in headers:
                        for pattern in academic_patterns:
                            if pattern in header:
                                academic_metadata_headers += 1
                                break
                    
                    print(f"  ⚠️  Metadados como headers: {academic_metadata_headers}")
                
            else:
                error_count += 1
                print(f"  ❌ Falha na conversão")
                
        except Exception as e:
            error_count += 1
            print(f"  ❌ ERRO: {str(e)}")
    
    # Estatísticas finais
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print("RESULTADOS FINAIS")
    print("=" * 80)
    print(f"📁 Total de arquivos processados: {total_files}")
    print(f"✅ Conversões bem-sucedidas: {success_count}")
    print(f"❌ Falhas: {error_count}")
    print(f"⏱️  Tempo total: {total_time:.1f} segundos")
    print(f"📈 Taxa de sucesso: {(success_count/total_files)*100:.1f}%")
    print(f"📊 Tempo médio por arquivo: {total_time/total_files:.1f} segundos")
    print("=" * 80)
    
    if error_count > 0:
        print(f"\n⚠️  ATENÇÃO: {error_count} arquivos falharam na conversão.")
        print("Verifique os logs acima para identificar os problemas.")
    
    print(f"\n🎯 Conversões concluídas! Verifique os arquivos em: {output_dir}")

if __name__ == "__main__":
    process_all_pdfs()

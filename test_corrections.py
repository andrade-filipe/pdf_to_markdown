#!/usr/bin/env python3
"""Teste das correções implementadas"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter.pipeline import ConversionPipeline
import tempfile
import shutil

def test_corrections_on_sample_pdfs():
    """Testa as correções em alguns PDFs de exemplo"""
    
    # Diretórios
    pdf_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/"
    output_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    
    # Listar alguns PDFs para teste
    pdf_files = []
    for file in os.listdir(pdf_dir):
        if file.endswith('.pdf'):
            pdf_files.append(file)
            if len(pdf_files) >= 3:  # Testar apenas 3 arquivos
                break
    
    print(f"Testando correções em {len(pdf_files)} arquivos:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    # Criar pipeline
    pipeline = ConversionPipeline(output_dir)
    
    # Processar arquivos
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"\nProcessando: {pdf_file}")
        
        try:
            # Executar pipeline
            result = pipeline.convert(pdf_path)
            
            # Verificar resultado
            if result and 'markdown_content' in result:
                markdown_content = result['markdown_content']
            else:
                # Tentar ler do arquivo gerado
                output_file = os.path.join(output_dir, pdf_file.replace('.pdf', '.md'))
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        markdown_content = f.read()
                else:
                    print(f"  - ERRO: Nenhum conteúdo encontrado")
                    continue
                
                # Análise do resultado
                lines = markdown_content.split('\n')
                headers = [line for line in lines if line.startswith('#')]
                
                print(f"  - Total de linhas: {len(lines)}")
                print(f"  - Headers encontrados: {len(headers)}")
                print(f"  - Tamanho do arquivo: {len(markdown_content)} caracteres")
                
                # Verificar duplicações
                duplicate_lines = 0
                seen_lines = set()
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped and line_stripped in seen_lines:
                        duplicate_lines += 1
                    seen_lines.add(line_stripped)
                
                duplicate_percentage = (duplicate_lines / len(lines)) * 100 if lines else 0
                print(f"  - Linhas duplicadas: {duplicate_lines} ({duplicate_percentage:.1f}%)")
                
                # Verificar metadados acadêmicos incorretamente marcados como headers
                academic_metadata_headers = 0
                academic_patterns = [
                    'Proceedings', 'Volume', 'Article', 'Print Reference', 'DOI:', 
                    'Available at:', 'Follow this and additional works', 'CedarCommons repository',
                    'Recommended Citation', 'Browse the contents', 'University', 'College'
                ]
                
                for header in headers:
                    for pattern in academic_patterns:
                        if pattern in header:
                            academic_metadata_headers += 1
                            break
                
                print(f"  - Metadados acadêmicos marcados como headers: {academic_metadata_headers}")
                
                # Salvar resultado para análise
                output_file = os.path.join(output_dir, pdf_file.replace('.pdf', '.md'))
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print(f"  - Arquivo salvo: {output_file}")
                
            else:
                print(f"  - ERRO: Falha na conversão")
                
        except Exception as e:
            print(f"  - ERRO: {str(e)}")
    
    print(f"\nTeste concluído! Verifique os arquivos gerados em: {output_dir}")

if __name__ == "__main__":
    test_corrections_on_sample_pdfs()

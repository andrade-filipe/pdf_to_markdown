#!/usr/bin/env python3
"""Teste da iteração final das correções"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter.pipeline import ConversionPipeline

def test_final_corrections():
    """Testa as correções finais em alguns arquivos problemáticos"""
    
    # Diretórios
    pdf_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/"
    output_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
    
    # Arquivos problemáticos identificados
    problematic_files = [
        "003.pdf",
        "Hypercanes Following the Genesis Flood.pdf",
        "Dark Matter and Dark Energy.pdf"
    ]
    
    print(f"Testando correções finais em {len(problematic_files)} arquivos problemáticos...")
    print("=" * 80)
    
    # Criar pipeline
    pipeline = ConversionPipeline(output_dir)
    
    for i, pdf_file in enumerate(problematic_files, 1):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"\n[{i}/{len(problematic_files)}] Processando: {pdf_file}")
        
        try:
            # Executar conversão
            result = pipeline.convert(pdf_path)
            
            if result and 'markdown_content' in result:
                markdown_content = result['markdown_content']
            else:
                # Tentar ler do arquivo gerado
                output_file = os.path.join(output_dir, pdf_file.replace('.pdf', '.md'))
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        markdown_content = f.read()
                else:
                    print(f"  ❌ Nenhum conteúdo encontrado")
                    continue
                
                # Análise do resultado
                lines = markdown_content.split('\n')
                headers = [line for line in lines if line.startswith('#')]
                
                print(f"  📊 Linhas: {len(lines)}")
                print(f"  📋 Headers: {len(headers)}")
                print(f"  📏 Tamanho: {len(markdown_content)} chars")
                
                # Verificar metadados acadêmicos incorretamente marcados como headers
                academic_metadata_headers = 0
                academic_patterns = [
                    'Proceedings', 'Volume', 'Article', 'Print Reference', 'DOI:', 
                    'Available at:', 'Follow this and additional works', 'CedarCommons repository',
                    'Recommended Citation', 'Browse the contents', 'University', 'College',
                    'Copyright', 'All Rights Reserved', 'Journal Policies', 'Editorial Board',
                    'Assistant Editor:', 'Editor:', 'About the', 'Founded in', 'BSG membership',
                    'Occas. Papers', 'www.', 'Email:', 'USA', 'Center for Origins',
                    'Weatherford, TX', 'Dayton, TN', 'Tallahassee, FL'
                ]
                
                problematic_headers = []
                for header in headers:
                    for pattern in academic_patterns:
                        if pattern in header:
                            academic_metadata_headers += 1
                            problematic_headers.append(header.strip())
                            break
                
                print(f"  ⚠️  Metadados como headers: {academic_metadata_headers}")
                
                if problematic_headers:
                    print(f"  ❌ Headers problemáticos encontrados:")
                    for header in problematic_headers[:3]:  # Mostrar apenas os 3 primeiros
                        print(f"     - {header[:80]}...")
                    if len(problematic_headers) > 3:
                        print(f"     ... e mais {len(problematic_headers) - 3}")
                else:
                    print(f"  ✅ Nenhum header problemático detectado!")
                
                # Verificar duplicações
                duplicate_lines = 0
                seen_lines = set()
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped and line_stripped in seen_lines:
                        duplicate_lines += 1
                    seen_lines.add(line_stripped)
                
                duplicate_percentage = (duplicate_lines / len(lines)) * 100 if lines else 0
                print(f"  🔄 Duplicações: {duplicate_lines} ({duplicate_percentage:.1f}%)")
                
                # Avaliação
                if academic_metadata_headers == 0 and duplicate_percentage < 5:
                    print(f"  🎉 EXCELENTE! Arquivo convertido com sucesso.")
                elif academic_metadata_headers < 3 and duplicate_percentage < 10:
                    print(f"  👍 BOM! Melhorias significativas alcançadas.")
                else:
                    print(f"  ⚠️  REGULAR. Ainda há problemas a resolver.")
                
                # Salvar resultado
                output_file = os.path.join(output_dir, pdf_file.replace('.pdf', '.md'))
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print(f"  💾 Arquivo salvo: {output_file}")
                
            else:
                print(f"  ❌ Falha na conversão")
                
        except Exception as e:
            print(f"  ❌ ERRO: {str(e)}")
    
    print(f"\n🎯 Teste final concluído!")
    print(f"📂 Verifique os arquivos em: {output_dir}")

if __name__ == "__main__":
    test_final_corrections()

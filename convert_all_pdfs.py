#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import fitz
import re

def convert_pdfs():
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    output_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown Debug")
    
    # Criar diretório de saída
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Listar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Encontrados {len(pdf_files)} PDFs")
    
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processando: {pdf_file.name}")
        
        try:
            # Analisar PDF
            doc = fitz.open(str(pdf_file))
            total_pages = len(doc)
            total_words = 0
            
            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text()
                words = re.findall(r'\b\w+\b', text.lower())
                total_words += len(words)
            
            doc.close()
            
            print(f"  PDF: {total_pages} páginas, {total_words} palavras")
            
            # Converter usando o pipeline
            from converter.pipeline import ConversionPipeline
            pipeline = ConversionPipeline(str(output_dir))
            output_path = pipeline.convert(str(pdf_file))
            
            if output_path.exists():
                # Analisar resultado
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                md_words = len(re.findall(r'\b\w+\b', content.lower()))
                titles = len([line for line in content.split('\n') if line.startswith('#')])
                
                print(f"  MD: {md_words} palavras, {titles} títulos")
                
                if total_words > 0:
                    ratio = md_words / total_words
                    print(f"  Taxa de preservação: {ratio*100:.1f}%")
                    
                    if ratio < 0.5:
                        print(f"  ⚠️ ALERTA: Baixa preservação!")
                    elif ratio < 0.8:
                        print(f"  ⚠️ ATENÇÃO: Preservação moderada")
                    else:
                        print(f"  ✅ Boa preservação")
                
                success_count += 1
            else:
                print(f"  ❌ Arquivo não criado")
                error_count += 1
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            error_count += 1
    
    # Relatório final
    print(f"\n{'='*50}")
    print(f"RELATÓRIO FINAL")
    print(f"{'='*50}")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {error_count}")
    print(f"Taxa de sucesso: {(success_count/(success_count+error_count)*100):.1f}%")

if __name__ == "__main__":
    convert_pdfs()

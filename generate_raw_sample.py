#!/usr/bin/env python3
"""Script para gerar arquivo raw de qualquer PDF"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import fitz  # PyMuPDF

def extract_raw_pdf_content(pdf_path: str) -> str:
    """Extrai todo o conteúdo bruto do PDF sem processamento"""
    try:
        doc = fitz.open(pdf_path)
        raw_content = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extrair texto bruto
            text = page.get_text()
            raw_content += f"\n--- PÁGINA {page_num + 1} ---\n"
            raw_content += text
            raw_content += "\n"
        
        doc.close()
        return raw_content
    except Exception as e:
        return f"Erro ao extrair PDF: {e}"

def main():
    # Listar PDFs disponíveis
    pdf_dirs = [
        "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/",
        "/home/andrade/Documentos/Artigos/",
        "/home/andrade/Documentos/big-data-any-format/"
    ]
    
    available_pdfs = []
    for pdf_dir in pdf_dirs:
        if os.path.exists(pdf_dir):
            for file in os.listdir(pdf_dir):
                if file.lower().endswith('.pdf'):
                    available_pdfs.append(os.path.join(pdf_dir, file))
    
    if not available_pdfs:
        print("Nenhum PDF encontrado nos diretórios padrão.")
        return
    
    # Usar o primeiro PDF disponível
    pdf_path = available_pdfs[0]
    print(f"Extraindo conteúdo bruto de: {pdf_path}")
    
    # Extrair conteúdo bruto
    raw_content = extract_raw_pdf_content(pdf_path)
    
    # Salvar arquivo raw
    pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
    output_path = f"output/RAW_SAMPLE_{pdf_name}.txt"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(raw_content)
    
    print(f"Arquivo raw salvo em: {output_path}")
    print(f"Tamanho: {len(raw_content)} caracteres")
    print(f"Linhas: {raw_content.count(chr(10)) + 1}")
    
    # Mostrar primeiras linhas
    print("\n=== PRIMEIRAS 20 LINHAS ===")
    lines = raw_content.split('\n')
    for i, line in enumerate(lines[:20]):
        print(f"{i+1:2d}: {line}")

if __name__ == "__main__":
    main()

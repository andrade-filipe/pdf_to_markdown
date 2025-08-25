#!/usr/bin/env python3
"""
Teste de conversão de um único PDF com debug detalhado
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import re

def test_single_pdf():
    # Testar com um PDF específico
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    output_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown Debug")
    
    # Criar diretório de saída
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Pegar o primeiro PDF
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ Nenhum PDF encontrado")
        return
    
    pdf_file = pdf_files[0]
    print(f"🧪 Testando conversão de: {pdf_file.name}")
    
    # Análise do PDF
    try:
        doc = fitz.open(str(pdf_file))
        print(f"📄 PDF: {len(doc)} páginas")
        
        # Extrair texto da primeira página
        page = doc[0]
        text = page.get_text()
        words = re.findall(r'\b\w+\b', text.lower())
        print(f"📝 Primeira página: {len(words)} palavras")
        print(f"📄 Amostra de texto: {text[:200]}...")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ Erro ao analisar PDF: {e}")
        return
    
    # Tentar conversão
    try:
        from converter.pipeline import ConversionPipeline
        print(f"\n🔄 Iniciando conversão...")
        
        pipeline = ConversionPipeline(str(output_dir))
        output_path = pipeline.convert(str(pdf_file))
        
        if output_path.exists():
            print(f"✅ Conversão concluída: {output_path.name}")
            
            # Analisar resultado
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            md_words = len(re.findall(r'\b\w+\b', content.lower()))
            titles = len([line for line in content.split('\n') if line.startswith('#')])
            
            print(f"📊 Resultado:")
            print(f"  • Palavras: {md_words}")
            print(f"  • Títulos: {titles}")
            print(f"  • Linhas: {len(content.split('\n'))}")
            
            if md_words > 0:
                ratio = md_words / len(words)
                print(f"  • Taxa de preservação: {ratio*100:.1f}%")
            
        else:
            print(f"❌ Arquivo não foi criado")
            
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_pdf()

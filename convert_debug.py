#!/usr/bin/env python3

import sys
from pathlib import Path

def main():
    print("=== CONVERSÃO E DEBUG DE PDFs ===")
    
    # Configurar diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    output_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown Debug")
    
    print(f"PDF dir: {pdf_dir}")
    print(f"Output dir: {output_dir}")
    
    # Criar diretório de saída
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Listar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Encontrados {len(pdf_files)} PDFs")
    
    if not pdf_files:
        print("Nenhum PDF encontrado!")
        return
    
    # Testar com os primeiros 3 PDFs
    for i, pdf_file in enumerate(pdf_files[:3], 1):
        print(f"\n--- [{i}/3] Processando: {pdf_file.name} ---")
        
        try:
            # Importar pipeline
            from converter.pipeline import ConversionPipeline
            print("Pipeline importado com sucesso")
            
            # Criar pipeline
            pipeline = ConversionPipeline(str(output_dir))
            print("Pipeline criado")
            
            # Converter
            print("Iniciando conversão...")
            output_path = pipeline.convert(str(pdf_file))
            print(f"Conversão concluída: {output_path}")
            
            # Verificar resultado
            if output_path.exists():
                print("✅ Arquivo criado com sucesso!")
                
                # Analisar resultado
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                words = len([word for word in content.split() if len(word) > 2])
                titles = len([line for line in lines if line.startswith('#')])
                
                print(f"📊 Resultado: {len(lines)} linhas, {words} palavras, {titles} títulos")
                
            else:
                print("❌ Arquivo não foi criado")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== CONVERSÃO CONCLUÍDA ===")

if __name__ == "__main__":
    main()

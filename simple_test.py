#!/usr/bin/env python3

print("Iniciando teste de conversão...")

try:
    from pathlib import Path
    print("✓ Pathlib importado")
    
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    output_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown Debug")
    
    print(f"✓ Diretórios configurados")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Diretório de saída criado: {output_dir}")
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"✓ Encontrados {len(pdf_files)} PDFs")
    
    if pdf_files:
        test_pdf = pdf_files[0]
        print(f"✓ Testando com: {test_pdf.name}")
        
        from converter.pipeline import ConversionPipeline
        print("✓ Pipeline importado")
        
        pipeline = ConversionPipeline(str(output_dir))
        print("✓ Pipeline criado")
        
        output_path = pipeline.convert(str(test_pdf))
        print(f"✓ Conversão concluída: {output_path}")
        
        if output_path.exists():
            print("✓ Arquivo criado com sucesso!")
        else:
            print("❌ Arquivo não foi criado")
    
    print("Teste concluído!")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

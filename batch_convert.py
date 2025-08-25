#!/usr/bin/env python3
"""
Script para processar todos os PDFs em lote
Usado para treinar e melhorar o algoritmo de conversão
"""

import os
import sys
from pathlib import Path
from converter.pipeline import ConversionPipeline

def main():
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    markdown_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown")
    
    # Criar diretório de saída se não existir
    markdown_dir.mkdir(parents=True, exist_ok=True)
    
    # Listar todos os PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📚 Encontrados {len(pdf_files)} arquivos PDF para processar")
    
    # Estatísticas
    success_count = 0
    error_count = 0
    errors = []
    
    # Processar cada PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n🔄 [{i}/{len(pdf_files)}] Processando: {pdf_file.name}")
        
        try:
            # Criar pipeline
            pipeline = ConversionPipeline(str(markdown_dir))
            
            # Converter
            output_path = pipeline.convert(str(pdf_file))
            
            # Verificar resultado
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"✅ Sucesso: {output_path.name} ({file_size} bytes)")
                success_count += 1
                
                # Analisar qualidade do resultado
                analyze_result(output_path)
            else:
                print(f"❌ Erro: Arquivo não foi criado")
                error_count += 1
                errors.append((pdf_file.name, "Arquivo não criado"))
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            error_count += 1
            errors.append((pdf_file.name, str(e)))
    
    # Relatório final
    print(f"\n📊 RELATÓRIO FINAL")
    print(f"✅ Sucessos: {success_count}")
    print(f"❌ Erros: {error_count}")
    print(f"📈 Taxa de sucesso: {(success_count/(success_count+error_count)*100):.1f}%")
    
    if errors:
        print(f"\n❌ Erros encontrados:")
        for pdf_name, error in errors:
            print(f"  - {pdf_name}: {error}")

def analyze_result(markdown_path):
    """Analisa a qualidade do resultado"""
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Métricas básicas
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Detectar problemas comuns
        issues = []
        
        # Verificar se há muito texto corrompido
        corrupted_chars = sum(1 for char in content if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
        if corrupted_chars > len(content) * 0.1:  # Mais de 10% de caracteres estranhos
            issues.append("Muitos caracteres corrompidos")
        
        # Verificar se há texto legível
        readable_words = len([word for word in content.split() if len(word) > 2 and word.isalpha()])
        if readable_words < 50:
            issues.append("Pouco texto legível")
        
        # Verificar se há títulos
        titles = [line for line in lines if line.startswith('#')]
        if len(titles) < 3:
            issues.append("Poucos títulos detectados")
        
        if issues:
            print(f"⚠️  Problemas detectados: {', '.join(issues)}")
        else:
            print(f"✅ Qualidade boa: {len(non_empty_lines)} linhas, {len(titles)} títulos")
            
    except Exception as e:
        print(f"⚠️  Erro ao analisar resultado: {e}")

if __name__ == "__main__":
    main()

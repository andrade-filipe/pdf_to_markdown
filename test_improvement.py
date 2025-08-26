#!/usr/bin/env python3
"""
Script para testar as melhorias implementadas
"""

import os
import sys
from pathlib import Path
import fitz
import re
import time

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from converter.pipeline import ConversionPipeline

def compare_conversions():
    """Compara conversões antes e depois das melhorias"""
    
    # Arquivo para testar
    pdf_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/Mount St. Helens and Catastrophism.pdf"
    original_md_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown/Mount St. Helens and Catastrophism.md"
    test_output_dir = "/tmp/test_improvement"
    
    print("🧪 TESTANDO MELHORIAS IMPLEMENTADAS")
    print("="*60)
    
    # 1. Análise do PDF original
    print(f"\n📄 ANALISANDO PDF ORIGINAL")
    print("-" * 40)
    
    doc = fitz.open(pdf_path)
    total_chars = sum(len(page.get_text()) for page in doc)
    total_words = sum(len(re.findall(r'\b\w+\b', page.get_text().lower())) for page in doc)
    doc.close()
    
    print(f"   Total de caracteres: {total_chars:,}")
    print(f"   Total de palavras: {total_words:,}")
    
    # 2. Análise da conversão original (problemática)
    print(f"\n📝 ANALISANDO CONVERSÃO ORIGINAL (PROBLEMÁTICA)")
    print("-" * 40)
    
    with open(original_md_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    original_chars = len(original_content)
    original_words = len(re.findall(r'\b\w+\b', original_content.lower()))
    original_lines = len(original_content.split('\n'))
    original_empty_lines = len([line for line in original_content.split('\n') if line.strip() == ''])
    
    print(f"   Caracteres: {original_chars:,}")
    print(f"   Palavras: {original_words:,}")
    print(f"   Linhas: {original_lines}")
    print(f"   Linhas vazias: {original_empty_lines}")
    print(f"   Taxa de linhas vazias: {original_empty_lines/original_lines*100:.1f}%")
    print(f"   Taxa de preservação: {original_chars/total_chars*100:.1f}% caracteres, {original_words/total_words*100:.1f}% palavras")
    
    # 3. Testar conversão com melhorias
    print(f"\n🚀 TESTANDO CONVERSÃO COM MELHORIAS")
    print("-" * 40)
    
    # Criar diretório de teste
    test_dir = Path(test_output_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Criar pipeline com melhorias
    pipeline = ConversionPipeline(str(test_dir))
    
    start_time = time.time()
    try:
        output_path = pipeline.convert(pdf_path, "mount_st_helens_improved.md")
        conversion_time = time.time() - start_time
        
        print(f"   ✅ Conversão concluída em {conversion_time:.2f}s")
        print(f"   📁 Arquivo gerado: {output_path}")
        
        # 4. Análise da nova conversão
        print(f"\n📊 ANÁLISE DA NOVA CONVERSÃO")
        print("-" * 40)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        new_chars = len(new_content)
        new_words = len(re.findall(r'\b\w+\b', new_content.lower()))
        new_lines = len(new_content.split('\n'))
        new_empty_lines = len([line for line in new_content.split('\n') if line.strip() == ''])
        
        print(f"   Caracteres: {new_chars:,}")
        print(f"   Palavras: {new_words:,}")
        print(f"   Linhas: {new_lines}")
        print(f"   Linhas vazias: {new_empty_lines}")
        print(f"   Taxa de linhas vazias: {new_empty_lines/new_lines*100:.1f}%")
        print(f"   Taxa de preservação: {new_chars/total_chars*100:.1f}% caracteres, {new_words/total_words*100:.1f}% palavras")
        
        # 5. Comparação de resultados
        print(f"\n📈 COMPARAÇÃO DE RESULTADOS")
        print("-" * 40)
        
        char_improvement = new_chars - original_chars
        word_improvement = new_words - original_words
        empty_line_reduction = original_empty_lines - new_empty_lines
        empty_line_percentage_improvement = (original_empty_lines/original_lines - new_empty_lines/new_lines) * 100
        
        print(f"   Melhoria em caracteres: {char_improvement:+,}")
        print(f"   Melhoria em palavras: {word_improvement:+,}")
        print(f"   Redução de linhas vazias: {empty_line_reduction:+d}")
        print(f"   Melhoria na taxa de linhas vazias: {empty_line_percentage_improvement:+.1f}%")
        
        # Estatísticas do pipeline
        stats = pipeline.get_statistics()
        print(f"\n📊 ESTATÍSTICAS DO PIPELINE:")
        print(f"   Páginas processadas: {stats['total_pages']}")
        print(f"   Blocos de texto: {stats['text_blocks']}")
        print(f"   Método escolhido: {stats['method_chosen']}")
        
        # 6. Mostrar amostra da melhoria
        print(f"\n📄 AMOSTRA DA MELHORIA")
        print("-" * 40)
        
        # Primeiros 500 caracteres da nova conversão
        print("NOVA CONVERSÃO (primeiros 500 chars):")
        print(new_content[:500])
        print("-" * 40)
        
        # Avaliação final
        improvement_score = 0
        
        if char_improvement > 0:
            improvement_score += 2
            print(f"✅ Melhoria na preservação de conteúdo")
        
        if empty_line_reduction > 0:
            improvement_score += 3
            print(f"✅ Redução significativa de linhas vazias")
        
        if word_improvement > 0:
            improvement_score += 2
            print(f"✅ Melhoria na preservação de palavras")
        
        if empty_line_percentage_improvement > 10:
            improvement_score += 2
            print(f"✅ Melhoria significativa na densidade de conteúdo")
        
        print(f"\n🎯 SCORE DE MELHORIA: {improvement_score}/9")
        
        if improvement_score >= 6:
            print("🏆 MELHORIA SIGNIFICATIVA ALCANÇADA!")
        elif improvement_score >= 3:
            print("👍 MELHORIA MODERADA ALCANÇADA")
        else:
            print("⚠️ POUCA MELHORIA DETECTADA")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na conversão: {e}")
        return False

def test_multiple_files():
    """Testa a melhoria em múltiplos arquivos"""
    
    # Arquivos para testar (baseados na análise anterior)
    test_files = [
        "Mount St. Helens and Catastrophism.pdf",
        "The Hydrothermal Biome.pdf", 
        "astronomical-distance-light-travel-problem.pdf"
    ]
    
    pdf_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
    test_output_dir = "/tmp/test_improvement_multiple"
    
    print(f"\n🧪 TESTANDO MELHORIAS EM MÚLTIPLOS ARQUIVOS")
    print("="*60)
    
    # Criar diretório de teste
    test_dir = Path(test_output_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Criar pipeline
    pipeline = ConversionPipeline(str(test_dir))
    
    results = []
    
    for filename in test_files:
        pdf_path = Path(pdf_dir) / filename
        original_md_path = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown") / (filename.replace('.pdf', '.md'))
        
        if not pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {filename}")
            continue
        
        print(f"\n📄 Testando: {filename}")
        
        try:
            # Conversão com melhorias
            start_time = time.time()
            output_path = pipeline.convert(str(pdf_path))
            conversion_time = time.time() - start_time
            
            # Ler conteúdo original e novo
            with open(original_md_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            with open(output_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            # Calcular métricas
            original_lines = len(original_content.split('\n'))
            original_empty = len([line for line in original_content.split('\n') if line.strip() == ''])
            new_lines = len(new_content.split('\n'))
            new_empty = len([line for line in new_content.split('\n') if line.strip() == ''])
            
            improvement = original_empty - new_empty
            percentage_improvement = (original_empty/original_lines - new_empty/new_lines) * 100
            
            result = {
                'filename': filename,
                'original_empty': original_empty,
                'new_empty': new_empty,
                'improvement': improvement,
                'percentage_improvement': percentage_improvement,
                'conversion_time': conversion_time
            }
            
            results.append(result)
            
            print(f"   Original - linhas vazias: {original_empty}")
            print(f"   Nova - linhas vazias: {new_empty}")
            print(f"   Melhoria: {improvement:+d} ({percentage_improvement:+.1f}%)")
            print(f"   Tempo: {conversion_time:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # Resumo dos resultados
    if results:
        print(f"\n📊 RESUMO DOS TESTES")
        print("-" * 40)
        
        total_improvement = sum(r['improvement'] for r in results)
        avg_percentage = sum(r['percentage_improvement'] for r in results) / len(results)
        total_time = sum(r['conversion_time'] for r in results)
        
        print(f"   Total de arquivos testados: {len(results)}")
        print(f"   Melhoria total em linhas vazias: {total_improvement:+d}")
        print(f"   Melhoria média percentual: {avg_percentage:+.1f}%")
        print(f"   Tempo total de conversão: {total_time:.2f}s")
        print(f"   Tempo médio por arquivo: {total_time/len(results):.2f}s")

def main():
    """Função principal"""
    print("🔬 TESTE DE MELHORIAS - PDF TO MARKDOWN CONVERTER")
    print("="*60)
    
    # Teste individual
    success = compare_conversions()
    
    if success:
        # Teste em múltiplos arquivos
        test_multiple_files()
    
    print(f"\n🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()

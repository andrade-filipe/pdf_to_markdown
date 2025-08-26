#!/usr/bin/env python3
"""
Script para testar as melhorias da Fase 1
- Correção do conflito de processamento
- Adição de métrica de densidade de conteúdo
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

def test_phase1_improvements():
    """Testa as melhorias da Fase 1 implementadas"""
    
    # Arquivo para testar (caso mais problemático identificado)
    pdf_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/Mount St. Helens and Catastrophism.pdf"
    original_md_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown/Mount St. Helens and Catastrophism.md"
    test_output_dir = "/tmp/test_phase1"
    
    print("🧪 TESTE DAS MELHORIAS DA FASE 1")
    print("="*60)
    print("✅ Conflito de processamento corrigido")
    print("✅ Métrica de densidade de conteúdo adicionada")
    print("✅ Otimização movida para após seleção de método")
    print("-" * 60)
    
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
    print(f"\n📝 CONVERSÃO ORIGINAL (ANTES DAS MELHORIAS)")
    print("-" * 40)
    
    with open(original_md_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    original_chars = len(original_content)
    original_words = len(re.findall(r'\b\w+\b', original_content.lower()))
    original_lines = len(original_content.split('\n'))
    original_empty_lines = len([line for line in original_content.split('\n') if line.strip() == ''])
    original_density = 1 - (original_empty_lines / original_lines) if original_lines > 0 else 0
    
    print(f"   Caracteres: {original_chars:,}")
    print(f"   Palavras: {original_words:,}")
    print(f"   Linhas: {original_lines}")
    print(f"   Linhas vazias: {original_empty_lines}")
    print(f"   Taxa de linhas vazias: {original_empty_lines/original_lines*100:.1f}%")
    print(f"   Densidade de conteúdo: {original_density:.3f}")
    print(f"   Taxa de preservação: {original_chars/total_chars*100:.1f}% caracteres, {original_words/total_words*100:.1f}% palavras")
    
    # 3. Testar conversão com melhorias
    print(f"\n🚀 TESTANDO CONVERSÃO COM MELHORIAS DA FASE 1")
    print("-" * 40)
    
    # Criar diretório de teste
    test_dir = Path(test_output_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Criar pipeline com melhorias
    pipeline = ConversionPipeline(str(test_dir))
    
    start_time = time.time()
    try:
        output_path = pipeline.convert(pdf_path, "mount_st_helens_phase1.md")
        conversion_time = time.time() - start_time
        
        print(f"   ✅ Conversão concluída em {conversion_time:.2f}s")
        print(f"   📁 Arquivo gerado: {output_path}")
        
        # 4. Análise da nova conversão
        print(f"\n📊 CONVERSÃO COM MELHORIAS (DEPOIS)")
        print("-" * 40)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        new_chars = len(new_content)
        new_words = len(re.findall(r'\b\w+\b', new_content.lower()))
        new_lines = len(new_content.split('\n'))
        new_empty_lines = len([line for line in new_content.split('\n') if line.strip() == ''])
        new_density = 1 - (new_empty_lines / new_lines) if new_lines > 0 else 0
        
        print(f"   Caracteres: {new_chars:,}")
        print(f"   Palavras: {new_words:,}")
        print(f"   Linhas: {new_lines}")
        print(f"   Linhas vazias: {new_empty_lines}")
        print(f"   Taxa de linhas vazias: {new_empty_lines/new_lines*100:.1f}%")
        print(f"   Densidade de conteúdo: {new_density:.3f}")
        print(f"   Taxa de preservação: {new_chars/total_chars*100:.1f}% caracteres, {new_words/total_words*100:.1f}% palavras")
        
        # 5. Comparação de resultados
        print(f"\n📈 COMPARAÇÃO DE RESULTADOS")
        print("-" * 40)
        
        char_improvement = new_chars - original_chars
        word_improvement = new_words - original_words
        empty_line_reduction = original_empty_lines - new_empty_lines
        density_improvement = new_density - original_density
        empty_line_percentage_improvement = (original_empty_lines/original_lines - new_empty_lines/new_lines) * 100
        
        print(f"   Melhoria em caracteres: {char_improvement:+,}")
        print(f"   Melhoria em palavras: {word_improvement:+,}")
        print(f"   Redução de linhas vazias: {empty_line_reduction:+d}")
        print(f"   Melhoria na densidade: {density_improvement:+.3f}")
        print(f"   Melhoria na taxa de linhas vazias: {empty_line_percentage_improvement:+.1f}%")
        
        # Estatísticas do pipeline
        stats = pipeline.get_statistics()
        print(f"\n📊 ESTATÍSTICAS DO PIPELINE:")
        print(f"   Páginas processadas: {stats['total_pages']}")
        print(f"   Blocos de texto: {stats['text_blocks']}")
        print(f"   Método escolhido: {stats['method_chosen']}")
        
        # 6. Avaliação das melhorias
        print(f"\n🎯 AVALIAÇÃO DAS MELHORIAS")
        print("-" * 40)
        
        improvement_score = 0
        improvements = []
        issues = []
        
        # Verificar melhorias na densidade de conteúdo
        if density_improvement > 0.05:  # Melhoria significativa na densidade
            improvement_score += 3
            improvements.append("✅ Melhoria significativa na densidade de conteúdo")
        elif density_improvement > 0.01:  # Melhoria moderada
            improvement_score += 2
            improvements.append("✅ Melhoria moderada na densidade de conteúdo")
        else:
            issues.append("⚠️ Pouca melhoria na densidade de conteúdo")
        
        # Verificar redução de linhas vazias
        if empty_line_reduction > 10:
            improvement_score += 3
            improvements.append("✅ Redução significativa de linhas vazias")
        elif empty_line_reduction > 0:
            improvement_score += 2
            improvements.append("✅ Redução moderada de linhas vazias")
        else:
            issues.append("⚠️ Pouca redução de linhas vazias")
        
        # Verificar preservação de conteúdo
        if word_improvement > 0:
            improvement_score += 2
            improvements.append("✅ Melhoria na preservação de palavras")
        elif word_improvement == 0:
            improvements.append("✅ Preservação de palavras mantida")
        else:
            issues.append("⚠️ Perda de palavras detectada")
        
        # Verificar taxa de linhas vazias
        if new_empty_lines/new_lines < 0.3:  # Menos de 30% de linhas vazias
            improvement_score += 2
            improvements.append("✅ Taxa de linhas vazias aceitável (<30%)")
        elif new_empty_lines/new_lines < original_empty_lines/original_lines:
            improvement_score += 1
            improvements.append("✅ Taxa de linhas vazias melhorada")
        else:
            issues.append("⚠️ Taxa de linhas vazias ainda alta")
        
        # Exibir melhorias e problemas
        for improvement in improvements:
            print(f"   {improvement}")
        
        for issue in issues:
            print(f"   {issue}")
        
        print(f"\n🎯 SCORE DE MELHORIA: {improvement_score}/10")
        
        if improvement_score >= 8:
            print("🏆 MELHORIA EXCELENTE ALCANÇADA!")
            return True
        elif improvement_score >= 6:
            print("👍 MELHORIA SIGNIFICATIVA ALCANÇADA")
            return True
        elif improvement_score >= 4:
            print("✅ MELHORIA MODERADA ALCANÇADA")
            return True
        else:
            print("⚠️ POUCA MELHORIA DETECTADA - REQUER REVISÃO")
            return False
        
    except Exception as e:
        print(f"   ❌ Erro na conversão: {e}")
        return False

def test_multiple_files():
    """Testa as melhorias em múltiplos arquivos problemáticos"""
    
    # Arquivos para testar (baseados na análise anterior)
    test_files = [
        "Mount St. Helens and Catastrophism.pdf",
        "The Hydrothermal Biome.pdf", 
        "astronomical-distance-light-travel-problem.pdf"
    ]
    
    pdf_dir = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
    test_output_dir = "/tmp/test_phase1_multiple"
    
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
            original_density = 1 - (original_empty / original_lines) if original_lines > 0 else 0
            
            new_lines = len(new_content.split('\n'))
            new_empty = len([line for line in new_content.split('\n') if line.strip() == ''])
            new_density = 1 - (new_empty / new_lines) if new_lines > 0 else 0
            
            improvement = original_empty - new_empty
            density_improvement = new_density - original_density
            percentage_improvement = (original_empty/original_lines - new_empty/new_lines) * 100
            
            result = {
                'filename': filename,
                'original_empty': original_empty,
                'new_empty': new_empty,
                'original_density': original_density,
                'new_density': new_density,
                'improvement': improvement,
                'density_improvement': density_improvement,
                'percentage_improvement': percentage_improvement,
                'conversion_time': conversion_time
            }
            
            results.append(result)
            
            print(f"   Original - linhas vazias: {original_empty}, densidade: {original_density:.3f}")
            print(f"   Nova - linhas vazias: {new_empty}, densidade: {new_density:.3f}")
            print(f"   Melhoria: {improvement:+d} linhas vazias, {density_improvement:+.3f} densidade ({percentage_improvement:+.1f}%)")
            print(f"   Tempo: {conversion_time:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # Resumo dos resultados
    if results:
        print(f"\n📊 RESUMO DOS TESTES DA FASE 1")
        print("-" * 40)
        
        total_improvement = sum(r['improvement'] for r in results)
        avg_density_improvement = sum(r['density_improvement'] for r in results) / len(results)
        avg_percentage = sum(r['percentage_improvement'] for r in results) / len(results)
        total_time = sum(r['conversion_time'] for r in results)
        
        print(f"   Total de arquivos testados: {len(results)}")
        print(f"   Melhoria total em linhas vazias: {total_improvement:+d}")
        print(f"   Melhoria média de densidade: {avg_density_improvement:+.3f}")
        print(f"   Melhoria média percentual: {avg_percentage:+.1f}%")
        print(f"   Tempo total de conversão: {total_time:.2f}s")
        print(f"   Tempo médio por arquivo: {total_time/len(results):.2f}s")
        
        # Avaliação geral
        if avg_density_improvement > 0.05 and avg_percentage > 10:
            print(f"\n🏆 RESULTADO: MELHORIA SIGNIFICATIVA NA FASE 1!")
        elif avg_density_improvement > 0.01 and avg_percentage > 5:
            print(f"\n👍 RESULTADO: MELHORIA MODERADA NA FASE 1")
        else:
            print(f"\n⚠️ RESULTADO: POUCA MELHORIA NA FASE 1 - REQUER REVISÃO")

def main():
    """Função principal"""
    print("🔬 TESTE DAS MELHORIAS DA FASE 1 - PDF TO MARKDOWN CONVERTER")
    print("="*60)
    
    # Teste individual
    success = test_phase1_improvements()
    
    if success:
        # Teste em múltiplos arquivos
        test_multiple_files()
        
        print(f"\n✅ FASE 1 CONCLUÍDA COM SUCESSO!")
        print("Próximo passo: Implementar Fase 2 (investigar perda de conteúdo)")
    else:
        print(f"\n⚠️ FASE 1 COM PROBLEMAS - REQUER REVISÃO")
        print("Recomendação: Investigar e corrigir problemas antes da Fase 2")
    
    print(f"\n🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()

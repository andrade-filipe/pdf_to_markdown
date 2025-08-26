#!/usr/bin/env python3
"""
Script para testar as melhorias na extração de texto
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

def test_extraction_improvements():
    """Testa as melhorias na extração de texto"""
    
    # Arquivo para testar
    pdf_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/Mount St. Helens and Catastrophism.pdf"
    test_output_dir = "/tmp/test_extraction_improvements"
    
    print("🧪 TESTE DAS MELHORIAS NA EXTRAÇÃO DE TEXTO")
    print("="*60)
    print("✅ Algoritmo de junção inteligente de spans implementado")
    print("✅ Preservação de estrutura de parágrafos")
    print("✅ Melhor tratamento de espaçamento")
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
    
    # 2. Testar conversão com melhorias
    print(f"\n🚀 TESTANDO CONVERSÃO COM MELHORIAS NA EXTRAÇÃO")
    print("-" * 40)
    
    # Criar diretório de teste
    test_dir = Path(test_output_dir)
    test_dir.mkdir(exist_ok=True)
    
    # Criar pipeline com melhorias
    pipeline = ConversionPipeline(str(test_dir))
    
    start_time = time.time()
    try:
        output_path = pipeline.convert(pdf_path, "mount_st_helens_extraction_improved.md")
        conversion_time = time.time() - start_time
        
        print(f"   ✅ Conversão concluída em {conversion_time:.2f}s")
        print(f"   📁 Arquivo gerado: {output_path}")
        
        # 3. Análise da nova conversão
        print(f"\n📊 CONVERSÃO COM MELHORIAS NA EXTRAÇÃO")
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
        
        # 4. Comparação com conversão anterior
        print(f"\n📈 COMPARAÇÃO COM CONVERSÃO ANTERIOR")
        print("-" * 40)
        
        original_md_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias in Markdown/Mount St. Helens and Catastrophism.md"
        
        if Path(original_md_path).exists():
            with open(original_md_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            original_chars = len(original_content)
            original_words = len(re.findall(r'\b\w+\b', original_content.lower()))
            original_lines = len(original_content.split('\n'))
            original_empty_lines = len([line for line in original_content.split('\n') if line.strip() == ''])
            original_density = 1 - (original_empty_lines / original_lines) if original_lines > 0 else 0
            
            char_improvement = new_chars - original_chars
            word_improvement = new_words - original_words
            density_improvement = new_density - original_density
            empty_line_reduction = original_empty_lines - new_empty_lines
            
            print(f"   Melhoria em caracteres: {char_improvement:+,}")
            print(f"   Melhoria em palavras: {word_improvement:+,}")
            print(f"   Melhoria na densidade: {density_improvement:+.3f}")
            print(f"   Redução de linhas vazias: {empty_line_reduction:+d}")
            print(f"   Melhoria na preservação: {(new_chars/total_chars - original_chars/total_chars)*100:+.1f}%")
        
        # 5. Análise da qualidade do texto extraído
        print(f"\n📝 ANÁLISE DA QUALIDADE DO TEXTO EXTRAÍDO")
        print("-" * 40)
        
        # Verificar se o texto está bem formatado
        sample_text = new_content[:1000]  # Primeiros 1000 caracteres
        
        # Contar palavras juntas (problema anterior)
        words_together = len(re.findall(r'[a-z][A-Z]', sample_text))
        
        # Contar frases quebradas
        sentences = re.split(r'[.!?]', sample_text)
        broken_sentences = sum(1 for s in sentences if len(s.strip()) < 10 and len(s.strip()) > 0)
        
        # Verificar parágrafos
        paragraphs = [p.strip() for p in new_content.split('\n\n') if p.strip()]
        avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        print(f"   Palavras juntas no texto: {words_together}")
        print(f"   Frases quebradas: {broken_sentences}")
        print(f"   Parágrafos identificados: {len(paragraphs)}")
        print(f"   Comprimento médio de parágrafo: {avg_paragraph_length:.1f} caracteres")
        
        if words_together < 10:
            print("   ✅ Texto bem formatado (poucas palavras juntas)")
        else:
            print("   ⚠️ Ainda há muitas palavras juntas")
        
        if broken_sentences < len(sentences) * 0.1:
            print("   ✅ Frases bem estruturadas")
        else:
            print("   ⚠️ Muitas frases quebradas")
        
        if avg_paragraph_length > 100:
            print("   ✅ Parágrafos bem formados")
        else:
            print("   ⚠️ Parágrafos muito curtos")
        
        # 6. Mostrar amostra do texto melhorado
        print(f"\n📖 AMOSTRA DO TEXTO MELHORADO (primeiros 500 chars)")
        print("-" * 40)
        print(new_content[:500])
        print("...")
        
        # 7. Avaliação geral
        print(f"\n🎯 AVALIAÇÃO GERAL DAS MELHORIAS")
        print("-" * 40)
        
        improvement_score = 0
        improvements = []
        issues = []
        
        # Verificar melhoria na preservação
        if new_chars > original_chars * 1.1:  # 10% mais caracteres
            improvement_score += 3
            improvements.append("✅ Melhoria significativa na preservação de caracteres")
        elif new_chars > original_chars:
            improvement_score += 2
            improvements.append("✅ Melhoria moderada na preservação")
        else:
            issues.append("⚠️ Pouca melhoria na preservação")
        
        # Verificar melhoria na densidade
        if density_improvement > 0.1:  # 10% de melhoria
            improvement_score += 3
            improvements.append("✅ Melhoria significativa na densidade")
        elif density_improvement > 0.05:
            improvement_score += 2
            improvements.append("✅ Melhoria moderada na densidade")
        else:
            issues.append("⚠️ Pouca melhoria na densidade")
        
        # Verificar qualidade do texto
        if words_together < 5 and broken_sentences < len(sentences) * 0.05:
            improvement_score += 2
            improvements.append("✅ Texto bem formatado e legível")
        elif words_together < 10:
            improvement_score += 1
            improvements.append("✅ Texto moderadamente bem formatado")
        else:
            issues.append("⚠️ Texto ainda mal formatado")
        
        # Verificar preservação de conteúdo
        if new_words > original_words * 1.05:  # 5% mais palavras
            improvement_score += 2
            improvements.append("✅ Melhoria na preservação de palavras")
        elif new_words >= original_words:
            improvements.append("✅ Preservação de palavras mantida")
        else:
            issues.append("⚠️ Perda de palavras detectada")
        
        # Exibir melhorias e problemas
        for improvement in improvements:
            print(f"   {improvement}")
        
        for issue in issues:
            print(f"   {issue}")
        
        print(f"\n🎯 SCORE DE MELHORIA: {improvement_score}/10")
        
        if improvement_score >= 8:
            print("🏆 MELHORIA EXCELENTE NA EXTRAÇÃO!")
            return True
        elif improvement_score >= 6:
            print("👍 MELHORIA SIGNIFICATIVA NA EXTRAÇÃO")
            return True
        elif improvement_score >= 4:
            print("✅ MELHORIA MODERADA NA EXTRAÇÃO")
            return True
        else:
            print("⚠️ POUCA MELHORIA DETECTADA - REQUER MAIS AJUSTES")
            return False
        
    except Exception as e:
        print(f"   ❌ Erro na conversão: {e}")
        return False

def main():
    """Função principal"""
    print("🔬 TESTE DAS MELHORIAS NA EXTRAÇÃO DE TEXTO - PDF TO MARKDOWN CONVERTER")
    print("="*60)
    
    # Teste das melhorias
    success = test_extraction_improvements()
    
    if success:
        print(f"\n✅ MELHORIAS NA EXTRAÇÃO VALIDADAS COM SUCESSO!")
        print("Próximo passo: Aplicar melhorias globalmente")
    else:
        print(f"\n⚠️ MELHORIAS NA EXTRAÇÃO COM PROBLEMAS - REQUER REVISÃO")
        print("Recomendação: Investigar e ajustar algoritmos")
    
    print(f"\n🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()

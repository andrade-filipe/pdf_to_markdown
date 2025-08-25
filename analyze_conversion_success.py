#!/usr/bin/env python3
"""
Script para analisar detalhadamente a taxa de sucesso de cada conversão PDF para Markdown
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import re

def count_pdf_pages(pdf_path):
    """Conta o número de páginas do PDF"""
    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        return page_count
    except Exception as e:
        print(f"Erro ao contar páginas de {pdf_path}: {e}")
        return 0

def count_pdf_words(pdf_path):
    """Conta o número aproximado de palavras no PDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        # Limpar texto e contar palavras
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)
    except Exception as e:
        print(f"Erro ao contar palavras de {pdf_path}: {e}")
        return 0

def analyze_markdown_quality(markdown_path):
    """Analisa a qualidade do arquivo Markdown"""
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Métricas básicas
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Contar palavras
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = len(words)
        
        # Contar títulos
        titles = [line for line in lines if line.startswith('#')]
        title_count = len(titles)
        
        # Contar parágrafos
        paragraphs = [line for line in lines if line.strip() and not line.startswith('#') and not line.startswith('!')]
        paragraph_count = len(paragraphs)
        
        # Detectar problemas
        issues = []
        
        # Verificar se há muito texto corrompido
        corrupted_chars = sum(1 for char in content if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
        if corrupted_chars > len(content) * 0.1:
            issues.append("Muitos caracteres corrompidos")
        
        # Verificar se há texto legível
        if word_count < 50:
            issues.append("Pouco texto legível")
        
        # Verificar se há títulos
        if title_count < 3:
            issues.append("Poucos títulos detectados")
        
        # Verificar se há parágrafos
        if paragraph_count < 10:
            issues.append("Poucos parágrafos")
        
        return {
            'lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'words': word_count,
            'titles': title_count,
            'paragraphs': paragraph_count,
            'issues': issues,
            'file_size': os.path.getsize(markdown_path)
        }
    except Exception as e:
        print(f"Erro ao analisar {markdown_path}: {e}")
        return None

def calculate_success_rate(pdf_path, markdown_path):
    """Calcula a taxa de sucesso da conversão"""
    try:
        # Informações do PDF
        pdf_pages = count_pdf_pages(pdf_path)
        pdf_words = count_pdf_words(pdf_path)
        
        # Informações do Markdown
        md_analysis = analyze_markdown_quality(markdown_path)
        
        if md_analysis is None:
            return 0.0, "Erro na análise"
        
        # Calcular taxa de sucesso baseada em múltiplos critérios
        success_factors = []
        
        # Fator 1: Presença de conteúdo (não vazio)
        if md_analysis['words'] > 0:
            success_factors.append(1.0)
        else:
            success_factors.append(0.0)
        
        # Fator 2: Proporção de palavras preservadas (mínimo 10% do original)
        if pdf_words > 0:
            word_ratio = min(md_analysis['words'] / pdf_words, 1.0)
            if word_ratio >= 0.1:
                success_factors.append(word_ratio)
            else:
                success_factors.append(0.0)
        else:
            success_factors.append(0.0)
        
        # Fator 3: Estrutura adequada (títulos e parágrafos)
        structure_score = 0.0
        if md_analysis['titles'] >= 3:
            structure_score += 0.5
        if md_analysis['paragraphs'] >= 10:
            structure_score += 0.5
        success_factors.append(structure_score)
        
        # Fator 4: Qualidade do texto (sem problemas graves)
        quality_score = 1.0
        for issue in md_analysis['issues']:
            if "caracteres corrompidos" in issue:
                quality_score -= 0.3
            elif "pouco texto" in issue:
                quality_score -= 0.2
        success_factors.append(max(0.0, quality_score))
        
        # Taxa de sucesso final (média dos fatores)
        success_rate = sum(success_factors) / len(success_factors) * 100
        
        return success_rate, md_analysis
        
    except Exception as e:
        print(f"Erro ao calcular taxa de sucesso: {e}")
        return 0.0, None

def main():
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    markdown_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown")
    
    # Listar todos os PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📚 Analisando {len(pdf_files)} arquivos PDF...")
    
    # Resultados
    results = []
    total_success_rate = 0.0
    
    # Analisar cada conversão
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n🔄 [{i}/{len(pdf_files)}] Analisando: {pdf_file.name}")
        
        # Encontrar arquivo Markdown correspondente
        markdown_name = pdf_file.stem + ".md"
        markdown_path = markdown_dir / markdown_name
        
        if markdown_path.exists():
            # Calcular taxa de sucesso
            success_rate, analysis = calculate_success_rate(str(pdf_file), str(markdown_path))
            
            # Informações do PDF
            pdf_pages = count_pdf_pages(str(pdf_file))
            pdf_words = count_pdf_words(str(pdf_file))
            
            result = {
                'pdf_name': pdf_file.name,
                'pdf_pages': pdf_pages,
                'pdf_words': pdf_words,
                'markdown_name': markdown_name,
                'success_rate': success_rate,
                'analysis': analysis,
                'status': '✅ Sucesso' if success_rate >= 50 else '⚠️ Baixa qualidade'
            }
            
            results.append(result)
            total_success_rate += success_rate
            
            print(f"  📊 Taxa de sucesso: {success_rate:.1f}%")
            print(f"  📄 PDF: {pdf_pages} páginas, {pdf_words} palavras")
            if analysis:
                print(f"  📝 Markdown: {analysis['words']} palavras, {analysis['titles']} títulos, {analysis['paragraphs']} parágrafos")
                if analysis['issues']:
                    print(f"  ⚠️ Problemas: {', '.join(analysis['issues'])}")
        else:
            print(f"  ❌ Arquivo Markdown não encontrado")
            results.append({
                'pdf_name': pdf_file.name,
                'success_rate': 0.0,
                'status': '❌ Falha na conversão'
            })
    
    # Relatório final
    print(f"\n" + "="*80)
    print(f"📊 RELATÓRIO DETALHADO DE TAXA DE SUCESSO")
    print(f"="*80)
    
    # Estatísticas gerais
    successful_conversions = [r for r in results if r['success_rate'] > 0]
    failed_conversions = [r for r in results if r['success_rate'] == 0]
    
    print(f"\n📈 ESTATÍSTICAS GERAIS:")
    print(f"  • Total de PDFs: {len(pdf_files)}")
    print(f"  • Conversões bem-sucedidas: {len(successful_conversions)}")
    print(f"  • Conversões falharam: {len(failed_conversions)}")
    print(f"  • Taxa de sucesso geral: {(len(successful_conversions)/len(pdf_files)*100):.1f}%")
    
    if successful_conversions:
        avg_success_rate = total_success_rate / len(successful_conversions)
        print(f"  • Taxa de sucesso média (conversões bem-sucedidas): {avg_success_rate:.1f}%")
    
    # Classificação por qualidade
    print(f"\n🏆 CLASSIFICAÇÃO POR QUALIDADE:")
    excellent = [r for r in results if r['success_rate'] >= 80]
    good = [r for r in results if 60 <= r['success_rate'] < 80]
    fair = [r for r in results if 40 <= r['success_rate'] < 60]
    poor = [r for r in results if 20 <= r['success_rate'] < 40]
    failed = [r for r in results if r['success_rate'] < 20]
    
    print(f"  • Excelente (80-100%): {len(excellent)} arquivos")
    print(f"  • Boa (60-79%): {len(good)} arquivos")
    print(f"  • Regular (40-59%): {len(fair)} arquivos")
    print(f"  • Baixa (20-39%): {len(poor)} arquivos")
    print(f"  • Falhou (<20%): {len(failed)} arquivos")
    
    # Lista detalhada por taxa de sucesso
    print(f"\n📋 LISTA DETALHADA POR TAXA DE SUCESSO:")
    print(f"{'Taxa':<6} {'Status':<12} {'PDF':<50} {'Páginas':<8} {'Palavras':<10}")
    print("-" * 90)
    
    # Ordenar por taxa de sucesso (decrescente)
    sorted_results = sorted(results, key=lambda x: x['success_rate'], reverse=True)
    
    for result in sorted_results:
        pdf_name = result['pdf_name'][:47] + "..." if len(result['pdf_name']) > 50 else result['pdf_name']
        pages = result.get('pdf_pages', 'N/A')
        words = result.get('pdf_words', 'N/A')
        
        print(f"{result['success_rate']:5.1f}% {result['status']:<12} {pdf_name:<50} {pages:<8} {words:<10}")
    
    # Top 10 melhores conversões
    print(f"\n🥇 TOP 10 MELHORES CONVERSÕES:")
    for i, result in enumerate(sorted_results[:10], 1):
        print(f"  {i:2d}. {result['success_rate']:5.1f}% - {result['pdf_name']}")
    
    # Piores conversões
    print(f"\n⚠️ PIORES CONVERSÕES:")
    for i, result in enumerate(sorted_results[-5:], 1):
        print(f"  {i:2d}. {result['success_rate']:5.1f}% - {result['pdf_name']}")
    
    print(f"\n" + "="*80)

if __name__ == "__main__":
    main()

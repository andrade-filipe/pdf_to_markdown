#!/usr/bin/env python3
"""
Teste da versão otimizada do OCR seletivo
"""

import os
import json
import time
from pathlib import Path
from converter.pipeline import ConversionPipeline

# Configurações
PDF_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
MARKDOWN_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"

# Casos problemáticos para teste
PROBLEMATIC_CASES = [
    "181014cronologia_ap.pdf",  # Preservação: 305.8% - muito repetições
    "Biostratigraphic Continuity and Earth History.pdf",  # Palavras repetidas: 1882x
    "coming-to-grips-with-genesis-ch6.pdf",  # Muitas linhas repetidas: 396
]

def analyze_content_quality(content):
    """Análise detalhada da qualidade do conteúdo"""
    lines = content.split('\n')
    
    # Estatísticas básicas
    total_lines = len(lines)
    non_empty_lines = len([l for l in lines if l.strip()])
    empty_lines = total_lines - non_empty_lines
    
    # Densidade de conteúdo
    density = non_empty_lines / total_lines if total_lines > 0 else 0
    
    # Contar repetições
    seen_lines = set()
    repeated_lines = 0
    line_freq = {}
    
    for line in lines:
        line = line.strip()
        if line:
            normalized = line.lower()
            line_freq[normalized] = line_freq.get(normalized, 0) + 1
            if normalized in seen_lines:
                repeated_lines += 1
            else:
                seen_lines.add(normalized)
    
    # Análise de palavras repetidas
    word_freq = {}
    all_text = ' '.join([line.strip() for line in lines if line.strip()])
    words = all_text.split()
    
    for word in words:
        word_lower = word.lower()
        if len(word_lower) > 2:
            word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
    
    max_word_repetition = max(word_freq.values()) if word_freq else 0
    
    # Análise de duplicação
    content_length = len(content)
    is_likely_duplicated = content_length > 50000
    
    # Análise de estrutura
    paragraphs = content.split('\n\n')
    avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
    
    # Calcular score de qualidade
    quality_score = 0
    
    # Densidade (0-25 pontos)
    quality_score += density * 25
    
    # Comprimento médio das linhas (0-25 pontos)
    line_lengths = [len(l.strip()) for l in lines if l.strip()]
    avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
    quality_score += min(25, avg_line_length / 4)
    
    # Penalizar repetições (0-25 pontos)
    repetition_penalty = min(25, repeated_lines * 0.1 + max_word_repetition * 0.01)
    quality_score -= repetition_penalty
    
    # Qualidade da estrutura (0-25 pontos)
    if avg_paragraph_length > 200 and len(paragraphs) > 5:
        quality_score += 25
    elif avg_paragraph_length > 100 and len(paragraphs) > 3:
        quality_score += 20
    elif avg_paragraph_length > 50:
        quality_score += 15
    
    quality_score = max(0, quality_score)
    
    return {
        'total_lines': total_lines,
        'non_empty_lines': non_empty_lines,
        'empty_lines': empty_lines,
        'density': density,
        'repeated_lines': repeated_lines,
        'max_word_repetition': max_word_repetition,
        'content_length': content_length,
        'is_likely_duplicated': is_likely_duplicated,
        'avg_line_length': avg_line_length,
        'avg_paragraph_length': avg_paragraph_length,
        'paragraph_count': len(paragraphs),
        'quality_score': quality_score,
        'problematic_words': [word for word, count in word_freq.items() if count > 50]
    }

def main():
    print("🚀 TESTE DO OCR SELETIVO OTIMIZADO")
    print("=" * 70)
    print("✅ Algoritmo de combinação inteligente aprimorado")
    print("✅ Limpeza pós-OCR mais agressiva")
    print("✅ Detecção e remoção de duplicações")
    print("=" * 70)
    
    # Criar pipeline com OCR seletivo otimizado
    pipeline = ConversionPipeline(str(Path(MARKDOWN_DIR)))
    
    results = {}
    
    for pdf_name in PROBLEMATIC_CASES:
        print(f"\n📄 TESTANDO OCR OTIMIZADO: {pdf_name}")
        print("-" * 60)
        
        pdf_path = Path(PDF_DIR) / pdf_name
        
        if not pdf_path.exists():
            print(f"❌ PDF não encontrado: {pdf_path}")
            continue
        
        try:
            # Converter com OCR seletivo otimizado
            print("🔄 Convertendo com OCR otimizado...")
            start_time = time.time()
            
            output_filename = f"{pdf_name.replace('.pdf', '_optimized.md')}"
            output_path = pipeline.convert(str(pdf_path), output_filename)
            
            conversion_time = time.time() - start_time
            
            print(f"   ✅ Conversão concluída: {conversion_time:.2f}s")
            print(f"   📁 Arquivo: {output_path}")
            
            # Verificar se OCR foi aplicado
            ocr_applied = pipeline.current_data.get('ocr_applied', False)
            ocr_pages = pipeline.current_data.get('ocr_pages_processed', 0)
            
            if ocr_applied:
                print(f"   🔍 OCR aplicado em {ocr_pages} páginas")
            else:
                print(f"   📝 OCR não necessário - texto de boa qualidade")
            
            # Analisar resultado otimizado
            print("📊 Analisando resultado otimizado...")
            
            with open(output_path, 'r', encoding='utf-8') as f:
                optimized_content = f.read()
            
            optimized_analysis = analyze_content_quality(optimized_content)
            
            print(f"   📊 Linhas totais: {optimized_analysis['total_lines']:,}")
            print(f"   📝 Linhas com conteúdo: {optimized_analysis['non_empty_lines']:,}")
            print(f"   📈 Densidade: {optimized_analysis['density']:.3f}")
            print(f"   📏 Comprimento médio das linhas: {optimized_analysis['avg_line_length']:.1f}")
            print(f"   🔄 Linhas repetidas: {optimized_analysis['repeated_lines']}")
            print(f"   📚 Máx repetição de palavra: {optimized_analysis['max_word_repetition']}")
            print(f"   📄 Parágrafos: {optimized_analysis['paragraph_count']}")
            print(f"   📊 Score de qualidade: {optimized_analysis['quality_score']:.1f}/100")
            
            # Comparar com versão anterior
            old_md_path = Path(MARKDOWN_DIR) / f"{pdf_name.replace('.pdf', '.md')}"
            
            if old_md_path.exists():
                print("\n📄 Comparando com versão anterior...")
                
                with open(old_md_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                
                old_analysis = analyze_content_quality(old_content)
                
                improvement_density = optimized_analysis['density'] - old_analysis['density']
                improvement_repetitions = old_analysis['repeated_lines'] - optimized_analysis['repeated_lines']
                improvement_word_repetitions = old_analysis['max_word_repetition'] - optimized_analysis['max_word_repetition']
                improvement_quality = optimized_analysis['quality_score'] - old_analysis['quality_score']
                
                print(f"   📈 Melhoria na densidade: {improvement_density:+.3f}")
                print(f"   🔄 Redução de linhas repetidas: {improvement_repetitions:+d}")
                print(f"   📚 Redução de palavras repetidas: {improvement_word_repetitions:+d}")
                print(f"   🎯 Melhoria no score de qualidade: {improvement_quality:+.1f}")
                
                # Verificar se o tamanho foi reduzido (menos duplicação)
                size_reduction = (len(old_content) - len(optimized_content)) / len(old_content) * 100
                print(f"   📉 Redução no tamanho: {size_reduction:+.1f}%")
                
                if improvement_quality > 10 or improvement_word_repetitions > 100:
                    print("   🚀 MELHORIA SIGNIFICATIVA DETECTADA!")
                elif improvement_quality > 0:
                    print("   ✅ Melhoria moderada detectada")
                else:
                    print("   ⚠️ Nenhuma melhoria detectada")
            
            # Detectar problemas remanescentes
            problems = []
            
            if optimized_analysis['repeated_lines'] > 50:
                problems.append(f"Muitas linhas repetidas ({optimized_analysis['repeated_lines']})")
            
            if optimized_analysis['max_word_repetition'] > 200:
                problems.append(f"Palavras muito repetidas (máx: {optimized_analysis['max_word_repetition']})")
            
            if optimized_analysis['is_likely_duplicated']:
                problems.append("Possível duplicação de conteúdo")
            
            if optimized_analysis['quality_score'] < 50:
                problems.append(f"Score de qualidade baixo ({optimized_analysis['quality_score']:.1f}/100)")
            
            if problems:
                print(f"   ⚠️ Problemas remanescentes:")
                for problem in problems:
                    print(f"      - {problem}")
                    
                if optimized_analysis['problematic_words']:
                    print(f"   🔍 Palavras problemáticas: {optimized_analysis['problematic_words'][:5]}...")
            else:
                print("   ✅ Nenhum problema detectado!")
            
            results[pdf_name] = {
                'optimized_analysis': optimized_analysis,
                'ocr_applied': ocr_applied,
                'ocr_pages': ocr_pages,
                'conversion_time': conversion_time,
                'problems': problems,
                'improvements': {
                    'density_improvement': improvement_density if old_md_path.exists() else 0,
                    'repetition_reduction': improvement_repetitions if old_md_path.exists() else 0,
                    'word_repetition_reduction': improvement_word_repetitions if old_md_path.exists() else 0,
                    'quality_improvement': improvement_quality if old_md_path.exists() else 0,
                    'size_reduction': size_reduction if old_md_path.exists() else 0
                }
            }
            
        except Exception as e:
            print(f"   ❌ Erro na conversão: {e}")
            results[pdf_name] = {'error': str(e)}
    
    # Resumo dos resultados
    print("\n🎯 RESUMO DOS RESULTADOS OTIMIZADOS")
    print("=" * 70)
    
    successful_tests = 0
    ocr_used = 0
    significant_improvements = 0
    moderate_improvements = 0
    
    for pdf_name, result in results.items():
        if 'error' not in result:
            successful_tests += 1
            
            if result['ocr_applied']:
                ocr_used += 1
            
            analysis = result['optimized_analysis']
            improvements = result['improvements']
            
            # Determinar status da melhoria
            if improvements['quality_improvement'] > 10 or improvements['word_repetition_reduction'] > 100:
                status = "🚀 SIGNIFICATIVAMENTE MELHORADO"
                significant_improvements += 1
            elif improvements['quality_improvement'] > 0:
                status = "✅ MELHORADO"
                moderate_improvements += 1
            elif improvements['quality_improvement'] == 0 and improvements['word_repetition_reduction'] == 0:
                status = "🔄 IGUAL"
            else:
                status = "⚠️ PIORADO"
            
            ocr_info = f"OCR:{result['ocr_pages']}p" if result['ocr_applied'] else "SEM OCR"
            quality_info = f"Q:{analysis['quality_score']:.0f}"
            
            print(f"   {pdf_name}: {status} [{ocr_info}] [{quality_info}]")
            print(f"      Densidade: {analysis['density']:.3f} (Δ{improvements['density_improvement']:+.3f})")
            print(f"      Repetições: {analysis['repeated_lines']} (Δ{improvements['repetition_reduction']:+d})")
            print(f"      Palavras repetidas: {analysis['max_word_repetition']} (Δ{improvements['word_repetition_reduction']:+d})")
            print(f"      Score: {analysis['quality_score']:.1f}/100 (Δ{improvements['quality_improvement']:+.1f})")
            print(f"      Tamanho: {analysis['content_length']:,} chars (Δ{improvements['size_reduction']:+.1f}%)")
        else:
            print(f"   {pdf_name}: ❌ ERRO - {result['error']}")
    
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   Testes bem-sucedidos: {successful_tests}/{len(PROBLEMATIC_CASES)}")
    print(f"   OCR utilizado: {ocr_used}/{successful_tests}")
    print(f"   Melhorias significativas: {significant_improvements}/{successful_tests}")
    print(f"   Melhorias moderadas: {moderate_improvements}/{successful_tests}")
    print(f"   Total de melhorias: {significant_improvements + moderate_improvements}/{successful_tests}")
    
    # Salvar resultados
    output_file = "ocr_optimized_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    # Avaliação final
    improvement_rate = (significant_improvements + moderate_improvements) / successful_tests if successful_tests > 0 else 0
    
    if improvement_rate >= 0.8:
        print(f"\n🎉 EXCELENTE: Melhorias em {improvement_rate*100:.0f}% dos casos!")
        print("   ✅ OCR seletivo otimizado funcionando perfeitamente!")
    elif improvement_rate >= 0.6:
        print(f"\n✅ BOM: Melhorias em {improvement_rate*100:.0f}% dos casos!")
        print("   🔧 Pequenos ajustes ainda necessários")
    elif improvement_rate >= 0.4:
        print(f"\n⚠️ MODERADO: Melhorias em {improvement_rate*100:.0f}% dos casos!")
        print("   🚧 Ajustes significativos necessários")
    else:
        print(f"\n❌ BAIXO: Melhorias em apenas {improvement_rate*100:.0f}% dos casos!")
        print("   🔄 Revisão completa do algoritmo necessária")

if __name__ == "__main__":
    main()

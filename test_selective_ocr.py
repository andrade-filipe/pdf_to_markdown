#!/usr/bin/env python3
"""
Teste do OCR seletivo nos casos problemáticos
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
    """Análise rápida da qualidade do conteúdo"""
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
    for line in lines:
        line = line.strip()
        if line:
            normalized = line.lower()
            if normalized in seen_lines:
                repeated_lines += 1
            else:
                seen_lines.add(normalized)
    
    # Contar palavras repetidas
    word_freq = {}
    all_text = ' '.join([line.strip() for line in lines if line.strip()])
    words = all_text.split()
    
    for word in words:
        word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
    
    max_word_repetition = max(word_freq.values()) if word_freq else 0
    
    # Verificar duplicação de conteúdo
    content_length = len(content)
    is_likely_duplicated = content_length > 50000
    
    return {
        'total_lines': total_lines,
        'non_empty_lines': non_empty_lines,
        'empty_lines': empty_lines,
        'density': density,
        'repeated_lines': repeated_lines,
        'max_word_repetition': max_word_repetition,
        'content_length': content_length,
        'is_likely_duplicated': is_likely_duplicated
    }

def main():
    print("🔍 TESTE DO OCR SELETIVO")
    print("=" * 60)
    print("✅ OCR aplicado apenas em páginas problemáticas")
    print("✅ Performance otimizada para hardware limitado")
    print("✅ Combinação inteligente de métodos")
    print("=" * 60)
    
    # Criar pipeline com OCR seletivo
    pipeline = ConversionPipeline(str(Path(MARKDOWN_DIR)))
    
    results = {}
    
    for pdf_name in PROBLEMATIC_CASES:
        print(f"\n📄 TESTANDO OCR SELETIVO: {pdf_name}")
        print("-" * 50)
        
        pdf_path = Path(PDF_DIR) / pdf_name
        md_path = Path(MARKDOWN_DIR) / f"{pdf_name.replace('.pdf', '.md')}"
        
        if not pdf_path.exists():
            print(f"❌ PDF não encontrado: {pdf_path}")
            continue
        
        try:
            # Converter com OCR seletivo
            print("🔄 Convertendo com OCR seletivo...")
            start_time = time.time()
            
            output_filename = f"{pdf_name.replace('.pdf', '.md')}"
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
            
            # Analisar resultado
            print("📊 Analisando resultado...")
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = analyze_content_quality(content)
            
            print(f"   📊 Linhas totais: {analysis['total_lines']:,}")
            print(f"   📝 Linhas com conteúdo: {analysis['non_empty_lines']:,}")
            print(f"   📈 Densidade: {analysis['density']:.3f}")
            print(f"   🔄 Linhas repetidas: {analysis['repeated_lines']}")
            print(f"   📚 Máx repetição de palavra: {analysis['max_word_repetition']}")
            print(f"   🔢 Tamanho do conteúdo: {analysis['content_length']:,} chars")
            
            # Comparar com versão sem OCR (se existir)
            if md_path.exists():
                print("\n📄 Comparando com versão sem OCR...")
                
                with open(md_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                
                old_analysis = analyze_content_quality(old_content)
                
                improvement_density = analysis['density'] - old_analysis['density']
                improvement_repetitions = old_analysis['repeated_lines'] - analysis['repeated_lines']
                improvement_word_repetitions = old_analysis['max_word_repetition'] - analysis['max_word_repetition']
                
                print(f"   📈 Melhoria na densidade: {improvement_density:+.3f}")
                print(f"   🔄 Redução de linhas repetidas: {improvement_repetitions:+d}")
                print(f"   📚 Redução de palavras repetidas: {improvement_word_repetitions:+d}")
                
                if (improvement_density > 0.05 or 
                    improvement_repetitions > 10 or 
                    improvement_word_repetitions > 100):
                    print("   🚀 MELHORIA SIGNIFICATIVA DETECTADA!")
            
            # Detectar problemas remanescentes
            problems = []
            
            if analysis['repeated_lines'] > 50:
                problems.append(f"Muitas linhas repetidas ({analysis['repeated_lines']})")
            
            if analysis['max_word_repetition'] > 200:
                problems.append(f"Palavras muito repetidas (máx: {analysis['max_word_repetition']})")
            
            if analysis['is_likely_duplicated']:
                problems.append("Possível duplicação de conteúdo")
            
            if problems:
                print(f"   ⚠️ Problemas remanescentes:")
                for problem in problems:
                    print(f"      - {problem}")
            else:
                print("   ✅ Nenhum problema detectado!")
            
            results[pdf_name] = {
                'analysis': analysis,
                'ocr_applied': ocr_applied,
                'ocr_pages': ocr_pages,
                'conversion_time': conversion_time,
                'problems': problems,
                'improvements': {
                    'density_improvement': improvement_density if md_path.exists() else 0,
                    'repetition_reduction': improvement_repetitions if md_path.exists() else 0,
                    'word_repetition_reduction': improvement_word_repetitions if md_path.exists() else 0
                }
            }
            
        except Exception as e:
            print(f"   ❌ Erro na conversão: {e}")
            results[pdf_name] = {'error': str(e)}
    
    # Resumo dos resultados
    print("\n🎯 RESUMO DOS RESULTADOS")
    print("=" * 60)
    
    successful_tests = 0
    ocr_used = 0
    improvements_detected = 0
    
    for pdf_name, result in results.items():
        if 'error' not in result:
            successful_tests += 1
            
            if result['ocr_applied']:
                ocr_used += 1
            
            analysis = result['analysis']
            improvements = result['improvements']
            
            status = "✅ MELHORADO"
            if (improvements['density_improvement'] > 0.05 or 
                improvements['repetition_reduction'] > 10 or 
                improvements['word_repetition_reduction'] > 100):
                status = "🚀 SIGNIFICATIVAMENTE MELHORADO"
            elif (improvements['density_improvement'] == 0 and 
                  improvements['repetition_reduction'] == 0 and 
                  improvements['word_repetition_reduction'] == 0):
                status = "🔄 IGUAL"
            
            ocr_info = f"OCR:{result['ocr_pages']}p" if result['ocr_applied'] else "SEM OCR"
            print(f"   {pdf_name}: {status} [{ocr_info}]")
            print(f"      Densidade: {analysis['density']:.3f} (Δ{improvements['density_improvement']:+.3f})")
            print(f"      Repetições: {analysis['repeated_lines']} (Δ{improvements['repetition_reduction']:+d})")
            print(f"      Palavras repetidas: {analysis['max_word_repetition']} (Δ{improvements['word_repetition_reduction']:+d})")
            
            if len(result['problems']) == 0:
                improvements_detected += 1
        else:
            print(f"   {pdf_name}: ❌ ERRO - {result['error']}")
    
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   Testes bem-sucedidos: {successful_tests}/{len(PROBLEMATIC_CASES)}")
    print(f"   OCR utilizado: {ocr_used}/{successful_tests}")
    print(f"   Melhorias detectadas: {improvements_detected}/{successful_tests}")
    
    # Salvar resultados
    output_file = "selective_ocr_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    if ocr_used > 0:
        print(f"\n🎉 SUCESSO: OCR seletivo foi aplicado em {ocr_used} casos!")
        if improvements_detected >= successful_tests * 0.7:
            print("   ✅ Melhorias funcionaram em pelo menos 70% dos casos!")
        else:
            print("   ⚠️ Melhorias precisam de ajustes adicionais")
    else:
        print(f"\n📝 NOTA: OCR não foi necessário - texto de boa qualidade")

if __name__ == "__main__":
    main()

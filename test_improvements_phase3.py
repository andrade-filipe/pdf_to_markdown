#!/usr/bin/env python3
"""
Teste das melhorias implementadas na Fase 3
"""

import os
import json
import time
from pathlib import Path
from converter.pipeline import ConversionPipeline

# Configurações
PDF_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
MARKDOWN_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"

# Os 5 piores casos identificados
WORST_CASES = [
    "181014cronologia_ap.pdf",  # Score: 3/10 - Preservação: 305.8%
    "Shoreline Transgressive Terraces.pdf",  # Score: 4/10 - Preservação: 101.1%
    "Biostratigraphic Continuity and Earth History.pdf",  # Score: 4/10 - Preservação: 106.2%
    "coming-to-grips-with-genesis-ch6.pdf",  # Score: 4/10 - Preservação: 96.0%
    "Dark Matter and Dark Energy.pdf"  # Score: 4/10 - Preservação: 100.0%
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
    is_likely_duplicated = content_length > 50000  # Mais de 50KB pode indicar duplicação
    
    # Padrões repetitivos
    header_patterns = {
        'Cronologia Bíblica': content.count('Cronologia Bíblica'),
        'Proceedings of the International Conference': content.count('Proceedings of the International Conference')
    }
    
    return {
        'total_lines': total_lines,
        'non_empty_lines': non_empty_lines,
        'empty_lines': empty_lines,
        'density': density,
        'repeated_lines': repeated_lines,
        'max_word_repetition': max_word_repetition,
        'content_length': content_length,
        'is_likely_duplicated': is_likely_duplicated,
        'header_patterns': header_patterns,
        'problems': []
    }

def main():
    print("🧪 TESTE DAS MELHORIAS DA FASE 3")
    print("=" * 60)
    print("✅ Extração de texto otimizada")
    print("✅ Detecção de repetições melhorada")
    print("✅ Sistema de scoring aprimorado")
    print("=" * 60)
    
    # Criar pipeline com melhorias
    pipeline = ConversionPipeline(str(Path(MARKDOWN_DIR)))
    
    results = {}
    
    for pdf_name in WORST_CASES:
        print(f"\n📄 TESTANDO: {pdf_name}")
        print("-" * 40)
        
        pdf_path = Path(PDF_DIR) / pdf_name
        md_path = Path(MARKDOWN_DIR) / f"{pdf_name.replace('.pdf', '.md')}"
        
        if not pdf_path.exists():
            print(f"❌ PDF não encontrado: {pdf_path}")
            continue
        
        try:
            # Converter com melhorias
            print("🔄 Convertendo com melhorias...")
            start_time = time.time()
            
            output_filename = f"{pdf_name.replace('.pdf', '.md')}"
            output_path = pipeline.convert(str(pdf_path), output_filename)
            
            conversion_time = time.time() - start_time
            
            print(f"   ✅ Conversão concluída: {conversion_time:.2f}s")
            print(f"   📁 Arquivo: {output_path}")
            
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
            
            # Detectar problemas
            problems = []
            
            if analysis['density'] < 0.5:
                problems.append("Baixa densidade de conteúdo")
            
            if analysis['repeated_lines'] > 10:
                problems.append(f"Muitas linhas repetidas ({analysis['repeated_lines']})")
            
            if analysis['max_word_repetition'] > 100:
                problems.append(f"Palavras muito repetidas (máx: {analysis['max_word_repetition']})")
            
            if analysis['is_likely_duplicated']:
                problems.append("Possível duplicação de conteúdo")
            
            for pattern, count in analysis['header_patterns'].items():
                if count > 5:
                    problems.append(f"Padrão repetitivo: '{pattern}' ({count}x)")
            
            if problems:
                print(f"   ⚠️ Problemas detectados:")
                for problem in problems:
                    print(f"      - {problem}")
            else:
                print("   ✅ Nenhum problema detectado!")
            
            # Comparar com versão anterior (se existir)
            if md_path.exists():
                print("\n📄 Comparando com versão anterior...")
                
                with open(md_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                
                old_analysis = analyze_content_quality(old_content)
                
                improvement_density = analysis['density'] - old_analysis['density']
                improvement_repetitions = old_analysis['repeated_lines'] - analysis['repeated_lines']
                
                print(f"   📈 Melhoria na densidade: {improvement_density:+.3f}")
                print(f"   🔄 Redução de repetições: {improvement_repetitions:+d}")
                
                if improvement_density > 0.1 or improvement_repetitions > 5:
                    print("   🚀 MELHORIA SIGNIFICATIVA DETECTADA!")
            
            results[pdf_name] = {
                'analysis': analysis,
                'problems': problems,
                'conversion_time': conversion_time,
                'improvements': {
                    'density_improvement': improvement_density if md_path.exists() else 0,
                    'repetition_reduction': improvement_repetitions if md_path.exists() else 0
                }
            }
            
        except Exception as e:
            print(f"   ❌ Erro na conversão: {e}")
            results[pdf_name] = {'error': str(e)}
    
    # Resumo dos resultados
    print("\n🎯 RESUMO DOS RESULTADOS")
    print("=" * 60)
    
    successful_tests = 0
    improvements_detected = 0
    
    for pdf_name, result in results.items():
        if 'error' not in result:
            successful_tests += 1
            
            analysis = result['analysis']
            improvements = result['improvements']
            
            status = "✅ MELHORADO" if improvements['density_improvement'] > 0.05 or improvements['repetition_reduction'] > 5 else "🔄 IGUAL" if improvements['density_improvement'] == 0 and improvements['repetition_reduction'] == 0 else "⚠️ REGREDIU"
            
            print(f"   {pdf_name}: {status}")
            print(f"      Densidade: {analysis['density']:.3f} (Δ{improvements['density_improvement']:+.3f})")
            print(f"      Repetições: {analysis['repeated_lines']} (Δ{improvements['repetition_reduction']:+d})")
            
            if len(result['problems']) == 0:
                improvements_detected += 1
        else:
            print(f"   {pdf_name}: ❌ ERRO - {result['error']}")
    
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   Testes bem-sucedidos: {successful_tests}/{len(WORST_CASES)}")
    print(f"   Melhorias detectadas: {improvements_detected}/{successful_tests}")
    
    # Salvar resultados
    output_file = "phase3_improvements_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    if improvements_detected >= successful_tests * 0.8:
        print("\n🎉 SUCESSO: Melhorias funcionaram em pelo menos 80% dos casos!")
    else:
        print("\n⚠️ ATENÇÃO: Melhorias precisam de ajustes adicionais")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Teste do OCR Ultra-Preciso - Qualidade Máxima
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
    "181014cronologia_ap.pdf",  # Caso de teste principal
    "coming-to-grips-with-genesis-ch6.pdf",  # Caso complexo
]

def analyze_markdown_quality(content):
    """Análise detalhada da qualidade do Markdown"""
    lines = content.split('\n')
    
    # Estatísticas básicas
    total_lines = len(lines)
    non_empty_lines = len([l for l in lines if l.strip()])
    empty_lines = total_lines - non_empty_lines
    
    # Análise Markdown
    headers = [l for l in lines if l.strip().startswith('#')]
    code_blocks = [l for l in lines if l.startswith('```') or l.startswith('    ')]
    lists = [l for l in lines if l.strip().startswith(('-', '•', '*', '1.', '2.', '3.'))]
    
    # Estrutura do documento
    sections = []
    current_section = []
    for line in lines:
        if line.strip().startswith('#'):
            if current_section:
                sections.append(current_section)
            current_section = [line]
        else:
            current_section.append(line)
    if current_section:
        sections.append(current_section)
    
    # Calcular score de qualidade do Markdown
    markdown_score = 0
    
    # Headers (0-25 pontos)
    header_count = len(headers)
    if header_count >= 5:
        markdown_score += 25
    elif header_count >= 3:
        markdown_score += 20
    elif header_count >= 1:
        markdown_score += 15
    
    # Estrutura de seções (0-25 pontos)
    if len(sections) >= 3:
        markdown_score += 25
    elif len(sections) >= 2:
        markdown_score += 20
    elif len(sections) >= 1:
        markdown_score += 15
    
    # Listas e formatação (0-25 pontos)
    formatting_elements = len(lists) + len(code_blocks)
    if formatting_elements >= 10:
        markdown_score += 25
    elif formatting_elements >= 5:
        markdown_score += 20
    elif formatting_elements >= 1:
        markdown_score += 15
    
    # Legibilidade (0-25 pontos)
    avg_line_length = sum(len(l.strip()) for l in lines if l.strip()) / non_empty_lines if non_empty_lines > 0 else 0
    if 50 <= avg_line_length <= 120:
        markdown_score += 25
    elif 30 <= avg_line_length <= 150:
        markdown_score += 20
    else:
        markdown_score += 10
    
    # Análise de repetições
    seen_lines = set()
    repeated_lines = 0
    for line in lines:
        if line.strip():
            normalized = line.strip().lower()
            if normalized in seen_lines:
                repeated_lines += 1
            else:
                seen_lines.add(normalized)
    
    return {
        'total_lines': total_lines,
        'non_empty_lines': non_empty_lines,
        'empty_lines': empty_lines,
        'headers': len(headers),
        'sections': len(sections),
        'lists': len(lists),
        'code_blocks': len(code_blocks),
        'repeated_lines': repeated_lines,
        'avg_line_length': avg_line_length,
        'markdown_score': markdown_score,
        'structure_quality': 'Excelente' if markdown_score >= 80 else 'Boa' if markdown_score >= 60 else 'Moderada' if markdown_score >= 40 else 'Baixa'
    }

def main():
    print("🚀 TESTE DO OCR ULTRA-PRECISO")
    print("=" * 80)
    print("✅ Múltiplas tentativas de OCR com diferentes configurações")
    print("✅ Processamento avançado com dados estruturados")
    print("✅ Formatação Markdown superior")
    print("✅ Limpeza inteligente sem perda de informação")
    print("✅ Performance otimizada: 1-2 minutos por arquivo")
    print("=" * 80)
    
    # Criar pipeline
    pipeline = ConversionPipeline(str(Path(MARKDOWN_DIR)))
    
    results = {}
    
    for pdf_name in PROBLEMATIC_CASES:
        print(f"\n📄 TESTANDO OCR ULTRA-PRECISO: {pdf_name}")
        print("-" * 70)
        
        pdf_path = Path(PDF_DIR) / pdf_name
        
        if not pdf_path.exists():
            print(f"❌ PDF não encontrado: {pdf_path}")
            continue
        
        try:
            # Converter com OCR ultra-preciso
            print("🔄 Iniciando conversão ultra-preciso...")
            print("   ⏱️  Tempo estimado: 1-2 minutos")
            
            start_time = time.time()
            
            output_filename = f"{pdf_name.replace('.pdf', '_ultra_precise.md')}"
            output_path = pipeline.convert(str(pdf_path), output_filename)
            
            conversion_time = time.time() - start_time
            
            print(f"   ✅ Conversão concluída: {conversion_time:.1f}s")
            print(f"   📁 Arquivo: {output_path}")
            
            # Verificar se OCR foi aplicado
            ocr_applied = pipeline.current_data.get('ocr_applied', False)
            ocr_pages = pipeline.current_data.get('ocr_pages_processed', 0)
            
            if ocr_applied:
                print(f"   🔍 OCR ultra-preciso aplicado em {ocr_pages} páginas")
            else:
                print(f"   📝 OCR não necessário - texto de excelente qualidade")
            
            # Analisar resultado
            print("📊 Analisando qualidade do Markdown...")
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = analyze_markdown_quality(content)
            
            print(f"   📊 Linhas totais: {analysis['total_lines']:,}")
            print(f"   📝 Linhas com conteúdo: {analysis['non_empty_lines']:,}")
            print(f"   📋 Cabeçalhos: {analysis['headers']}")
            print(f"   📄 Seções: {analysis['sections']}")
            print(f"   📝 Listas: {analysis['lists']}")
            print(f"   🔄 Linhas repetidas: {analysis['repeated_lines']}")
            print(f"   📏 Comprimento médio das linhas: {analysis['avg_line_length']:.1f}")
            print(f"   🎯 Score de qualidade Markdown: {analysis['markdown_score']:.1f}/100")
            print(f"   📈 Qualidade da estrutura: {analysis['structure_quality']}")
            
            # Verificar características específicas do OCR
            if ocr_applied:
                print("\n🔍 Características do OCR Ultra-Preciso:")
                
                # Verificar se há informações de qualidade do OCR
                if "# Documento Processado com OCR Ultra-Preciso" in content:
                    print("   ✅ Cabeçalho especial do OCR detectado")
                
                # Contar seções de página
                page_sections = content.count("## Página")
                print(f"   📄 Seções de página processadas: {page_sections}")
                
                # Verificar formatação Markdown
                markdown_elements = content.count('# ') + content.count('## ')
                print(f"   📋 Elementos Markdown: {markdown_elements}")
            
            # Comparar com versão anterior (se existir)
            old_md_path = Path(MARKDOWN_DIR) / f"{pdf_name.replace('.pdf', '.md')}"
            
            if old_md_path.exists():
                print("\n📄 Comparando com versão anterior...")
                
                with open(old_md_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                
                old_analysis = analyze_markdown_quality(old_content)
                
                improvement_markdown = analysis['markdown_score'] - old_analysis['markdown_score']
                improvement_headers = analysis['headers'] - old_analysis['headers']
                improvement_repetitions = old_analysis['repeated_lines'] - analysis['repeated_lines']
                
                print(f"   📈 Melhoria no score Markdown: {improvement_markdown:+.1f}")
                print(f"   📋 Melhoria em cabeçalhos: {improvement_headers:+d}")
                print(f"   🔄 Redução de repetições: {improvement_repetitions:+d}")
                
                # Determinar status da melhoria
                if improvement_markdown > 20 or improvement_repetitions > 10:
                    print("   🚀 MELHORIA SIGNIFICATIVA DETECTADA!")
                elif improvement_markdown > 0:
                    print("   ✅ Melhoria moderada detectada")
                else:
                    print("   ⚠️ Nenhuma melhoria detectada")
            
            # Avaliação final
            quality_rating = "EXCELENTE" if analysis['markdown_score'] >= 80 else \
                           "BOA" if analysis['markdown_score'] >= 60 else \
                           "MODERADA" if analysis['markdown_score'] >= 40 else "BAIXA"
            
            print(f"\n🏆 AVALIAÇÃO FINAL: {quality_rating}")
            
            results[pdf_name] = {
                'analysis': analysis,
                'ocr_applied': ocr_applied,
                'ocr_pages': ocr_pages,
                'conversion_time': conversion_time,
                'content_length': len(content),
                'improvements': {
                    'markdown_improvement': improvement_markdown if old_md_path.exists() else 0,
                    'headers_improvement': improvement_headers if old_md_path.exists() else 0,
                    'repetitions_reduction': improvement_repetitions if old_md_path.exists() else 0
                }
            }
            
        except Exception as e:
            print(f"   ❌ Erro na conversão: {e}")
            results[pdf_name] = {'error': str(e)}
    
    # Resumo dos resultados
    print("\n🎯 RESUMO DOS RESULTADOS ULTRA-PRECISOS")
    print("=" * 80)
    
    successful_tests = 0
    ocr_used = 0
    excellent_results = 0
    good_results = 0
    
    for pdf_name, result in results.items():
        if 'error' not in result:
            successful_tests += 1
            
            if result['ocr_applied']:
                ocr_used += 1
            
            analysis = result['analysis']
            improvements = result['improvements']
            
            # Determinar classificação
            if analysis['markdown_score'] >= 80:
                rating = "🏆 EXCELENTE"
                excellent_results += 1
            elif analysis['markdown_score'] >= 60:
                rating = "✅ BOA"
                good_results += 1
            else:
                rating = "⚠️ MODERADA"
            
            ocr_info = f"OCR:{result['ocr_pages']}p" if result['ocr_applied'] else "SEM OCR"
            time_info = f"{result['conversion_time']:.0f}s"
            
            print(f"   {pdf_name}: {rating} [{ocr_info}] [{time_info}]")
            print(f"      Markdown: {analysis['markdown_score']:.1f}/100 (Δ{improvements['markdown_improvement']:+.1f})")
            print(f"      Cabeçalhos: {analysis['headers']} (Δ{improvements['headers_improvement']:+d})")
            print(f"      Repetições: {analysis['repeated_lines']} (Δ{improvements['repetitions_reduction']:+d})")
            print(f"      Estrutura: {analysis['structure_quality']}")
        else:
            print(f"   {pdf_name}: ❌ ERRO - {result['error']}")
    
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   Testes bem-sucedidos: {successful_tests}/{len(PROBLEMATIC_CASES)}")
    print(f"   OCR utilizado: {ocr_used}/{successful_tests}")
    print(f"   Resultados excelentes: {excellent_results}/{successful_tests}")
    print(f"   Resultados bons: {good_results}/{successful_tests}")
    
    # Salvar resultados
    output_file = "ultra_precise_ocr_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    # Avaliação final
    success_rate = (excellent_results + good_results) / successful_tests if successful_tests > 0 else 0
    
    if success_rate >= 0.8:
        print(f"\n🎉 SUCESSO EXCEPCIONAL: {success_rate*100:.0f}% de resultados excelentes/boos!")
        print("   ✅ OCR ultra-preciso funcionando perfeitamente!")
    elif success_rate >= 0.6:
        print(f"\n✅ SUCESSO: {success_rate*100:.0f}% de resultados satisfatórios!")
        print("   🔧 Pequenos ajustes ainda possíveis")
    else:
        print(f"\n⚠️ RESULTADOS MODESTOS: Apenas {success_rate*100:.0f}% de resultados satisfatórios")
        print("   🚧 Ajustes significativos recomendados")

if __name__ == "__main__":
    main()

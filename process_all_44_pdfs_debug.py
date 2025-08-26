#!/usr/bin/env python3
"""
Processamento Debug de todos os 44 PDFs
Análise crítica completa: dados extraídos + resultados Markdown
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from converter.pipeline import ConversionPipeline

# Configurações
PDF_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF"
MARKDOWN_DIR = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown"
DEBUG_OUTPUT_DIR = Path("debug_analysis")

# Criar diretório de debug
DEBUG_OUTPUT_DIR.mkdir(exist_ok=True)

def get_all_pdfs():
    """Obtém todos os PDFs do diretório"""
    pdf_files = list(Path(PDF_DIR).glob("*.pdf"))
    return sorted(pdf_files)

def analyze_extracted_data(raw_text, tables, images, font_info):
    """Análise detalhada dos dados extraídos do PDF"""
    analysis = {
        'raw_text_length': len(raw_text),
        'text_lines': len(raw_text.split('\n')),
        'text_words': len(raw_text.split()),
        'tables_count': len(tables),
        'images_count': len(images),
        'font_info_count': len(font_info),
        'issues': []
    }
    
    # Problemas no texto extraído
    lines = raw_text.split('\n')
    
    # 1. Linhas vazias excessivas
    empty_lines = len([l for l in lines if not l.strip()])
    empty_line_ratio = empty_lines / len(lines) if lines else 0
    if empty_line_ratio > 0.3:
        analysis['issues'].append(f"Muitas linhas vazias: {empty_line_ratio:.1%}")
    
    # 2. Linhas muito curtas (fragmentação)
    short_lines = len([l for l in lines if len(l.strip()) < 5 and l.strip()])
    if short_lines > len(lines) * 0.2:
        analysis['issues'].append(f"Muitas linhas curtas: {short_lines} linhas")
    
    # 3. Palavras repetidas excessivamente
    words = raw_text.split()
    word_freq = {}
    for word in words:
        word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
    
    max_repetitions = max(word_freq.values()) if word_freq else 0
    if max_repetitions > 100:
        analysis['issues'].append(f"Palavra muito repetida: {max_repetitions}x")
    
    # 4. Caracteres estranhos
    strange_chars = len([c for c in raw_text if ord(c) > 127 and c not in 'áéíóúâêîôûãõç'])
    if strange_chars > len(raw_text) * 0.05:
        analysis['issues'].append(f"Muitos caracteres estranhos: {strange_chars}")
    
    # 5. Texto muito pequeno
    if len(raw_text) < 1000:
        analysis['issues'].append(f"Texto muito pequeno: {len(raw_text)} chars")
    
    # 6. Duplicação de conteúdo
    if len(raw_text) > 50000:
        analysis['issues'].append("Possível duplicação de conteúdo (texto muito longo)")
    
    return analysis

def analyze_markdown_output(content):
    """Análise detalhada do output Markdown"""
    analysis = {
        'total_length': len(content),
        'total_lines': len(content.split('\n')),
        'content_lines': len([l for l in content.split('\n') if l.strip()]),
        'headers': len([l for l in content.split('\n') if l.strip().startswith('#')]),
        'lists': len([l for l in content.split('\n') if l.strip().startswith(('-', '•', '*', '1.', '2.'))]),
        'issues': []
    }
    
    lines = content.split('\n')
    
    # 1. Estrutura Markdown
    if analysis['headers'] == 0:
        analysis['issues'].append("Nenhum cabeçalho Markdown detectado")
    elif analysis['headers'] < 3:
        analysis['issues'].append(f"Poucos cabeçalhos: {analysis['headers']}")
    
    # 2. Densidade de conteúdo
    density = analysis['content_lines'] / analysis['total_lines'] if analysis['total_lines'] > 0 else 0
    if density < 0.3:
        analysis['issues'].append(f"Baixa densidade de conteúdo: {density:.1%}")
    
    # 3. Comprimento das linhas
    line_lengths = [len(l) for l in lines if l.strip()]
    if line_lengths:
        avg_length = sum(line_lengths) / len(line_lengths)
        if avg_length < 20:
            analysis['issues'].append(f"Linhas muito curtas (média: {avg_length:.1f} chars)")
        elif avg_length > 200:
            analysis['issues'].append(f"Linhas muito longas (média: {avg_length:.1f} chars)")
    
    # 4. Repetições
    seen_lines = set()
    repeated_lines = 0
    for line in lines:
        if line.strip():
            normalized = line.strip().lower()
            if normalized in seen_lines:
                repeated_lines += 1
            else:
                seen_lines.add(normalized)
    
    if repeated_lines > analysis['content_lines'] * 0.1:
        analysis['issues'].append(f"Muitas linhas repetidas: {repeated_lines}")
    
    # 5. Formatação específica
    if '```' in content:
        analysis['issues'].append("Detectados blocos de código (pode indicar erro de formatação)")
    
    # 6. Conteúdo vazio ou muito pequeno
    if len(content) < 500:
        analysis['issues'].append(f"Conteúdo muito pequeno: {len(content)} chars")
    
    return analysis

def create_detailed_report(pdf_name, extracted_analysis, markdown_analysis, ocr_info, conversion_time):
    """Cria relatório detalhado para um PDF"""
    report = f"""# Análise Debug: {pdf_name}

## Informações Gerais
- **Data/Hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tempo de Conversão**: {conversion_time:.2f}s
- **OCR Aplicado**: {ocr_info['applied']}
- **Páginas OCR**: {ocr_info['pages']}

## Análise dos Dados Extraídos

### Estatísticas Básicas
- **Tamanho do texto**: {extracted_analysis['raw_text_length']:,} caracteres
- **Linhas de texto**: {extracted_analysis['text_lines']:,}
- **Palavras**: {extracted_analysis['text_words']:,}
- **Tabelas**: {extracted_analysis['tables_count']}
- **Imagens**: {extracted_analysis['images_count']}
- **Informações de fonte**: {extracted_analysis['font_info_count']}

### Problemas Detectados na Extração
"""
    
    if extracted_analysis['issues']:
        for issue in extracted_analysis['issues']:
            report += f"- ❌ {issue}\n"
    else:
        report += "- ✅ Nenhum problema detectado\n"
    
    report += f"""
## Análise do Output Markdown

### Estatísticas Básicas
- **Tamanho total**: {markdown_analysis['total_length']:,} caracteres
- **Linhas totais**: {markdown_analysis['total_lines']:,}
- **Linhas com conteúdo**: {markdown_analysis['content_lines']:,}
- **Cabeçalhos**: {markdown_analysis['headers']}
- **Listas**: {markdown_analysis['lists']}

### Problemas Detectados no Markdown
"""
    
    if markdown_analysis['issues']:
        for issue in markdown_analysis['issues']:
            report += f"- ❌ {issue}\n"
    else:
        report += "- ✅ Nenhum problema detectado\n"
    
    # Calcular score de qualidade
    extracted_score = 100 - len(extracted_analysis['issues']) * 25
    markdown_score = 100 - len(markdown_analysis['issues']) * 25
    total_score = (extracted_score + markdown_score) / 2
    
    report += f"""
## Avaliação Final
- **Score Extração**: {max(0, extracted_score):.1f}/100
- **Score Markdown**: {max(0, markdown_score):.1f}/100
- **Score Total**: {max(0, total_score):.1f}/100
- **Status**: {'✅ EXCELENTE' if total_score >= 80 else '✅ BOM' if total_score >= 60 else '⚠️ MODERADO' if total_score >= 40 else '❌ PROBLEMÁTICO'}

---
"""
    
    return report, total_score

def main():
    print("🔍 PROCESSAMENTO DEBUG DE TODOS OS 44 PDFs")
    print("=" * 80)
    print("📊 Análise crítica completa: dados extraídos + resultados Markdown")
    print("📝 Documentação detalhada de todos os problemas encontrados")
    print("=" * 80)
    
    # Obter todos os PDFs
    pdf_files = get_all_pdfs()
    print(f"📚 Encontrados {len(pdf_files)} arquivos PDF para processar")
    
    # Criar pipeline
    pipeline = ConversionPipeline(str(Path(MARKDOWN_DIR)))
    
    # Resultados gerais
    all_results = []
    successful_conversions = 0
    failed_conversions = 0
    
    # Relatório principal
    main_report = f"""# RELATÓRIO GERAL DE DEBUG - TODOS OS 44 PDFs

**Data/Hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total de PDFs**: {len(pdf_files)}

## Resumo Executivo

"""
    
    for i, pdf_path in enumerate(pdf_files, 1):
        pdf_name = pdf_path.name
        print(f"\n📄 [{i}/{len(pdf_files)}] PROCESSANDO: {pdf_name}")
        print("-" * 60)
        
        try:
            # Converter PDF
            conversion_start = time.time()
            
            output_filename = f"{pdf_name.replace('.pdf', '.md')}"
            output_path = pipeline.convert(str(pdf_path), output_filename)
            
            conversion_time = time.time() - conversion_start
            
            print(f"   ✅ Conversão concluída: {conversion_time:.2f}s")
            
            # Obter dados da conversão
            ocr_applied = pipeline.current_data.get('ocr_applied', False)
            ocr_pages = pipeline.current_data.get('ocr_pages_processed', 0)
            
            # Analisar dados extraídos (antes da conversão)
            print("   🔍 Analisando dados extraídos...")
            raw_text = pipeline.current_data.get('raw_text', '')
            tables = pipeline.current_data.get('tables', [])
            images = pipeline.current_data.get('images', [])
            font_info = pipeline.current_data.get('font_info', [])
            
            extracted_analysis = analyze_extracted_data(raw_text, tables, images, font_info)
            
            print(f"      Texto: {extracted_analysis['raw_text_length']:,} chars")
            print(f"      Problemas: {len(extracted_analysis['issues'])}")
            
            # Analisar output Markdown
            print("   📝 Analisando output Markdown...")
            with open(output_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            markdown_analysis = analyze_markdown_output(markdown_content)
            
            print(f"      Markdown: {markdown_analysis['total_length']:,} chars")
            print(f"      Problemas: {len(markdown_analysis['issues'])}")
            
            # Criar relatório detalhado
            ocr_info = {'applied': ocr_applied, 'pages': ocr_pages}
            detailed_report, score = create_detailed_report(
                pdf_name, extracted_analysis, markdown_analysis, ocr_info, conversion_time
            )
            
            # Salvar relatório individual
            report_filename = f"debug_{pdf_name.replace('.pdf', '.md')}"
            report_path = DEBUG_OUTPUT_DIR / report_filename
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(detailed_report)
            
            # Adicionar ao relatório principal
            all_results.append({
                'pdf_name': pdf_name,
                'score': score,
                'extracted_issues': len(extracted_analysis['issues']),
                'markdown_issues': len(markdown_analysis['issues']),
                'ocr_applied': ocr_applied,
                'ocr_pages': ocr_pages,
                'conversion_time': conversion_time,
                'report_file': report_filename
            })
            
            successful_conversions += 1
            
            # Status da conversão
            if score >= 80:
                status = "🏆 EXCELENTE"
            elif score >= 60:
                status = "✅ BOM"
            elif score >= 40:
                status = "⚠️ MODERADO"
            else:
                status = "❌ PROBLEMÁTICO"
            
            print(f"   🎯 Score: {score:.1f}/100 - {status}")
            
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            failed_conversions += 1
            
            all_results.append({
                'pdf_name': pdf_name,
                'score': 0,
                'extracted_issues': 999,
                'markdown_issues': 999,
                'ocr_applied': False,
                'ocr_pages': 0,
                'conversion_time': 0,
                'report_file': 'ERRO',
                'error': str(e)
            })
    
    # Gerar relatório final
    print(f"\n📊 GERANDO RELATÓRIO FINAL...")
    
    # Estatísticas gerais
    successful_scores = [r['score'] for r in all_results if r['score'] > 0]
    avg_score = sum(successful_scores) / len(successful_scores) if successful_scores else 0
    
    excellent_count = len([r for r in all_results if r['score'] >= 80])
    good_count = len([r for r in all_results if 60 <= r['score'] < 80])
    moderate_count = len([r for r in all_results if 40 <= r['score'] < 60])
    poor_count = len([r for r in all_results if 0 < r['score'] < 40])
    error_count = len([r for r in all_results if r['score'] == 0 and 'error' in r])
    
    main_report += f"""
## Estatísticas Gerais
- **Conversões bem-sucedidas**: {successful_conversions}/{len(pdf_files)} ({successful_conversions/len(pdf_files)*100:.1f}%)
- **Falhas**: {failed_conversions}/{len(pdf_files)} ({failed_conversions/len(pdf_files)*100:.1f}%)
- **Score médio**: {avg_score:.1f}/100

## Distribuição de Qualidade
- 🏆 **Excelente** (≥80): {excellent_count} PDFs
- ✅ **Bom** (60-79): {good_count} PDFs  
- ⚠️ **Moderado** (40-59): {moderate_count} PDFs
- ❌ **Problemático** (1-39): {poor_count} PDFs
- 💥 **Erro**: {error_count} PDFs

## Problemas Mais Frequentes

### Problemas na Extração
"""
    
    # Análise de problemas frequentes
    all_extracted_issues = []
    all_markdown_issues = []
    
    for result in all_results:
        if 'error' not in result:
            # Ler relatório detalhado para extrair problemas
            report_path = DEBUG_OUTPUT_DIR / result['report_file']
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                    
                    # Extrair problemas da extração
                    if "### Problemas Detectados na Extração" in report_content:
                        extraction_section = report_content.split("### Problemas Detectados na Extração")[1].split("##")[0]
                        issues = [line.strip()[4:] for line in extraction_section.split('\n') if line.strip().startswith('- ❌')]
                        all_extracted_issues.extend(issues)
                    
                    # Extrair problemas do Markdown
                    if "### Problemas Detectados no Markdown" in report_content:
                        markdown_section = report_content.split("### Problemas Detectados no Markdown")[1].split("##")[0]
                        issues = [line.strip()[4:] for line in markdown_section.split('\n') if line.strip().startswith('- ❌')]
                        all_markdown_issues.extend(issues)
    
    # Contar problemas mais frequentes
    from collections import Counter
    extracted_counter = Counter(all_extracted_issues)
    markdown_counter = Counter(all_markdown_issues)
    
    main_report += "\n**Problemas mais frequentes na extração:**\n"
    for issue, count in extracted_counter.most_common(5):
        percentage = count / successful_conversions * 100
        main_report += f"- {issue}: {count}x ({percentage:.1f}% dos PDFs)\n"
    
    main_report += "\n**Problemas mais frequentes no Markdown:**\n"
    for issue, count in markdown_counter.most_common(5):
        percentage = count / successful_conversions * 100
        main_report += f"- {issue}: {count}x ({percentage:.1f}% dos PDFs)\n"
    
    main_report += f"""
## Resultados Individuais

| PDF | Score | Extração | Markdown | OCR | Tempo | Status |
|-----|-------|----------|----------|-----|-------|--------|
"""
    
    # Ordenar por score
    sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=True)
    
    for result in sorted_results:
        pdf_name = result['pdf_name']
        score = result['score']
        extracted_issues = result['extracted_issues']
        markdown_issues = result['markdown_issues']
        ocr_info = f"{result['ocr_pages']}p" if result['ocr_applied'] else "Não"
        time = f"{result['conversion_time']:.1f}s"
        
        if score >= 80:
            status = "🏆"
        elif score >= 60:
            status = "✅"
        elif score >= 40:
            status = "⚠️"
        elif 'error' in result:
            status = "💥"
        else:
            status = "❌"
        
        main_report += f"| {pdf_name} | {score:.1f} | {extracted_issues} | {markdown_issues} | {ocr_info} | {time} | {status} |\n"
    
    main_report += f"""
## Arquivos de Relatório Individual
Todos os relatórios detalhados estão disponíveis em: `{DEBUG_OUTPUT_DIR}/`

## Próximos Passos Recomendados
1. **Analisar PDFs com score < 60** para identificar padrões de problemas
2. **Revisar problemas mais frequentes** na extração e Markdown
3. **Implementar correções** para os problemas identificados
4. **Retestar** os PDFs problemáticos após as correções
"""
    
    # Salvar relatório principal
    main_report_path = DEBUG_OUTPUT_DIR / "RELATORIO_GERAL_DEBUG.md"
    with open(main_report_path, 'w', encoding='utf-8') as f:
        f.write(main_report)
    
    # Salvar dados JSON para análise posterior
    json_path = DEBUG_OUTPUT_DIR / "debug_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 RESUMO FINAL:")
    print(f"   PDFs processados: {len(pdf_files)}")
    print(f"   Conversões bem-sucedidas: {successful_conversions}")
    print(f"   Falhas: {failed_conversions}")
    print(f"   Score médio: {avg_score:.1f}/100")
    print(f"   Excelente/Bom: {excellent_count + good_count}/{len(pdf_files)}")
    
    print(f"\n💾 RELATÓRIOS SALVOS:")
    print(f"   Relatório geral: {main_report_path}")
    print(f"   Dados JSON: {json_path}")
    print(f"   Relatórios individuais: {DEBUG_OUTPUT_DIR}/")
    
    if avg_score >= 70:
        print(f"\n🎉 RESULTADO GERAL: EXCELENTE!")
    elif avg_score >= 50:
        print(f"\n✅ RESULTADO GERAL: BOM")
    else:
        print(f"\n⚠️ RESULTADO GERAL: PRECISA DE MELHORIAS")

if __name__ == "__main__":
    main()

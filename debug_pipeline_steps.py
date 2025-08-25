#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/andrade/Repos/pdf_to_markdown')

from converter.pipeline import ConversionPipeline
from converter.steps.text_extraction_step import TextExtractionStep
from converter.steps.cleanup_step import CleanupStep

def debug_pipeline_steps():
    """Debuga cada etapa do pipeline para ver onde o conteúdo está sendo perdido"""
    pdf_path = "/home/andrade/Documentos/quantum/pdf/quantum-exportar-xls.pdf"
    
    print("🔍 DEBUGANDO ETAPAS DO PIPELINE - quantum-exportar-xls.pdf")
    print("=" * 60)
    
    # 1. Extração de texto
    print("\n1️⃣ ETAPA: TextExtraction")
    text_step = TextExtractionStep()
    context = {'pdf_path': pdf_path}
    context = text_step.process(context)
    
    raw_text = context.get('raw_text', '')
    print(f"   Texto bruto extraído: {len(raw_text)} caracteres")
    print(f"   Primeiros 500 caracteres: {raw_text[:500]}...")
    
    # Verificar conteúdo Excel no texto bruto
    excel_count = raw_text.count('Excel')
    export_count = raw_text.count('Export')
    template_count = raw_text.count('Template')
    print(f"   Palavras-chave encontradas:")
    print(f"     - Excel: {excel_count}")
    print(f"     - Export: {export_count}")
    print(f"     - Template: {template_count}")
    
    # 2. Cleanup
    print("\n2️⃣ ETAPA: Cleanup")
    cleanup_step = CleanupStep()
    context = cleanup_step.process(context)
    
    cleaned_text = context.get('cleaned_text', '')
    print(f"   Texto limpo: {len(cleaned_text)} caracteres")
    print(f"   Primeiros 500 caracteres: {cleaned_text[:500]}...")
    
    # Verificar conteúdo Excel no texto limpo
    excel_count_clean = cleaned_text.count('Excel')
    export_count_clean = cleaned_text.count('Export')
    template_count_clean = cleaned_text.count('Template')
    print(f"   Palavras-chave após cleanup:")
    print(f"     - Excel: {excel_count_clean}")
    print(f"     - Export: {export_count_clean}")
    print(f"     - Template: {template_count_clean}")
    
    # Verificar se houve perda
    if excel_count != excel_count_clean:
        print(f"   ⚠️  PERDA DETECTADA: Excel {excel_count} -> {excel_count_clean}")
    if export_count != export_count_clean:
        print(f"   ⚠️  PERDA DETECTADA: Export {export_count} -> {export_count_clean}")
    if template_count != template_count_clean:
        print(f"   ⚠️  PERDA DETECTADA: Template {template_count} -> {template_count_clean}")
    
    # 3. Verificar seções importantes
    print("\n3️⃣ SEÇÕES IMPORTANTES:")
    sections = ['Resultado Regra de Negócio', 'Diagrama Regra de Negócio', 'Sumário de Regras', 'Detalhamento do Código']
    
    for section in sections:
        count_raw = raw_text.count(section)
        count_clean = cleaned_text.count(section)
        print(f"   {section}: {count_raw} -> {count_clean}")
    
    # 4. Verificar onde está o conteúdo Excel
    print("\n4️⃣ LOCALIZAÇÃO DO CONTEÚDO EXCEL:")
    lines = cleaned_text.split('\n')
    excel_lines = []
    
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in ['Excel', 'Export', 'Template']):
            excel_lines.append((i+1, line.strip()))
    
    if excel_lines:
        print(f"   Encontradas {len(excel_lines)} linhas com conteúdo Excel:")
        for line_num, content in excel_lines[:10]:
            print(f"     {line_num:4d}: {content}")
        if len(excel_lines) > 10:
            print(f"     ... e mais {len(excel_lines) - 10} linhas")
    else:
        print("   ❌ Nenhuma linha com conteúdo Excel encontrada!")
    
    return context

if __name__ == "__main__":
    debug_pipeline_steps()

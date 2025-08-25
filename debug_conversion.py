#!/usr/bin/env python3
"""
Script para converter e debugar cada PDF individualmente
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import re
from converter.pipeline import ConversionPipeline

def analyze_pdf_before_conversion(pdf_path):
    """Análise detalhada do PDF antes da conversão"""
    try:
        doc = fitz.open(pdf_path)
        
        analysis = {
            'total_pages': len(doc),
            'total_words': 0,
            'total_images': 0,
            'page_details': [],
            'issues': []
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            words = re.findall(r'\b\w+\b', text.lower())
            images = page.get_images()
            
            # Detectar problemas na página
            page_issues = []
            
            # Verificar se há texto
            if len(words) < 10:
                page_issues.append("Pouco texto")
            
            # Verificar caracteres estranhos
            strange_chars = sum(1 for char in text if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
            if strange_chars > len(text) * 0.1:
                page_issues.append(f"Muitos caracteres estranhos ({strange_chars})")
            
            page_detail = {
                'page': page_num + 1,
                'words': len(words),
                'images': len(images),
                'issues': page_issues,
                'text_sample': text[:200] + "..." if len(text) > 200 else text
            }
            
            analysis['page_details'].append(page_detail)
            analysis['total_words'] += len(words)
            analysis['total_images'] += len(images)
            
            if page_issues:
                analysis['issues'].extend([f"Página {page_num + 1}: {', '.join(page_issues)}"])
        
        doc.close()
        return analysis
        
    except Exception as e:
        return {'error': str(e)}

def analyze_markdown_after_conversion(markdown_path):
    """Análise detalhada do Markdown após conversão"""
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'lines': len(content.split('\n')),
            'words': len(re.findall(r'\b\w+\b', content.lower())),
            'titles': len([line for line in content.split('\n') if line.startswith('#')]),
            'lists': len([line for line in content.split('\n') if re.match(r'^\s*[-•*]\s', line)]),
            'images': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)),
            'issues': []
        }
        
        # Detectar problemas
        if analysis['words'] < 50:
            analysis['issues'].append("Muito pouco texto")
        
        if analysis['titles'] < 3:
            analysis['issues'].append("Poucos títulos")
        
        # Caracteres corrompidos
        corrupted_chars = sum(1 for char in content if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
        if corrupted_chars > len(content) * 0.05:
            analysis['issues'].append(f"Muitos caracteres corrompidos ({corrupted_chars})")
        
        return analysis
        
    except Exception as e:
        return {'error': str(e)}

def debug_conversion(pdf_path, output_dir):
    """Converte um PDF e faz debug detalhado"""
    pdf_name = Path(pdf_path).name
    print(f"\n{'='*80}")
    print(f"🔄 CONVERTENDO: {pdf_name}")
    print(f"{'='*80}")
    
    # 1. Análise prévia do PDF
    print(f"\n📄 ANÁLISE PRÉVIA DO PDF:")
    pdf_analysis = analyze_pdf_before_conversion(pdf_path)
    
    if 'error' in pdf_analysis:
        print(f"❌ Erro ao analisar PDF: {pdf_analysis['error']}")
        return False
    
    print(f"  • Páginas: {pdf_analysis['total_pages']}")
    print(f"  • Palavras: {pdf_analysis['total_words']}")
    print(f"  • Imagens: {pdf_analysis['total_images']}")
    
    if pdf_analysis['issues']:
        print(f"  ⚠️ Problemas detectados:")
        for issue in pdf_analysis['issues'][:5]:  # Mostrar apenas os primeiros 5
            print(f"    - {issue}")
    
    # 2. Conversão
    print(f"\n🔄 INICIANDO CONVERSÃO:")
    try:
        pipeline = ConversionPipeline(str(output_dir))
        output_path = pipeline.convert(pdf_path)
        
        if output_path.exists():
            print(f"✅ Conversão concluída: {output_path.name}")
        else:
            print(f"❌ Arquivo não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        return False
    
    # 3. Análise pós-conversão
    print(f"\n📝 ANÁLISE PÓS-CONVERSÃO:")
    md_analysis = analyze_markdown_after_conversion(output_path)
    
    if 'error' in md_analysis:
        print(f"❌ Erro ao analisar Markdown: {md_analysis['error']}")
        return False
    
    print(f"  • Linhas: {md_analysis['lines']}")
    print(f"  • Palavras: {md_analysis['words']}")
    print(f"  • Títulos: {md_analysis['titles']}")
    print(f"  • Listas: {md_analysis['lists']}")
    print(f"  • Imagens: {md_analysis['images']}")
    
    if md_analysis['issues']:
        print(f"  ⚠️ Problemas detectados:")
        for issue in md_analysis['issues']:
            print(f"    - {issue}")
    
    # 4. Comparação e taxa de sucesso
    if pdf_analysis['total_words'] > 0:
        content_ratio = min(md_analysis['words'] / pdf_analysis['total_words'], 1.0)
        print(f"\n📊 TAXA DE SUCESSO:")
        print(f"  • Preservação de conteúdo: {content_ratio*100:.1f}%")
        
        if content_ratio < 0.5:
            print(f"  ⚠️ ALERTA: Baixa preservação de conteúdo!")
            return False
        elif content_ratio < 0.8:
            print(f"  ⚠️ ATENÇÃO: Preservação moderada de conteúdo")
        else:
            print(f"  ✅ Boa preservação de conteúdo")
    
    return True

def main():
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    output_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown Debug")
    
    # Criar diretório de saída
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Listar todos os PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📚 Encontrados {len(pdf_files)} arquivos PDF para converter e debugar")
    
    # Estatísticas
    success_count = 0
    error_count = 0
    errors = []
    
    # Converter cada PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{'#'*80}")
        print(f"📊 [{i}/{len(pdf_files)}] PROCESSANDO: {pdf_file.name}")
        print(f"{'#'*80}")
        
        try:
            success = debug_conversion(str(pdf_file), str(output_dir))
            
            if success:
                success_count += 1
                print(f"✅ SUCESSO: {pdf_file.name}")
            else:
                error_count += 1
                errors.append(pdf_file.name)
                print(f"❌ FALHA: {pdf_file.name}")
                
        except Exception as e:
            error_count += 1
            errors.append(f"{pdf_file.name}: {e}")
            print(f"❌ ERRO: {pdf_file.name} - {e}")
    
    # Relatório final
    print(f"\n{'='*80}")
    print(f"📊 RELATÓRIO FINAL DE DEBUG")
    print(f"{'='*80}")
    print(f"✅ Sucessos: {success_count}")
    print(f"❌ Erros: {error_count}")
    print(f"📈 Taxa de sucesso: {(success_count/(success_count+error_count)*100):.1f}%")
    
    if errors:
        print(f"\n❌ ARQUIVOS COM PROBLEMAS:")
        for error in errors:
            print(f"  - {error}")
    
    print(f"\n📁 Arquivos convertidos salvos em: {output_dir}")

if __name__ == "__main__":
    main()

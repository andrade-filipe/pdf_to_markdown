#!/usr/bin/env python3
"""
Script de teste para verificar as melhorias implementadas
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import re
from difflib import SequenceMatcher

def analyze_single_pdf(pdf_path, markdown_path):
    """Análise detalhada de um único PDF"""
    
    print(f"🔍 Analisando: {Path(pdf_path).name}")
    
    # Análise do PDF
    try:
        doc = fitz.open(pdf_path)
        pdf_info = {
            'total_pages': len(doc),
            'total_words': 0,
            'total_images': 0,
            'page_details': []
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            words = re.findall(r'\b\w+\b', text.lower())
            images = page.get_images()
            
            page_detail = {
                'page': page_num + 1,
                'words': len(words),
                'images': len(images),
                'text_sample': text[:100] + "..." if len(text) > 100 else text
            }
            
            pdf_info['page_details'].append(page_detail)
            pdf_info['total_words'] += len(words)
            pdf_info['total_images'] += len(images)
        
        doc.close()
        print(f"  📄 PDF: {pdf_info['total_pages']} páginas, {pdf_info['total_words']} palavras, {pdf_info['total_images']} imagens")
        
    except Exception as e:
        print(f"  ❌ Erro ao analisar PDF: {e}")
        return None
    
    # Análise do Markdown
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        titles = [line for line in lines if line.startswith('#')]
        lists = [line for line in lines if re.match(r'^\s*[-•*]\s', line)]
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        words = re.findall(r'\b\w+\b', content.lower())
        
        md_info = {
            'lines': len(lines),
            'titles': len(titles),
            'lists': len(lists),
            'images': len(images),
            'words': len(words),
            'file_size': os.path.getsize(markdown_path)
        }
        
        print(f"  📝 MD: {md_info['words']} palavras, {md_info['titles']} títulos, {md_info['lists']} listas, {md_info['images']} imagens")
        
    except Exception as e:
        print(f"  ❌ Erro ao analisar Markdown: {e}")
        return None
    
    # Calcular taxa de sucesso realista
    if pdf_info['total_words'] > 0:
        content_ratio = min(md_info['words'] / pdf_info['total_words'], 1.0)
        structure_score = min(md_info['titles'] / max(pdf_info['total_pages'], 1), 1.0)
        
        success_rate = (content_ratio * 0.7 + structure_score * 0.3) * 100
        print(f"  📊 Taxa de sucesso: {success_rate:.1f}%")
        print(f"  📈 Preservação de conteúdo: {content_ratio*100:.1f}%")
        print(f"  🏗️ Preservação de estrutura: {structure_score*100:.1f}%")
        
        return {
            'pdf_info': pdf_info,
            'md_info': md_info,
            'success_rate': success_rate,
            'content_ratio': content_ratio,
            'structure_score': structure_score
        }
    
    return None

def main():
    # Testar com alguns arquivos
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    markdown_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown")
    
    # Listar alguns PDFs para teste
    pdf_files = list(pdf_dir.glob("*.pdf"))[:5]  # Primeiros 5 arquivos
    
    print(f"🧪 Testando análise detalhada com {len(pdf_files)} arquivos...")
    
    results = []
    
    for pdf_file in pdf_files:
        markdown_name = pdf_file.stem + ".md"
        markdown_path = markdown_dir / markdown_name
        
        if markdown_path.exists():
            result = analyze_single_pdf(str(pdf_file), str(markdown_path))
            if result:
                results.append(result)
        else:
            print(f"❌ Markdown não encontrado para {pdf_file.name}")
    
    # Estatísticas finais
    if results:
        rates = [r['success_rate'] for r in results]
        avg_rate = sum(rates) / len(rates)
        
        print(f"\n📊 RESULTADOS DO TESTE")
        print(f"  • Arquivos testados: {len(results)}")
        print(f"  • Taxa de sucesso média: {avg_rate:.1f}%")
        print(f"  • Melhor conversão: {max(rates):.1f}%")
        print(f"  • Pior conversão: {min(rates):.1f}%")
        
        # Análise detalhada
        print(f"\n🔍 ANÁLISE DETALHADA:")
        for i, result in enumerate(results, 1):
            pdf_name = Path(result['pdf_info'].get('pdf_path', 'Unknown')).name
            print(f"  {i}. {pdf_name}: {result['success_rate']:.1f}% (Conteúdo: {result['content_ratio']*100:.1f}%, Estrutura: {result['structure_score']*100:.1f}%)")

if __name__ == "__main__":
    main()

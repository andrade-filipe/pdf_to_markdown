o no linu
#!/usr/bin/env python3
"""
Analisador Avançado de Conversão PDF para Markdown
Com métricas confiáveis, análise prévia e pós-tratamento
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF
from difflib import SequenceMatcher
from collections import defaultdict

class EnhancedConversionAnalyzer:
    def __init__(self):
        # Dicionário simples de palavras comuns em inglês e português
        self.common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'o', 'a', 'os', 'as', 'um', 'uma', 'e', 'ou', 'mas', 'em', 'no', 'na', 'nos', 'nas',
            'para', 'por', 'com', 'sem', 'sob', 'sobre', 'entre', 'contra', 'desde', 'até',
            'é', 'são', 'era', 'eram', 'foi', 'foram', 'ser', 'estar', 'ter', 'haver',
            'fazer', 'dizer', 'ver', 'dar', 'vir', 'saber', 'poder', 'dever', 'querer'
        }
        
    def analyze_pdf_structure(self, pdf_path: str) -> Dict:
        """Análise prévia detalhada do PDF"""
        try:
            doc = fitz.open(pdf_path)
            
            analysis = {
                'total_pages': len(doc),
                'pages_analyzed': 0,
                'total_words': 0,
                'total_images': 0,
                'total_tables': 0,
                'page_details': [],
                'structure_elements': {
                    'titles': 0,
                    'paragraphs': 0,
                    'lists': 0,
                    'figures': 0,
                    'references': 0
                },
                'text_quality': {
                    'readable_pages': 0,
                    'scanned_pages': 0,
                    'mixed_pages': 0
                }
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extrair texto da página
                text = page.get_text()
                words = re.findall(r'\b\w+\b', text.lower())
                
                # Detectar imagens
                images = page.get_images()
                
                # Detectar tabelas (heurística simples)
                table_indicators = len(re.findall(r'\|\s*\w+', text)) + len(re.findall(r'\t+', text))
                
                # Detectar elementos estruturais
                titles = len(re.findall(r'^[A-Z][A-Z\s]{3,}$', text, re.MULTILINE))
                paragraphs = len(re.findall(r'\n\s*\n', text))
                lists = len(re.findall(r'^\s*[-•*]\s', text, re.MULTILINE))
                
                # Classificar qualidade da página
                if len(words) > 100:
                    page_type = 'readable'
                    analysis['text_quality']['readable_pages'] += 1
                elif len(words) > 10:
                    page_type = 'mixed'
                    analysis['text_quality']['mixed_pages'] += 1
                else:
                    page_type = 'scanned'
                    analysis['text_quality']['scanned_pages'] += 1
                
                page_detail = {
                    'page_number': page_num + 1,
                    'word_count': len(words),
                    'image_count': len(images),
                    'table_indicators': table_indicators,
                    'titles': titles,
                    'paragraphs': paragraphs,
                    'lists': lists,
                    'page_type': page_type,
                    'text_sample': text[:200] + "..." if len(text) > 200 else text
                }
                
                analysis['page_details'].append(page_detail)
                analysis['total_words'] += len(words)
                analysis['total_images'] += len(images)
                analysis['total_tables'] += table_indicators
                analysis['structure_elements']['titles'] += titles
                analysis['structure_elements']['paragraphs'] += paragraphs
                analysis['structure_elements']['lists'] += lists
                analysis['pages_analyzed'] += 1
            
            doc.close()
            return analysis
            
        except Exception as e:
            print(f"Erro ao analisar PDF {pdf_path}: {e}")
            return None
    
    def simple_spell_check(self, text: str) -> Tuple[str, Dict]:
        """Correção ortográfica simples baseada em similaridade"""
        corrections = {
            'corrected_words': 0,
            'suggestions_made': 0,
            'corrections': []
        }
        
        # Dividir em palavras
        words = re.findall(r'\b\w+\b', text)
        corrected_words = []
        
        for word in words:
            original_word = word
            corrected_word = word
            
            # Verificar se a palavra está correta (é uma palavra comum ou tem formato válido)
            if len(word) > 2 and word.lower() not in self.common_words:
                # Verificar se parece com uma palavra comum
                best_match = None
                best_similarity = 0
                
                for common_word in self.common_words:
                    if len(common_word) > 3:  # Ignorar palavras muito curtas
                        similarity = SequenceMatcher(None, word.lower(), common_word).ratio()
                        if similarity > best_similarity and similarity > 0.8:
                            best_similarity = similarity
                            best_match = common_word
                
                if best_match:
                    corrected_word = best_match
                    corrections['corrected_words'] += 1
                    corrections['corrections'].append({
                        'original': original_word,
                        'corrected': corrected_word,
                        'similarity': best_similarity
                    })
            
            corrected_words.append(corrected_word)
        
        corrected_text = ' '.join(corrected_words)
        return corrected_text, corrections
    
    def analyze_markdown_quality(self, markdown_path: str, pdf_analysis: Dict) -> Dict:
        """Análise detalhada da qualidade do Markdown"""
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Métricas básicas
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            # Contar elementos estruturais
            titles = [line for line in lines if line.startswith('#')]
            title_hierarchy = defaultdict(int)
            for title in titles:
                level = len(title) - len(title.lstrip('#'))
                title_hierarchy[level] += 1
            
            # Detectar listas
            lists = [line for line in lines if re.match(r'^\s*[-•*]\s', line)]
            
            # Detectar links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            # Detectar imagens
            images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
            
            # Detectar tabelas
            table_lines = [line for line in lines if '|' in line and line.strip().startswith('|')]
            
            # Análise de qualidade do texto
            words = re.findall(r'\b\w+\b', content.lower())
            word_count = len(words)
            
            # Detectar problemas
            issues = []
            
            # Caracteres corrompidos
            corrupted_chars = sum(1 for char in content if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
            if corrupted_chars > len(content) * 0.05:
                issues.append(f"Muitos caracteres corrompidos ({corrupted_chars})")
            
            # Palavras repetidas
            word_freq = defaultdict(int)
            for word in words:
                if len(word) > 3:
                    word_freq[word] += 1
            
            repeated_words = [word for word, count in word_freq.items() if count > 10]
            if repeated_words:
                issues.append(f"Palavras excessivamente repetidas: {repeated_words[:5]}")
            
            # Estrutura inadequada
            if len(titles) < 3:
                issues.append("Poucos títulos detectados")
            
            if len(lists) < 2:
                issues.append("Poucas listas detectadas")
            
            return {
                'lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'words': word_count,
                'titles': len(titles),
                'title_hierarchy': dict(title_hierarchy),
                'lists': len(lists),
                'links': len(links),
                'images': len(images),
                'tables': len(table_lines),
                'issues': issues,
                'file_size': os.path.getsize(markdown_path),
                'corrupted_chars': corrupted_chars
            }
            
        except Exception as e:
            print(f"Erro ao analisar Markdown {markdown_path}: {e}")
            return None
    
    def calculate_realistic_success_rate(self, pdf_analysis: Dict, md_analysis: Dict) -> Dict:
        """Cálculo realista da taxa de sucesso baseado em múltiplos critérios"""
        
        if not pdf_analysis or not md_analysis:
            return {'overall_rate': 0, 'details': {}}
        
        # Critérios de avaliação
        criteria = {}
        
        # 1. Preservação de conteúdo (40% do peso)
        if pdf_analysis['total_words'] > 0:
            content_ratio = min(md_analysis['words'] / pdf_analysis['total_words'], 1.0)
            criteria['content_preservation'] = content_ratio * 100
        else:
            criteria['content_preservation'] = 0
        
        # 2. Preservação de estrutura (30% do peso)
        structure_score = 0
        
        # Títulos preservados
        if pdf_analysis['structure_elements']['titles'] > 0:
            title_ratio = min(md_analysis['titles'] / pdf_analysis['structure_elements']['titles'], 1.0)
            structure_score += title_ratio * 0.5
        
        # Parágrafos preservados
        if pdf_analysis['structure_elements']['paragraphs'] > 0:
            para_ratio = min(md_analysis['non_empty_lines'] / pdf_analysis['structure_elements']['paragraphs'], 1.0)
            structure_score += para_ratio * 0.5
        
        criteria['structure_preservation'] = structure_score * 100
        
        # 3. Qualidade do texto (20% do peso)
        quality_score = 100
        
        # Penalizar caracteres corrompidos
        if md_analysis['corrupted_chars'] > 0:
            corruption_ratio = md_analysis['corrupted_chars'] / len(md_analysis.get('content', ''))
            quality_score -= corruption_ratio * 50
        
        # Penalizar problemas detectados
        quality_score -= len(md_analysis['issues']) * 10
        
        criteria['text_quality'] = max(0, quality_score)
        
        # 4. Preservação de elementos especiais (10% do peso)
        special_elements = 0
        
        # Imagens
        if pdf_analysis['total_images'] > 0:
            img_ratio = min(md_analysis['images'] / pdf_analysis['total_images'], 1.0)
            special_elements += img_ratio * 0.5
        
        # Tabelas
        if pdf_analysis['total_tables'] > 0:
            table_ratio = min(md_analysis['tables'] / pdf_analysis['total_tables'], 1.0)
            special_elements += table_ratio * 0.5
        
        criteria['special_elements'] = special_elements * 100
        
        # Cálculo da taxa geral
        overall_rate = (
            criteria['content_preservation'] * 0.4 +
            criteria['structure_preservation'] * 0.3 +
            criteria['text_quality'] * 0.2 +
            criteria['special_elements'] * 0.1
        )
        
        return {
            'overall_rate': overall_rate,
            'details': criteria
        }
    
    def generate_detailed_report(self, pdf_path: str, markdown_path: str) -> Dict:
        """Gera relatório detalhado de uma conversão"""
        
        print(f"🔍 Analisando: {Path(pdf_path).name}")
        
        # Análise prévia do PDF
        pdf_analysis = self.analyze_pdf_structure(pdf_path)
        if not pdf_analysis:
            return None
        
        # Análise do Markdown
        md_analysis = self.analyze_markdown_quality(markdown_path, pdf_analysis)
        if not md_analysis:
            return None
        
        # Aplicar spell checking
        with open(markdown_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        corrected_content, spell_corrections = self.simple_spell_check(original_content)
        
        # Salvar versão corrigida
        corrected_path = markdown_path.replace('.md', '_corrected.md')
        with open(corrected_path, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        
        # Calcular taxa de sucesso realista
        success_rate = self.calculate_realistic_success_rate(pdf_analysis, md_analysis)
        
        report = {
            'pdf_name': Path(pdf_path).name,
            'markdown_name': Path(markdown_path).name,
            'pdf_analysis': pdf_analysis,
            'markdown_analysis': md_analysis,
            'spell_corrections': spell_corrections,
            'success_rate': success_rate,
            'corrected_file': corrected_path
        }
        
        return report

def main():
    analyzer = EnhancedConversionAnalyzer()
    
    # Diretórios
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    markdown_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em Markdown")
    
    # Listar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"🔍 Iniciando análise detalhada de {len(pdf_files)} arquivos...")
    
    reports = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n📊 [{i}/{len(pdf_files)}] Processando: {pdf_file.name}")
        
        # Encontrar Markdown correspondente
        markdown_name = pdf_file.stem + ".md"
        markdown_path = markdown_dir / markdown_name
        
        if markdown_path.exists():
            report = analyzer.generate_detailed_report(str(pdf_file), str(markdown_path))
            if report:
                reports.append(report)
                
                # Mostrar resumo
                rate = report['success_rate']['overall_rate']
                details = report['success_rate']['details']
                
                print(f"  📈 Taxa de sucesso: {rate:.1f}%")
                print(f"  📄 PDF: {report['pdf_analysis']['total_pages']} páginas, {report['pdf_analysis']['total_words']} palavras")
                print(f"  📝 MD: {report['markdown_analysis']['words']} palavras, {report['markdown_analysis']['titles']} títulos")
                print(f"  🔧 Correções: {report['spell_corrections']['corrected_words']} palavras corrigidas")
                
                if report['markdown_analysis']['issues']:
                    print(f"  ⚠️ Problemas: {', '.join(report['markdown_analysis']['issues'])}")
        else:
            print(f"  ❌ Markdown não encontrado")
    
    # Salvar relatório completo
    with open('detailed_conversion_report.json', 'w', encoding='utf-8') as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)
    
    # Estatísticas finais
    if reports:
        rates = [r['success_rate']['overall_rate'] for r in reports]
        avg_rate = sum(rates) / len(rates)
        
        print(f"\n📊 RELATÓRIO FINAL")
        print(f"  • Arquivos analisados: {len(reports)}")
        print(f"  • Taxa de sucesso média: {avg_rate:.1f}%")
        print(f"  • Melhor conversão: {max(rates):.1f}%")
        print(f"  • Pior conversão: {min(rates):.1f}%")
        print(f"  • Relatório salvo em: detailed_conversion_report.json")

if __name__ == "__main__":
    main()

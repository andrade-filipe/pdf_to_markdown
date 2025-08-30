#!/usr/bin/env python3
"""
PDF to Markdown Converter - Sistema de Conversão Inteligente
============================================================

Sistema robusto para conversão de PDFs acadêmicos para Markdown com análise linguística avançada.
"""

import argparse
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter.pipeline import ConversionPipeline
from converter.steps.markdown_conversion_step import MarkdownConversionStep
from converter.steps.advanced_markdown_conversion_step import AdvancedMarkdownConversionStep


class PDFConverterCLI:
    """Interface de linha de comando para o conversor PDF to Markdown"""
    
    def __init__(self):
        self.pipeline = ConversionPipeline()
        
    def convert_single(self, pdf_path: str, output_dir: str, verbose: bool = False, 
                      pt_br: bool = False, book: bool = False, article: bool = False) -> dict:
        """Converte um único PDF para Markdown"""
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
        
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar fluxo específico baseado nos argumentos
        self._configure_processing_flow(pt_br, book, article)
        
        if verbose:
            print(f"🔄 Convertendo: {pdf_path.name}")
            print(f"Iniciando conversão de {pdf_path.name}...")
        
        # Executar conversão
        result = self.pipeline.convert(str(pdf_path))
        
        # Verificar se é um PDF digitalizado
        if result.get('is_scanned_pdf', False):
            if verbose:
                print(f"⚠️  PDF digitalizado detectado: {pdf_path.name}")
            
            # Criar arquivo de aviso
            warning_filename = pdf_path.stem + '_SCANNED_WARNING.md'
            warning_path = output_dir / warning_filename
            
            with open(warning_path, 'w', encoding='utf-8') as f:
                f.write(result['markdown_content'])
            
            if verbose:
                print(f"📄 Arquivo de aviso criado: {warning_path}")
            
            return {
                'success': False,
                'is_scanned_pdf': True,
                'output_path': str(warning_path),
                'warning': result['markdown_content'],
                'statistics': result.get('statistics', {})
            }
        
        # Salvar arquivo
        output_filename = pdf_path.stem + '.md'
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['markdown_content'])
        
        if verbose:
            print(f"✅ Conversão concluída: {output_path}")
            print(f"📊 Tamanho: {len(result['markdown_content']):,} caracteres")
        
        return {
            'success': True,
            'output_path': str(output_path),
            'size': len(result['markdown_content']),
            'statistics': result.get('statistics', {})
        }
    
    def _configure_processing_flow(self, pt_br: bool, book: bool, article: bool):
        """
        Configura o fluxo de processamento baseado nos argumentos
        """
        # Configurar idioma
        if pt_br:
            self.pipeline.set_language('pt-br')
            print("[CLI] Configurado para processamento em Português do Brasil")
        else:
            self.pipeline.set_language('en')
            print("[CLI] Configurado para processamento em Inglês")
        
        # Configurar tipo de conteúdo
        if book:
            self.pipeline.set_content_type('book')
            print("[CLI] Configurado para processamento de livros")
        elif article:
            self.pipeline.set_content_type('article')
            print("[CLI] Configurado para processamento de artigos científicos")
        else:
            # Detecção automática baseada no nome do arquivo ou conteúdo
            self.pipeline.set_content_type('auto')
            print("[CLI] Detecção automática do tipo de conteúdo")
    
    def convert_batch(self, input_dir: str, output_dir: str, verbose: bool = False,
                     pt_br: bool = False, book: bool = False, article: bool = False) -> dict:
        """Converte múltiplos PDFs para Markdown"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {input_path}")
        
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar fluxo específico
        self._configure_processing_flow(pt_br, book, article)
        
        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(f"Nenhum arquivo PDF encontrado em {input_path}")
        
        results = []
        total_size = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            if verbose:
                print(f"\n🔄 Processando {i}/{len(pdf_files)}: {pdf_file.name}")
            
            try:
                result = self.convert_single(str(pdf_file), str(output_path), verbose)
                
                if result.get('is_scanned_pdf', False):
                    results.append({
                        'file': pdf_file.name,
                        'success': False,
                        'is_scanned_pdf': True,
                        'warning': result.get('warning', 'PDF digitalizado detectado')
                    })
                else:
                    results.append({
                        'file': pdf_file.name,
                        'success': True,
                        'size': result['size']
                    })
                    total_size += result['size']
                
            except Exception as e:
                if verbose:
                    print(f"❌ Erro ao processar {pdf_file.name}: {e}")
                results.append({
                    'file': pdf_file.name,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'total_files': len(pdf_files),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'total_size': total_size,
            'results': results
        }
    
    def analyze_conversion(self, output_dir: str) -> dict:
        """Analisa os resultados da conversão"""
        output_path = Path(output_dir)
        
        if not output_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {output_path}")
        
        md_files = list(output_path.glob("*.md"))
        
        analysis = {
            'total_files': len(md_files),
            'total_size': 0,
            'avg_size': 0,
            'size_distribution': {
                'small': 0,    # < 10KB
                'medium': 0,   # 10KB - 100KB
                'large': 0,    # 100KB - 1MB
                'xlarge': 0    # > 1MB
            },
            'files': []
        }
        
        for md_file in md_files:
            size = md_file.stat().st_size
            analysis['total_size'] += size
            analysis['files'].append({
                'name': md_file.name,
                'size': size,
                'size_kb': size / 1024
            })
            
            # Categorizar por tamanho
            if size < 10 * 1024:
                analysis['size_distribution']['small'] += 1
            elif size < 100 * 1024:
                analysis['size_distribution']['medium'] += 1
            elif size < 1024 * 1024:
                analysis['size_distribution']['large'] += 1
            else:
                analysis['size_distribution']['xlarge'] += 1
        
        if analysis['total_files'] > 0:
            analysis['avg_size'] = analysis['total_size'] / analysis['total_files']
        
        return analysis
    
    def test_title_detection(self, test_cases: list = None) -> dict:
        """Testa a detecção de títulos"""
        if test_cases is None:
            test_cases = [
                # Casos em inglês
                ("Abstract", True),
                ("Introduction", True),
                ("Methods and Materials", True),
                ("Results and Discussion", True),
                ("Conclusion", True),
                ("References", True),
                ("This study examines", False),
                ("We found that", False),
                ("The analysis shows", False),
                ("In conclusion", False),
                
                # Casos em português
                ("Resumo", True),
                ("Introdução", True),
                ("Métodos e Materiais", True),
                ("Resultados e Discussão", True),
                ("Conclusão", True),
                ("Referências", True),
                ("Este estudo examina", False),
                ("Encontramos que", False),
                ("A análise mostra", False),
                ("Em conclusão", False),
                
                # Casos de livros
                ("Capítulo 1", True),
                ("1. Introdução", True),
                ("I. Fundamentos", True),
                ("II. Aplicações", True),
                ("Apêndice A", True),
                ("Índice", True),
                ("Bibliografia", True),
                
                # Casos específicos de programação
                ("Getting Started", True),
                ("Installation", True),
                ("Configuration", True),
                ("API Reference", True),
                ("Examples", True),
                ("Troubleshooting", True),
            ]
        
        converter = MarkdownConversionStep()
        results = []
        correct = 0
        
        for text, expected in test_cases:
            # Testar com diferentes configurações
            for language in ['en', 'pt-br']:
                for content_type in ['article', 'book']:
                    converter.language = language
                    converter.content_type = content_type
                    
                    result = converter._is_title(text)
                    is_correct = result == expected
                    if is_correct:
                        correct += 1
                    
                    results.append({
                        'text': text,
                        'expected': expected,
                        'actual': result,
                        'correct': is_correct,
                        'language': language,
                        'content_type': content_type
                    })
        
        total_tests = len(results)
        accuracy = (correct / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'correct': correct,
            'accuracy': accuracy,
            'results': results
        }
    
    def analyze_fidelity(self, pdf_path: str, markdown_content: str) -> Dict[str, Any]:
        """Analisa a fidelidade da conversão"""
        # Implementação simplificada da análise de fidelidade
        total_chars = len(markdown_content)
        total_lines = len(markdown_content.split('\n'))
        headers_count = len([line for line in markdown_content.split('\n') if line.startswith('#')])
        
        # Análise básica de qualidade
        empty_lines = len([line for line in markdown_content.split('\n') if line.strip() == ''])
        empty_ratio = empty_lines / total_lines if total_lines > 0 else 0
        
        # Detectar problemas críticos
        critical_issues = []
        if empty_ratio > 0.3:
            critical_issues.append("Muitas linhas vazias")
        if total_chars < 1000:
            critical_issues.append("Conteúdo muito pequeno")
        if headers_count == 0:
            critical_issues.append("Nenhum cabeçalho detectado")
        
        # Calcular score de fidelidade
        fidelity_score = 100.0
        if empty_ratio > 0.3:
            fidelity_score -= 20
        if total_chars < 1000:
            fidelity_score -= 30
        if headers_count == 0:
            fidelity_score -= 15
        
        # Determinar status
        if fidelity_score >= 95:
            status = "EXCELENTE"
        elif fidelity_score >= 85:
            status = "BOM"
        elif fidelity_score >= 70:
            status = "REGULAR"
        else:
            status = "POBRE"
        
        return {
            'fidelity_score': max(0, fidelity_score),
            'status': status,
            'total_chars': total_chars,
            'total_lines': total_lines,
            'headers_count': headers_count,
            'empty_ratio': empty_ratio,
            'critical_issues': critical_issues
        }
    
    def process_with_analysis(self, input_dir: str, output_dir: str = None, verbose: bool = False) -> Dict[str, Any]:
        """Processa PDFs com análise crítica de fidelidade"""
        input_path = Path(input_dir)
        pdf_files = list(input_path.glob("*.pdf"))
        
        if output_dir is None:
            output_dir = input_path
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        results = {
            'total_files': len(pdf_files),
            'processed': 0,
            'failures': 0,
            'excellent': 0,
            'good': 0,
            'regular': 0,
            'poor': 0,
            'total_fidelity_score': 0,
            'results': {}
        }
        
        start_time = time.time()
        
        for i, pdf_path in enumerate(pdf_files, 1):
            pdf_name = pdf_path.name
            
            if verbose:
                print(f"\n[{i}/{len(pdf_files)}] 🔍 ANÁLISE CRÍTICA: {pdf_name}")
            
            try:
                # Converter
                result = self.pipeline.convert(str(pdf_path))
                
                if result and 'markdown_content' in result:
                    markdown_content = result['markdown_content']
                    
                    # Análise de fidelidade
                    fidelity_metrics = self.analyze_fidelity(str(pdf_path), markdown_content)
                    
                    # Salvar arquivo
                    output_file = output_dir / f"{pdf_path.stem}.md"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    
                    # Acumular estatísticas
                    results['processed'] += 1
                    results['total_fidelity_score'] += fidelity_metrics['fidelity_score']
                    
                    if fidelity_metrics['status'] == "EXCELENTE":
                        results['excellent'] += 1
                    elif fidelity_metrics['status'] == "BOM":
                        results['good'] += 1
                    elif fidelity_metrics['status'] == "REGULAR":
                        results['regular'] += 1
                    else:
                        results['poor'] += 1
                    
                    results['results'][pdf_name] = fidelity_metrics
                    
                    if verbose:
                        print(f"  📊 Fidelidade: {fidelity_metrics['fidelity_score']:.1f}% - {fidelity_metrics['status']}")
                        print(f"  📏 Tamanho: {fidelity_metrics['total_chars']:,} chars")
                        print(f"  📋 Linhas: {fidelity_metrics['total_lines']}")
                        print(f"  🏷️  Headers: {fidelity_metrics['headers_count']}")
                        if fidelity_metrics['critical_issues']:
                            print(f"  ⚠️  Problemas: {', '.join(fidelity_metrics['critical_issues'])}")
                        else:
                            print(f"  ✅ Sem problemas críticos")
                        print(f"  💾 Salvo: {output_file}")
                
                else:
                    results['failures'] += 1
                    if verbose:
                        print(f"  ❌ Falha na conversão")
            
            except Exception as e:
                results['failures'] += 1
                if verbose:
                    print(f"  ❌ ERRO: {str(e)}")
        
        elapsed_time = time.time() - start_time
        
        if verbose:
            print(f"\n" + "=" * 80)
            print(f"🎯 RESULTADOS DA ANÁLISE CRÍTICA")
            print(f"=" * 80)
            print(f"📁 Total processado: {results['processed']}/{len(pdf_files)}")
            print(f"⏱️  Tempo total: {elapsed_time:.1f} segundos")
            
            if results['processed'] > 0:
                avg_fidelity = results['total_fidelity_score'] / results['processed']
                print(f"🎯 Fidelidade média: {avg_fidelity:.1f}%")
            
            print(f"\n📈 DISTRIBUIÇÃO DE QUALIDADE:")
            print(f"  🎉 EXCELENTE (≥95%): {results['excellent']} arquivos")
            print(f"  👍 BOM (85-94%): {results['good']} arquivos")
            print(f"  ⚠️  REGULAR (70-84%): {results['regular']} arquivos")
            print(f"  ❌ POBRE (<70%): {results['poor']} arquivos")
            print(f"  💥 FALHAS: {results['failures']} arquivos")
        
        results['elapsed_time'] = elapsed_time
        return results


def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description="Conversor de PDF para Markdown com suporte a múltiplos idiomas e tipos de conteúdo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Converter artigo científico em inglês (padrão)
  ./pdf2md convert single "article.pdf" --output "./output/"

  # Converter livro em português
  ./pdf2md convert single "livro.pdf" --output "./output/" --pt-br --book

  # Converter artigo científico em português
  ./pdf2md convert single "artigo.pdf" --output "./output/" --pt-br --article

  # Converter múltiplos livros em inglês
  ./pdf2md convert batch "./books/" --output "./output/" --book

  # Analisar resultados
  ./pdf2md analyze "./output/"

  # Testar detecção de títulos
  ./pdf2md test titles
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando convert
    convert_parser = subparsers.add_parser('convert', help='Converter PDFs para Markdown')
    convert_subparsers = convert_parser.add_subparsers(dest='convert_type', help='Tipo de conversão')
    
    # Convert single
    single_parser = convert_subparsers.add_parser('single', help='Converter um único PDF')
    single_parser.add_argument('pdf_path', help='Caminho para o arquivo PDF')
    single_parser.add_argument('--output', '-o', required=True, help='Diretório de saída')
    single_parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    single_parser.add_argument('--pt-br', action='store_true', help='Processar em Português do Brasil')
    single_parser.add_argument('--book', action='store_true', help='Processar como livro')
    single_parser.add_argument('--article', action='store_true', help='Processar como artigo científico')
    
    # Convert batch
    batch_parser = convert_subparsers.add_parser('batch', help='Converter múltiplos PDFs')
    batch_parser.add_argument('input_dir', help='Diretório com PDFs')
    batch_parser.add_argument('--output', '-o', required=True, help='Diretório de saída')
    batch_parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    batch_parser.add_argument('--pt-br', action='store_true', help='Processar em Português do Brasil')
    batch_parser.add_argument('--book', action='store_true', help='Processar como livros')
    batch_parser.add_argument('--article', action='store_true', help='Processar como artigos científicos')
    
    # Comando analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analisar resultados da conversão')
    analyze_parser.add_argument('output_dir', help='Diretório com arquivos Markdown')
    analyze_parser.add_argument('--json', action='store_true', help='Saída em formato JSON')
    
    # Comando test
    test_parser = subparsers.add_parser('test', help='Testar funcionalidades')
    test_subparsers = test_parser.add_subparsers(dest='test_type', help='Tipo de teste')
    
    # Test titles
    titles_parser = test_subparsers.add_parser('titles', help='Testar detecção de títulos')
    titles_parser.add_argument('--json', action='store_true', help='Saída em formato JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PDFConverterCLI()
    
    try:
        if args.command == 'convert':
            if args.convert_type == 'single':
                result = cli.convert_single(
                    args.pdf_path, 
                    args.output, 
                    args.verbose,
                    args.pt_br,
                    args.book,
                    args.article
                )
                print("✅ Conversão concluída com sucesso!")
                
            elif args.convert_type == 'batch':
                result = cli.convert_batch(
                    args.input_dir,
                    args.output,
                    args.verbose,
                    args.pt_br,
                    args.book,
                    args.article
                )
                print(f"✅ Conversão em lote concluída!")
                print(f"📊 Total: {result['total_files']} arquivos")
                print(f"✅ Sucessos: {result['successful']}")
                print(f"❌ Falhas: {result['failed']}")
                print(f"📏 Tamanho total: {result['total_size']:,} caracteres")
        
        elif args.command == 'analyze':
            result = cli.analyze_conversion(args.output_dir)
            
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"📊 Análise de {result['total_files']} arquivos:")
                print(f"📏 Tamanho total: {result['total_size']:,} bytes")
                print(f"📏 Tamanho médio: {result['avg_size']:,.0f} bytes")
                print("\n📈 Distribuição por tamanho:")
                for category, count in result['size_distribution'].items():
                    print(f"  {category.capitalize()}: {count} arquivos")
        
        elif args.command == 'test':
            if args.test_type == 'titles':
                result = cli.test_title_detection()
                
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(f"🎯 Teste de Detecção de Títulos:")
                    print(f"📊 Total de testes: {result['total_tests']}")
                    print(f"✅ Corretos: {result['correct']}")
                    print(f"📈 Acurácia: {result['accuracy']:.1f}%")
                    
                    # Mostrar alguns resultados incorretos
                    incorrect = [r for r in result['results'] if not r['correct']]
                    if incorrect:
                        print(f"\n❌ Exemplos de falhas:")
                        for i, r in enumerate(incorrect[:5]):
                            print(f"  {i+1}. '{r['text']}' - Esperado: {r['expected']}, Obtido: {r['actual']}")
    
    except Exception as e:
        print(f"❌ ERRO: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

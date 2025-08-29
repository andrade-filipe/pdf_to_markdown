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


class PDFConverterCLI:
    """Interface de linha de comando para o conversor PDF to Markdown"""
    
    def __init__(self):
        self.pipeline = ConversionPipeline()
        self.markdown_step = MarkdownConversionStep()
    
    def convert_single(self, pdf_path: str, output_dir: str = None, verbose: bool = False) -> Dict[str, Any]:
        """Converte um único PDF"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
        
        if verbose:
            print(f"🔄 Convertendo: {pdf_path.name}")
        
        # Definir diretório de saída
        if output_dir is None:
            output_dir = pdf_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        # Executar conversão
        result = self.pipeline.convert(str(pdf_path))
        
        if result and 'markdown_content' in result:
            # Salvar arquivo
            output_file = output_dir / f"{pdf_path.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['markdown_content'])
            
            if verbose:
                print(f"✅ Conversão concluída: {output_file}")
                print(f"📊 Tamanho: {len(result['markdown_content']):,} caracteres")
            
            return {
                'success': True,
                'output_file': str(output_file),
                'content_length': len(result['markdown_content']),
                'markdown_content': result['markdown_content']
            }
        else:
            if verbose:
                print(f"❌ Falha na conversão")
            return {'success': False, 'error': 'Falha na conversão'}
    
    def convert_batch(self, input_dir: str, output_dir: str = None, verbose: bool = False) -> Dict[str, Any]:
        """Converte todos os PDFs em um diretório"""
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {input_dir}")
        
        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"Nenhum PDF encontrado em: {input_dir}")
        
        if verbose:
            print(f"📁 Encontrados {len(pdf_files)} PDFs em {input_dir}")
        
        # Definir diretório de saída
        if output_dir is None:
            output_dir = input_path
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        results = {
            'total_files': len(pdf_files),
            'successful': 0,
            'failed': 0,
            'files': {}
        }
        
        start_time = time.time()
        
        for i, pdf_file in enumerate(pdf_files, 1):
            if verbose:
                print(f"\n[{i}/{len(pdf_files)}] 🔄 {pdf_file.name}")
            
            try:
                result = self.convert_single(str(pdf_file), str(output_dir), verbose=False)
                if result['success']:
                    results['successful'] += 1
                    results['files'][pdf_file.name] = {
                        'status': 'success',
                        'output_file': result['output_file'],
                        'content_length': result['content_length']
                    }
                else:
                    results['failed'] += 1
                    results['files'][pdf_file.name] = {
                        'status': 'failed',
                        'error': result.get('error', 'Unknown error')
                    }
            except Exception as e:
                results['failed'] += 1
                results['files'][pdf_file.name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                if verbose:
                    print(f"❌ Erro: {e}")
        
        elapsed_time = time.time() - start_time
        
        if verbose:
            print(f"\n📊 RESULTADOS:")
            print(f"   ✅ Sucessos: {results['successful']}")
            print(f"   ❌ Falhas: {results['failed']}")
            print(f"   ⏱️  Tempo total: {elapsed_time:.1f}s")
            print(f"   📁 Arquivos salvos em: {output_dir}")
        
        results['elapsed_time'] = elapsed_time
        return results
    
    def test_title_detection(self, test_cases: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """Testa o algoritmo de detecção de títulos"""
        if test_cases is None:
            # Casos de teste padrão
            test_cases = [
                # Títulos válidos
                "Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion",
                "1. Introduction", "2. Methods and Materials", "3. Results and Analysis",
                "A Refined Baramin Concept", "Accelerated Decay: Theoretical Models",
                "The Genesis Flood", "Catastrophic Plate Tectonics",
                
                # Casos problemáticos (devem ser rejeitados)
                "do", "da", "de", "Davi", "Saul", "Daniel", "Ezequiel", "Jeremias",
                "OPBSG", "Number Three Occasional Papers", "Baraminology Study Group",
                "All Rights Reserved", "Cronologia Bíblica", "Bill Jones",
                "O que vamos estudar hoje", "Qual o principal", "Montando o quebra cabeça",
                "Ordens dadas por Deus", "Tentação (def.):", "O desejo de satisfazer",
                "Ouvindo o homem", "passos do Senhor Deus", "jardim quando soprava",
                "dia", "Quando soprava a brisa", "entardecer, o homem",
                "ouviram o SENHOR Deus", "pelo jardim e se esconderam",
                "A aliança Adâmica:", "Farei que haja inimizade",
                "entre você e a mulher", "entre a sua descendência", "o descendente"
            ]
        
        results = {
            'total_tests': len(test_cases),
            'valid_titles': [],
            'rejected_titles': [],
            'accuracy': 0.0
        }
        
        if verbose:
            print("🔍 TESTE DE DETECÇÃO DE TÍTULOS")
            print("=" * 60)
        
        for case in test_cases:
            is_title = self.markdown_step._is_title(case)
            
            if is_title:
                results['valid_titles'].append(case)
                if verbose:
                    print(f"✅ TÍTULO: '{case}'")
            else:
                results['rejected_titles'].append(case)
                if verbose:
                    print(f"❌ REJEITADO: '{case}'")
        
        # Calcular acurácia (assumindo que os primeiros 12 são válidos e o resto são problemáticos)
        expected_valid = 12
        actual_valid = len(results['valid_titles'])
        results['accuracy'] = (actual_valid / expected_valid) * 100 if expected_valid > 0 else 0
        
        if verbose:
            print(f"\n📊 RESULTADOS:")
            print(f"   Títulos detectados: {len(results['valid_titles'])}")
            print(f"   Títulos rejeitados: {len(results['rejected_titles'])}")
            print(f"   Acurácia estimada: {results['accuracy']:.1f}%")
        
        return results
    
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
        description="PDF to Markdown Converter - Sistema de Conversão Inteligente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:

  # Converter um único PDF
  python main.py convert single documento.pdf --output ./markdown/ --verbose

  # Converter todos os PDFs de um diretório
  python main.py convert batch ./pdfs/ --output ./markdown/ --verbose

  # Processar com análise crítica de fidelidade
  python main.py analyze ./pdfs/ --output ./markdown/ --verbose

  # Testar algoritmo de detecção de títulos
  python main.py test titles --verbose

  # Testar com casos específicos
  python main.py test titles --cases "Abstract,Introduction,Methods,do,da,de" --verbose
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando convert
    convert_parser = subparsers.add_parser('convert', help='Converter PDFs')
    convert_subparsers = convert_parser.add_subparsers(dest='convert_type', help='Tipo de conversão')
    
    # Convert single
    single_parser = convert_subparsers.add_parser('single', help='Converter um único PDF')
    single_parser.add_argument('pdf_path', help='Caminho para o PDF')
    single_parser.add_argument('--output', '-o', help='Diretório de saída')
    single_parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    
    # Convert batch
    batch_parser = convert_subparsers.add_parser('batch', help='Converter todos os PDFs de um diretório')
    batch_parser.add_argument('input_dir', help='Diretório com PDFs')
    batch_parser.add_argument('--output', '-o', help='Diretório de saída')
    batch_parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    
    # Comando analyze
    analyze_parser = subparsers.add_parser('analyze', help='Processar com análise crítica')
    analyze_parser.add_argument('input_dir', help='Diretório com PDFs')
    analyze_parser.add_argument('--output', '-o', help='Diretório de saída')
    analyze_parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    analyze_parser.add_argument('--report', '-r', help='Arquivo de relatório JSON')
    
    # Comando test
    test_parser = subparsers.add_parser('test', help='Testes e validações')
    test_subparsers = test_parser.add_subparsers(dest='test_type', help='Tipo de teste')
    
    # Test titles
    titles_parser = test_subparsers.add_parser('titles', help='Testar detecção de títulos')
    titles_parser.add_argument('--cases', help='Casos de teste separados por vírgula')
    titles_parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    titles_parser.add_argument('--output', '-o', help='Arquivo de resultado JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PDFConverterCLI()
    
    try:
        if args.command == 'convert':
            if args.convert_type == 'single':
                result = cli.convert_single(args.pdf_path, args.output, args.verbose)
                if args.verbose and result['success']:
                    print(f"✅ Conversão concluída com sucesso!")
            
            elif args.convert_type == 'batch':
                result = cli.convert_batch(args.input_dir, args.output, args.verbose)
                if args.verbose:
                    print(f"✅ Processamento em lote concluído!")
        
        elif args.command == 'analyze':
            result = cli.process_with_analysis(args.input_dir, args.output, args.verbose)
            
            # Salvar relatório se solicitado
            if args.report:
                with open(args.report, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"📄 Relatório salvo: {args.report}")
        
        elif args.command == 'test':
            if args.test_type == 'titles':
                test_cases = None
                if args.cases:
                    test_cases = [case.strip() for case in args.cases.split(',')]
                
                result = cli.test_title_detection(test_cases, args.verbose)
                
                # Salvar resultado se solicitado
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"📄 Resultado salvo: {args.output}")
    
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

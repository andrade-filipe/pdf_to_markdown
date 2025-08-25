#!/usr/bin/env python3
"""
Conversor de PDF para Markdown
Ferramenta CLI para converter artigos científicos em PDF para Markdown
"""

import argparse
import sys
from pathlib import Path

from converter.pipeline import ConversionPipeline


def main():
    """Função principal da CLI"""
    parser = argparse.ArgumentParser(
        description="Conversor de PDF para Markdown - Artigos Científicos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py artigo.pdf
  python main.py artigo.pdf -o artigo_convertido.md
  python main.py artigo.pdf -d output/personalizado
        """
    )
    
    parser.add_argument(
        'pdf_file',
        help='Caminho para o arquivo PDF a ser convertido'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Nome do arquivo de saída (padrão: nome_do_pdf.md)'
    )
    
    parser.add_argument(
        '-d', '--output-dir',
        default='output',
        help='Diretório de saída (padrão: output)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verboso (mais informações de debug)'
    )
    
    args = parser.parse_args()
    
    # Validar arquivo de entrada
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"Erro: Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    if not pdf_path.suffix.lower() == '.pdf':
        print(f"Erro: Arquivo deve ser um PDF: {pdf_path}")
        sys.exit(1)
    
    try:
        # Criar pipeline de conversão
        pipeline = ConversionPipeline(args.output_dir)
        
        # Executar conversão
        output_path = pipeline.convert(
            str(pdf_path),
            args.output
        )
        
        print(f"\n✅ Conversão concluída com sucesso!")
        print(f"📄 Arquivo Markdown: {output_path}")
        print(f"📁 Diretório de saída: {args.output_dir}")
        
        if args.verbose:
            stats = pipeline.get_statistics()
            print(f"\n📊 Estatísticas:")
            print(f"   - Páginas processadas: {stats['total_pages']}")
            print(f"   - Blocos de texto: {stats['text_blocks']}")
            print(f"   - Tabelas extraídas: {stats['tables']}")
            print(f"   - Imagens extraídas: {stats['images']}")
            print(f"   - Entradas de fonte: {stats['font_info_entries']}")
            print(f"   - Tamanho texto bruto: {stats['raw_text_length']:,} chars")
            print(f"   - Tamanho texto limpo: {stats['cleaned_text_length']:,} chars")
            print(f"   - Tamanho Markdown: {stats['markdown_length']:,} chars")
            print(f"   - Linhas Markdown: {stats['markdown_lines']}")
            print(f"   - Método escolhido: {stats['method_chosen']}")
        
    except Exception as e:
        print(f"❌ Erro durante a conversão: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

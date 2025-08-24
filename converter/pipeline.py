"""Pipeline principal de conversão de PDF para Markdown"""

from typing import Dict, Any, List
from pathlib import Path

from .steps.text_extraction_step import TextExtractionStep
from .steps.table_extraction_step import TableExtractionStep
from .steps.cleanup_step import CleanupStep
from .steps.image_extraction_step import ImageExtractionStep
from .steps.markdown_conversion_step import MarkdownConversionStep
from .steps.markdown_formatting_step import MarkdownFormattingStep


class ConversionPipeline:
    """Pipeline principal para conversão de PDF para Markdown"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar passos do pipeline
        self.steps = [
            TextExtractionStep(),
            TableExtractionStep(),
            CleanupStep(),
            ImageExtractionStep(str(self.output_dir)),
            MarkdownConversionStep(),
            MarkdownFormattingStep()
        ]
    
    def convert(self, pdf_path: str, output_filename: str = None) -> Path:
        """
        Converte PDF para Markdown
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            output_filename: Nome do arquivo de saída (opcional)
        
        Returns:
            Path para o arquivo Markdown gerado
        """
        # Validar entrada
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
        
        # Preparar dados iniciais
        data = {
            'pdf_path': str(pdf_path),
            'output_dir': str(self.output_dir)
        }
        
        # Executar pipeline
        print(f"Iniciando conversão de {pdf_path.name}...")
        
        for step in self.steps:
            print(f"Executando passo: {step.name}")
            try:
                data = step.process(data)
            except Exception as e:
                print(f"Erro no passo {step.name}: {e}")
                raise
        
        # Gerar nome do arquivo de saída
        if output_filename is None:
            output_filename = pdf_path.stem + ".md"
        
        output_path = self.output_dir / output_filename
        
        # Salvar arquivo Markdown
        markdown_content = data.get('markdown_content', '')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Conversão concluída: {output_path}")
        return output_path
    
    def get_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna estatísticas da conversão"""
        stats = {
            'total_pages': data.get('total_pages', 0),
            'text_blocks': len(data.get('text_blocks', [])),
            'tables': len(data.get('tables', [])),
            'images': len(data.get('images', [])),
            'font_info_entries': len(data.get('font_info', []))
        }
        return stats

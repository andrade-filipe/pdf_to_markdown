"""Pipeline principal de conversão de PDF para Markdown"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

import fitz
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from .steps.text_extraction_step import TextExtractionStep
from .steps.table_extraction_step import TableExtractionStep
from .steps.selective_ocr_step import SelectiveOCRStep
from .steps.image_extraction_step import ImageExtractionStep
from .steps.markdown_conversion_step import MarkdownConversionStep
from .steps.advanced_markdown_conversion_step import AdvancedMarkdownConversionStep
from .steps.text_cleanup_step import TextCleanupStep
from .steps.spell_checking_step import SpellCheckingStep
from .steps.book_conversion_step import BookConversionStep
from .steps.list_detection_step import ListDetectionStep
from .steps.quote_code_step import QuoteCodeStep
from .steps.footnote_step import FootnoteStep
from .steps.header_footer_filter_step import HeaderFooterFilterStep
from .steps.citation_step import CitationStep
from .steps.table_processing_step import TableProcessingStep
from .steps.robust_processing_step import RobustProcessingStep

class ConversionPipeline:
    """Pipeline de conversão de PDF para Markdown com fluxos específicos por idioma e tipo"""
    
    def __init__(self):
        # Configurações de processamento
        self.language = 'en'  # 'en' ou 'pt-br'
        self.content_type = 'auto'  # 'auto', 'article', 'book'
        self.current_data = {}
        
        # Steps comuns a todos os fluxos
        self.common_steps = [
            TextExtractionStep(),
            TableExtractionStep(),
            ImageExtractionStep("output"),
        ]
        
        # Steps específicos por idioma
        self.language_specific_steps = {}
        
        # Steps específicos por tipo de conteúdo
        self.content_specific_steps = {}
        
        # Inicializar steps específicos
        self._initialize_specific_steps()
        
    def _initialize_specific_steps(self):
        """Inicializa steps específicos por idioma e tipo de conteúdo"""
        
        # Steps específicos por idioma
        self.language_specific_steps = {
            'en': [
                SelectiveOCRStep(),  # OCR otimizado para inglês
            ],
            'pt-br': [
                SelectiveOCRStep(),  # OCR otimizado para português
            ]
        }
        
        # Steps específicos por tipo de conteúdo
        self.content_specific_steps = {
            'article': [
                MarkdownConversionStep(),  # Conversão otimizada para artigos
                AdvancedMarkdownConversionStep(),  # Processamento avançado para artigos
                TextCleanupStep(),  # Limpeza e correção de texto
                RobustProcessingStep(),  # Processamento robusto - ignora estruturas problemáticas
                TableProcessingStep(),  # Processamento de tabelas
                ListDetectionStep(),  # Detecção de listas
                QuoteCodeStep(),  # Blocos de citação e código
                FootnoteStep(),  # Notas de rodapé
                HeaderFooterFilterStep(),  # Filtragem de cabeçalhos/rodapés
                CitationStep(),  # Citações e bibliografia
                SpellCheckingStep(),  # Correção ortográfica específica para artigos
            ],
            'book': [
                MarkdownConversionStep(),  # Conversão otimizada para livros
                BookConversionStep(),  # Otimizações específicas para livros
                AdvancedMarkdownConversionStep(),  # Processamento avançado para livros
                TextCleanupStep(),  # Limpeza e correção de texto
                RobustProcessingStep(),  # Processamento robusto - ignora estruturas problemáticas
                TableProcessingStep(),  # Processamento de tabelas
                ListDetectionStep(),  # Detecção de listas
                QuoteCodeStep(),  # Blocos de citação e código
                FootnoteStep(),  # Notas de rodapé
                HeaderFooterFilterStep(),  # Filtragem de cabeçalhos/rodapés
                CitationStep(),  # Citações e bibliografia
                SpellCheckingStep(),  # Correção ortográfica específica para livros
            ]
        }
        
    def set_language(self, language: str):
        """Define o idioma de processamento"""
        if language not in ['en', 'pt-br']:
            raise ValueError(f"Idioma não suportado: {language}")
        
        self.language = language
        print(f"[Pipeline] Idioma configurado: {language}")
        
        # Propagar configuração para todos os steps
        self._propagate_configuration()
    
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo"""
        if content_type not in ['auto', 'article', 'book']:
            raise ValueError(f"Tipo de conteúdo não suportado: {content_type}")
        
        self.content_type = content_type
        print(f"[Pipeline] Tipo de conteúdo configurado: {content_type}")
        
        # Propagar configuração para todos os steps
        self._propagate_configuration()
    
    def _propagate_configuration(self):
        """Propaga configurações para todos os steps"""
        
        # Configurar steps comuns
        for step in self.common_steps:
            if hasattr(step, 'language'):
                step.language = self.language
            if hasattr(step, 'content_type'):
                step.content_type = self.content_type
            if hasattr(step, 'set_language'):
                step.set_language(self.language)
            if hasattr(step, 'set_content_type'):
                step.set_content_type(self.content_type)
        
        # Configurar steps específicos por idioma
        for language, steps in self.language_specific_steps.items():
            for step in steps:
                if hasattr(step, 'language'):
                    step.language = self.language
                if hasattr(step, 'content_type'):
                    step.content_type = self.content_type
                if hasattr(step, 'set_language'):
                    step.set_language(self.language)
                if hasattr(step, 'set_content_type'):
                    step.set_content_type(self.content_type)
        
        # Configurar steps específicos por tipo de conteúdo
        for content_type, steps in self.content_specific_steps.items():
            for step in steps:
                if hasattr(step, 'language'):
                    step.language = self.language
                if hasattr(step, 'content_type'):
                    step.content_type = self.content_type
                if hasattr(step, 'set_language'):
                    step.set_language(self.language)
                if hasattr(step, 'set_content_type'):
                    step.set_content_type(self.content_type)
    
    def _get_pipeline_steps(self) -> List:
        """Retorna a lista de steps para o pipeline atual"""
        steps = []
        
        # Adicionar steps comuns
        steps.extend(self.common_steps)
        
        # Adicionar steps específicos por idioma
        if self.language in self.language_specific_steps:
            steps.extend(self.language_specific_steps[self.language])
        
        # Adicionar steps específicos por tipo de conteúdo
        if self.content_type in self.content_specific_steps:
            steps.extend(self.content_specific_steps[self.content_type])
        elif self.content_type == 'auto':
            # Para 'auto', usar steps de artigo como padrão
            steps.extend(self.content_specific_steps['article'])
        
        return steps
    
    def convert(self, pdf_path: str) -> Dict[str, Any]:
        """Executa a conversão completa do PDF"""
        print(f"[Pipeline] Iniciando conversão de {Path(pdf_path).name}...")
        print(f"[Pipeline] Configuração: Idioma={self.language}, Tipo={self.content_type}")
        
        # Inicializar dados
        self.current_data = {
            'pdf_path': pdf_path,
            'language': self.language,
            'content_type': self.content_type,
            'statistics': {
                'start_time': time.time(),
                'steps_executed': [],
                'errors': [],
                'pipeline_config': {
                    'language': self.language,
                    'content_type': self.content_type
                }
            }
        }
        
        # Obter steps para este pipeline
        steps = self._get_pipeline_steps()
        
        # Executar cada step
        for i, step in enumerate(steps, 1):
            try:
                print(f"[Pipeline] Executando passo {i}/{len(steps)}: {step.__class__.__name__}")
                
                # Executar step
                self.current_data = step.process(self.current_data)
                
                # Verificar se é um PDF digitalizado após o primeiro step (TextExtractionStep)
                if i == 1 and self.current_data.get('is_scanned_pdf', False):
                    print(f"[Pipeline] ⚠️  PDF digitalizado detectado: {Path(pdf_path).name}")
                    print(f"[Pipeline] Este arquivo será ignorado - extração de texto não suportada")
                    
                    # Criar arquivo de aviso
                    output_path = self._save_scanned_pdf_warning(pdf_path)
                    
                    return {
                        'markdown_content': self.current_data.get('extraction_warning', ''),
                        'output_path': str(output_path),
                        'statistics': self.get_statistics(),
                        'is_scanned_pdf': True
                    }
                
                # Registrar step executado
                self.current_data['statistics']['steps_executed'].append({
                    'step': step.__class__.__name__,
                    'order': i,
                    'status': 'success',
                    'language': self.language,
                    'content_type': self.content_type
                })
                
            except Exception as e:
                error_msg = f"Erro no passo {step.__class__.__name__}: {str(e)}"
                print(f"[Pipeline] {error_msg}")
                self.current_data['statistics']['errors'].append(error_msg)
                
                # Registrar step com erro
                self.current_data['statistics']['steps_executed'].append({
                    'step': step.__class__.__name__,
                    'order': i,
                    'status': 'error',
                    'error': str(e),
                    'language': self.language,
                    'content_type': self.content_type
                })
                
                # Continuar com o próximo step se possível
                continue
        
        # Calcular estatísticas finais
        self.current_data['statistics']['end_time'] = time.time()
        self.current_data['statistics']['total_time'] = (
            self.current_data['statistics']['end_time'] - 
            self.current_data['statistics']['start_time']
        )
        
        print(f"[Pipeline] Conversão concluída")
        
        # Retornar dados da conversão
        return {
            'markdown_content': self.current_data.get('markdown_content', ''),
            'statistics': self.get_statistics()
        }
    
    def _save_markdown_file(self, pdf_path: str) -> Path:
        """Salva o arquivo Markdown"""
        pdf_path = Path(pdf_path)
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"{pdf_path.stem}.md"
        output_path = output_dir / output_filename
        
        markdown_content = self.current_data.get('markdown_content', '')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_path
    
    def _save_scanned_pdf_warning(self, pdf_path: str) -> Path:
        """Salva um arquivo de aviso para PDFs digitalizados"""
        pdf_path = Path(pdf_path)
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"{pdf_path.stem}_SCANNED_WARNING.md"
        output_path = output_dir / output_filename
        
        warning_content = f"""# ⚠️ PDF Digitalizado Detectado

**Arquivo:** `{pdf_path.name}`

## Aviso

Este arquivo foi identificado como um **PDF digitalizado** (apenas imagem). 

O algoritmo de conversão PDF para Markdown **não suporta** a extração de texto de PDFs digitalizados, pois:

- O conteúdo é uma imagem, não texto real
- Não há informações de fonte ou estrutura de texto
- A extração seria imprecisa e de baixa qualidade

## Recomendações

1. **Use um arquivo PDF original** (não digitalizado) se disponível
2. **Converta o PDF digitalizado** para texto usando ferramentas de OCR especializadas
3. **Digitalize novamente** o documento original com melhor qualidade

## Detalhes Técnicos

- **Tipo detectado:** PDF digitalizado (imagem)
- **Data de detecção:** {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Algoritmo:** Detecção automática baseada em densidade de texto e imagens

---
*Gerado automaticamente pelo conversor PDF para Markdown*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(warning_content)
        
        return output_path
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da conversão"""
        return self.current_data.get('statistics', {})
    
    def get_step_data(self, step_name: str) -> Dict[str, Any]:
        """Retorna dados de um step específico"""
        return self.current_data.get(step_name, {})
    
    def execute_step(self, step_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa um step específico"""
        all_steps = self._get_pipeline_steps()
        for step in all_steps:
            if step.__class__.__name__ == step_name:
                return step.process(data)
        raise ValueError(f"Step '{step_name}' não encontrado")
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o pipeline atual"""
        steps = self._get_pipeline_steps()
        return {
            'language': self.language,
            'content_type': self.content_type,
            'total_steps': len(steps),
            'steps': [step.__class__.__name__ for step in steps],
            'common_steps': len(self.common_steps),
            'language_specific_steps': len(self.language_specific_steps.get(self.language, [])),
            'content_specific_steps': len(self.content_specific_steps.get(self.content_type, []))
        }

"""Passo de conversão para Markdown"""

import re
from typing import Dict, Any, List
from .base_step import BaseStep
from ..converter import converter_texto, converter_tabela, detectar_titulos, processar_imagem


class MarkdownConversionStep(BaseStep):
    """Passo responsável por converter dados extraídos para Markdown"""
    
    def __init__(self):
        super().__init__("MarkdownConversion")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte dados extraídos para formato Markdown"""
        markdown_content = []
        
        # Processar informações de fonte para detectar títulos (prioridade)
        font_info = data.get('font_info', [])
        if font_info:
            markdown_content.append(self._process_font_info(font_info))
        else:
            # Fallback: processar texto raw se não houver informações de fonte
            raw_text = data.get('raw_text', '')
            if raw_text:
                markdown_content.append(self._process_raw_text(raw_text))
            else:
                # Fallback final: processar texto limpo
                cleaned_text = data.get('cleaned_text', '')
                if cleaned_text:
                    markdown_content.append(converter_texto(cleaned_text))
        
        # Processar tabelas
        tables = data.get('tables', [])
        for table in tables:
            table_markdown = converter_tabela(table['dados'])
            if table_markdown:
                markdown_content.append(f"\n## Tabela {table['numero']} (Página {table['pagina']})\n")
                markdown_content.append(table_markdown)
                markdown_content.append("\n")
        
        # Processar imagens
        images = data.get('images', [])
        for image in images:
            image_markdown = processar_imagem(image['caminho'])
            if image_markdown:
                markdown_content.append(f"\n## Imagem {image['numero']} (Página {image['pagina']})\n")
                markdown_content.append(image_markdown)
                markdown_content.append("\n")
        
        # Juntar todo o conteúdo
        final_markdown = '\n\n'.join(markdown_content)
        
        # Adicionar markdown final ao contexto
        data['markdown_content'] = final_markdown
        return data
    
    def _process_font_info(self, font_info: List[Dict[str, Any]]) -> str:
        """Processa informações de fonte para detectar títulos"""
        # Agrupar por página e ordenar por posição
        pages = {}
        for info in font_info:
            page = info['pagina']
            if page not in pages:
                pages[page] = []
            pages[page].append(info)
        
        # Ordenar por posição Y (topo para baixo)
        for page in pages:
            pages[page].sort(key=lambda x: x['posicao'][1])
        
        # Converter para markdown
        markdown_parts = []
        for page_num in sorted(pages.keys()):
            page_content = []
            for info in pages[page_num]:
                text = info['text']
                size = info['tamanho']
                
                # Detectar títulos baseado no tamanho da fonte
                if size >= 14:  # Títulos têm fonte maior
                    page_content.append(f"# {text}")
                else:
                    page_content.append(text)
            
            if page_content:
                markdown_parts.append('\n\n'.join(page_content))
        
        return '\n\n'.join(markdown_parts)
    
    def _process_raw_text(self, raw_text: str) -> str:
        """Processa texto raw extraído do PDF"""
        if not raw_text:
            return ""
        
        # Verificar se o texto está muito corrompido
        if self._is_text_corrupted(raw_text):
            # Tentar limpar o texto corrompido
            raw_text = self._clean_corrupted_text(raw_text)
        
        # Dividir em parágrafos
        paragraphs = raw_text.split('\n\n')
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Detectar títulos por padrões comuns
            if self._is_title(paragraph):
                processed_paragraphs.append(f"# {paragraph}")
            else:
                processed_paragraphs.append(paragraph)
        
        return '\n\n'.join(processed_paragraphs)
    
    def _is_text_corrupted(self, text: str) -> bool:
        """Detecta se o texto está corrompido"""
        if not text:
            return True
        
        # Contar caracteres estranhos
        strange_chars = sum(1 for char in text if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
        total_chars = len(text)
        
        # Se mais de 20% dos caracteres são estranhos, considerar corrompido
        return strange_chars / total_chars > 0.2 if total_chars > 0 else True
    
    def _clean_corrupted_text(self, text: str) -> str:
        """Tenta limpar texto corrompido"""
        # Remover caracteres muito estranhos
        cleaned = ""
        for char in text:
            # Manter caracteres ASCII básicos, espaços, quebras de linha e alguns caracteres especiais
            if (ord(char) < 128 or char in 'áéíóúâêîôûãõçàèìòùäëïöüñ') and char != '\x00':
                cleaned += char
            else:
                cleaned += ' '  # Substituir por espaço
        
        # Remover linhas muito estranhas
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            # Se a linha tem muitos caracteres estranhos, pular
            if len(line.strip()) > 0:
                strange_chars = sum(1 for char in line if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
                if strange_chars / len(line) < 0.5:  # Menos de 50% de caracteres estranhos
                    cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _is_title(self, text: str) -> bool:
        """Detecta se um texto é um título"""
        # Padrões comuns de títulos
        title_patterns = [
            r'^\d+\.\s+[A-Z]',  # 1. Título
            r'^[A-Z][A-Z\s]+$',  # TÍTULO EM MAIÚSCULAS
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
            r'^Abstract$', r'^Introduction$', r'^Conclusion$',  # Palavras-chave
            r'^References$', r'^Bibliography$', r'^Appendix$'
        ]
        
        for pattern in title_patterns:
            if re.match(pattern, text.strip()):
                return True
        
        return False

"""Step de Conversão Markdown para Conteúdo Estruturado"""

import time
from typing import Dict, Any, List
from .base_step import BaseStep


class StructuredMarkdownConversionStep(BaseStep):
    """Step que converte conteúdo estruturado para Markdown"""
    
    def __init__(self):
        super().__init__("StructuredMarkdownConversion")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte conteúdo estruturado para Markdown"""
        self.log_info("Iniciando conversão Markdown estruturada")
        
        if 'structured_content' not in data:
            self.log_warning("Nenhum conteúdo estruturado encontrado")
            return data
        
        structured_content = data['structured_content']
        start_time = time.time()
        
        try:
            # Converter para Markdown
            markdown_content = self._convert_to_markdown(structured_content)
            
            # Adicionar ao resultado
            data['markdown_content'] = markdown_content
            
            processing_time = time.time() - start_time
            self.log_info(f"Conversão Markdown estruturada concluída em {processing_time:.2f}s")
            
        except Exception as e:
            self.log_error(f"Erro na conversão Markdown estruturada: {e}")
        
        return data
    
    def _convert_to_markdown(self, structured_content: Dict[str, Any]) -> str:
        """Converte conteúdo estruturado para Markdown"""
        markdown_parts = []
        
        # Adicionar títulos
        titles = structured_content.get('titles', [])
        for title in titles:
            markdown_parts.append(f"# {title}\n")
        
        # Adicionar parágrafos
        paragraphs = structured_content.get('paragraphs', [])
        for paragraph in paragraphs:
            if paragraph.strip():
                markdown_parts.append(f"{paragraph}\n\n")
        
        # Adicionar tabelas
        tables = structured_content.get('tables', [])
        for table in tables:
            if table.strip():
                markdown_table = self._format_table_markdown(table)
                markdown_parts.append(f"{markdown_table}\n\n")
        
        # Adicionar elementos de artigo relevantes
        article_elements = structured_content.get('article_elements', [])
        for element in article_elements:
            if self._is_relevant_article_element(element):
                markdown_parts.append(f"**{element}**\n\n")
        
        # Adicionar referências
        references = structured_content.get('references', [])
        if references:
            markdown_parts.append("## Referências\n\n")
            for ref in references:
                markdown_parts.append(f"- {ref}\n")
            markdown_parts.append("\n")
        
        return "".join(markdown_parts)
    
    def _format_table_markdown(self, table_content: str) -> str:
        """Formata tabela para Markdown"""
        lines = table_content.strip().split('\n')
        if not lines:
            return ""
        
        # Tentar detectar se é uma tabela real
        if len(lines) < 2:
            return f"```\n{table_content}\n```"
        
        # Verificar se tem estrutura de tabela
        first_line = lines[0]
        if self._looks_like_table_header(first_line):
            return self._format_proper_table(lines)
        else:
            return f"```\n{table_content}\n```"
    
    def _looks_like_table_header(self, line: str) -> bool:
        """Verifica se uma linha parece ser cabeçalho de tabela"""
        words = line.split()
        if len(words) < 2:
            return False
        
        # Verificar se tem palavras em maiúsculas ou números
        has_caps = any(word.isupper() for word in words)
        has_numbers = any(any(c.isdigit() for c in word) for word in words)
        
        return has_caps or has_numbers
    
    def _format_proper_table(self, lines: List[str]) -> str:
        """Formata uma tabela real para Markdown"""
        if not lines:
            return ""
        
        markdown_lines = []
        
        # Cabeçalho
        header = lines[0]
        header_cells = header.split()
        markdown_lines.append("| " + " | ".join(header_cells) + " |")
        
        # Separador
        separator = "| " + " | ".join(["---"] * len(header_cells)) + " |"
        markdown_lines.append(separator)
        
        # Linhas de dados
        for line in lines[1:]:
            cells = line.split()
            if len(cells) == len(header_cells):
                markdown_lines.append("| " + " | ".join(cells) + " |")
            else:
                # Linha com número diferente de células
                markdown_lines.append(f"| {line} |")
        
        return "\n".join(markdown_lines)
    
    def _is_relevant_article_element(self, element: str) -> bool:
        """Verifica se um elemento de artigo é relevante para o Markdown"""
        relevant_elements = [
            'Abstract', 'Introduction', 'Methods', 'Results', 
            'Discussion', 'Conclusion', 'Keywords'
        ]
        
        return any(relevant in element for relevant in relevant_elements)

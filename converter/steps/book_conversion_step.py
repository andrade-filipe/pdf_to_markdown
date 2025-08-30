"""Passo de conversão específico para livros"""

import re
from typing import Dict, Any, List
from .base_step import BaseStep


class BookConversionStep(BaseStep):
    """Passo responsável por conversão específica para livros"""
    
    def __init__(self):
        super().__init__("BookConversion")
        self.language = 'en'
        self.content_type = 'book'
        
    def set_language(self, language: str):
        """Define o idioma para conversão específica"""
        self.language = language
        
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo"""
        self.content_type = content_type
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo com otimizações específicas para livros"""
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            return data
        
        self.log_info("Aplicando otimizações específicas para livros...")
        
        # Aplicar otimizações específicas para livros
        optimized_content = self._apply_book_optimizations(markdown_content)
        
        # Atualizar o conteúdo
        data['markdown_content'] = optimized_content
        data['book_optimizations_applied'] = True
        
        return data
    
    def _apply_book_optimizations(self, content: str) -> str:
        """Aplica otimizações específicas para livros"""
        if not content:
            return content
        
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Pular linhas vazias
            if not line:
                optimized_lines.append('')
                continue
            
            # Otimizar estrutura de capítulos
            line = self._optimize_chapter_structure(line)
            
            # Otimizar listas e índices
            line = self._optimize_lists_and_indexes(line)
            
            # Otimizar referências bibliográficas
            line = self._optimize_bibliographic_references(line)
            
            # Otimizar figuras e tabelas
            line = self._optimize_figures_and_tables(line)
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _optimize_chapter_structure(self, line: str) -> str:
        """Otimiza a estrutura de capítulos"""
        
        # Detectar e formatar títulos de capítulos
        chapter_patterns = [
            # Padrões em inglês
            (r'^Chapter\s+(\d+)[:\s]*(.+)$', r'# Chapter \1: \2'),
            (r'^CHAPTER\s+(\d+)[:\s]*(.+)$', r'# Chapter \1: \2'),
            (r'^Part\s+(\d+)[:\s]*(.+)$', r'## Part \1: \2'),
            (r'^PART\s+(\d+)[:\s]*(.+)$', r'## Part \1: \2'),
            (r'^Section\s+(\d+)[:\s]*(.+)$', r'### Section \1: \2'),
            (r'^SECTION\s+(\d+)[:\s]*(.+)$', r'### Section \1: \2'),
            
            # Padrões em português
            (r'^Capítulo\s+(\d+)[:\s]*(.+)$', r'# Capítulo \1: \2'),
            (r'^CAPÍTULO\s+(\d+)[:\s]*(.+)$', r'# Capítulo \1: \2'),
            (r'^Parte\s+(\d+)[:\s]*(.+)$', r'## Parte \1: \2'),
            (r'^PARTE\s+(\d+)[:\s]*(.+)$', r'## Parte \1: \2'),
            (r'^Seção\s+(\d+)[:\s]*(.+)$', r'### Seção \1: \2'),
            (r'^SEÇÃO\s+(\d+)[:\s]*(.+)$', r'### Seção \1: \2'),
        ]
        
        for pattern, replacement in chapter_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                break
        
        return line
    
    def _optimize_lists_and_indexes(self, line: str) -> str:
        """Otimiza listas e índices"""
        
        # Detectar e formatar listas numeradas
        numbered_list_patterns = [
            (r'^(\d+)\.\s+(.+)$', r'\1. \2'),
            (r'^(\d+)\)\s+(.+)$', r'\1. \2'),
        ]
        
        for pattern, replacement in numbered_list_patterns:
            if re.match(pattern, line):
                line = re.sub(pattern, replacement, line)
                break
        
        # Detectar e formatar listas com marcadores
        bullet_list_patterns = [
            (r'^[-•*]\s+(.+)$', r'- \1'),
            (r'^[▪▫]\s+(.+)$', r'- \1'),
        ]
        
        for pattern, replacement in bullet_list_patterns:
            if re.match(pattern, line):
                line = re.sub(pattern, replacement, line)
                break
        
        return line
    
    def _optimize_bibliographic_references(self, line: str) -> str:
        """Otimiza referências bibliográficas"""
        
        # Detectar e formatar referências bibliográficas
        bib_patterns = [
            # Padrões de citação
            (r'\(([A-Z][a-z]+ [A-Z][a-z]+, \d{4})\)', r'(\1)'),
            (r'\[([A-Z][a-z]+ [A-Z][a-z]+, \d{4})\]', r'[\1]'),
            
            # Padrões de referência
            (r'^([A-Z][a-z]+ [A-Z][a-z]+), ([A-Z][a-z]+)\. (.+)\. (\d{4})\.$', r'**\1, \2.** \3. \4.'),
        ]
        
        for pattern, replacement in bib_patterns:
            line = re.sub(pattern, replacement, line)
        
        return line
    
    def _optimize_figures_and_tables(self, line: str) -> str:
        """Otimiza figuras e tabelas"""
        
        # Detectar e formatar legendas de figuras
        figure_patterns = [
            (r'^Figure\s+(\d+)[:\s]*(.+)$', r'**Figure \1:** \2'),
            (r'^FIGURA\s+(\d+)[:\s]*(.+)$', r'**Figura \1:** \2'),
            (r'^Figura\s+(\d+)[:\s]*(.+)$', r'**Figura \1:** \2'),
        ]
        
        for pattern, replacement in figure_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                break
        
        # Detectar e formatar legendas de tabelas
        table_patterns = [
            (r'^Table\s+(\d+)[:\s]*(.+)$', r'**Table \1:** \2'),
            (r'^TABELA\s+(\d+)[:\s]*(.+)$', r'**Tabela \1:** \2'),
            (r'^Tabela\s+(\d+)[:\s]*(.+)$', r'**Tabela \1:** \2'),
        ]
        
        for pattern, replacement in table_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                break
        
        return line

"""Passo de filtragem de cabeçalhos e rodapés"""

import re
from typing import Dict, Any, List, Set
from .base_step import BaseStep


class HeaderFooterFilterStep(BaseStep):
    """Passo responsável por filtrar cabeçalhos e rodapés repetitivos"""
    
    def __init__(self):
        super().__init__("HeaderFooterFilter")
        self.language = 'en'
        self.content_type = 'auto'
        self.header_patterns = set()
        self.footer_patterns = set()
        
    def set_language(self, language: str):
        """Define o idioma para detecção específica"""
        self.language = language
        self._load_patterns()
        
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo para detecção específica"""
        self.content_type = content_type
        self._load_patterns()
        
    def _load_patterns(self):
        """Carrega padrões de cabeçalhos e rodapés baseado no idioma e tipo de conteúdo"""
        # Padrões gerais
        general_patterns = [
            r'^\d+$',  # Apenas números (páginas)
            r'^página\s+\d+',  # Página X
            r'^page\s+\d+',  # Page X
            r'^\d+\s*/\s*\d+$',  # X/Y
            r'^\d+\s*-\s*\d+$',  # X-Y
        ]
        
        # Padrões específicos de artigos acadêmicos
        academic_patterns = [
            r'^©.*\d{4}',  # Copyright
            r'^Copyright.*\d{4}',  # Copyright
            r'^All rights reserved',  # Direitos reservados
            r'^Confidential|Proprietary|Draft',  # Marcadores
            r'^Volume \d+.*Article \d+',  # Volume/Article
            r'^Print Reference: \d+-\d+ \d{4}',  # Referência de impressão
            r'^Proceedings of.*Conference',  # Proceedings
            r'^Journal of.*\d{4}',  # Journal
            r'^DOI:.*',  # DOI
            r'^ISSN:.*',  # ISSN
            r'^ISBN:.*',  # ISBN
        ]
        
        # Padrões específicos de livros
        book_patterns = [
            r'^Chapter \d+',  # Chapter X
            r'^Capítulo \d+',  # Capítulo X
            r'^Part \d+',  # Part X
            r'^Parte \d+',  # Parte X
            r'^Section \d+',  # Section X
            r'^Seção \d+',  # Seção X
        ]
        
        # Padrões em português
        portuguese_patterns = [
            r'^página\s+\d+',  # página X
            r'^©.*\d{4}',  # Copyright
            r'^Todos os direitos reservados',  # Direitos reservados
            r'^Confidencial|Proprietário|Rascunho',  # Marcadores
            r'^Volume \d+.*Artigo \d+',  # Volume/Artigo
            r'^Referência de Impressão: \d+-\d+ \d{4}',  # Referência
            r'^Anais de.*Conferência',  # Anais
            r'^Revista de.*\d{4}',  # Revista
        ]
        
        # Combinar padrões baseado no idioma e tipo
        all_patterns = general_patterns + academic_patterns
        
        if self.language == 'pt-br':
            all_patterns.extend(portuguese_patterns)
        
        if self.content_type == 'book':
            all_patterns.extend(book_patterns)
        
        # Compilar padrões
        self.header_patterns = set(all_patterns)
        self.footer_patterns = set(all_patterns)  # Por enquanto, usar os mesmos
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filtra cabeçalhos e rodapés repetitivos"""
        self.log_info("Iniciando filtragem de cabeçalhos e rodapés")
        
        # Obter texto processado
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            self.log_info("Nenhum conteúdo Markdown encontrado")
            return data
        
        # Filtrar cabeçalhos e rodapés
        processed_content = self._filter_headers_footers(markdown_content)
        
        # Atualizar dados
        data['markdown_content'] = processed_content
        data['headers_footers_removed'] = self._count_removed_items(markdown_content, processed_content)
        
        self.log_info(f"Filtragem concluída. {data['headers_footers_removed']} itens removidos")
        return data
    
    def _filter_headers_footers(self, content: str) -> str:
        """Filtra cabeçalhos e rodapés do conteúdo"""
        lines = content.split('\n')
        filtered_lines = []
        repeated_patterns = self._detect_repeated_patterns(lines)
        
        for line in lines:
            if not self._should_remove_line(line, repeated_patterns):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _detect_repeated_patterns(self, lines: List[str]) -> Dict[str, int]:
        """Detecta padrões repetitivos nas linhas"""
        pattern_counts = {}
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped:
                # Normalizar linha para comparação
                normalized = self._normalize_line(line_stripped)
                pattern_counts[normalized] = pattern_counts.get(normalized, 0) + 1
        
        return pattern_counts
    
    def _normalize_line(self, line: str) -> str:
        """Normaliza uma linha para comparação"""
        # Converter para minúsculas
        line = line.lower()
        
        # Remover números variáveis (substituir por placeholder)
        line = re.sub(r'\d+', 'N', line)
        
        # Remover espaços extras
        line = re.sub(r'\s+', ' ', line)
        
        return line.strip()
    
    def _should_remove_line(self, line: str, repeated_patterns: Dict[str, int]) -> bool:
        """Verifica se uma linha deve ser removida"""
        line_stripped = line.strip()
        
        if not line_stripped:
            return False
        
        # Verificar padrões específicos de cabeçalhos/rodapés
        for pattern in self.header_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return True
        
        # Verificar se é um padrão muito repetitivo
        normalized = self._normalize_line(line_stripped)
        if repeated_patterns.get(normalized, 0) > 3:  # Se aparece mais de 3 vezes
            return True
        
        # Verificar linhas muito curtas que parecem cabeçalhos/rodapés
        if len(line_stripped) < 10:
            # Verificar se contém apenas números, símbolos ou palavras muito comuns
            if re.match(r'^[\d\s\.\-_/]+$', line_stripped):
                return True
            
            # Verificar palavras muito comuns em cabeçalhos/rodapés
            common_words = ['page', 'página', 'copyright', 'confidential', 'draft', 'volume', 'article']
            if any(word in line_stripped.lower() for word in common_words):
                return True
        
        return False
    
    def _filter_by_position(self, lines: List[str]) -> List[str]:
        """Filtra linhas baseado na posição (topo e rodapé)"""
        if len(lines) < 10:
            return lines  # Arquivo muito pequeno, não filtrar
        
        filtered_lines = []
        
        for i, line in enumerate(lines):
            # Verificar se está no topo (primeiras 5 linhas) ou rodapé (últimas 5 linhas)
            is_header = i < 5
            is_footer = i >= len(lines) - 5
            
            if is_header or is_footer:
                # Aplicar filtros mais rigorosos para cabeçalhos e rodapés
                if not self._is_header_footer_line(line):
                    filtered_lines.append(line)
            else:
                # Linha do meio, aplicar filtros normais
                if not self._should_remove_line(line, {}):
                    filtered_lines.append(line)
        
        return filtered_lines
    
    def _is_header_footer_line(self, line: str) -> bool:
        """Verifica se uma linha é claramente cabeçalho ou rodapé"""
        line_stripped = line.strip()
        
        if not line_stripped:
            return False
        
        # Padrões muito específicos de cabeçalhos/rodapés
        specific_patterns = [
            r'^\d+$',  # Apenas número
            r'^página\s+\d+$',  # Página X
            r'^page\s+\d+$',  # Page X
            r'^©.*$',  # Copyright
            r'^Copyright.*$',  # Copyright
            r'^All rights reserved$',  # Direitos reservados
            r'^Confidential$',  # Confidencial
            r'^Draft$',  # Rascunho
            r'^Volume \d+.*Article \d+$',  # Volume/Article
            r'^DOI:.*$',  # DOI
            r'^ISSN:.*$',  # ISSN
            r'^ISBN:.*$',  # ISBN
        ]
        
        for pattern in specific_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return True
        
        return False
    
    def _filter_metadata(self, content: str) -> str:
        """Filtra metadados desnecessários"""
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not self._is_metadata_line(line):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _is_metadata_line(self, line: str) -> bool:
        """Verifica se uma linha é metadados desnecessários"""
        line_stripped = line.strip()
        
        if not line_stripped:
            return False
        
        # Padrões de metadados
        metadata_patterns = [
            r'^Author:.*$',  # Author: X
            r'^Autor:.*$',  # Autor: X
            r'^Date:.*$',  # Date: X
            r'^Data:.*$',  # Data: X
            r'^Subject:.*$',  # Subject: X
            r'^Assunto:.*$',  # Assunto: X
            r'^Keywords:.*$',  # Keywords: X
            r'^Palavras-chave:.*$',  # Palavras-chave: X
            r'^Created:.*$',  # Created: X
            r'^Criado:.*$',  # Criado: X
            r'^Modified:.*$',  # Modified: X
            r'^Modificado:.*$',  # Modificado: X
            r'^File:.*$',  # File: X
            r'^Arquivo:.*$',  # Arquivo: X
        ]
        
        for pattern in metadata_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return True
        
        return False
    
    def _count_removed_items(self, original_content: str, filtered_content: str) -> int:
        """Conta quantos itens foram removidos"""
        original_lines = original_content.split('\n')
        filtered_lines = filtered_content.split('\n')
        
        return len(original_lines) - len(filtered_lines)
    
    def _preserve_important_headers(self, content: str) -> str:
        """Preserva cabeçalhos importantes (títulos de seções)"""
        lines = content.split('\n')
        preserved_lines = []
        
        for line in lines:
            # Verificar se é um título importante
            if self._is_important_header(line):
                preserved_lines.append(line)
            elif not self._should_remove_line(line, {}):
                preserved_lines.append(line)
        
        return '\n'.join(preserved_lines)
    
    def _is_important_header(self, line: str) -> bool:
        """Verifica se uma linha é um cabeçalho importante"""
        line_stripped = line.strip()
        
        if not line_stripped:
            return False
        
        # Verificar se é um título de seção
        if line_stripped.startswith('#'):
            return True
        
        # Verificar se é um título importante (não muito curto, não muito longo)
        if 5 < len(line_stripped) < 100:
            # Verificar se não contém padrões de cabeçalho/rodapé
            for pattern in self.header_patterns:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    return False
            
            # Verificar se parece um título (primeira letra maiúscula, não termina com pontuação)
            if line_stripped[0].isupper() and not line_stripped.endswith(('.', '!', '?')):
                return True
        
        return False

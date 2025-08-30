"""Analisador Probabilístico para Estruturação de Conteúdo PDF"""

import re
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum, auto
from dataclasses import dataclass
from collections import defaultdict
import math


class TokenType(Enum):
    """Tipos de tokens identificados no conteúdo"""
    TITLE = auto()
    PARAGRAPH = auto()
    TABLE_ROW = auto()
    ARTICLE_ELEMENT = auto()
    PAGE_BREAK = auto()
    HEADER_FOOTER = auto()
    REFERENCE = auto()
    FIGURE_CAPTION = auto()
    UNKNOWN = auto()


@dataclass
class ContentToken:
    """Token de conteúdo com informações estruturais"""
    text: str
    token_type: TokenType
    page: int
    line_number: int
    word_count: int
    char_count: int
    has_numbers: bool
    has_capitalization: bool
    has_punctuation: bool
    position_score: float = 0.0
    content_score: float = 0.0


class ProbabilisticAnalyzer:
    """Analisador probabilístico para estruturação de conteúdo PDF"""
    
    def __init__(self):
        self.patterns = {
            'page_break': r'^--- PÁGINA \d+ ---$',
            'title_patterns': [
                r'^[A-Z][^.!?]{3,50}$',  # Títulos curtos
                r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Títulos em camelCase
                r'^\d+\.\s+[A-Z]',  # Títulos numerados
                r'^[A-Z\s]{5,}$',  # Títulos em maiúsculas
            ],
            'article_elements': [
                r'^Abstract$', r'^Introduction$', r'^Methods$', r'^Results$', 
                r'^Discussion$', r'^Conclusion$', r'^References$',
                r'^Keywords:', r'^Article history:', r'^Received', r'^Accepted',
                r'^Editor:', r'^Corresponding author', r'^E-mail:',
                r'^DOI:', r'^ISSN:', r'^© \d{4}', r'^All rights reserved'
            ],
            'table_indicators': [
                r'^\d+\s+\d+',  # Linhas com números
                r'^[A-Z]\s+\d+',  # Letra + número
                r'^\w+\s+\w+\s+\d+',  # Palavras + números
                r'^\d+\.\d+',  # Decimais
            ],
            'reference_patterns': [
                r'^\[\d+\]',  # [1], [2], etc.
                r'^\(\d+\)',  # (1), (2), etc.
                r'^[A-Z][a-z]+,\s+\d{4}',  # Autor, ano
            ]
        }
        
        # Compilar padrões
        self.compiled_patterns = {}
        for category, patterns in self.patterns.items():
            if isinstance(patterns, list):
                self.compiled_patterns[category] = [re.compile(p, re.MULTILINE) for p in patterns]
            else:
                self.compiled_patterns[category] = re.compile(patterns, re.MULTILINE)
    
    def analyze_content(self, raw_content: str) -> Dict[str, Any]:
        """Analisa o conteúdo bruto e retorna estrutura classificada"""
        
        # Dividir em linhas e páginas
        lines = raw_content.split('\n')
        pages = self._split_into_pages(lines)
        
        # Tokenizar e classificar
        all_tokens = []
        for page_num, page_lines in pages.items():
            page_tokens = self._tokenize_page(page_lines, page_num)
            all_tokens.extend(page_tokens)
        
        # Análise probabilística
        classified_content = self._probabilistic_classification(all_tokens)
        
        # Estruturação final
        structured_content = self._structure_content(classified_content)
        
        return structured_content
    
    def _split_into_pages(self, lines: List[str]) -> Dict[int, List[str]]:
        """Divide o conteúdo em páginas"""
        pages = {}
        current_page = 1
        current_lines = []
        
        for line in lines:
            page_match = re.match(r'^--- PÁGINA (\d+) ---$', line)
            if page_match:
                if current_lines:
                    pages[current_page] = current_lines
                current_page = int(page_match.group(1))
                current_lines = []
            else:
                current_lines.append(line)
        
        if current_lines:
            pages[current_page] = current_lines
        
        return pages
    
    def _tokenize_page(self, lines: List[str], page_num: int) -> List[ContentToken]:
        """Tokeniza as linhas de uma página"""
        tokens = []
        
        for line_num, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Análise da linha
            word_count = len(line.split())
            char_count = len(line)
            has_numbers = bool(re.search(r'\d', line))
            has_capitalization = line[0].isupper() if line else False
            has_punctuation = bool(re.search(r'[.!?;:,]', line))
            
            # Classificação inicial
            token_type = self._classify_line(line, word_count, char_count)
            
            # Criar token
            token = ContentToken(
                text=line.strip(),
                token_type=token_type,
                page=page_num,
                line_number=line_num,
                word_count=word_count,
                char_count=char_count,
                has_numbers=has_numbers,
                has_capitalization=has_capitalization,
                has_punctuation=has_punctuation
            )
            
            # Calcular scores
            token.position_score = self._calculate_position_score(line_num, len(lines))
            token.content_score = self._calculate_content_score(token)
            
            tokens.append(token)
        
        return tokens
    
    def _classify_line(self, line: str, word_count: int, char_count: int) -> TokenType:
        """Classifica uma linha baseado em padrões"""
        
        # Verificar se tem números
        has_numbers = bool(re.search(r'\d', line))
        
        # Verificar padrões específicos
        for pattern in self.compiled_patterns['article_elements']:
            if pattern.match(line):
                return TokenType.ARTICLE_ELEMENT
        
        for pattern in self.compiled_patterns['reference_patterns']:
            if pattern.match(line):
                return TokenType.REFERENCE
        
        for pattern in self.compiled_patterns['table_indicators']:
            if pattern.match(line):
                return TokenType.TABLE_ROW
        
        # Verificar padrões de título
        for pattern in self.compiled_patterns['title_patterns']:
            if pattern.match(line):
                return TokenType.TITLE
        
        # Classificação baseada em características
        if word_count <= 3 and char_count <= 50:
            return TokenType.ARTICLE_ELEMENT
        elif word_count >= 15:
            return TokenType.PARAGRAPH
        elif has_numbers and word_count <= 8:
            return TokenType.TABLE_ROW
        else:
            return TokenType.PARAGRAPH
    
    def _calculate_position_score(self, line_num: int, total_lines: int) -> float:
        """Calcula score baseado na posição da linha"""
        # Linhas no início e fim têm scores diferentes
        if line_num < total_lines * 0.1:  # Primeiros 10%
            return 0.8
        elif line_num > total_lines * 0.9:  # Últimos 10%
            return 0.6
        else:
            return 0.5
    
    def _calculate_content_score(self, token: ContentToken) -> float:
        """Calcula score baseado no conteúdo do token"""
        score = 0.0
        
        # Score baseado no tipo
        type_scores = {
            TokenType.TITLE: 0.9,
            TokenType.PARAGRAPH: 0.7,
            TokenType.TABLE_ROW: 0.6,
            TokenType.ARTICLE_ELEMENT: 0.4,
            TokenType.REFERENCE: 0.5,
            TokenType.UNKNOWN: 0.3
        }
        score += type_scores.get(token.token_type, 0.5)
        
        # Score baseado no comprimento
        if 10 <= token.word_count <= 30:
            score += 0.2
        elif token.word_count > 30:
            score += 0.1
        
        # Score baseado na capitalização
        if token.has_capitalization:
            score += 0.1
        
        # Score baseado na pontuação
        if token.has_punctuation:
            score += 0.1
        
        return min(score, 1.0)
    
    def _probabilistic_classification(self, tokens: List[ContentToken]) -> Dict[str, Any]:
        """Classificação probabilística dos tokens"""
        
        # Agrupar por tipo
        classified = {
            'titles': [],
            'paragraphs': [],
            'tables': [],
            'article_elements': [],
            'references': [],
            'unknown': []
        }
        
        # Primeira passagem: classificação direta
        for token in tokens:
            if token.token_type == TokenType.TITLE:
                classified['titles'].append(token)
            elif token.token_type == TokenType.PARAGRAPH:
                classified['paragraphs'].append(token)
            elif token.token_type == TokenType.TABLE_ROW:
                classified['tables'].append(token)
            elif token.token_type == TokenType.ARTICLE_ELEMENT:
                classified['article_elements'].append(token)
            elif token.token_type == TokenType.REFERENCE:
                classified['references'].append(token)
            else:
                classified['unknown'].append(token)
        
        # Segunda passagem: análise de contexto
        self._analyze_context(classified, tokens)
        
        return classified
    
    def _analyze_context(self, classified: Dict[str, List[ContentToken]], all_tokens: List[ContentToken]):
        """Analisa o contexto para melhorar a classificação"""
        
        # Agrupar parágrafos relacionados
        paragraphs = self._group_related_paragraphs(classified['paragraphs'])
        classified['paragraphs'] = paragraphs
        
        # Agrupar linhas de tabela
        tables = self._group_table_rows(classified['tables'])
        classified['tables'] = tables
        
        # Reclassificar tokens desconhecidos
        self._reclassify_unknown_tokens(classified, all_tokens)
    
    def _group_related_paragraphs(self, paragraphs: List[ContentToken]) -> List[List[ContentToken]]:
        """Agrupa parágrafos relacionados"""
        if not paragraphs:
            return []
        
        groups = []
        current_group = [paragraphs[0]]
        
        for i in range(1, len(paragraphs)):
            current = paragraphs[i]
            previous = paragraphs[i-1]
            
            # Calcular probabilidade de serem do mesmo parágrafo
            probability = self._calculate_paragraph_probability(previous, current)
            
            if probability > 0.6:  # Threshold para agrupar
                current_group.append(current)
            else:
                groups.append(current_group)
                current_group = [current]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _calculate_paragraph_probability(self, token1: ContentToken, token2: ContentToken) -> float:
        """Calcula a probabilidade de dois tokens serem do mesmo parágrafo"""
        probability = 0.0
        
        # Proximidade de linha
        line_diff = abs(token2.line_number - token1.line_number)
        if line_diff == 1:
            probability += 0.4
        elif line_diff <= 3:
            probability += 0.2
        
        # Mesma página
        if token1.page == token2.page:
            probability += 0.2
        
        # Características similares
        if token1.word_count > 10 and token2.word_count > 10:
            probability += 0.2
        
        # Pontuação no final
        if token1.has_punctuation and token1.text.endswith(('.', '!', '?')):
            probability -= 0.1  # Menos provável de continuar
        
        return min(probability, 1.0)
    
    def _group_table_rows(self, table_rows: List[ContentToken]) -> List[List[ContentToken]]:
        """Agrupa linhas de tabela relacionadas"""
        if not table_rows:
            return []
        
        groups = []
        current_group = [table_rows[0]]
        
        for i in range(1, len(table_rows)):
            current = table_rows[i]
            previous = table_rows[i-1]
            
            # Verificar se são da mesma tabela
            if self._are_same_table(previous, current):
                current_group.append(current)
            else:
                groups.append(current_group)
                current_group = [current]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _are_same_table(self, token1: ContentToken, token2: ContentToken) -> bool:
        """Verifica se dois tokens são da mesma tabela"""
        # Mesma página
        if token1.page != token2.page:
            return False
        
        # Proximidade de linha
        line_diff = abs(token2.line_number - token1.line_number)
        if line_diff > 5:
            return False
        
        # Características similares
        if abs(token1.word_count - token2.word_count) > 3:
            return False
        
        return True
    
    def _reclassify_unknown_tokens(self, classified: Dict[str, List[ContentToken]], all_tokens: List[ContentToken]):
        """Reclassifica tokens desconhecidos baseado no contexto"""
        for token in classified['unknown']:
            # Tentar reclassificar baseado no contexto
            best_type = self._find_best_classification(token, all_tokens)
            if best_type:
                token.token_type = best_type
                # Mover para a categoria correta
                if best_type == TokenType.PARAGRAPH:
                    classified['paragraphs'].append([token])
                elif best_type == TokenType.TABLE_ROW:
                    classified['tables'].append([token])
                elif best_type == TokenType.ARTICLE_ELEMENT:
                    classified['article_elements'].append(token)
    
    def _find_best_classification(self, token: ContentToken, all_tokens: List[ContentToken]) -> Optional[TokenType]:
        """Encontra a melhor classificação para um token desconhecido"""
        scores = defaultdict(float)
        
        for other_token in all_tokens:
            if other_token == token:
                continue
            
            # Calcular similaridade
            similarity = self._calculate_similarity(token, other_token)
            scores[other_token.token_type] += similarity
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return None
    
    def _calculate_similarity(self, token1: ContentToken, token2: ContentToken) -> float:
        """Calcula similaridade entre dois tokens"""
        similarity = 0.0
        
        # Proximidade
        if abs(token1.line_number - token2.line_number) <= 2:
            similarity += 0.3
        
        # Características similares
        if abs(token1.word_count - token2.word_count) <= 2:
            similarity += 0.2
        
        if token1.has_numbers == token2.has_numbers:
            similarity += 0.2
        
        if token1.has_capitalization == token2.has_capitalization:
            similarity += 0.2
        
        return similarity
    
    def _structure_content(self, classified: Dict[str, Any]) -> Dict[str, Any]:
        """Estrutura o conteúdo classificado para conversão Markdown"""
        
        structured = {
            'metadata': {
                'total_titles': len(classified['titles']),
                'total_paragraphs': len(classified['paragraphs']),
                'total_tables': len(classified['tables']),
                'total_article_elements': len(classified['article_elements']),
                'total_references': len(classified['references'])
            },
            'content': {
                'titles': [t.text for t in classified['titles']],
                'paragraphs': [self._join_paragraph_group(group) for group in classified['paragraphs']],
                'tables': [self._format_table_group(group) for group in classified['tables']],
                'article_elements': [t.text for t in classified['article_elements']],
                'references': [t.text for t in classified['references']]
            },
            'raw_tokens': classified
        }
        
        return structured
    
    def _join_paragraph_group(self, group: List[ContentToken]) -> str:
        """Junta tokens de um grupo de parágrafo"""
        if not group:
            return ""
        
        texts = [token.text for token in group]
        return " ".join(texts)
    
    def _format_table_group(self, group: List[ContentToken]) -> str:
        """Formata um grupo de linhas de tabela"""
        if not group:
            return ""
        
        lines = [token.text for token in group]
        return "\n".join(lines)

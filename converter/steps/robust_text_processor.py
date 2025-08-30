#!/usr/bin/env python3
"""Processador de texto robusto baseado em conceitos de compiladores e autômatos"""

import re
import unicodedata
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum, auto

class TokenType(Enum):
    """Tipos de tokens para o parser"""
    TEXT = auto()
    TITLE = auto()
    PARAGRAPH_BREAK = auto()
    SECTION_BREAK = auto()
    PROBLEMATIC_STRUCTURE = auto()
    WHITESPACE = auto()
    PUNCTUATION = auto()

class TextToken:
    """Token de texto com informações de contexto"""
    
    def __init__(self, text: str, token_type: TokenType, position: int = 0):
        self.text = text
        self.token_type = token_type
        self.position = position
        self.length = len(text)
    
    def __str__(self):
        return f"Token({self.token_type.name}: '{self.text[:50]}...')"

class RobustTextProcessor:
    """Processador de texto robusto baseado em autômatos finitos"""
    
    def __init__(self):
        # Padrões regex para detecção de estruturas
        self.patterns = {
            'problematic_structures': [
                r'[A-Z]{3,}',  # Palavras em caps lock
                r'\b[A-Z]{2,}\s+[A-Z]{2,}\s+[A-Z]{2,}\b',  # Múltiplas palavras caps
                r'[^\w\s]{3,}',  # Sequências de símbolos
                r'\d{4,}',  # Números longos
                r'[A-Z]\.[A-Z]\.[A-Z]',  # Iniciais múltiplas
            ],
            'title_patterns': [
                r'^[A-Z][^.!?]*$',  # Frase sem pontuação final
                r'^[A-Z][^.!?]{3,50}$',  # Frase de tamanho médio
                r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
            ],
            'paragraph_breaks': [
                r'\n\s*\n',  # Quebras duplas
                r'\n\s*[A-Z]',  # Quebra seguida de maiúscula
            ],
            'section_breaks': [
                r'\n\s*[0-9]+\.',  # Números de seção
                r'\n\s*[A-Z]+\s*$',  # Títulos em caps
            ]
        }
        
        # Compilar padrões para eficiência
        self.compiled_patterns = {}
        for category, patterns in self.patterns.items():
            self.compiled_patterns[category] = [re.compile(p, re.MULTILINE) for p in patterns]
    
    def tokenize_text(self, text: str) -> List[TextToken]:
        """Tokeniza o texto usando autômato finito"""
        tokens = []
        position = 0
        
        # Normalizar texto
        text = self._normalize_text(text)
        
        # Dividir em linhas para análise
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                tokens.append(TextToken('\n\n', TokenType.PARAGRAPH_BREAK, position))
                position += 2
                continue
            
            # Analisar tipo da linha
            token_type = self._classify_line(line)
            
            if token_type == TokenType.PROBLEMATIC_STRUCTURE:
                # Ignorar estruturas problemáticas
                continue
            elif token_type == TokenType.TITLE:
                tokens.append(TextToken(line, TokenType.TITLE, position))
            else:
                tokens.append(TextToken(line, TokenType.TEXT, position))
            
            position += len(line) + 1  # +1 para \n
        
        return tokens
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto usando conceitos de compiladores"""
        # Normalização Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remover caracteres problemáticos
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalizar quebras de linha
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Normalizar espaços
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text
    
    def _classify_line(self, line: str) -> TokenType:
        """Classifica uma linha usando autômato finito"""
        if not line:
            return TokenType.WHITESPACE
        
        # Verificar se é estrutura problemática
        for pattern in self.compiled_patterns['problematic_structures']:
            if pattern.search(line):
                return TokenType.PROBLEMATIC_STRUCTURE
        
        # Verificar se é título
        for pattern in self.compiled_patterns['title_patterns']:
            if pattern.match(line):
                return TokenType.TITLE
        
        # Verificar se é quebra de seção
        for pattern in self.compiled_patterns['section_breaks']:
            if pattern.search(line):
                return TokenType.SECTION_BREAK
        
        return TokenType.TEXT
    
    def process_text(self, text: str) -> str:
        """Processa o texto removendo estruturas problemáticas"""
        tokens = self.tokenize_text(text)
        
        # Reconstruir texto apenas com tokens válidos
        processed_lines = []
        current_paragraph = []
        
        for token in tokens:
            if token.token_type == TokenType.PROBLEMATIC_STRUCTURE:
                continue
            elif token.token_type == TokenType.PARAGRAPH_BREAK:
                if current_paragraph:
                    processed_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                processed_lines.append('')
            elif token.token_type == TokenType.TITLE:
                if current_paragraph:
                    processed_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                processed_lines.append(f'# {token.text}')
            elif token.token_type == TokenType.TEXT:
                current_paragraph.append(token.text)
        
        # Adicionar último parágrafo
        if current_paragraph:
            processed_lines.append(' '.join(current_paragraph))
        
        return '\n'.join(processed_lines)
    
    def clean_problematic_structures(self, text: str) -> str:
        """Remove estruturas problemáticas de forma flexível"""
        # Padrões para estruturas que devem ser ignoradas
        problematic_patterns = [
            r'[A-Z]{4,}',  # Palavras muito longas em caps
            r'\b[A-Z]{2,}\s+[A-Z]{2,}\s+[A-Z]{2,}\b',  # Múltiplas palavras caps
            r'[^\w\s]{4,}',  # Sequências longas de símbolos
            r'\d{6,}',  # Números muito longos
            r'[A-Z]\.[A-Z]\.[A-Z]\.[A-Z]',  # Muitas iniciais
            r'[A-Z][A-Z][A-Z][A-Z]+',  # Acrônimos longos
        ]
        
        for pattern in problematic_patterns:
            text = re.sub(pattern, '', text)
        
        # Limpar linhas vazias múltiplas
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text.strip()

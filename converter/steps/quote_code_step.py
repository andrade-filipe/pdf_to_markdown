"""Passo de detecção e formatação de blocos de citação e código"""

import re
from typing import Dict, Any, List, Tuple
from .base_step import BaseStep


class QuoteCodeStep(BaseStep):
    """Passo responsável por detectar e formatar blocos de citação e código"""
    
    def __init__(self):
        super().__init__("QuoteCode")
        self.language = 'en'
        self.content_type = 'auto'
        
    def set_language(self, language: str):
        """Define o idioma para detecção específica"""
        self.language = language
        
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo para detecção específica"""
        self.content_type = content_type
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta e formata blocos de citação e código"""
        self.log_info("Iniciando detecção de citações e código")
        
        # Obter texto processado
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            self.log_info("Nenhum conteúdo Markdown encontrado")
            return data
        
        # Detectar e formatar citações
        processed_content = self._detect_and_format_quotes(markdown_content)
        
        # Detectar e formatar código
        processed_content = self._detect_and_format_code(processed_content)
        
        # Atualizar dados
        data['markdown_content'] = processed_content
        data['quotes_detected'] = self._count_quotes(processed_content)
        data['code_blocks_detected'] = self._count_code_blocks(processed_content)
        
        self.log_info(f"Detecção concluída. {data['quotes_detected']} citações e {data['code_blocks_detected']} blocos de código encontrados")
        return data
    
    def _detect_and_format_quotes(self, content: str) -> str:
        """Detecta e formata blocos de citação"""
        lines = content.split('\n')
        processed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Verificar se é início de citação
            if self._is_quote_start(line):
                # Processar citação completa
                quote_lines, new_i = self._process_quote(lines, i)
                processed_lines.extend(quote_lines)
                i = new_i
            else:
                # Linha normal, manter como está
                processed_lines.append(lines[i])
                i += 1
        
        return '\n'.join(processed_lines)
    
    def _is_quote_start(self, line: str) -> bool:
        """Verifica se uma linha é início de citação"""
        if not line:
            return False
        
        # Padrões de citação
        quote_patterns = [
            # Recuo significativo (mais de 4 espaços)
            r'^\s{4,}',
            # Aspas no início
            r'^["""''].*',
            # Frases que começam com citações comuns
            r'^(According to|As stated by|As mentioned in|In the words of|As noted by)',
            # Padrões específicos de artigos acadêmicos
            r'^(Smith et al\.|Johnson|According to the study|The research shows)',
        ]
        
        for pattern in quote_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _process_quote(self, lines: List[str], start_index: int) -> Tuple[List[str], int]:
        """
        Processa um bloco de citação completo
        Retorna: (linhas_processadas, próximo_índice)
        """
        quote_lines = []
        i = start_index
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Verificar se ainda é parte da citação
            if self._is_quote_continuation(line, i == start_index):
                # Formatar linha de citação
                formatted_line = self._format_quote_line(line, i == start_index)
                quote_lines.append(formatted_line)
                i += 1
            elif line == '':
                # Linha vazia - pode ser separador ou fim da citação
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if self._is_quote_continuation(next_line, False):
                        # Continuação da citação
                        quote_lines.append('')
                        i += 1
                    else:
                        # Fim da citação
                        break
                else:
                    # Última linha
                    break
            else:
                # Fim da citação
                break
        
        return quote_lines, i
    
    def _is_quote_continuation(self, line: str, is_first_line: bool) -> bool:
        """Verifica se uma linha é continuação de citação"""
        if not line:
            return False
        
        # Se é a primeira linha, usar padrões de início
        if is_first_line:
            return self._is_quote_start(line)
        
        # Para continuações, verificar recuo ou padrões de continuação
        continuation_patterns = [
            # Recuo significativo
            r'^\s{4,}',
            # Continuação com aspas
            r'^["""''].*',
            # Frases que continuam citações
            r'^(Furthermore|Moreover|Additionally|Also|However|Nevertheless)',
            # Padrões de continuação acadêmica
            r'^(The study|Research|Analysis|Results|Findings)',
        ]
        
        for pattern in continuation_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _format_quote_line(self, line: str, is_first_line: bool) -> str:
        """Formata uma linha de citação"""
        # Remover recuo excessivo
        line = line.lstrip()
        
        # Remover aspas no início e fim se existirem
        line = re.sub(r'^["""'']+', '', line)
        line = re.sub(r'["""'']+$', '', line)
        
        # Formatar como citação Markdown
        return f"> {line}"
    
    def _detect_and_format_code(self, content: str) -> str:
        """Detecta e formata blocos de código"""
        lines = content.split('\n')
        processed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Verificar se é início de código
            if self._is_code_start(line):
                # Processar bloco de código completo
                code_lines, new_i = self._process_code_block(lines, i)
                processed_lines.extend(code_lines)
                i = new_i
            else:
                # Linha normal, manter como está
                processed_lines.append(lines[i])
                i += 1
        
        return '\n'.join(processed_lines)
    
    def _is_code_start(self, line: str) -> bool:
        """Verifica se uma linha é início de código"""
        if not line:
            return False
        
        # Padrões de código
        code_patterns = [
            # Palavras-chave de programação
            r'\b(def|function|class|import|from|if|else|for|while|try|except|return|print|console\.log|var|let|const)\b',
            # Sintaxe de programação
            r'[{}();=<>!&|]',
            # Números e variáveis
            r'\b\d+\.\d+|\b[a-zA-Z_]\w*\s*[=<>!]',
            # Comentários
            r'^(\/\/|#|\/\*|<!--)',
            # Indentação com caracteres especiais
            r'^\s*[{}();=<>!&|]',
        ]
        
        # Verificar se a linha contém padrões de código
        code_score = 0
        for pattern in code_patterns:
            if re.search(pattern, line):
                code_score += 1
        
        # Se tem pelo menos 2 indicadores de código
        return code_score >= 2
    
    def _process_code_block(self, lines: List[str], start_index: int) -> Tuple[List[str], int]:
        """
        Processa um bloco de código completo
        Retorna: (linhas_processadas, próximo_índice)
        """
        code_lines = []
        i = start_index
        
        # Detectar linguagem de programação
        language = self._detect_language(lines[start_index])
        
        # Adicionar início do bloco de código
        code_lines.append(f"```{language}")
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Verificar se ainda é parte do código
            if self._is_code_continuation(line):
                # Adicionar linha de código
                code_lines.append(lines[i])  # Manter formatação original
                i += 1
            elif line == '':
                # Linha vazia - pode ser separador ou fim do código
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if self._is_code_continuation(next_line):
                        # Continuação do código
                        code_lines.append('')
                        i += 1
                    else:
                        # Fim do código
                        break
                else:
                    # Última linha
                    break
            else:
                # Fim do código
                break
        
        # Adicionar fim do bloco de código
        code_lines.append("```")
        
        return code_lines, i
    
    def _is_code_continuation(self, line: str) -> bool:
        """Verifica se uma linha é continuação de código"""
        if not line:
            return True  # Linhas vazias são permitidas em código
        
        # Padrões de continuação de código
        continuation_patterns = [
            # Sintaxe de programação
            r'[{}();=<>!&|]',
            # Indentação
            r'^\s+',
            # Comentários
            r'^(\/\/|#|\/\*|<!--)',
            # Strings
            r'["""''].*["""'']',
            # Números
            r'\d+',
        ]
        
        # Verificar se a linha contém padrões de código
        code_score = 0
        for pattern in continuation_patterns:
            if re.search(pattern, line):
                code_score += 1
        
        return code_score >= 1
    
    def _detect_language(self, line: str) -> str:
        """Detecta a linguagem de programação baseada no conteúdo"""
        line_lower = line.lower()
        
        # Padrões de linguagens específicas
        language_patterns = {
            'python': [r'\b(def|import|from|print|if __name__)\b', r'\.py\b'],
            'javascript': [r'\b(function|var|let|const|console\.log)\b', r'\.js\b'],
            'java': [r'\b(public|private|class|static|void)\b', r'\.java\b'],
            'cpp': [r'\b(#include|using namespace|std::)\b', r'\.cpp\b'],
            'c': [r'\b(#include|printf|scanf|int main)\b', r'\.c\b'],
            'html': [r'<[^>]+>', r'\.html?\b'],
            'css': [r'[.#][a-zA-Z-]+\s*{', r'\.css\b'],
            'sql': [r'\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)\b', r'\.sql\b'],
            'bash': [r'\b(#!/bin/bash|echo|ls|cd|mkdir)\b', r'\.sh\b'],
        }
        
        for language, patterns in language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line_lower):
                    return language
        
        return ''  # Linguagem não detectada
    
    def _count_quotes(self, content: str) -> int:
        """Conta o número de citações detectadas"""
        lines = content.split('\n')
        quote_count = 0
        in_quote = False
        
        for line in lines:
            if line.strip().startswith('>'):
                if not in_quote:
                    quote_count += 1
                    in_quote = True
            else:
                in_quote = False
        
        return quote_count
    
    def _count_code_blocks(self, content: str) -> int:
        """Conta o número de blocos de código detectados"""
        return content.count('```') // 2  # Cada bloco tem início e fim

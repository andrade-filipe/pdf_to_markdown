"""Passo de detecção e formatação de listas"""

import re
from typing import Dict, Any, List, Tuple
from .base_step import BaseStep


class ListDetectionStep(BaseStep):
    """Passo responsável por detectar e formatar listas ordenadas e não ordenadas"""
    
    def __init__(self):
        super().__init__("ListDetection")
        self.language = 'en'
        self.content_type = 'auto'
        
    def set_language(self, language: str):
        """Define o idioma para detecção específica"""
        self.language = language
        
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo para detecção específica"""
        self.content_type = content_type
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta e formata listas no texto"""
        self.log_info("Iniciando detecção de listas")
        
        # Obter texto processado
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            self.log_info("Nenhum conteúdo Markdown encontrado")
            return data
        
        # Detectar e formatar listas
        processed_content = self._detect_and_format_lists(markdown_content)
        
        # Atualizar dados
        data['markdown_content'] = processed_content
        data['lists_detected'] = self._count_lists(processed_content)
        
        self.log_info(f"Detecção de listas concluída. {data['lists_detected']} listas encontradas")
        return data
    
    def _detect_and_format_lists(self, content: str) -> str:
        """Detecta e formata listas no conteúdo"""
        lines = content.split('\n')
        processed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Verificar se é início de lista
            list_type, level = self._detect_list_item(line)
            
            if list_type:
                # Processar lista completa
                list_lines, new_i = self._process_list(lines, i, list_type, level)
                processed_lines.extend(list_lines)
                i = new_i
            else:
                # Linha normal, manter como está
                processed_lines.append(lines[i])
                i += 1
        
        return '\n'.join(processed_lines)
    
    def _detect_list_item(self, line: str) -> Tuple[str, int]:
        """
        Detecta se uma linha é um item de lista com análise contextual avançada
        Retorna: (tipo_lista, nível_indentação)
        """
        if not line:
            return None, 0
        
        # Padrões para listas não ordenadas
        unordered_patterns = [
            r'^[-*•]\s+',  # -, *, •
            r'^\s*[-*•]\s+',  # Com indentação
            r'^[▪▫▬▭▮▯]\s+',  # Símbolos Unicode
            r'^\s*[▪▫▬▭▮▯]\s+',  # Com indentação
        ]
        
        # Padrões para listas ordenadas
        ordered_patterns = [
            r'^\d+\.\s+',  # 1., 2., etc.
            r'^\s*\d+\.\s+',  # Com indentação
            r'^[a-z]\.\s+',  # a., b., etc.
            r'^\s*[a-z]\.\s+',  # Com indentação
            r'^[A-Z]\.\s+',  # A., B., etc.
            r'^\s*[A-Z]\.\s+',  # Com indentação
            r'^[ivxlcdm]+\.\s+',  # i., ii., iii., etc.
            r'^\s*[ivxlcdm]+\.\s+',  # Com indentação
            r'^\(\d+\)\s+',  # (1), (2), etc.
            r'^\s*\(\d+\)\s+',  # Com indentação
            r'^[a-z]\)\s+',  # a), b), etc.
            r'^\s*[a-z]\)\s+',  # Com indentação
            r'^[A-Z]\)\s+',  # A), B), etc.
            r'^\s*[A-Z]\)\s+',  # Com indentação
        ]
        
        # Verificar listas não ordenadas
        for pattern in unordered_patterns:
            if re.match(pattern, line):
                level = len(line) - len(line.lstrip())
                return 'unordered', level
        
        # Verificar listas ordenadas
        for pattern in ordered_patterns:
            if re.match(pattern, line):
                level = len(line) - len(line.lstrip())
                return 'ordered', level
        
        # Verificar padrões de lista mais complexos
        if self._is_complex_list_item(line):
            level = len(line) - len(line.lstrip())
            return 'complex', level
        
        return None, 0
    
    def _is_complex_list_item(self, line: str) -> bool:
        """Verifica se uma linha é um item de lista complexo"""
        # Padrões complexos de lista
        complex_patterns = [
            r'^[A-Z][a-z]+\.\s+',  # Primeira., Segunda., etc.
            r'^\d+\)\s+',  # 1), 2), etc.
            r'^[A-Z][a-z]+\s+\d+\.\s+',  # Item 1., etc.
            r'^[a-z]+\s+\d+\.\s+',  # item 1., etc.
            r'^[A-Z]+\.\s+',  # I., II., etc.
            r'^[a-z]+\.\s+',  # i., ii., etc.
        ]
        
        for pattern in complex_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _process_list(self, lines: List[str], start_index: int, list_type: str, level: int) -> Tuple[List[str], int]:
        """Processa uma lista completa com detecção de aninhamento"""
        list_lines = []
        i = start_index
        current_level = level
        list_items = []
        
        # Coletar todos os itens da lista
        while i < len(lines):
            line = lines[i].strip()
            
            # Verificar se ainda é parte da lista
            item_type, item_level = self._detect_list_item(line)
            
            if item_type and item_level >= level:
                # É um item da lista
                list_items.append({
                    'line': line,
                    'type': item_type,
                    'level': item_level,
                    'content': self._extract_list_content(line, item_type)
                })
                i += 1
            elif self._is_list_continuation(line, list_items):
                # Continuação do item anterior
                if list_items:
                    list_items[-1]['content'] += ' ' + line
                i += 1
            else:
                # Fim da lista
                break
        
        # Formatar a lista
        formatted_list = self._format_list_items(list_items, list_type)
        list_lines.extend(formatted_list)
        
        return list_lines, i
    
    def _extract_list_content(self, line: str, list_type: str) -> str:
        """Extrai o conteúdo de um item de lista"""
        if list_type == 'unordered':
            # Remover marcadores de lista não ordenada
            content = re.sub(r'^[-*•▪▫▬▭▮▯]\s*', '', line)
        elif list_type == 'ordered':
            # Remover marcadores de lista ordenada
            content = re.sub(r'^\d+\.\s*', '', line)
            content = re.sub(r'^[a-zA-Z]\.\s*', '', content)
            content = re.sub(r'^[ivxlcdm]+\.\s*', '', content)
            content = re.sub(r'^\(\d+\)\s*', '', content)
            content = re.sub(r'^[a-zA-Z]\)\s*', '', content)
        else:
            # Lista complexa
            content = re.sub(r'^[A-Z][a-z]+\.\s*', '', line)
            content = re.sub(r'^\d+\)\s*', '', content)
            content = re.sub(r'^[A-Z][a-z]+\s+\d+\.\s*', '', content)
            content = re.sub(r'^[a-z]+\s+\d+\.\s*', '', content)
            content = re.sub(r'^[A-Z]+\.\s*', '', content)
            content = re.sub(r'^[a-z]+\.\s*', '', content)
        
        return content.strip()
    
    def _is_list_continuation(self, line: str, list_items: List[Dict]) -> bool:
        """Verifica se uma linha é continuação do item anterior da lista"""
        if not list_items:
            return False
        
        # Se a linha não tem marcador de lista e não está vazia
        if line and not self._detect_list_item(line)[0]:
            # Verificar se parece continuação
            if not line[0].isupper() or line.endswith(('.', '!', '?')):
                return True
        
        return False
    
    def _format_list_items(self, list_items: List[Dict], list_type: str) -> List[str]:
        """Formata os itens da lista com suporte a aninhamento"""
        formatted_lines = []
        
        for item in list_items:
            content = item['content']
            level = item['level']
            
            # Determinar o marcador baseado no tipo e nível
            if list_type == 'unordered':
                marker = self._get_unordered_marker(level)
            else:
                marker = self._get_ordered_marker(level, len(formatted_lines))
            
            # Aplicar indentação baseada no nível
            indent = '  ' * (level // 2)  # 2 espaços por nível
            
            # Formatar o item
            formatted_item = f"{indent}{marker} {content}"
            formatted_lines.append(formatted_item)
        
        return formatted_lines
    
    def _get_unordered_marker(self, level: int) -> str:
        """Retorna o marcador apropriado para lista não ordenada baseado no nível"""
        markers = ['-', '*', '•', '▪']
        return markers[min(level, len(markers) - 1)]
    
    def _get_ordered_marker(self, level: int, item_index: int) -> str:
        """Retorna o marcador apropriado para lista ordenada baseado no nível"""
        if level == 0:
            return f"{item_index + 1}."
        elif level == 1:
            return f"{chr(97 + item_index)}."  # a, b, c, etc.
        elif level == 2:
            return f"{chr(65 + item_index)}."  # A, B, C, etc.
        else:
            return f"{item_index + 1}."
    
    def _count_lists(self, content: str) -> Dict[str, int]:
        """Conta o número de listas detectadas"""
        lines = content.split('\n')
        unordered_count = 0
        ordered_count = 0
        in_list = False
        current_type = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                in_list = False
                current_type = None
                continue
            
            # Verificar se é item de lista
            if line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
                if not in_list or current_type != 'unordered':
                    unordered_count += 1
                    in_list = True
                    current_type = 'unordered'
            elif re.match(r'^\d+\.\s+', line):
                if not in_list or current_type != 'ordered':
                    ordered_count += 1
                    in_list = True
                    current_type = 'ordered'
            else:
                in_list = False
                current_type = None
        
        return {
            'unordered': unordered_count,
            'ordered': ordered_count,
            'total': unordered_count + ordered_count
        }
    
    def _detect_nested_lists(self, content: str) -> str:
        """Detecta e formata listas aninhadas"""
        lines = content.split('\n')
        processed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Verificar se é início de lista aninhada
            if self._is_nested_list_start(line, lines, i):
                # Processar lista aninhada
                nested_lines, new_i = self._process_nested_list(lines, i)
                processed_lines.extend(nested_lines)
                i = new_i
            else:
                # Linha normal
                processed_lines.append(lines[i])
                i += 1
        
        return '\n'.join(processed_lines)
    
    def _is_nested_list_start(self, line: str, lines: List[str], index: int) -> bool:
        """Verifica se uma linha é início de lista aninhada"""
        if index + 1 >= len(lines):
            return False
        
        current_item_type, current_level = self._detect_list_item(line)
        if not current_item_type:
            return False
        
        # Verificar se a próxima linha tem nível maior
        next_line = lines[index + 1].strip()
        next_item_type, next_level = self._detect_list_item(next_line)
        
        if next_item_type and next_level > current_level:
            return True
        
        return False
    
    def _process_nested_list(self, lines: List[str], start_index: int) -> Tuple[List[str], int]:
        """Processa uma lista aninhada"""
        # Implementação similar ao _process_list mas com suporte a aninhamento
        return self._process_list(lines, start_index, 'nested', 0)

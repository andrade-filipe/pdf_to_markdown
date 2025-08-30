"""Passo de detecção e formatação de notas de rodapé"""

import re
from typing import Dict, Any, List, Tuple
from .base_step import BaseStep


class FootnoteStep(BaseStep):
    """Passo responsável por detectar e formatar notas de rodapé"""
    
    def __init__(self):
        super().__init__("Footnote")
        self.language = 'en'
        self.content_type = 'auto'
        
    def set_language(self, language: str):
        """Define o idioma para detecção específica"""
        self.language = language
        
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo para detecção específica"""
        self.content_type = content_type
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta e formata notas de rodapé"""
        self.log_info("Iniciando detecção de notas de rodapé")
        
        # Obter texto processado
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            self.log_info("Nenhum conteúdo Markdown encontrado")
            return data
        
        # Detectar e formatar notas de rodapé
        processed_content, footnotes = self._detect_and_format_footnotes(markdown_content)
        
        # Adicionar notas de rodapé ao final do documento
        if footnotes:
            processed_content += '\n\n' + self._format_footnotes_section(footnotes)
        
        # Atualizar dados
        data['markdown_content'] = processed_content
        data['footnotes_detected'] = len(footnotes)
        data['footnotes_content'] = footnotes
        
        self.log_info(f"Detecção de notas de rodapé concluída. {len(footnotes)} notas encontradas")
        return data
    
    def _detect_and_format_footnotes(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Detecta e formata notas de rodapé no conteúdo"""
        lines = content.split('\n')
        processed_lines = []
        footnotes = []
        footnote_counter = 1
        
        for line in lines:
            # Verificar se a linha contém referências de nota de rodapé
            processed_line, new_footnotes = self._process_footnote_references(line, footnote_counter)
            processed_lines.append(processed_line)
            
            if new_footnotes:
                footnotes.extend(new_footnotes)
                footnote_counter += len(new_footnotes)
        
        return '\n'.join(processed_lines), footnotes
    
    def _process_footnote_references(self, line: str, start_counter: int) -> Tuple[str, List[Dict[str, Any]]]:
        """Processa referências de notas de rodapé em uma linha"""
        footnotes = []
        counter = start_counter
        
        # Padrões de referências de notas de rodapé
        footnote_patterns = [
            # [1], [2], etc.
            r'\[(\d+)\]',
            # ^1, ^2, etc.
            r'\^(\d+)',
            # ¹, ², ³, etc.
            r'[¹²³⁴⁵⁶⁷⁸⁹]',
            # (1), (2), etc.
            r'\((\d+)\)',
        ]
        
        processed_line = line
        
        for pattern in footnote_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Extrair número da nota
                if pattern == r'[¹²³⁴⁵⁶⁷⁸⁹]':
                    # Converter símbolos para números
                    symbol_to_number = {'¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', 
                                      '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
                    footnote_number = symbol_to_number.get(match.group(0), '1')
                else:
                    footnote_number = match.group(1)
                
                # Criar nota de rodapé
                footnote = {
                    'original_number': footnote_number,
                    'markdown_number': counter,
                    'content': self._extract_footnote_content(footnote_number),
                    'position': match.start()
                }
                
                footnotes.append(footnote)
                
                # Substituir referência por formato Markdown
                markdown_reference = f'[^{counter}]'
                processed_line = processed_line[:match.start()] + markdown_reference + processed_line[match.end():]
                
                counter += 1
        
        return processed_line, footnotes
    
    def _extract_footnote_content(self, footnote_number: str) -> str:
        """Extrai o conteúdo de uma nota de rodapé"""
        # Por enquanto, retorna conteúdo genérico
        # Em uma implementação completa, isso extrairia o conteúdo real da nota
        return f"Nota de rodapé {footnote_number}"
    
    def _format_footnotes_section(self, footnotes: List[Dict[str, Any]]) -> str:
        """Formata a seção de notas de rodapé"""
        if not footnotes:
            return ""
        
        section_lines = ["## Notas de Rodapé", ""]
        
        for footnote in footnotes:
            section_lines.append(f"[^{footnote['markdown_number']}]: {footnote['content']}")
        
        return '\n'.join(section_lines)
    
    def _detect_footnote_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Detecta blocos de notas de rodapé no final do documento"""
        lines = content.split('\n')
        footnotes = []
        
        # Padrões para blocos de notas de rodapé
        footnote_block_patterns = [
            # 1. Conteúdo da nota
            r'^\d+\.\s+(.+)',
            # [1] Conteúdo da nota
            r'^\[\d+\]\s+(.+)',
            # ¹ Conteúdo da nota
            r'^[¹²³⁴⁵⁶⁷⁸⁹]\s+(.+)',
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            for pattern in footnote_block_patterns:
                match = re.match(pattern, line)
                if match:
                    # Extrair número da nota
                    if pattern == r'^\d+\.\s+(.+)':
                        number = re.match(r'^(\d+)\.', line).group(1)
                    elif pattern == r'^\[\d+\]\s+(.+)':
                        number = re.match(r'^\[(\d+)\]', line).group(1)
                    elif pattern == r'^[¹²³⁴⁵⁶⁷⁸⁹]\s+(.+)':
                        symbol_to_number = {'¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', 
                                          '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
                        number = symbol_to_number.get(line[0], '1')
                    
                    # Extrair conteúdo
                    content = match.group(1)
                    
                    # Verificar se há continuação na próxima linha
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not re.match(r'^\d+\.|^\[\d+\]|^[¹²³⁴⁵⁶⁷⁸⁹]', next_line):
                            content += ' ' + next_line
                    
                    footnote = {
                        'number': number,
                        'content': content,
                        'line_number': i
                    }
                    
                    footnotes.append(footnote)
                    break
        
        return footnotes
    
    def _link_footnotes_to_references(self, content: str, footnotes: List[Dict[str, Any]]) -> str:
        """Vincula notas de rodapé às suas referências no texto"""
        lines = content.split('\n')
        
        for footnote in footnotes:
            number = footnote['number']
            
            # Padrões de referência para substituir
            reference_patterns = [
                rf'\[{number}\]',
                rf'\^{number}',
                rf'\({number}\)',
            ]
            
            for i, line in enumerate(lines):
                for pattern in reference_patterns:
                    if re.search(pattern, line):
                        # Substituir por formato Markdown
                        markdown_reference = f'[^{number}]'
                        lines[i] = re.sub(pattern, markdown_reference, line)
        
        return '\n'.join(lines)
    
    def _clean_footnote_blocks(self, content: str) -> str:
        """Remove blocos de notas de rodapé do texto principal"""
        lines = content.split('\n')
        cleaned_lines = []
        in_footnote_block = False
        
        for line in lines:
            # Verificar se estamos em um bloco de notas de rodapé
            if re.match(r'^\d+\.\s+|^\[\d+\]\s+|^[¹²³⁴⁵⁶⁷⁸⁹]\s+', line.strip()):
                in_footnote_block = True
                continue
            
            # Se estamos em um bloco de notas e encontramos uma linha vazia, sair do bloco
            if in_footnote_block and not line.strip():
                in_footnote_block = False
                continue
            
            # Se não estamos em um bloco de notas, manter a linha
            if not in_footnote_block:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _count_footnotes(self, content: str) -> int:
        """Conta o número de notas de rodapé detectadas"""
        # Contar referências de notas de rodapé
        reference_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\^\d+',    # ^1, ^2, etc.
            r'[¹²³⁴⁵⁶⁷⁸⁹]',  # ¹, ², ³, etc.
            r'\(\d+\)',  # (1), (2), etc.
        ]
        
        count = 0
        for pattern in reference_patterns:
            count += len(re.findall(pattern, content))
        
        return count

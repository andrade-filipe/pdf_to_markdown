"""Step de Regex Avançado para Extração e Estruturação de Conteúdo"""

import re
from typing import Dict, Any, List, Tuple, Optional, Match
from .base_step import BaseStep


class AdvancedRegexStep(BaseStep):
    """Step que usa regex avançado para extração e estruturação de conteúdo"""
    
    def __init__(self):
        super().__init__("AdvancedRegex")
        self.patterns = self._load_advanced_patterns()
        self.extraction_rules = self._load_extraction_rules()
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo usando regex avançado"""
        self.log_info("Iniciando processamento com regex avançado")
        
        # Tentar diferentes campos de conteúdo
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            markdown_content = data.get('raw_text', '')
        if not markdown_content:
            markdown_content = data.get('text', '')
        
        if not markdown_content:
            self.log_warning("Nenhum conteúdo encontrado para processamento")
            return data
        
        try:
            # Aplicar regex avançado
            processed_content = self._apply_advanced_regex(markdown_content)
            
            if processed_content:
                data['markdown_content'] = processed_content
                data['advanced_regex_stats'] = {
                    'original_length': len(markdown_content),
                    'final_length': len(processed_content),
                    'patterns_applied': len(self.patterns),
                    'extractions_made': self._count_extractions(markdown_content),
                    'improvement_ratio': len(processed_content) / len(markdown_content) if markdown_content else 1.0
                }
                
                self.log_info(f"Regex avançado concluído")
                self.log_info(f"Padrões aplicados: {data['advanced_regex_stats']['patterns_applied']}")
                self.log_info(f"Extrações realizadas: {data['advanced_regex_stats']['extractions_made']}")
            else:
                self.log_warning("Regex avançado não retornou conteúdo processado")
                
        except Exception as e:
            self.log_error(f"Erro no regex avançado: {e}")
        
        return data
    
    def _apply_advanced_regex(self, content: str) -> Optional[str]:
        """Aplica regex avançado ao conteúdo"""
        
        # Dividir em linhas para processamento
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = self._process_line_with_regex(line)
            if processed_line:
                processed_lines.append(processed_line)
        
        # Aplicar padrões de estruturação global
        result = '\n'.join(processed_lines)
        result = self._apply_global_patterns(result)
        
        return result
    
    def _process_line_with_regex(self, line: str) -> Optional[str]:
        """Processa uma linha com regex avançado"""
        
        # Aplicar cada padrão de extração
        for pattern_name, pattern_info in self.extraction_rules.items():
            pattern = pattern_info['pattern']
            replacement = pattern_info['replacement']
            flags = pattern_info.get('flags', 0)
            
            # Aplicar regex com lookahead/lookbehind
            if pattern_info.get('use_lookaround', False):
                line = self._apply_lookaround_regex(line, pattern, replacement, flags)
            else:
                line = re.sub(pattern, replacement, line, flags=flags)
        
        return line.strip() if line.strip() else None
    
    def _apply_lookaround_regex(self, line: str, pattern: str, replacement: str, flags: int) -> str:
        """Aplica regex com lookahead/lookbehind"""
        
        try:
            # Usar regex recursivo para padrões complexos
            if '(?R)' in pattern:
                # Padrão recursivo - implementar recursão manual
                return self._apply_recursive_regex(line, pattern, replacement, flags)
            else:
                # Padrão normal com lookaround
                return re.sub(pattern, replacement, line, flags=flags)
        except Exception as e:
            self.log_warning(f"Erro ao aplicar regex lookaround: {e}")
            return line
    
    def _apply_recursive_regex(self, line: str, pattern: str, replacement: str, flags: int) -> str:
        """Aplica regex recursivo manualmente"""
        
        # Substituir (?R) por recursão manual
        if '(?R)' in pattern:
            # Padrão para detectar estruturas aninhadas
            nested_pattern = pattern.replace('(?R)', r'(?:\g<0>|[^()]*)')
            return re.sub(nested_pattern, replacement, line, flags=flags)
        
        return line
    
    def _apply_global_patterns(self, content: str) -> str:
        """Aplica padrões globais ao conteúdo"""
        
        # 1. Limpar linhas vazias excessivas
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 2. Corrigir espaçamento de títulos
        content = re.sub(r'^(\s*#{1,6}\s+.*?)\s*$', r'\1\n', content, flags=re.MULTILINE)
        
        # 3. Agrupar linhas de lista
        content = self._group_list_items(content)
        
        # 4. Corrigir formatação de tabelas
        content = self._fix_table_formatting(content)
        
        # 5. Limpar caracteres especiais problemáticos
        content = self._clean_special_characters(content)
        
        return content
    
    def _group_list_items(self, content: str) -> str:
        """Agrupa itens de lista"""
        
        lines = content.split('\n')
        grouped_lines = []
        in_list = False
        
        for line in lines:
            # Detectar início de lista
            if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                if not in_list:
                    grouped_lines.append('')  # Espaço antes da lista
                    in_list = True
                grouped_lines.append(line)
            else:
                if in_list and line.strip():
                    grouped_lines.append('')  # Espaço após lista
                    in_list = False
                grouped_lines.append(line)
        
        return '\n'.join(grouped_lines)
    
    def _fix_table_formatting(self, content: str) -> str:
        """Corrige formatação de tabelas"""
        
        # Detectar linhas que parecem tabelas
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Se linha contém múltiplos |, é provavelmente uma tabela
            if line.count('|') >= 2:
                # Garantir que há espaços adequados
                line = re.sub(r'\|\s*', '| ', line)
                line = re.sub(r'\s*\|', ' |', line)
                
                # Adicionar linha de separação se não existir
                if i + 1 < len(lines) and not re.match(r'^\s*\|[\s\-:|]+\|\s*$', lines[i + 1]):
                    fixed_lines.append(line)
                    # Criar linha de separação
                    separator = re.sub(r'[^|]', '-', line)
                    separator = re.sub(r'\|', '|', separator)
                    fixed_lines.append(separator)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _clean_special_characters(self, content: str) -> str:
        """Limpa caracteres especiais problemáticos"""
        
        # Substituir caracteres Unicode problemáticos
        replacements = {
            '\u2013': '-',  # En dash
            '\u2014': '--',  # Em dash
            '\u2018': "'",   # Left single quote
            '\u2019': "'",   # Right single quote
            '\u201c': '"',   # Left double quote
            '\u201d': '"',   # Right double quote
            '\u2022': '-',   # Bullet
            '\u2026': '...', # Ellipsis
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Remover caracteres de controle
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        return content
    
    def _count_extractions(self, content: str) -> int:
        """Conta quantas extrações foram feitas"""
        count = 0
        
        for pattern_name, pattern_info in self.extraction_rules.items():
            pattern = pattern_info['pattern']
            flags = pattern_info.get('flags', 0)
            matches = re.findall(pattern, content, flags=flags)
            count += len(matches)
        
        return count
    
    def _load_advanced_patterns(self) -> Dict[str, str]:
        """Carrega padrões regex avançados"""
        return {
            'title_detection': r'^(?=.*[A-Z])(?=.*[a-z])(?!.*[.!?]$)(?=.{3,80}$).*$',
            'list_item': r'^\s*[-*+]\s+(.+)$',
            'numbered_list': r'^\s*\d+\.\s+(.+)$',
            'table_row': r'^\s*\|.*\|.*\|\s*$',
            'code_block': r'```[\s\S]*?```',
            'inline_code': r'`[^`]+`',
            'bold_text': r'\*\*([^*]+)\*\*',
            'italic_text': r'\*([^*]+)\*',
            'link': r'\[([^\]]+)\]\(([^)]+)\)',
            'image': r'!\[([^\]]*)\]\(([^)]+)\)',
            'footnote': r'\[\^([^\]]+)\]',
            'citation': r'\[([^\]]+)\]',
        }
    
    def _load_extraction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Carrega regras de extração com regex avançado"""
        return {
            'fix_hyphenation': {
                'pattern': r'(\w+)-\s*\n\s*(\w+)',
                'replacement': r'\1\2',
                'flags': re.MULTILINE,
                'description': 'Corrige palavras hifenizadas'
            },
            'detect_titles': {
                'pattern': r'^(?=.*[A-Z])(?=.*[a-z])(?!.*[.!?]$)(?=.{3,80}$)(.*)$',
                'replacement': r'## \1',
                'flags': re.MULTILINE,
                'description': 'Detecta títulos baseado em características'
            },
            'fix_list_formatting': {
                'pattern': r'^\s*[-*+]\s+(.+)$',
                'replacement': r'- \1',
                'flags': re.MULTILINE,
                'description': 'Padroniza formatação de listas'
            },
            'detect_paragraphs': {
                'pattern': r'([.!?])\s*\n\s*([A-Z])',
                'replacement': r'\1\n\n\2',
                'flags': re.MULTILINE,
                'description': 'Adiciona quebras de parágrafo'
            },
            'fix_table_alignment': {
                'pattern': r'^\s*\|(.*)\|\s*$',
                'replacement': lambda m: self._fix_table_row(m),
                'flags': re.MULTILINE,
                'description': 'Corrige alinhamento de tabelas'
            },
            'detect_code_blocks': {
                'pattern': r'```(\w+)?\n([\s\S]*?)\n```',
                'replacement': r'```\1\n\2\n```',
                'flags': re.MULTILINE,
                'description': 'Formata blocos de código'
            },
            'fix_quotes': {
                'pattern': r'["""]([^"""]+)["""]',
                'replacement': r'"\1"',
                'flags': re.MULTILINE,
                'description': 'Corrige aspas Unicode'
            },
            'detect_sections': {
                'pattern': r'^(abstract|introduction|methods|results|discussion|conclusion|references|bibliography):?\s*$',
                'replacement': r'# \1',
                'flags': re.MULTILINE | re.IGNORECASE,
                'description': 'Detecta seções principais'
            },
            'fix_spacing': {
                'pattern': r'([.!?])\s*([A-Z])',
                'replacement': r'\1 \2',
                'flags': re.MULTILINE,
                'description': 'Corrige espaçamento após pontuação'
            },
            'detect_emphasis': {
                'pattern': r'\*\*([^*]+)\*\*',
                'replacement': r'**\1**',
                'flags': re.MULTILINE,
                'description': 'Formata texto em negrito'
            }
        }
    
    def _fix_table_row(self, match: Match) -> str:
        """Corrige uma linha de tabela"""
        content = match.group(1)
        cells = [cell.strip() for cell in content.split('|')]
        
        # Garantir que todas as células tenham conteúdo
        fixed_cells = []
        for cell in cells:
            if cell:
                fixed_cells.append(f' {cell} ')
            else:
                fixed_cells.append('   ')
        
        return f'|{"|".join(fixed_cells)}|'
    
    def add_custom_pattern(self, name: str, pattern: str, replacement: str, flags: int = 0):
        """Adiciona padrão customizado"""
        self.extraction_rules[name] = {
            'pattern': pattern,
            'replacement': replacement,
            'flags': flags,
            'description': f'Custom pattern: {name}'
        }
        self.log_info(f"Padrão customizado adicionado: {name}")
    
    def get_pattern_stats(self) -> Dict[str, int]:
        """Retorna estatísticas dos padrões"""
        stats = {}
        for name in self.extraction_rules:
            stats[name] = 0
        return stats

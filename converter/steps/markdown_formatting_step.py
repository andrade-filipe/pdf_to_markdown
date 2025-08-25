"""Passo de formatação e limpeza do Markdown"""

import re
from typing import Dict, Any, List
from .base_step import BaseStep


class MarkdownFormattingStep(BaseStep):
    """Passo responsável por melhorar a formatação do Markdown"""
    
    def __init__(self):
        super().__init__("MarkdownFormatting")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Melhora a formatação do Markdown"""
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            return data
        
        # Aplicar melhorias de formatação
        formatted_content = self._format_markdown(markdown_content)
        
        # Atualizar o conteúdo
        data['markdown_content'] = formatted_content
        return data
    
    def _format_markdown(self, content: str) -> str:
        """Aplica melhorias de formatação ao Markdown"""
        lines = content.split('\n')
        formatted_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Pular linhas vazias no início
            if not line and i == 0:
                i += 1
                continue
            
            # Remover números soltos no início
            if re.match(r'^\d+$', line) and i < 5:
                i += 1
                continue
            
            # Consolidar títulos duplicados
            if line.startswith('#'):
                title = self._consolidate_title(lines, i)
                if title:
                    formatted_lines.append(title)
                # Pular linhas duplicadas
                while i + 1 < len(lines) and lines[i + 1].strip().startswith('#'):
                    i += 1
            else:
                # Para parágrafos normais, apenas adicionar a linha
                if line:
                    formatted_lines.append(line)
                else:
                    formatted_lines.append("")
            
            i += 1
        
        # Juntar linhas e aplicar limpezas finais
        result = '\n'.join(formatted_lines)
        result = self._final_cleanup(result)
        
        return result
    
    def _pre_cleanup(self, content: str) -> str:
        """Limpeza prévia do conteúdo"""
        # Remover caracteres muito estranhos
        content = re.sub(r'[^\x00-\x7F\u00A0-\uFFFF\s]', ' ', content)
        
        # Remover linhas com apenas caracteres especiais
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Se a linha tem muitos caracteres especiais, pular
            special_chars = len(re.findall(r'[^\w\s\-:.,()!?;]', line))
            if special_chars < len(line) * 0.5:  # Menos de 50% de caracteres especiais (mais permissivo)
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _consolidate_title(self, lines: List[str], start_idx: int) -> str:
        """Consolida títulos duplicados em um só"""
        title_parts = []
        i = start_idx
        
        # Coletar todas as partes do título
        while i < len(lines) and lines[i].strip().startswith('#'):
            title_part = lines[i].strip()
            # Remover o # e espaços
            clean_title = re.sub(r'^#+\s*', '', title_part)
            if clean_title:
                title_parts.append(clean_title)
            i += 1
        
        if not title_parts:
            return ""
        
        # Juntar partes do título
        full_title = ' '.join(title_parts)
        
        # Limpar caracteres estranhos e quebras
        full_title = re.sub(r'\s+', ' ', full_title).strip()
        
        # Remover caracteres muito estranhos, mas manter pontuação útil
        full_title = re.sub(r'[^\w\s\-:.,()!?]', '', full_title)
        full_title = re.sub(r'\s+', ' ', full_title).strip()
        
        # Se o título ficou muito curto ou estranho, tentar uma abordagem diferente
        if len(full_title) < 3 or full_title.isupper():
            # Tentar juntar de forma mais inteligente
            words = []
            for part in title_parts:
                words.extend(part.split())
            
            # Filtrar palavras muito curtas ou estranhas
            filtered_words = []
            for word in words:
                if len(word) > 1 and not re.match(r'^[^\w]*$', word):
                    filtered_words.append(word)
            
            if filtered_words:
                full_title = ' '.join(filtered_words)
        
        # Se ainda está muito curto, tentar juntar títulos consecutivos
        if len(full_title) < 5 and len(title_parts) > 1:
            # Juntar apenas as primeiras palavras de cada parte
            first_words = []
            for part in title_parts:
                words = part.split()
                if words:
                    first_words.append(words[0])
            if first_words:
                full_title = ' '.join(first_words)
        
        # Determinar nível do título baseado no contexto
        if any(word in full_title.lower() for word in ['chapter', 'capítulo', 'introduction', 'conclusion', 'abstract']):
            return f"# {full_title}"
        elif any(word in full_title.lower() for word in ['section', 'seção', 'part']):
            return f"## {full_title}"
        else:
            return f"### {full_title}"
    
    def _consolidate_paragraph(self, lines: List[str], start_idx: int) -> List[str]:
        """Consolida linhas em parágrafos bem formatados"""
        paragraph_lines = []
        i = start_idx
        
        while i < len(lines) and not self._is_new_section(lines[i]):
            line = lines[i].strip()
            
            if line:
                # Se a linha termina com hífen, é continuação
                if line.endswith('-'):
                    paragraph_lines.append(line[:-1])  # Remove o hífen
                else:
                    paragraph_lines.append(line)
            else:
                # Linha vazia indica fim do parágrafo
                if paragraph_lines:
                    paragraph_lines.append("")
                break
            
            i += 1
        
        if paragraph_lines:
            # Juntar linhas do parágrafo
            paragraph_text = ' '.join(paragraph_lines)
            # Limpar espaços extras
            paragraph_text = re.sub(r'\s+', ' ', paragraph_text).strip()
            
            # Verificar se é uma lista ou parágrafo normal
            if re.match(r'^\d+\.', paragraph_text):
                return [paragraph_text]
            else:
                return [paragraph_text, ""]
        
        return []
    
    def _is_new_section(self, line: str) -> bool:
        """Verifica se uma linha indica nova seção"""
        line = line.strip()
        
        # Títulos
        if line.startswith('#'):
            return True
        
        # Números de seção
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return True
        
        # Palavras-chave de seção
        section_keywords = [
            'introduction', 'conclusion', 'abstract', 'references', 'bibliography',
            'appendix', 'chapter', 'section', 'part',
            'introdução', 'conclusão', 'resumo', 'referências', 'bibliografia',
            'apêndice', 'capítulo', 'seção', 'parte'
        ]
        
        if any(keyword in line.lower() for keyword in section_keywords):
            return True
        
        return False
    
    def _final_cleanup(self, content: str) -> str:
        """Aplica limpezas finais"""
        # Remover linhas vazias excessivas
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Limpar espaços no início e fim
        content = content.strip()
        
        # Melhorar formatação de listas
        content = re.sub(r'(\d+\.)\s+', r'\1 ', content)
        
        # Melhorar formatação de citações
        content = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', content)
        
        return content

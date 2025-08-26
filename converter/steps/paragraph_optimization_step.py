"""Passo de otimização de parágrafos e redução de quebras de linha"""

import re
from typing import Dict, Any, List, Tuple
from .base_step import BaseStep


class ParagraphOptimizationStep(BaseStep):
    """Passo responsável por otimizar parágrafos e reduzir quebras de linha desnecessárias"""
    
    def __init__(self):
        super().__init__("ParagraphOptimization")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o texto para otimizar parágrafos e reduzir quebras desnecessárias"""
        text_blocks = data.get('text_blocks', [])
        font_info_entries = data.get('font_info_entries', [])
        
        if not text_blocks:
            return data
        
        # Otimizar cada bloco de texto
        optimized_blocks = []
        for text in text_blocks:
            optimized_text = self._optimize_paragraph(text)
            if optimized_text.strip():
                optimized_blocks.append(optimized_text)
        
        # Criar texto final otimizado
        optimized_content = self._create_final_content(optimized_blocks, font_info_entries)
        
        # Atualizar dados
        data['text_blocks'] = optimized_blocks
        data['cleaned_text'] = optimized_content
        data['optimized_content'] = optimized_content
        
        return data
    
    def _optimize_paragraph(self, text: str) -> str:
        """Otimiza um parágrafo individual"""
        if not text:
            return ""
        
        # Dividir em linhas
        lines = text.split('\n')
        
        # Filtrar linhas vazias e limpar
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        if not cleaned_lines:
            return ""
        
        # Detectar se é um título ou cabeçalho
        if self._is_title(cleaned_lines[0]):
            return '\n'.join(cleaned_lines)
        
        # Detectar se é uma lista
        if self._is_list(cleaned_lines):
            return '\n'.join(cleaned_lines)
        
        # Para parágrafos normais, juntar linhas relacionadas
        return self._join_related_lines(cleaned_lines)
    
    def _is_title(self, line: str) -> bool:
        """Detecta se uma linha é um título"""
        # Padrões de títulos
        title_patterns = [
            r'^[A-Z][A-Z\s]+$',  # TUDO EM MAIÚSCULO
            r'^\d+\.\s+[A-Z]',   # 1. Título
            r'^[IVXLCDM]+\.\s+[A-Z]',  # I. Título (romanos)
            r'^[A-Z]\.[A-Z]\s+',  # A.B Título
            r'^[A-Z][^a-z]+$',   # Títulos em maiúsculo sem minúsculas
        ]
        
        for pattern in title_patterns:
            if re.match(pattern, line.strip()):
                return True
        
        # Verificar comprimento típico de títulos
        words = line.split()
        if len(words) <= 10 and len(line) <= 100:
            # Verificar se todas as palavras começam com maiúscula
            if all(word[0].isupper() for word in words if word):
                return True
        
        return False
    
    def _is_list(self, lines: List[str]) -> bool:
        """Detecta se as linhas formam uma lista"""
        list_indicators = 0
        total_lines = len(lines)
        
        for line in lines:
            # Verificar indicadores de lista
            if re.match(r'^\s*[-•*]\s', line):
                list_indicators += 1
            elif re.match(r'^\s*\d+\.\s', line):
                list_indicators += 1
            elif re.match(r'^\s*[a-z]\)\s', line):
                list_indicators += 1
        
        # Se mais de 50% das linhas são itens de lista
        return list_indicators > total_lines * 0.5
    
    def _join_related_lines(self, lines: List[str]) -> str:
        """Junta linhas relacionadas em um parágrafo"""
        if not lines:
            return ""
        
        if len(lines) == 1:
            return lines[0]
        
        joined_lines = []
        current_paragraph = []
        
        for i, line in enumerate(lines):
            # Verificar se esta linha deve ser juntada à anterior
            should_join = self._should_join_with_previous(line, lines, i)
            
            if should_join and current_paragraph:
                # Juntar com parágrafo atual
                current_paragraph.append(line)
            else:
                # Finalizar parágrafo atual e começar novo
                if current_paragraph:
                    joined_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                current_paragraph.append(line)
        
        # Adicionar último parágrafo
        if current_paragraph:
            joined_lines.append(' '.join(current_paragraph))
        
        return '\n'.join(joined_lines)
    
    def _should_join_with_previous(self, line: str, lines: List[str], index: int) -> bool:
        """Determina se uma linha deve ser juntada à linha anterior"""
        if index == 0:
            return False
        
        prev_line = lines[index - 1]
        
        # Não juntar se a linha atual termina com pontuação final
        if line.rstrip().endswith(('.', '!', '?', ':', ';', '"', "'")):
            return False
        
        # Não juntar se a linha anterior termina com pontuação final
        if prev_line.rstrip().endswith(('.', '!', '?', ':', ';', '"', "'")):
            return False
        
        # Não juntar se a linha atual começa com maiúscula (possível início de frase)
        if line.strip() and line.strip()[0].isupper():
            # Mas verificar se não é um número ou abreviação
            if not re.match(r'^\d+', line.strip()):
                # Verificar se a linha anterior termina com pontuação
                if prev_line.rstrip().endswith(('.', '!', '?')):
                    return False
        
        # Não juntar linhas muito curtas (possíveis títulos)
        if len(line.strip()) < 30 and len(line.strip()) > 0:
            # Verificar se parece ser um título
            if line.strip().isupper() or self._is_title(line):
                return False
        
        # Juntar se as linhas são relacionadas semanticamente
        return True
    
    def _create_final_content(self, blocks: List[str], font_info: List[Dict]) -> str:
        """Cria o conteúdo final otimizado"""
        if not blocks:
            return ""
        
        # Usar informações de fonte se disponível
        if font_info:
            return self._create_structured_content(blocks, font_info)
        else:
            # Fallback para método simples
            return '\n\n'.join(blocks)
    
    def _create_structured_content(self, blocks: List[str], font_info: List[Dict]) -> str:
        """Cria conteúdo estruturado usando informações de fonte"""
        # Agrupar por fonte/size para detectar títulos
        font_groups = {}
        
        for entry in font_info:
            text = entry.get('text', '').strip()
            font_name = entry.get('font', '')
            font_size = entry.get('size', 0)
            
            if text:
                font_key = f"{font_name}_{font_size}"
                if font_key not in font_groups:
                    font_groups[font_key] = []
                font_groups[font_key].append(text)
        
        # Encontrar a fonte mais comum para texto normal
        if font_groups:
            normal_font = max(font_groups.keys(), 
                            key=lambda k: len(font_groups[k]) if font_groups[k] else 0)
        
        # Processar blocos e aplicar estrutura
        structured_lines = []
        
        for block in blocks:
            # Verificar se o bloco contém texto de título baseado na fonte
            is_title = False
            
            for entry in font_info:
                if entry.get('text', '').strip() in block:
                    font_size = entry.get('size', 0)
                    if font_size > 12:  # Tamanho de fonte maior indica título
                        is_title = True
                        break
            
            if is_title:
                # Adicionar como título
                structured_lines.append(f"# {block}")
            else:
                # Adicionar como parágrafo normal
                structured_lines.append(block)
        
        return '\n\n'.join(structured_lines)
    
    def _detect_and_clean_corrupted_text(self, text: str) -> str:
        """Detecta e limpa texto corrompido"""
        # Padrões de texto corrompido
        corrupted_patterns = [
            r'[^\w\s\.\,\;\:\!\"\'\(\)\[\]\{\}\-\–\—]',  # Caracteres estranhos
            r'\s{3,}',  # Múltiplos espaços
            r'([a-z])\s*([A-Z])',  # Palavras juntas sem espaço
        ]
        
        cleaned_text = text
        
        for pattern in corrupted_patterns:
            if pattern == r'[^\w\s\.\,\;\:\!\"\'\(\)\[\]\{\}\-\–\—]':
                # Substituir caracteres estranhos por espaços
                cleaned_text = re.sub(pattern, ' ', cleaned_text)
            elif pattern == r'\s{3,}':
                # Normalizar múltiplos espaços
                cleaned_text = re.sub(pattern, ' ', cleaned_text)
            elif pattern == r'([a-z])\s*([A-Z])':
                # Adicionar espaço entre palavras juntas
                cleaned_text = re.sub(pattern, r'\1 \2', cleaned_text)
        
        return cleaned_text.strip()

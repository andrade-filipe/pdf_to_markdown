#!/usr/bin/env python3
"""Step de processamento robusto baseado em conceitos de compiladores"""

import re
import time
from typing import Dict, Any, List
from .base_step import BaseStep
from .robust_text_processor import RobustTextProcessor

class RobustProcessingStep(BaseStep):
    """Step de processamento robusto que ignora estruturas problemáticas"""
    
    def __init__(self):
        super().__init__("RobustProcessingStep")
        self.processor = RobustTextProcessor()
        
        # Configurações de processamento
        self.config = {
            'ignore_problematic_structures': True,
            'clean_whitespace': True,
            'normalize_paragraphs': True,
            'detect_titles': True,
            'max_line_length': 100,
            'min_paragraph_length': 10
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo com foco em fidelidade e estrutura"""
        self.log_info("Iniciando processamento robusto")
        
        if 'content' not in data:
            self.log_warning("Nenhum conteúdo encontrado para processar")
            return data
        
        content = data['content']
        if not content or not isinstance(content, str):
            self.log_warning("Conteúdo inválido para processamento")
            return data
        
        start_time = time.time()
        
        try:
            # Fase 1: Limpeza básica
            self.log_info("Fase 1: Limpeza básica")
            content = self._basic_cleanup(content)
            
            # Fase 2: Detecção e remoção de estruturas problemáticas
            if self.config['ignore_problematic_structures']:
                self.log_info("Fase 2: Removendo estruturas problemáticas")
                content = self._remove_problematic_structures(content)
            
            # Fase 3: Normalização de parágrafos
            if self.config['normalize_paragraphs']:
                self.log_info("Fase 3: Normalizando parágrafos")
                content = self._normalize_paragraphs(content)
            
            # Fase 4: Detecção de títulos
            if self.config['detect_titles']:
                self.log_info("Fase 4: Detectando títulos")
                content = self._detect_and_format_titles(content)
            
            # Fase 5: Limpeza final
            self.log_info("Fase 5: Limpeza final")
            content = self._final_cleanup(content)
            
            # Atualizar dados
            data['content'] = content
            data['robust_processing_stats'] = {
                'processing_time': time.time() - start_time,
                'original_length': len(data.get('content', '')),
                'final_length': len(content),
                'structures_removed': self._count_removed_structures(data.get('content', ''), content)
            }
            
            self.log_info(f"Processamento robusto concluído em {time.time() - start_time:.2f}s")
            
        except Exception as e:
            self.log_error(f"Erro no processamento robusto: {e}")
            # Em caso de erro, manter conteúdo original
            pass
        
        return data
    
    def _basic_cleanup(self, content: str) -> str:
        """Limpeza básica do texto"""
        # Normalizar quebras de linha
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        # Normalizar espaços
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remover caracteres de controle
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        return content
    
    def _remove_problematic_structures(self, content: str) -> str:
        """Remove estruturas problemáticas usando regex avançado"""
        # Padrões de estruturas problemáticas
        problematic_patterns = [
            # Acrônimos muito longos
            r'\b[A-Z]{5,}\b',
            # Sequências de símbolos
            r'[^\w\s]{4,}',
            # Números muito longos
            r'\b\d{8,}\b',
            # Linhas com muitas iniciais
            r'^[A-Z]\.[A-Z]\.[A-Z]\.[A-Z].*$',
            # Texto em caps lock
            r'^[A-Z\s]{20,}$',
            # Sequências de caracteres repetidos
            r'(.)\1{10,}',
        ]
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
            
            # Verificar se a linha é problemática
            is_problematic = False
            for pattern in problematic_patterns:
                if re.search(pattern, line):
                    is_problematic = True
                    break
            
            if not is_problematic:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _normalize_paragraphs(self, content: str) -> str:
        """Normaliza parágrafos para melhor legibilidade"""
        lines = content.split('\n')
        normalized_lines = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Finalizar parágrafo atual
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) >= self.config['min_paragraph_length']:
                        normalized_lines.append(paragraph_text)
                    current_paragraph = []
                normalized_lines.append('')
            else:
                # Adicionar linha ao parágrafo atual
                current_paragraph.append(line)
        
        # Finalizar último parágrafo
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            if len(paragraph_text) >= self.config['min_paragraph_length']:
                normalized_lines.append(paragraph_text)
        
        return '\n'.join(normalized_lines)
    
    def _detect_and_format_titles(self, content: str) -> str:
        """Detecta e formata títulos"""
        lines = content.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                formatted_lines.append('')
                continue
            
            # Padrões para detecção de títulos
            title_patterns = [
                r'^[A-Z][^.!?]{3,50}$',  # Frase sem pontuação final
                r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
                r'^[0-9]+\.\s*[A-Z]',  # Número seguido de título
                r'^[A-Z]+\s*$',  # Tudo em maiúsculas
            ]
            
            is_title = False
            for pattern in title_patterns:
                if re.match(pattern, line):
                    is_title = True
                    break
            
            if is_title:
                # Verificar contexto (não é título se é continuação de parágrafo)
                if i > 0 and lines[i-1].strip() and not lines[i-1].strip().endswith('.'):
                    formatted_lines.append(f'# {line}')
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _final_cleanup(self, content: str) -> str:
        """Limpeza final do texto"""
        # Remover linhas vazias múltiplas
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Remover espaços no início e fim
        content = content.strip()
        
        # Garantir que não há linhas muito longas
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if len(line) > self.config['max_line_length']:
                # Quebrar linha longa em pontos naturais
                words = line.split()
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 > self.config['max_line_length']:
                        if current_line:
                            cleaned_lines.append(' '.join(current_line))
                            current_line = [word]
                            current_length = len(word)
                        else:
                            cleaned_lines.append(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + 1
                
                if current_line:
                    cleaned_lines.append(' '.join(current_line))
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _count_removed_structures(self, original: str, processed: str) -> int:
        """Conta quantas estruturas foram removidas"""
        original_lines = [line.strip() for line in original.split('\n') if line.strip()]
        processed_lines = [line.strip() for line in processed.split('\n') if line.strip()]
        
        return len(original_lines) - len(processed_lines)

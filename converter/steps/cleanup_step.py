"""Passo de limpeza de texto"""

import re
from typing import Dict, Any, List
from .base_step import BaseStep


class CleanupStep(BaseStep):
    """Passo responsável por limpar texto removendo cabeçalhos e rodapés"""
    
    def __init__(self):
        super().__init__("Cleanup")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove cabeçalhos e rodapés do texto extraído"""
        text_blocks = data.get('text_blocks', [])
        cleaned_blocks = []
        
        for text in text_blocks:
            cleaned_text = self._clean_text(text)
            if cleaned_text.strip():  # Só adiciona se não estiver vazio
                cleaned_blocks.append(cleaned_text)
        
        # Atualizar blocos de texto limpos
        data['text_blocks'] = cleaned_blocks
        data['cleaned_text'] = '\n'.join(cleaned_blocks)
        
        return data
    
    def _clean_text(self, text: str) -> str:
        """Remove padrões típicos de cabeçalho/rodapé"""
        if not text:
            return ""
        
        # Remove linhas que contêm padrões típicos de cabeçalho/rodapé
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Padrões para remover
            patterns_to_remove = [
                r'página\s+\d+',  # "página 5"
                r'page\s+\d+',    # "page 5"
                r'^\s*[-_]{3,}\s*$',  # Linhas com apenas traços
                r'^\s*\d+\s*$',   # Linhas com apenas números
                r'^\s*[ivxlcdm]+\s*$',  # Números romanos
            ]
            
            should_remove = False
            for pattern in patterns_to_remove:
                if re.search(pattern, line.lower()):
                    should_remove = True
                    break
            
            if not should_remove:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

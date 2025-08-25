"""Etapa para detectar o tipo de documento"""
import re
from typing import Dict, Any
from .base_step import BaseStep


class DocumentTypeDetectionStep(BaseStep):
    """Detecta o tipo de documento para aplicar processamento específico"""
    
    def __init__(self):
        super().__init__("DocumentTypeDetection")
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta o tipo de documento baseado no conteúdo"""
        # Usar texto bruto se disponível, senão usar blocos de texto
        raw_text = context.get('raw_text', '')
        if not raw_text:
            text_blocks = context.get('text_blocks', [])
            raw_text = '\n'.join(text_blocks)
        
        # Padrões para identificar relatórios do Verity Quantum
        quantum_patterns = [
            r'Resultado Regra De Negócio',
            r'Diagrama Regra de Negócio',
            r'Sumário de Regras',
            r'_BR_\d+',  # Padrão de IDs de regras de negócio
            r'Detalhamento do Código',
            r'ID\s+Descrição\s+Arquivo\s+Impacto'
        ]
        
        # Padrões para identificar artigos científicos
        academic_patterns = [
            r'Abstract',
            r'Introduction',
            r'References',
            r'Bibliography',
            r'DOI:',
            r'ISSN:',
            r'Journal of',
            r'Proceedings of',
            r'Conference on',
            r'University of',
            r'Department of'
        ]
        
        # Contar matches
        quantum_matches = sum(1 for pattern in quantum_patterns if re.search(pattern, raw_text, re.IGNORECASE))
        academic_matches = sum(1 for pattern in academic_patterns if re.search(pattern, raw_text, re.IGNORECASE))
        
        # Determinar tipo de documento
        if quantum_matches > academic_matches and quantum_matches >= 2:
            document_type = 'quantum_report'
            self.log_info(f"Detectado: Relatório Verity Quantum ({quantum_matches} indicadores)")
        else:
            document_type = 'academic_article'
            self.log_info(f"Detectado: Artigo Científico ({academic_matches} indicadores)")
        
        context['document_type'] = document_type
        return context

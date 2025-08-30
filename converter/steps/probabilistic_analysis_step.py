"""Step de Análise Probabilística para Estruturação de Conteúdo"""

import time
from typing import Dict, Any
from .base_step import BaseStep
from .probabilistic_analyzer import ProbabilisticAnalyzer


class ProbabilisticAnalysisStep(BaseStep):
    """Step que usa análise probabilística para estruturar conteúdo extraído"""
    
    def __init__(self):
        super().__init__("ProbabilisticAnalysis")
        self.analyzer = ProbabilisticAnalyzer()
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo usando análise probabilística"""
        self.log_info("Iniciando análise probabilística do conteúdo")
        
        if 'content' not in data:
            self.log_warning("Nenhum conteúdo encontrado para análise")
            return data
        
        content = data['content']
        if not content or not isinstance(content, str):
            self.log_warning("Conteúdo inválido para análise")
            return data
        
        start_time = time.time()
        
        try:
            # Análise probabilística
            analysis_result = self.analyzer.analyze_content(content)
            
            # Adicionar resultados à análise
            data['probabilistic_analysis'] = analysis_result
            
            # Atualizar conteúdo com estrutura melhorada
            if 'content' in analysis_result:
                data['structured_content'] = analysis_result['content']
            
            # Log das estatísticas
            metadata = analysis_result.get('metadata', {})
            self.log_info(f"Análise concluída:")
            self.log_info(f"  - Títulos: {metadata.get('total_titles', 0)}")
            self.log_info(f"  - Parágrafos: {metadata.get('total_paragraphs', 0)}")
            self.log_info(f"  - Tabelas: {metadata.get('total_tables', 0)}")
            self.log_info(f"  - Elementos de artigo: {metadata.get('total_article_elements', 0)}")
            self.log_info(f"  - Referências: {metadata.get('total_references', 0)}")
            
            processing_time = time.time() - start_time
            self.log_info(f"Análise probabilística concluída em {processing_time:.2f}s")
            
        except Exception as e:
            self.log_error(f"Erro na análise probabilística: {e}")
        
        return data

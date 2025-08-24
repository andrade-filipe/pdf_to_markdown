"""Passo de extração de tabelas do PDF"""

import pdfplumber
from typing import Dict, Any, List
from .base_step import BaseStep


class TableExtractionStep(BaseStep):
    """Passo responsável por extrair tabelas do PDF"""
    
    def __init__(self):
        super().__init__("TableExtraction")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai tabelas do PDF usando pdfplumber"""
        pdf_path = data.get('pdf_path')
        if not pdf_path:
            raise ValueError("pdf_path é obrigatório")
        
        extracted_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                
                for table_num, table in enumerate(tables):
                    if table:  # Verifica se a tabela não está vazia
                        table_info = {
                            'pagina': page_num + 1,
                            'numero': table_num + 1,
                            'dados': table,
                            'posicao': page.page_number
                        }
                        extracted_tables.append(table_info)
        
        # Adicionar tabelas extraídas ao contexto
        data['tables'] = extracted_tables
        return data

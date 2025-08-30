"""Passo de extração de tabelas do PDF"""

import pdfplumber
import re
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
                # Tentar diferentes métodos de extração
                tables = self._extract_tables_from_page(page, page_num)
                
                for table_info in tables:
                    if self._is_valid_table(table_info['dados']):
                        extracted_tables.append(table_info)
        
        self.log_info(f"Extraídas {len(extracted_tables)} tabelas válidas")
        
        # Adicionar tabelas extraídas ao contexto
        data['tables'] = extracted_tables
        return data
    
    def _extract_tables_from_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Extrai tabelas de uma página usando múltiplos métodos"""
        tables = []
        
        # Método 1: Extração padrão
        try:
            standard_tables = page.extract_tables()
            for table_num, table in enumerate(standard_tables):
                if table:
                    table_info = {
                        'pagina': page_num + 1,
                        'numero': table_num + 1,
                        'dados': table,
                        'metodo': 'padrao',
                        'posicao': page.page_number
                    }
                    tables.append(table_info)
        except Exception as e:
            self.log_warning(f"Erro na extração padrão da página {page_num + 1}: {e}")
        
        # Método 2: Extração com configurações específicas
        try:
            # Configurações para tabelas complexas
            custom_tables = page.extract_tables({
                'vertical_strategy': 'text',
                'horizontal_strategy': 'text',
                'intersection_x_tolerance': 10,
                'intersection_y_tolerance': 10
            })
            
            for table_num, table in enumerate(custom_tables):
                if table and not self._is_duplicate_table(table, tables):
                    table_info = {
                        'pagina': page_num + 1,
                        'numero': len(tables) + 1,
                        'dados': table,
                        'metodo': 'custom',
                        'posicao': page.page_number
                    }
                    tables.append(table_info)
        except Exception as e:
            self.log_warning(f"Erro na extração customizada da página {page_num + 1}: {e}")
        
        return tables
    
    def _is_valid_table(self, table_data: List[List[str]]) -> bool:
        """Verifica se uma tabela é válida e contém dados úteis"""
        if not table_data:
            return False
        
        # Verificar se há pelo menos 2 linhas e 2 colunas
        if len(table_data) < 2:
            return False
        
        # Verificar se há pelo menos 2 colunas
        max_cols = max(len(row) for row in table_data if row)
        if max_cols < 2:
            return False
        
        # Verificar se há conteúdo significativo
        total_cells = 0
        non_empty_cells = 0
        
        for row in table_data:
            for cell in row:
                total_cells += 1
                if cell and str(cell).strip():
                    non_empty_cells += 1
        
        # Pelo menos 30% das células devem ter conteúdo
        if total_cells == 0:
            return False
        
        content_ratio = non_empty_cells / total_cells
        if content_ratio < 0.3:
            return False
        
        # Verificar se não é apenas uma lista de números ou símbolos
        meaningful_content = 0
        for row in table_data:
            for cell in row:
                if cell and str(cell).strip():
                    cell_text = str(cell).strip()
                    # Verificar se contém texto significativo (não apenas números/símbolos)
                    if re.search(r'[a-zA-Z]', cell_text) or len(cell_text) > 3:
                        meaningful_content += 1
        
        # Pelo menos 20% das células devem ter conteúdo significativo
        if total_cells > 0:
            meaningful_ratio = meaningful_content / total_cells
            if meaningful_ratio < 0.2:
                return False
        
        return True
    
    def _is_duplicate_table(self, new_table: List[List[str]], existing_tables: List[Dict[str, Any]]) -> bool:
        """Verifica se uma tabela é duplicada"""
        for existing_table_info in existing_tables:
            existing_table = existing_table_info['dados']
            
            # Comparar tamanho
            if len(new_table) != len(existing_table):
                continue
            
            # Comparar conteúdo
            is_duplicate = True
            for i, row in enumerate(new_table):
                if i >= len(existing_table):
                    is_duplicate = False
                    break
                
                if len(row) != len(existing_table[i]):
                    is_duplicate = False
                    break
                
                for j, cell in enumerate(row):
                    if j >= len(existing_table[i]):
                        is_duplicate = False
                        break
                    
                    if str(cell).strip() != str(existing_table[i][j]).strip():
                        is_duplicate = False
                        break
            
            if is_duplicate:
                return True
        
        return False

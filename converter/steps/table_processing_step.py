"""Passo de processamento de tabelas extraídas"""

import re
from typing import Dict, Any, List
from .base_step import BaseStep


class TableProcessingStep(BaseStep):
    """Passo responsável por processar tabelas extraídas e inserir no local correto"""
    
    def __init__(self):
        super().__init__("TableProcessing")
    
    def process(self, data: Any) -> Any:
        """Processa tabelas extraídas e as insere no local correto do documento"""
        if isinstance(data, dict):
            content = data.get('markdown_content', '')
            tables = data.get('tables', [])
            metadata = data
        else:
            content = str(data)
            tables = []
            metadata = {}
        
        if not tables:
            return data
        
        self.log_info(f"Processando {len(tables)} tabelas extraídas")
        
        # Processar cada tabela
        processed_tables = []
        for table in tables:
            table_markdown = self._convert_table_to_markdown(table)
            if table_markdown:
                processed_tables.append({
                    'numero': table.get('numero', 1),
                    'pagina': table.get('pagina', 1),
                    'markdown': table_markdown,
                    'posicao': self._find_table_position(content, table)
                })
        
        # Inserir tabelas no local correto
        if processed_tables:
            content = self._insert_tables_in_content(content, processed_tables)
        
        if isinstance(data, dict):
            data['markdown_content'] = content
            return data
        else:
            return content
    
    def _convert_table_to_markdown(self, table: Dict[str, Any]) -> str:
        """Converte tabela extraída para Markdown formatado"""
        dados = table.get('dados', [])
        if not dados:
            return ""
        
        # Limpar e validar dados da tabela
        cleaned_data = self._clean_and_validate_table_data(dados)
        
        if not cleaned_data:
            return ""
        
        # Normalizar estrutura da tabela
        normalized_data = self._normalize_table_structure(cleaned_data)
        
        if not normalized_data:
            return ""
        
        # Gerar Markdown da tabela
        return self._generate_markdown_table(normalized_data)
    
    def _clean_and_validate_table_data(self, data: List[List[str]]) -> List[List[str]]:
        """Limpa e valida dados da tabela com foco na qualidade do texto"""
        if not data:
            return []
        
        cleaned_data = []
        
        for row in data:
            if not row:
                continue
            
            # Limpar cada célula
            cleaned_row = []
            for cell in row:
                cleaned_cell = self._clean_table_cell_text_quality(cell)
                if cleaned_cell:  # Só adicionar células não vazias
                    cleaned_row.append(cleaned_cell)
            
            # Só adicionar linhas que tenham conteúdo
            if cleaned_row and any(cell.strip() for cell in cleaned_row):
                cleaned_data.append(cleaned_row)
        
        return cleaned_data
    
    def _clean_table_cell_text_quality(self, cell: str) -> str:
        """Limpa célula da tabela focando na qualidade do texto"""
        if not cell:
            return ""
        
        # Remover quebras de linha e espaços extras
        cleaned = cell.replace('\n', ' ').replace('\r', ' ')
        
        # Normalizar espaços
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remover espaços no início e fim
        cleaned = cleaned.strip()
        
        # Se a célula ficou vazia após limpeza, retornar vazio
        if not cleaned:
            return ""
        
        # Se a célula tem apenas caracteres especiais ou números, manter
        if re.match(r'^[\d\s\-\.\,\+\-\*\/\(\)\[\]\{\}\=\<\>\|\&\^\%\#\@\!\?]+$', cleaned):
            return cleaned
        
        # Se a célula parece ser texto normal, melhorar a legibilidade
        if len(cleaned) > 3:
            # Corrigir palavras quebradas
            cleaned = self._fix_broken_words_in_cell(cleaned)
            
            # Adicionar espaços onde necessário
            cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)
        
        return cleaned
    
    def _fix_broken_words_in_cell(self, text: str) -> str:
        """Corrige palavras quebradas em células de tabela"""
        # Padrões comuns de palavras quebradas
        patterns = [
            (r'([a-z])([A-Z][a-z]+)', r'\1 \2'),  # camelCase
            (r'([a-z])(\d+)', r'\1 \2'),  # palavra123
            (r'(\d+)([A-Z][a-z]+)', r'\1 \2'),  # 123palavra
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _normalize_table_structure(self, data: List[List[str]]) -> List[List[str]]:
        """Normaliza estrutura da tabela para garantir consistência"""
        if not data:
            return []
        
        # Encontrar número máximo de colunas
        max_cols = max(len(row) for row in data) if data else 0
        
        # Normalizar todas as linhas para ter o mesmo número de colunas
        normalized_data = []
        for row in data:
            normalized_row = row[:max_cols]  # Truncar se necessário
            # Adicionar células vazias se necessário
            while len(normalized_row) < max_cols:
                normalized_row.append("")
            normalized_data.append(normalized_row)
        
        return normalized_data
    
    def _generate_markdown_table(self, data: List[List[str]]) -> str:
        """Gera tabela Markdown formatada com foco em legibilidade"""
        if not data:
            return ""
        
        # Calcular larguras das colunas
        col_widths = []
        for col_idx in range(len(data[0])):
            max_width = max(len(str(row[col_idx])) for row in data)
            col_widths.append(max_width)
        
        # Gerar cabeçalho
        markdown_table = "|"
        for i, cell in enumerate(data[0]):
            markdown_table += f" {cell:<{col_widths[i]}} |"
        markdown_table += "\n"
        
        # Gerar separador
        markdown_table += "|"
        for width in col_widths:
            markdown_table += f" {'-' * width} |"
        markdown_table += "\n"
        
        # Gerar linhas de dados
        for row in data[1:]:
            markdown_table += "|"
            for i, cell in enumerate(row):
                markdown_table += f" {cell:<{col_widths[i]}} |"
            markdown_table += "\n"
        
        return markdown_table.rstrip()
    
    def _calculate_column_widths(self, data: List[List[str]]) -> List[int]:
        """Calcula larguras ótimas para as colunas da tabela"""
        if not data:
            return []
        
        max_cols = max(len(row) for row in data)
        col_widths = []
        
        for col in range(max_cols):
            max_width = 10  # Largura mínima
            for row in data:
                if col < len(row):
                    cell_width = len(row[col].strip())
                    max_width = max(max_width, cell_width)
            
            # Limitar largura máxima para evitar tabelas muito largas
            max_width = min(max_width, 50)
            col_widths.append(max_width)
        
        return col_widths
    
    def _format_cell_for_markdown(self, cell: str, width: int) -> str:
        """Formata uma célula para Markdown com largura específica"""
        if not cell:
            return " " * width
        
        # Limpar a célula
        clean_cell = cell.strip()
        
        # Truncar se for muito longa
        if len(clean_cell) > width:
            clean_cell = clean_cell[:width-3] + "..."
        
        # Preencher com espaços se for muito curta
        clean_cell = clean_cell.ljust(width)
        
        return clean_cell
    
    def _find_table_position(self, content: str, table: Dict[str, Any]) -> int:
        """Encontra a posição ideal para inserir a tabela no conteúdo"""
        # Procurar por referências à tabela no texto
        table_num = table.get('numero', 1)
        page_num = table.get('pagina', 1)
        
        # Padrões para encontrar referências à tabela
        patterns = [
            rf"Table\s+{table_num}",
            rf"Tabela\s+{table_num}",
            rf"Table\s+{table_num}\.",
            rf"Tabela\s+{table_num}\.",
            rf"Table\s+{table_num}\s*\(",
            rf"Tabela\s+{table_num}\s*\(",
        ]
        
        content_lower = content.lower()
        for pattern in patterns:
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                return match.end()
        
        # Se não encontrar referência específica, procurar por contexto
        # Procurar por palavras-chave que indicam tabelas
        table_keywords = [
            "table", "tabela", "shows", "mostra", "presents", "apresenta",
            "data", "dados", "results", "resultados", "figure", "figura"
        ]
        
        for keyword in table_keywords:
            match = re.search(rf"\b{keyword}\b", content_lower)
            if match:
                return match.end()
        
        # Se não encontrar nada, inserir no final
        return len(content)
    
    def _insert_tables_in_content(self, content: str, processed_tables: List[Dict[str, Any]]) -> str:
        """Insere tabelas processadas no conteúdo na posição correta"""
        # Ordenar tabelas por posição
        processed_tables.sort(key=lambda x: x['posicao'])
        
        # Inserir tabelas de trás para frente para não alterar as posições
        for table in reversed(processed_tables):
            pos = table['posicao']
            table_markdown = table['markdown']
            table_num = table['numero']
            page_num = table['pagina']
            
            # Criar cabeçalho da tabela
            table_header = f"\n\n**Tabela {table_num}** (Página {page_num})\n\n"
            table_content = table_header + table_markdown + "\n\n"
            
            # Inserir no conteúdo
            content = content[:pos] + table_content + content[pos:]
        
        return content

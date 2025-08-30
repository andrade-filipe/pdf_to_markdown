"""Passo de detecção e formatação de citações e bibliografia"""

import re
from typing import Dict, Any, List, Tuple
from .base_step import BaseStep


class CitationStep(BaseStep):
    """Passo responsável por detectar e formatar citações e bibliografia"""
    
    def __init__(self):
        super().__init__("Citation")
        self.language = 'en'
        self.content_type = 'auto'
        self.citations = []
        self.bibliography = []
        
    def set_language(self, language: str):
        """Define o idioma para detecção específica"""
        self.language = language
        
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo para detecção específica"""
        self.content_type = content_type
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta e formata citações e bibliografia"""
        self.log_info("Iniciando detecção de citações e bibliografia")
        
        # Obter texto processado
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            self.log_info("Nenhum conteúdo Markdown encontrado")
            return data
        
        # Detectar e formatar citações
        processed_content = self._detect_and_format_citations(markdown_content)
        
        # Detectar bibliografia
        bibliography_section = self._extract_bibliography(processed_content)
        
        # Adicionar seção de bibliografia se encontrada
        if bibliography_section:
            processed_content += '\n\n' + bibliography_section
        
        # Atualizar dados
        data['markdown_content'] = processed_content
        data['citations_detected'] = len(self.citations)
        data['bibliography_entries'] = len(self.bibliography)
        data['citations_content'] = self.citations
        data['bibliography_content'] = self.bibliography
        
        self.log_info(f"Detecção concluída. {len(self.citations)} citações e {len(self.bibliography)} entradas de bibliografia encontradas")
        return data
    
    def _detect_and_format_citations(self, content: str) -> str:
        """Detecta e formata citações no conteúdo"""
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Processar citações na linha
            processed_line = self._process_citations_in_line(line)
            processed_lines.append(processed_line)
        
        return '\n'.join(processed_lines)
    
    def _process_citations_in_line(self, line: str) -> str:
        """Processa citações em uma linha individual"""
        # Padrões de citações
        citation_patterns = [
            # (Author, Year)
            r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?,\s+\d{4})\)',
            # [Author, Year]
            r'\[([A-Z][a-z]+(?:\s+et\s+al\.)?,\s+\d{4})\]',
            # Author (Year)
            r'([A-Z][a-z]+(?:\s+et\s+al\.)?)\s+\((\d{4})\)',
            # Author et al. (Year)
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+et\s+al\.)\s+\((\d{4})\)',
            # [1], [2], etc. (referências numéricas)
            r'\[(\d+)\]',
            # (1), (2), etc.
            r'\((\d+)\)',
        ]
        
        processed_line = line
        
        for pattern in citation_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                citation_text = match.group(0)
                citation_content = match.group(1)
                
                # Criar objeto de citação
                citation = {
                    'original': citation_text,
                    'content': citation_content,
                    'type': self._detect_citation_type(citation_text),
                    'position': match.start()
                }
                
                self.citations.append(citation)
                
                # Formatar para Markdown
                markdown_citation = self._format_citation_for_markdown(citation)
                
                # Substituir na linha
                processed_line = processed_line[:match.start()] + markdown_citation + processed_line[match.end():]
        
        return processed_line
    
    def _detect_citation_type(self, citation: str) -> str:
        """Detecta o tipo de citação"""
        if re.match(r'\([A-Z][a-z]+.*\d{4}\)', citation):
            return 'author_year'
        elif re.match(r'\[[A-Z][a-z]+.*\d{4}\]', citation):
            return 'author_year_brackets'
        elif re.match(r'[A-Z][a-z]+.*\d{4}', citation):
            return 'author_year_no_brackets'
        elif re.match(r'\[\d+\]', citation):
            return 'numeric'
        elif re.match(r'\(\d+\)', citation):
            return 'numeric_parentheses'
        else:
            return 'unknown'
    
    def _format_citation_for_markdown(self, citation: Dict[str, Any]) -> str:
        """Formata citação para Markdown"""
        citation_type = citation['type']
        content = citation['content']
        
        if citation_type == 'author_year':
            # (Author, Year) -> [Author, Year](#author-year)
            anchor = self._create_anchor(content)
            return f'[{content}](#{anchor})'
        elif citation_type == 'author_year_brackets':
            # [Author, Year] -> [Author, Year](#author-year)
            anchor = self._create_anchor(content)
            return f'[{content}](#{anchor})'
        elif citation_type == 'author_year_no_brackets':
            # Author (Year) -> [Author (Year)](#author-year)
            anchor = self._create_anchor(content)
            return f'[{content}](#{anchor})'
        elif citation_type == 'numeric':
            # [1] -> [^1]
            return f'[^{content}]'
        elif citation_type == 'numeric_parentheses':
            # (1) -> [^1]
            return f'[^{content}]'
        else:
            # Manter original
            return citation['original']
    
    def _create_anchor(self, text: str) -> str:
        """Cria âncora para link interno"""
        # Converter para minúsculas
        anchor = text.lower()
        
        # Remover caracteres especiais
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        
        # Substituir espaços por hífens
        anchor = re.sub(r'\s+', '-', anchor)
        
        # Remover hífens múltiplos
        anchor = re.sub(r'-+', '-', anchor)
        
        # Remover hífens no início e fim
        anchor = anchor.strip('-')
        
        return anchor
    
    def _extract_bibliography(self, content: str) -> str:
        """Extrai e formata seção de bibliografia"""
        lines = content.split('\n')
        bibliography_lines = []
        in_bibliography = False
        
        # Padrões para identificar início da bibliografia
        bibliography_start_patterns = [
            r'^References$',
            r'^Bibliography$',
            r'^Bibliografia$',
            r'^Referências$',
            r'^Works Cited$',
            r'^Literature Cited$',
            r'^Sources$',
            r'^Fontes$',
        ]
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Verificar se é início da bibliografia
            if not in_bibliography:
                for pattern in bibliography_start_patterns:
                    if re.match(pattern, line_stripped, re.IGNORECASE):
                        in_bibliography = True
                        bibliography_lines.append("## References")
                        bibliography_lines.append("")
                        break
            
            elif in_bibliography:
                # Verificar se chegou ao fim da bibliografia
                if self._is_end_of_bibliography(line_stripped, i, lines):
                    break
                
                # Processar entrada da bibliografia
                if line_stripped and not line_stripped.startswith('#'):
                    formatted_entry = self._format_bibliography_entry(line_stripped)
                    if formatted_entry:
                        bibliography_lines.append(formatted_entry)
                        self.bibliography.append({
                            'original': line_stripped,
                            'formatted': formatted_entry
                        })
        
        return '\n'.join(bibliography_lines)
    
    def _is_end_of_bibliography(self, line: str, line_index: int, all_lines: List[str]) -> bool:
        """Verifica se chegou ao fim da bibliografia"""
        if not line:
            return False
        
        # Verificar se é um título de seção
        if line.startswith('#'):
            return True
        
        # Verificar se é um título importante (não parece entrada de bibliografia)
        if len(line) > 100:  # Entradas de bibliografia geralmente são longas
            return False
        
        # Verificar se parece uma entrada de bibliografia
        bibliography_patterns = [
            r'^[A-Z][a-z]+,\s+[A-Z]\.',  # Author, A.
            r'^[A-Z][a-z]+,\s+[A-Z][a-z]+',  # Author, Author
            r'^[A-Z][a-z]+\s+et\s+al\.',  # Author et al.
            r'^\d+\.\s+',  # 1. Entry
            r'^\[[A-Z][a-z]+.*\d{4}\]',  # [Author et al., 2024]
        ]
        
        for pattern in bibliography_patterns:
            if re.match(pattern, line):
                return False
        
        return True
    
    def _format_bibliography_entry(self, entry: str) -> str:
        """Formata uma entrada de bibliografia"""
        # Remover numeração se existir
        entry = re.sub(r'^\d+\.\s*', '', entry)
        
        # Verificar se é uma entrada válida
        if len(entry) < 10:  # Muito curta para ser uma entrada válida
            return ""
        
        # Padrões de formatação
        if re.match(r'^[A-Z][a-z]+,\s+[A-Z]\.', entry):
            # Formato: Author, A. (Year). Title. Journal, Volume(Issue), Pages.
            return self._format_author_year_entry(entry)
        elif re.match(r'^[A-Z][a-z]+\s+et\s+al\.', entry):
            # Formato: Author et al. (Year). Title. Journal, Volume(Issue), Pages.
            return self._format_author_year_entry(entry)
        elif re.match(r'^\d+\.\s+', entry):
            # Formato numerado
            return self._format_numbered_entry(entry)
        else:
            # Formato genérico
            return f"- {entry}"
    
    def _format_author_year_entry(self, entry: str) -> str:
        """Formata entrada no formato autor-ano"""
        # Extrair autor e ano
        author_match = re.match(r'^([^,]+)', entry)
        year_match = re.search(r'\((\d{4})\)', entry)
        
        if author_match and year_match:
            author = author_match.group(1).strip()
            year = year_match.group(1)
            
            # Criar âncora
            anchor = self._create_anchor(f"{author} {year}")
            
            return f"- **{author}** ({year}). {entry}. [](#{anchor})"
        else:
            return f"- {entry}"
    
    def _format_numbered_entry(self, entry: str) -> str:
        """Formata entrada numerada"""
        # Remover numeração
        entry = re.sub(r'^\d+\.\s*', '', entry)
        
        # Extrair autor se possível
        author_match = re.match(r'^([^,]+)', entry)
        if author_match:
            author = author_match.group(1).strip()
            return f"- **{author}**. {entry}"
        else:
            return f"- {entry}"
    
    def _detect_doi_links(self, content: str) -> str:
        """Detecta e formata links DOI"""
        # Padrão para DOIs
        doi_pattern = r'DOI:\s*(10\.\d+/[^\s]+)'
        
        def replace_doi(match):
            doi = match.group(1)
            return f'DOI: [{doi}](https://doi.org/{doi})'
        
        return re.sub(doi_pattern, replace_doi, content)
    
    def _detect_urls(self, content: str) -> str:
        """Detecta e formata URLs"""
        # Padrão para URLs
        url_pattern = r'https?://[^\s]+'
        
        def replace_url(match):
            url = match.group(0)
            return f'[{url}]({url})'
        
        return re.sub(url_pattern, replace_url, content)
    
    def _count_citations(self, content: str) -> int:
        """Conta o número de citações no conteúdo"""
        citation_patterns = [
            r'\([A-Z][a-z]+.*\d{4}\)',  # (Author, Year)
            r'\[[A-Z][a-z]+.*\d{4}\]',  # [Author, Year]
            r'[A-Z][a-z]+.*\(\d{4}\)',  # Author (Year)
            r'\[\d+\]',  # [1], [2], etc.
            r'\(\d+\)',  # (1), (2), etc.
        ]
        
        count = 0
        for pattern in citation_patterns:
            count += len(re.findall(pattern, content))
        
        return count
    
    def _count_bibliography_entries(self, content: str) -> int:
        """Conta o número de entradas de bibliografia"""
        # Padrões para entradas de bibliografia
        entry_patterns = [
            r'^[A-Z][a-z]+,\s+[A-Z]\.',  # Author, A.
            r'^[A-Z][a-z]+,\s+[A-Z][a-z]+',  # Author, Author
            r'^[A-Z][a-z]+\s+et\s+al\.',  # Author et al.
            r'^\d+\.\s+',  # 1. Entry
        ]
        
        lines = content.split('\n')
        count = 0
        
        for line in lines:
            line_stripped = line.strip()
            for pattern in entry_patterns:
                if re.match(pattern, line_stripped):
                    count += 1
                    break
        
        return count

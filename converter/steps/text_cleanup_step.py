import re
import unicodedata
from typing import Dict, Any, List
from .base_step import BaseStep


class TextCleanupStep(BaseStep):
    """
    Step para limpeza e correção de texto usando algoritmos genéricos e inteligentes.
    Foca em soluções escaláveis em vez de correções hard-coded específicas.
    """
    
    def __init__(self):
        super().__init__("TextCleanupStep")
        
    def process(self, data: Any) -> Any:
        """Processa o conteúdo com limpeza básica apenas para estabilidade"""
        self.log_info("Iniciando limpeza básica de texto para estabilidade")
        
        if isinstance(data, dict):
            content = data.get('content', '')
            metadata = data.get('metadata', {})
        else:
            content = str(data)
            metadata = {}
        
        if not content:
            return data
            
        # Apenas limpeza básica para estabilidade
        content = self._normalize_unicode(content)
        content = self._normalize_whitespace_basic(content)
        
        self.log_info("Limpeza básica de texto concluída")
        
        if isinstance(data, dict):
            data['content'] = content
            return data
        else:
            return content
    
    def _normalize_unicode(self, content: str) -> str:
        """Normalização Unicode genérica para resolver problemas de codificação"""
        # Normalizar caracteres Unicode
        content = unicodedata.normalize('NFKC', content)
        
        # Corrigir caracteres comuns corrompidos
        unicode_fixes = {
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Horizontal ellipsis
            '\u00a0': ' ',  # Non-breaking space
            '\u00ad': '',   # Soft hyphen
        }
        
        for wrong, correct in unicode_fixes.items():
            content = content.replace(wrong, correct)
        
        return content
    
    def _normalize_whitespace_basic(self, content: str) -> str:
        """Normalização básica de espaços em branco"""
        # Normalizar quebras de linha
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        # Normalizar espaços múltiplos
        content = re.sub(r' +', ' ', content)
        
        # Normalizar quebras de linha múltiplas
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Remover espaços no início e fim
        content = content.strip()
        
        return content
    
    def _fix_line_breaks_intelligent(self, content: str) -> str:
        """Algoritmo inteligente para corrigir quebras de linha inadequadas com foco exclusivo na qualidade do texto"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            current_line = lines[i].strip()
            
            # Se a linha atual não está vazia
            if current_line:
                # Verificar se a próxima linha deve ser juntada
                if (i + 1 < len(lines) and 
                    self._should_join_with_next_line_text_quality(current_line, lines[i + 1].strip())):
                    
                    # Juntar linhas até encontrar uma quebra natural
                    joined_line = current_line
                    i += 1
                    
                    while (i < len(lines) and 
                           self._should_join_with_next_line_text_quality(joined_line, lines[i].strip())):
                        next_line = lines[i].strip()
                        if next_line:
                            # Adicionar espaço se necessário
                            if not joined_line.endswith(' ') and not next_line.startswith(' '):
                                joined_line += ' '
                            joined_line += next_line
                        i += 1
                    
                    fixed_lines.append(joined_line)
                else:
                    fixed_lines.append(current_line)
                    i += 1
            else:
                fixed_lines.append('')
                i += 1
        
        return '\n'.join(fixed_lines)
    
    def _should_join_with_next_line_text_quality(self, current_line: str, next_line: str) -> bool:
        """Determina se deve juntar linhas focando exclusivamente na qualidade do texto"""
        if not current_line or not next_line:
            return False
        
        # === REGRAS PARA QUALIDADE DO TEXTO ===
        
        # 1. Se a linha atual termina com pontuação de fim de frase, NÃO juntar
        if self._is_sentence_end(current_line):
            return False
        
        # 2. Se a próxima linha começa com maiúscula e a atual termina com pontuação, NÃO juntar
        if (next_line and next_line[0].isupper() and 
            current_line and current_line[-1] in '.!?'):
            return False
        
        # 3. Se a próxima linha é um título ou estrutura especial, NÃO juntar
        if self._is_title_or_structure(next_line):
            return False
        
        # 4. Se a linha atual termina com hífen, SEMPRE juntar (palavra quebrada)
        if current_line.endswith('-'):
            return True
        
        # 5. Se a próxima linha começa com minúscula, provavelmente deve juntar
        if next_line and next_line[0].islower():
            return True
        
        # 6. Se a linha atual é muito curta (menos de 40 caracteres), provavelmente deve juntar
        if len(current_line) < 40:
            return True
        
        # 7. Se a próxima linha é muito curta (menos de 30 caracteres), provavelmente deve juntar
        if len(next_line) < 30:
            return True
        
        # 8. Se ambas as linhas são curtas, juntar
        if len(current_line) < 60 and len(next_line) < 60:
            return True
        
        return False
    
    def _is_title_start(self, line: str) -> bool:
        """Verifica se a linha parece ser o início de um título"""
        if not line:
            return False
        
        # Padrões de títulos
        title_patterns = [
            r'^#+\s+',  # Markdown headers
            r'^\d+\.\s+[A-Z]',  # 1. Título
            r'^[A-Z][A-Z\s]{2,}$',  # TUDO MAIÚSCULO
            r'^[A-Z][a-z]+\s+[A-Z]',  # Primeira Palavra Segunda
        ]
        
        for pattern in title_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_list_item_start(self, line: str) -> bool:
        """Verifica se a linha parece ser o início de um item de lista"""
        if not line:
            return False
        
        list_patterns = [
            r'^[-*•]\s+',  # -, *, •
            r'^\d+\.\s+',  # 1., 2., etc.
            r'^[a-z]\.\s+',  # a., b., etc
            r'^\s*[-*•]\s+',  # Com indentação
        ]
        
        for pattern in list_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_table_row_start(self, line: str) -> bool:
        """Verifica se a linha parece ser o início de uma linha de tabela"""
        if not line:
            return False
        
        # Verificar se contém múltiplos | ou - (formato de tabela)
        if '|' in line or '-' in line:
            return True
        
        return False
    
    def _is_code_block_start(self, line: str) -> bool:
        """Verifica se a linha parece ser o início de um bloco de código"""
        if not line:
            return False
        
        code_patterns = [
            r'^```',  # ```code
            r'^`[^`]+`',  # `code`
            r'^\s*def\s+',  # def function
            r'^\s*class\s+',  # class Class
            r'^\s*import\s+',  # import module
            r'^\s*from\s+',  # from module
        ]
        
        for pattern in code_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_section_header(self, line: str) -> bool:
        """Verifica se a linha parece ser um cabeçalho de seção"""
        if not line:
            return False
        
        # Palavras-chave comuns em cabeçalhos
        header_keywords = [
            'abstract', 'introduction', 'conclusion', 'references', 'bibliography',
            'method', 'methods', 'results', 'discussion', 'appendix',
            'figure', 'table', 'algorithm', 'theorem', 'lemma', 'proof'
        ]
        
        line_lower = line.lower().strip()
        for keyword in header_keywords:
            if line_lower.startswith(keyword):
                return True
        
        return False
    
    def _starts_with_capital(self, line: str) -> bool:
        """Verifica se a linha começa com letra maiúscula"""
        if not line:
            return False
        return line[0].isupper()
    
    def _starts_with_lowercase(self, line: str) -> bool:
        """Verifica se a linha começa com letra minúscula"""
        if not line:
            return False
        return line[0].islower()
    
    def _is_special_structure(self, line: str) -> bool:
        """Verifica se a linha é uma estrutura especial que não deve ser juntada"""
        return (self._is_list_item_start(line) or 
                self._is_table_row_start(line) or 
                self._is_code_block_start(line) or
                self._is_section_header(line))
    
    def _fix_fragmented_paragraphs_generic(self, content: str) -> str:
        """Corrige parágrafos fragmentados com foco em legibilidade"""
        paragraphs = content.split('\n\n')
        fixed_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                fixed_paragraphs.append('')
                continue
            
            # Processar o parágrafo linha por linha
            lines = paragraph.split('\n')
            joined_lines = []
            current_line = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_line:
                        joined_lines.append(current_line)
                        current_line = ""
                    continue
                
                # Se a linha atual está vazia, começar nova linha
                if not current_line:
                    current_line = line
                else:
                    # Verificar se deve juntar com a linha atual
                    if self._should_join_lines_in_paragraph(current_line, line):
                        # Juntar com espaço se necessário
                        if not current_line.endswith(' ') and not line.startswith(' '):
                            current_line += ' '
                        current_line += line
                    else:
                        # Finalizar linha atual e começar nova
                        joined_lines.append(current_line)
                        current_line = line
            
            # Adicionar última linha se houver
            if current_line:
                joined_lines.append(current_line)
            
            # Juntar linhas do parágrafo
            fixed_paragraph = ' '.join(joined_lines)
            fixed_paragraphs.append(fixed_paragraph)
        
        return '\n\n'.join(fixed_paragraphs)
    
    def _should_join_lines_in_paragraph(self, current_line: str, next_line: str) -> bool:
        """Determina se duas linhas em um parágrafo devem ser juntadas"""
        if not next_line:
            return False
        
        # Regras para juntar linhas em parágrafo
        # 1. Se a linha atual termina com hífen
        if current_line.endswith('-'):
            return True
        
        # 2. Se a linha atual não termina com pontuação e a próxima não começa com maiúscula
        if (not self._is_sentence_end(current_line) and 
            not self._starts_with_capital(next_line)):
            return True
        
        # 3. Se a linha atual é muito curta
        if len(current_line) < 40 and not self._is_sentence_end(current_line):
            return True
        
        # 4. Se a próxima linha começa com letra minúscula
        if self._starts_with_lowercase(next_line):
            return True
        
        return False
    
    def _fix_hyphenated_words_generic(self, content: str) -> str:
        """Algoritmo genérico e robusto para corrigir palavras com hífen quebradas"""
        # Padrão genérico para palavras quebradas com hífen
        pattern = r'(\w+)-\s*\n\s*(\w+)'
        
        def replace_hyphenated(match):
            word1 = match.group(1)
            word2 = match.group(2)
            
            # Verificar se a junção faz sentido
            combined = word1 + word2
            
            # Se a palavra combinada é muito longa (>20 chars), pode ser erro
            if len(combined) > 20:
                return match.group(0)  # Manter como está
            
            # Se a segunda parte é muito curta (<2 chars), pode ser erro
            if len(word2) < 2:
                return match.group(0)  # Manter como está
            
            # Verificar se a combinação é válida
            if self._is_valid_word_combination(word1, word2):
                return combined
            else:
                return match.group(0)  # Manter como está
        
        content = re.sub(pattern, replace_hyphenated, content, flags=re.MULTILINE)
        
        # Corrigir palavras quebradas sem hífen (algoritmo mais inteligente)
        pattern2 = r'(\w{3,})\s*\n\s*(\w{2,})'
        
        def replace_broken_words(match):
            word1 = match.group(1)
            word2 = match.group(2)
            
            # Verificar se a junção faz sentido linguístico
            if self._is_valid_word_combination(word1, word2):
                return word1 + word2
            else:
                return match.group(0)  # Manter como está
        
        content = re.sub(pattern2, replace_broken_words, content, flags=re.MULTILINE)
        
        # Corrigir palavras quebradas em múltiplas linhas
        pattern3 = r'(\w{2,})\s*\n\s*(\w{2,})\s*\n\s*(\w{2,})'
        
        def replace_multi_broken_words(match):
            word1 = match.group(1)
            word2 = match.group(2)
            word3 = match.group(3)
            
            # Tentar diferentes combinações
            combinations = [
                (word1 + word2 + word3, 3),
                (word1 + word2, 2),
                (word2 + word3, 2)
            ]
            
            for combined, score in combinations:
                if self._is_valid_word_combination_advanced(combined, score):
                    return combined
            
            return match.group(0)  # Manter como está
        
        content = re.sub(pattern3, replace_multi_broken_words, content, flags=re.MULTILINE)
        
        return content
    
    def _is_valid_word_combination(self, word1: str, word2: str) -> bool:
        """Verifica se a combinação de duas palavras faz sentido"""
        combined = word1 + word2
        
        # Regras básicas para validar combinação
        # 1. Não pode ser muito longa
        if len(combined) > 20:
            return False
        
        # 2. Não pode ter consoantes duplas estranhas
        if re.search(r'([bcdfghjklmnpqrstvwxz])\1{2,}', combined):
            return False
        
        # 3. Não pode ter vogais duplas estranhas
        if re.search(r'([aeiou])\1{3,}', combined):
            return False
        
        # 4. Deve ter pelo menos uma vogal
        if not re.search(r'[aeiou]', combined):
            return False
        
        return True
    
    def _is_valid_word_combination_advanced(self, combined: str, score: int) -> bool:
        """Validação avançada para combinações de palavras com pontuação"""
        # Regras básicas
        if not self._is_valid_word_combination(combined, combined):
            return False
        
        # Pontuação baseada no número de partes
        if score == 3:  # Três partes combinadas
            # Deve ser uma palavra muito comum ou técnica
            common_long_words = [
                'international', 'classification', 'characteristics', 'mathematical',
                'computational', 'theoretical', 'experimental', 'methodological',
                'philosophical', 'psychological', 'sociological', 'technological'
            ]
            if combined.lower() in common_long_words:
                return True
            # Se não for comum, ser mais restritivo
            return len(combined) <= 15
        
        elif score == 2:  # Duas partes combinadas
            return len(combined) <= 20
        
        return True
    
    def _fix_common_patterns_generic(self, content: str) -> str:
        """Algoritmo genérico para corrigir padrões comuns"""
        # Corrigir números quebrados (algoritmo genérico)
        content = re.sub(r'(\d+)\s+(\d+)', r'\1\2', content)
        
        # Corrigir palavras com espaços no meio (algoritmo genérico)
        content = re.sub(r'(\w{2,})\s+(\w{2,})', self._fix_spaced_words, content)
        
        # Corrigir pontuação dupla
        content = re.sub(r'([.!?])\1+', r'\1', content)
        content = re.sub(r'([,;:])\1+', r'\1', content)
        
        # Corrigir espaços antes de pontuação
        content = re.sub(r'\s+([.!?,;:])', r'\1', content)
        
        # Corrigir espaços múltiplos
        content = re.sub(r' +', ' ', content)
        
        return content
    
    def _fix_spaced_words(self, match) -> str:
        """Algoritmo para decidir se palavras com espaço devem ser juntadas"""
        word1 = match.group(1)
        word2 = match.group(2)
        
        # Se ambas são muito curtas, provavelmente devem juntar
        if len(word1) <= 2 and len(word2) <= 2:
            return word1 + word2
        
        # Se a segunda palavra começa com maiúscula, provavelmente não deve juntar
        if word2 and word2[0].isupper():
            return match.group(0)
        
        # Se a combinação faz sentido, juntar
        if self._is_valid_word_combination(word1, word2):
            return word1 + word2
        
        return match.group(0)
    
    def _normalize_whitespace_advanced(self, content: str) -> str:
        """Normalização avançada de espaços em branco"""
        # Remove espaços múltiplos
        content = re.sub(r' +', ' ', content)
        
        # Remove espaços no início e fim de linhas
        content = re.sub(r'^\s+|\s+$', '', content, flags=re.MULTILINE)
        
        # Normaliza quebras de linha
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        # Remove linhas vazias excessivas
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _is_sentence_end(self, line: str) -> bool:
        """Verifica se a linha termina com pontuação de fim de frase"""
        if not line:
            return False
        return line.strip().endswith(('.', '!', '?', ':', ';'))
    
    def _is_sentence_start(self, text: str) -> bool:
        """Verifica se o texto parece ser início de sentença"""
        if not text:
            return False
        
        # Palavras que geralmente iniciam sentenças
        sentence_starters = [
            'the', 'a', 'an', 'this', 'that', 'these', 'those',
            'i', 'we', 'you', 'he', 'she', 'it', 'they',
            'there', 'here', 'where', 'when', 'why', 'how',
            'what', 'which', 'who', 'whose', 'whom'
        ]
        
        first_word = text.strip().lower().split()[0] if text.strip().split() else ''
        return first_word in sentence_starters
    
    def _ends_with_punctuation(self, text: str) -> bool:
        """Verifica se o texto termina com pontuação"""
        return text.rstrip().endswith(('.', '!', '?', ':', ';', ',', ';'))
    
    def _is_title_or_structure(self, line: str) -> bool:
        """Verifica se a linha é um título ou estrutura especial"""
        if not line:
            return False
        
        # Padrões de títulos
        title_patterns = [
            r'^#+\s+',  # Markdown headers
            r'^\d+\.\s+',  # Números de seção
            r'^[A-Z][A-Z\s]+$',  # Tudo maiúsculo
            r'^Abstract',  # Palavras-chave
            r'^Introduction',
            r'^Conclusion',
            r'^References',
            r'^Bibliography',
            r'^Table\s+\d+',
            r'^Figure\s+\d+',
        ]
        
        for pattern in title_patterns:
            if re.match(pattern, line.strip()):
                return True
        
        return False
    
    def _is_structure_start(self, line: str) -> bool:
        """Verifica se uma linha parece ser início de estrutura especial"""
        # Padrões que indicam início de estrutura
        patterns = [
            r'^#',  # Markdown heading
            r'^\d+\.',  # Numbered list
            r'^[-*+]\s',  # Bullet list
            r'^\|',  # Table
            r'^```',  # Code block
            r'^>',  # Quote
            r'^\[',  # Link or reference
            r'^http',  # URL
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS (likely title)
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        return False
    
    def _is_isolated_number(self, line: str) -> bool:
        """Verifica se uma linha é apenas um número isolado"""
        return bool(re.match(r'^\d+$', line))
    
    def _looks_like_sentence_start(self, line: str) -> bool:
        """Verifica se uma linha parece ser início de nova frase"""
        if not line:
            return False
        
        # Se começa com maiúscula e tem mais de 3 palavras, provavelmente é nova frase
        if (line[0].isupper() and 
            len(line.split()) > 3 and
            not self._is_structure_start(line)):
            return True
        
        return False

    def _should_join_lines_contextual(self, line1: str, line2: str, all_lines: List[str], current_index: int) -> bool:
        """Análise contextual avançada para decidir se duas linhas devem ser juntadas"""
        
        # === ANÁLISE SEMÂNTICA ===
        semantic_score = 0
        
        # Verificar se as linhas fazem sentido juntas semanticamente
        if self._semantic_analysis_suggests_join(line1, line2):
            semantic_score += 3
        
        # Verificar se a segunda linha parece continuação natural
        if self._looks_like_natural_continuation(line1, line2):
            semantic_score += 2
        
        # === ANÁLISE LINGUÍSTICA ===
        linguistic_score = 0
        
        # Se a primeira linha termina com hífen, sempre juntar
        if line1.endswith('-'):
            linguistic_score += 4
        
        # Se a segunda linha começa com minúscula, provavelmente deve juntar
        if line2 and line2[0].islower():
            linguistic_score += 2
        
        # Se a primeira linha não termina com pontuação e a segunda não começa com maiúscula
        if (not self._is_sentence_end(line1) and 
            line2 and not line2[0].isupper()):
            linguistic_score += 2
        
        # === ANÁLISE DE CONTEXTO ===
        context_score = 0
        
        # Verificar contexto das linhas anteriores e posteriores
        context_score += self._analyze_context_context(all_lines, current_index)
        
        # Verificar se não quebraria uma estrutura existente
        if not self._would_break_structure(line1, line2, all_lines, current_index):
            context_score += 2
        
        # === ANÁLISE DE COMPRIMENTO ===
        length_score = 0
        
        # Se ambas as linhas são muito curtas, provavelmente devem juntar
        if len(line1.split()) <= 3 and len(line2.split()) <= 3:
            length_score += 1
        
        # Se a linha resultante não seria muito longa
        combined_length = len(line1.split()) + len(line2.split())
        if combined_length <= 25:  # Limite razoável para uma linha
            length_score += 1
        
        # === CÁLCULO DO SCORE FINAL ===
        total_score = semantic_score + linguistic_score + context_score + length_score
        
        # Threshold para decidir se juntar
        threshold = 4
        
        return total_score >= threshold
    
    def _semantic_analysis_suggests_join(self, line1: str, line2: str) -> bool:
        """Análise semântica para verificar se as linhas fazem sentido juntas"""
        
        # Verificar se a combinação forma frases gramaticalmente corretas
        combined = line1 + ' ' + line2
        
        # Verificar se não quebra uma frase no meio
        if self._breaks_sentence_midway(line1, line2):
            return False
        
        # Verificar se forma uma expressão técnica válida
        if self._forms_valid_technical_expression(line1, line2):
            return True
        
        # Verificar se forma uma frase completa
        if self._forms_complete_sentence(combined):
            return True
        
        # Verificar se são parte de uma lista ou estrutura
        if self._is_part_of_list_or_structure(line1, line2):
            return False
        
        return True
    
    def _breaks_sentence_midway(self, line1: str, line2: str) -> bool:
        """Verifica se juntar as linhas quebraria uma frase no meio"""
        
        # Se a primeira linha termina com pontuação de frase, não quebrar
        if self._is_sentence_end(line1):
            return True
        
        # Se a segunda linha começa com conectores que indicam nova frase
        connectors = ['mas', 'porém', 'entretanto', 'contudo', 'todavia', 'no entanto',
                     'but', 'however', 'nevertheless', 'nonetheless', 'yet', 'still']
        
        if line2 and any(line2.lower().startswith(conn) for conn in connectors):
            return True
        
        # Se a segunda linha começa com pronomes demonstrativos
        demonstratives = ['este', 'esta', 'isto', 'esse', 'essa', 'isso', 'aquele', 'aquela', 'aquilo',
                         'this', 'that', 'these', 'those']
        
        if line2 and any(line2.lower().startswith(dem) for dem in demonstratives):
            return True
        
        return False
    
    def _forms_valid_technical_expression(self, line1: str, line2: str) -> bool:
        """Verifica se a combinação forma uma expressão técnica válida"""
        combined = line1 + ' ' + line2
        
        # Padrões de expressões técnicas
        technical_patterns = [
            r'[A-Z][a-z]+\s+[=<>]\s+[A-Za-z0-9]+',  # Variável = valor
            r'[a-z]+\s+[=<>]\s+[A-Za-z0-9]+',       # variável = valor
            r'[0-9]+\s*[+\-*/]\s*[0-9]+',           # Operação matemática
            r'[A-Z]{2,}\s+[A-Za-z]+',               # Sigla seguida de palavra
            r'[a-z]+\s*\([^)]*\)',                  # Função com parâmetros
        ]
        
        import re
        for pattern in technical_patterns:
            if re.search(pattern, combined):
                return True
        
        return False
    
    def _forms_complete_sentence(self, text: str) -> bool:
        """Verifica se o texto forma uma frase completa"""
        
        # Verificar se termina com pontuação de frase
        if text.endswith(('.', '!', '?')):
            return True
        
        # Verificar se tem verbo (simplificado)
        import re
        common_verbs = ['é', 'são', 'está', 'estão', 'tem', 'têm', 'faz', 'fazem', 'vai', 'vão',
                       'is', 'are', 'was', 'were', 'has', 'have', 'does', 'do', 'will', 'can']
        
        words = text.lower().split()
        if any(verb in words for verb in common_verbs):
            return True
        
        return False
    
    def _is_part_of_list_or_structure(self, line1: str, line2: str) -> bool:
        """Verifica se as linhas são parte de uma lista ou estrutura"""
        
        # Verificar se são itens de lista
        list_patterns = [
            r'^[-*•]\s+',  # Lista não ordenada
            r'^\d+\.\s+',  # Lista numerada
            r'^[a-zA-Z]\.\s+',  # Lista com letras
        ]
        
        import re
        for pattern in list_patterns:
            if re.match(pattern, line1) or re.match(pattern, line2):
                return True
        
        return False
    
    def _looks_like_natural_continuation(self, line1: str, line2: str) -> bool:
        """Verifica se a segunda linha parece continuação natural da primeira"""
        
        # Se a primeira linha termina com hífen
        if line1.endswith('-'):
            return True
        
        # Se a segunda linha começa com minúscula
        if line2 and line2[0].islower():
            return True
        
        # Se a primeira linha não termina com pontuação
        if not self._is_sentence_end(line1):
            return True
        
        # Se são parte de uma expressão técnica
        if self._is_technical_expression_part(line1, line2):
            return True
        
        return False
    
    def _is_technical_expression_part(self, line1: str, line2: str) -> bool:
        """Verifica se as linhas são parte de uma expressão técnica"""
        
        # Verificar se a primeira linha termina com operadores
        if line1.endswith(('=', '<', '>', '+', '-', '*', '/')):
            return True
        
        # Verificar se a segunda linha começa com números ou variáveis
        if line2 and (line2[0].isdigit() or line2[0].isalpha()):
            return True
        
        return False
    
    def _analyze_context_context(self, all_lines: List[str], current_index: int) -> int:
        """Analisa o contexto das linhas ao redor para decidir se juntar"""
        score = 0
        
        # Verificar linhas anteriores
        if current_index > 0:
            prev_line = all_lines[current_index - 1].strip()
            if self._is_sentence_end(prev_line):
                score += 1  # Provavelmente início de nova frase
        
        # Verificar linhas posteriores
        if current_index + 2 < len(all_lines):
            next_next_line = all_lines[current_index + 2].strip()
            if self._looks_like_sentence_start(next_next_line):
                score += 1  # Provavelmente fim de frase
        
        return score
    
    def _would_break_structure(self, line1: str, line2: str, all_lines: List[str], current_index: int) -> bool:
        """Verifica se juntar as linhas quebraria uma estrutura existente"""
        
        # Verificar se quebraria uma lista
        if self._is_part_of_list_or_structure(line1, line2):
            return True
        
        # Verificar se quebraria uma tabela
        if '|' in line1 or '|' in line2:
            return True
        
        # Verificar se quebraria um bloco de código
        if line1.startswith('```') or line2.startswith('```'):
            return True
        
        return False

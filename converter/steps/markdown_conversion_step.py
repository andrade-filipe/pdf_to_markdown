"""Passo de conversão para Markdown"""

import re
from typing import Dict, Any, List
from .base_step import BaseStep
from ..converter import converter_texto, converter_tabela, detectar_titulos, processar_imagem


class MarkdownConversionStep(BaseStep):
    """Passo responsável por converter dados extraídos para Markdown"""
    
    def __init__(self):
        super().__init__("MarkdownConversion")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte dados extraídos para formato Markdown"""
        markdown_content = []
        
        # Processar informações de fonte para detectar títulos (prioridade)
        font_info = data.get('font_info', [])
        if font_info:
            markdown_content.append(self._process_font_info(font_info))
        else:
            # Fallback: processar texto raw se não houver informações de fonte
            raw_text = data.get('raw_text', '')
            if raw_text:
                markdown_content.append(self._process_raw_text(raw_text))
            else:
                # Fallback final: processar texto limpo
                cleaned_text = data.get('cleaned_text', '')
                if cleaned_text:
                    markdown_content.append(converter_texto(cleaned_text))
        
        # Processar tabelas
        tables = data.get('tables', [])
        for table in tables:
            table_markdown = converter_tabela(table['dados'])
            if table_markdown:
                markdown_content.append(f"\n## Tabela {table['numero']} (Página {table['pagina']})\n")
                markdown_content.append(table_markdown)
                markdown_content.append("\n")
        
        # Processar imagens
        images = data.get('images', [])
        for image in images:
            image_markdown = processar_imagem(image['caminho'])
            if image_markdown:
                markdown_content.append(f"\n## Imagem {image['numero']} (Página {image['pagina']})\n")
                markdown_content.append(image_markdown)
                markdown_content.append("\n")
        
        # Juntar todo o conteúdo
        final_markdown = '\n\n'.join(markdown_content)
        
        # Aplicar remoção de duplicações
        final_markdown = self._remove_duplications(final_markdown)
        
        # Adicionar markdown final ao contexto (otimização será aplicada no AdvancedMarkdownConversionStep)
        data['markdown_content'] = final_markdown
        return data
    
    def _process_font_info(self, font_info: List[Dict[str, Any]]) -> str:
        """Processa informações de fonte para detectar títulos"""
        # Agrupar por página e ordenar por posição
        pages = {}
        for info in font_info:
            page = info['pagina']
            if page not in pages:
                pages[page] = []
            pages[page].append(info)
        
        # Ordenar por posição Y (topo para baixo)
        for page in pages:
            pages[page].sort(key=lambda x: x['posicao'][1])
        
        # Converter para markdown
        markdown_parts = []
        for page_num in sorted(pages.keys()):
            page_content = []
            for info in pages[page_num]:
                text = info['text']
                size = info['tamanho']
                
                # Detectar títulos usando a nova lógica inteligente
                if self._is_title(text) and size >= 12:  # Títulos têm fonte maior
                    page_content.append(f"# {text}")
                else:
                    page_content.append(text)
            
            if page_content:
                markdown_parts.append('\n\n'.join(page_content))
        
        return '\n\n'.join(markdown_parts)
    
    def _remove_duplications(self, text: str) -> str:
        """Remove duplicações consecutivas no texto"""
        if not text:
            return text
        
        lines = text.split('\n')
        if len(lines) <= 1:
            return text
        
        # Remover duplicações consecutivas
        cleaned_lines = []
        for i, line in enumerate(lines):
            # Pular linha se for igual à anterior
            if i > 0 and line.strip() == lines[i-1].strip():
                continue
            # Pular linha se for muito similar à anterior (diferença < 10%)
            if i > 0 and self._similarity(lines[i-1].strip(), line.strip()) > 0.9:
                continue
            cleaned_lines.append(line)
        
        # Remover blocos duplicados (3+ linhas consecutivas iguais)
        final_lines = []
        i = 0
        while i < len(cleaned_lines):
            # Verificar se há 3+ linhas consecutivas iguais
            if i + 2 < len(cleaned_lines):
                block1 = '\n'.join(cleaned_lines[i:i+3])
                if i + 5 < len(cleaned_lines):
                    block2 = '\n'.join(cleaned_lines[i+3:i+6])
                    if self._similarity(block1, block2) > 0.9:
                        # Remover bloco duplicado
                        final_lines.extend(cleaned_lines[i:i+3])
                        i += 6
                        continue
            
            final_lines.append(cleaned_lines[i])
            i += 1
        
        return '\n'.join(final_lines)
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos (0-1)"""
        if not text1 or not text2:
            return 0.0
        
        # Normalizar textos
        text1 = text1.strip().lower()
        text2 = text2.strip().lower()
        
        if text1 == text2:
            return 1.0
        
        # Distância de Levenshtein
        len1, len2 = len(text1), len(text2)
        if len1 == 0:
            return 0.0
        if len2 == 0:
            return 0.0
        
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if text1[i-1] == text2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1,    # deletion
                        matrix[i][j-1] + 1,    # insertion
                        matrix[i-1][j-1] + 1   # substitution
                    )
        
        max_len = max(len1, len2)
        return 1 - (matrix[len1][len2] / max_len)
    
    def _process_raw_text(self, raw_text: str) -> str:
        """Processa texto raw extraído do PDF"""
        if not raw_text:
            return ""
        
        # Verificar se o texto está muito corrompido
        if self._is_text_corrupted(raw_text):
            # Tentar limpar o texto corrompido
            raw_text = self._clean_corrupted_text(raw_text)
        
        # Dividir em parágrafos
        paragraphs = raw_text.split('\n\n')
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Detectar títulos usando a nova lógica inteligente
            if self._is_title(paragraph):
                processed_paragraphs.append(f"# {paragraph}")
            else:
                processed_paragraphs.append(paragraph)
        
        result = '\n\n'.join(processed_paragraphs)
        
        # Aplicar remoção de duplicações
        result = self._remove_duplications(result)
        
        return result
    
    def _is_text_corrupted(self, text: str) -> bool:
        """Detecta se o texto está corrompido"""
        if not text:
            return True
        
        # Contar caracteres estranhos
        strange_chars = sum(1 for char in text if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
        total_chars = len(text)
        
        # Se mais de 20% dos caracteres são estranhos, considerar corrompido
        return strange_chars / total_chars > 0.2 if total_chars > 0 else True
    
    def _clean_corrupted_text(self, text: str) -> str:
        """Tenta limpar texto corrompido"""
        # Remover caracteres muito estranhos
        cleaned = ""
        for char in text:
            # Manter caracteres ASCII básicos, espaços, quebras de linha e alguns caracteres especiais
            if (ord(char) < 128 or char in 'áéíóúâêîôûãõçàèìòùäëïöüñ') and char != '\x00':
                cleaned += char
            else:
                cleaned += ' '  # Substituir por espaço
        
        # Remover linhas muito estranhas
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            # Se a linha tem muitos caracteres estranhos, pular
            if len(line.strip()) > 0:
                strange_chars = sum(1 for char in line if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
                if strange_chars / len(line) < 0.5:  # Menos de 50% de caracteres estranhos
                    cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _is_title(self, text: str) -> bool:
        """
        Detecta se um texto é um título real usando análise linguística e estrutural robusta.
        Baseado em padrões linguísticos reais, não em listas específicas.
        """
        text_stripped = text.strip()
        
        # Verificações básicas de validade
        if not text_stripped or len(text_stripped) < 2:
            return False
        
        # 1. ANÁLISE LINGUÍSTICA ESTRUTURAL
        words = text_stripped.split()
        word_count = len(words)
        
        # 1.1 Verificar se é uma única palavra muito curta (não é título)
        # Mas permitir seções acadêmicas conhecidas
        if word_count == 1 and len(text_stripped) < 6:
            return False
        
        # 1.2 Verificar se é muito longo (títulos não são parágrafos)
        if len(text_stripped) > 200:
            return False
        
        # 2. ANÁLISE DE PADRÕES LINGUÍSTICOS
        # 2.1 Verificar se contém elementos de metadados (URLs, emails, etc.)
        if re.search(r'http[s]?://|www\.|@|\.com|\.org|\.edu', text_stripped, re.IGNORECASE):
            return False
        
        # 2.2 Verificar se contém muitas abreviações consecutivas (provavelmente metadados)
        consecutive_caps = len(re.findall(r'\b[A-Z]{2,}\b', text_stripped))
        if consecutive_caps > 3:
            return False
        
        # 2.3 Verificar se contém muitos números ou símbolos matemáticos isolados
        math_symbols = len(re.findall(r'[\+\-\*\/\=\<\>\[\]\(\)\{\}\^\~]', text_stripped))
        if math_symbols > 2:
            return False
        
        # 3. ANÁLISE DE ESTRUTURA GRAMATICAL
        # 3.1 Verificar se começa com artigo definido/indefinido seguido de substantivo (padrão de título)
        if re.match(r'^(The|A|An)\s+[A-Z][a-z]', text_stripped):
            return self._analyze_title_structure(text_stripped, words)
        
        # 3.2 Verificar se é uma frase imperativa (não é título)
        if text_stripped.endswith('!') or text_stripped.endswith('?'):
            return False
        
        # 3.3 Verificar se contém verbos no imperativo (não é título)
        imperative_verbs = ['follow', 'see', 'read', 'check', 'visit', 'click', 'download', 'view']
        if any(verb in text_stripped.lower() for verb in imperative_verbs):
            return False
        
        # 4. ANÁLISE DE PADRÕES ACADÊMICOS
        # 4.1 Verificar se é uma seção acadêmica padrão
        academic_sections = {
            'abstract', 'introduction', 'methods', 'method', 'materials', 'results', 'result', 'discussion', 
            'conclusion', 'conclusions', 'references', 'bibliography', 'appendix', 
            'appendices', 'acknowledgments', 'acknowledgements', 'summary', 'background',
            'literature review', 'methodology', 'analysis', 'evaluation', 'assessment'
        }
        if text_stripped.lower() in academic_sections:
            return True
        
        # 4.2 Verificar se é um título numerado (1. Introduction, etc.)
        if re.match(r'^\d+\.\s+[A-Z]', text_stripped):
            return self._analyze_title_structure(text_stripped, words)
        
        # 4.3 Verificar se é um título com subtítulo (Título: Subtítulo)
        if ':' in text_stripped and len(text_stripped.split(':')) == 2:
            return self._analyze_title_structure(text_stripped, words)
        
        # 5. ANÁLISE DE CAPITALIZAÇÃO E FORMATO
        # 5.1 Verificar se é Title Case (primeira letra de cada palavra em maiúscula)
        if self._is_title_case(text_stripped):
            return self._analyze_title_structure(text_stripped, words)
        
        # 5.2 Verificar se é ALL CAPS (título em maiúsculas)
        if text_stripped.isupper() and 10 <= len(text_stripped) <= 100:
            return self._analyze_title_structure(text_stripped, words)
        
        # 6. ANÁLISE DE CONTEÚDO SEMÂNTICO
        # 6.1 Verificar se contém palavras-chave de título acadêmico
        title_keywords = {
            'study', 'analysis', 'investigation', 'examination', 'evaluation', 'assessment',
            'review', 'survey', 'research', 'experiment', 'trial', 'test', 'model',
            'approach', 'method', 'technique', 'procedure', 'system', 'framework',
            'theory', 'hypothesis', 'concept', 'principle', 'mechanism', 'process',
            'development', 'implementation', 'application', 'comparison', 'comparative',
            'effect', 'impact', 'influence', 'relationship', 'correlation', 'association'
        }
        
        text_lower = text_stripped.lower()
        title_keyword_count = sum(1 for keyword in title_keywords if keyword in text_lower)
        
        # Se contém palavras-chave de título, analisar mais profundamente
        if title_keyword_count > 0:
            return self._analyze_title_structure(text_stripped, words)
        
        # 7. ANÁLISE DE PADRÕES NEGATIVOS (o que NÃO é título)
        # 7.1 Verificar se é uma frase completa com verbo conjugado
        if self._has_conjugated_verb(text_stripped):
            return False
        
        # 7.2 Verificar se contém informações de autor/instituição
        author_patterns = [
            r'\b(University|College|Institute|School|Department|Center|Laboratory|Lab)\b',
            r'\b(Professor|Dr\.|PhD|MSc|BA|MA)\b',
            r'\b(Street|Avenue|Road|Drive|Lane|Boulevard)\b',
            r'\b\d{5}(-\d{4})?\b',  # CEP/ZIP code
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone number
        ]
        
        for pattern in author_patterns:
            if re.search(pattern, text_stripped, re.IGNORECASE):
                return False
        
        # 7.3 Verificar se é uma citação ou referência
        if re.search(r'\[\d+\]|\(\d{4}\)|et al\.|pp\.|vol\.|no\.', text_stripped):
            return False
        
        # 8. ANÁLISE FINAL DE ESTRUTURA
        return self._analyze_title_structure(text_stripped, words)
    
    def _analyze_title_structure(self, text: str, words: list) -> bool:
        """
        Análise profunda da estrutura de um possível título
        """
        word_count = len(words)
        
        # 1. Verificar comprimento ideal de título (2-15 palavras)
        if not (2 <= word_count <= 15):
            return False
        
        # 2. Verificar se não contém muitas preposições/conjunções (indica texto corrido)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'within', 'without', 'against', 'toward',
            'towards', 'upon', 'across', 'behind', 'beneath', 'beside', 'beyond', 'inside',
            'outside', 'under', 'over', 'around', 'along', 'near', 'far', 'off', 'out'
        }
        
        stop_word_count = sum(1 for word in words if word.lower() in stop_words)
        if stop_word_count > word_count * 0.6:  # Mais de 60% são stop words
            return False
        
        # 3. Verificar se contém substantivos importantes (títulos têm substantivos)
        # Palavras que indicam conteúdo substantivo
        content_words = sum(1 for word in words if len(word) > 3 and word.lower() not in stop_words)
        if content_words < word_count * 0.3:  # Menos de 30% são palavras de conteúdo
            return False
        
        # 4. Verificar se não termina com pontuação de frase (indica texto corrido)
        if text.endswith('.') or text.endswith('!') or text.endswith('?'):
            return False
        
        # 5. Verificar se não contém muitas vírgulas (indica texto corrido)
        comma_count = text.count(',')
        if comma_count > 2:
            return False
        
        # 6. Verificar se não contém aspas (indica citação)
        if '"' in text or "'" in text:
            return False
        
        return True
    
    def _is_title_case(self, text: str) -> bool:
        """
        Verifica se o texto está em Title Case (primeira letra de cada palavra em maiúscula)
        """
        words = text.split()
        if not words:
            return False
        
        # Verificar se cada palavra começa com maiúscula
        for word in words:
            if not word:  # Palavra vazia
                continue
            if not word[0].isupper():
                return False
        
        return True
    
    def _has_conjugated_verb(self, text: str) -> bool:
        """
        Verifica se o texto contém verbos conjugados (indica frase completa, não título)
        """
        # Padrões de verbos conjugados comuns
        verb_patterns = [
            r'\b(is|are|was|were|be|been|being)\b',  # To be
            r'\b(have|has|had|having)\b',  # To have
            r'\b(do|does|did|doing)\b',  # To do
            r'\b(can|could|will|would|should|may|might|must)\b',  # Modal verbs
            r'\b(studies|studied|studying)\b',
            r'\b(analyzes|analyzed|analyzing)\b',
            r'\b(investigates|investigated|investigating)\b',
            r'\b(examines|examined|examining)\b',
            r'\b(evaluates|evaluated|evaluating)\b',
            r'\b(assesses|assessed|assessing)\b',
            r'\b(reviews|reviewed|reviewing)\b',
            r'\b(surveys|surveyed|surveying)\b',
            r'\b(researches|researched|researching)\b',
            r'\b(experiments|experimented|experimenting)\b',
            r'\b(tests|tested|testing)\b',
            r'\b(models|modeled|modeling)\b',
            r'\b(approaches|approached|approaching)\b',
            r'\b(methods|methoded|methoding)\b',
            r'\b(techniques|techniqued|techniquing)\b',
            r'\b(procedures|procedured|proceduring)\b',
            r'\b(systems|systemed|systeming)\b',
            r'\b(frameworks|frameworked|frameworking)\b',
            r'\b(theories|theorized|theorizing)\b',
            r'\b(hypothesizes|hypothesized|hypothesizing)\b',
            r'\b(concepts|concepted|concepting)\b',
            r'\b(principles|principled|principling)\b',
            r'\b(mechanisms|mechanized|mechanizing)\b',
            r'\b(processes|processed|processing)\b',
            r'\b(develops|developed|developing)\b',
            r'\b(implements|implemented|implementing)\b',
            r'\b(applies|applied|applying)\b',
            r'\b(compares|compared|comparing)\b',
            r'\b(effects|effected|effecting)\b',
            r'\b(impacts|impacted|impacting)\b',
            r'\b(influences|influenced|influencing)\b',
            r'\b(relates|related|relating)\b',
            r'\b(correlates|correlated|correlating)\b',
            r'\b(associates|associated|associating)\b'
        ]
        
        text_lower = text.lower()
        for pattern in verb_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _optimize_paragraphs(self, markdown_content: str) -> str:
        """Otimiza parágrafos reduzindo quebras de linha desnecessárias"""
        if not markdown_content:
            return markdown_content
        
        lines = markdown_content.split('\n')
        optimized_lines = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            # Se é um título, finalizar parágrafo anterior e adicionar título
            if line.startswith('#'):
                if current_paragraph:
                    optimized_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                optimized_lines.append(line)
            # Se é linha vazia, finalizar parágrafo atual
            elif not line:
                if current_paragraph:
                    optimized_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                optimized_lines.append('')  # Manter uma linha vazia
            # Se é lista, finalizar parágrafo anterior e manter como está
            elif line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line):
                if current_paragraph:
                    optimized_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                optimized_lines.append(line)
            # Para outras linhas, tentar juntar com parágrafo atual
            else:
                # Verificar se deve juntar com linha anterior
                if current_paragraph and self._should_join_lines(current_paragraph[-1], line):
                    current_paragraph.append(line)
                else:
                    # Finalizar parágrafo anterior e começar novo
                    if current_paragraph:
                        optimized_lines.append(' '.join(current_paragraph))
                        current_paragraph = []
                    current_paragraph.append(line)
        
        # Finalizar último parágrafo
        if current_paragraph:
            optimized_lines.append(' '.join(current_paragraph))
        
        return '\n'.join(optimized_lines)
    
    def _should_join_lines(self, prev_line: str, current_line: str) -> bool:
        """Determina se duas linhas devem ser juntadas"""
        # Não juntar se a linha anterior termina com pontuação final
        if prev_line.rstrip().endswith(('.', '!', '?', ':', ';')):
            return False
        
        # Não juntar se a linha atual começa com maiúscula e parece início de frase
        if current_line and current_line[0].isupper():
            # Verificar se não é número ou abreviação
            if not re.match(r'^\d+', current_line):
                return False
        
        # Não juntar linhas muito curtas (possíveis títulos)
        if len(current_line) < 30 and current_line.isupper():
            return False
        
        # Não juntar se parece ser uma lista ou item numerado
        if re.match(r'^[-•*]\s', current_line) or re.match(r'^\d+\.\s', current_line):
            return False
        
        # Juntar se as linhas são relacionadas
        return True

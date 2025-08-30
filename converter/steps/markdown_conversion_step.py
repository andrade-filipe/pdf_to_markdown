"""Passo de conversão para Markdown"""

import re
import string
from typing import Dict, Any, List
from .base_step import BaseStep
from ..converter import converter_texto, converter_tabela, detectar_titulos, processar_imagem


class MarkdownConversionStep(BaseStep):
    """Passo responsável por converter dados extraídos para Markdown"""
    
    def __init__(self):
        super().__init__("MarkdownConversion")
        self.language = 'en'  # Default to English
        self.content_type = 'auto'  # Default to auto-detection
        
    def set_language(self, language: str):
        """Define o idioma para conversão específica"""
        self.language = language
        
    def set_content_type(self, content_type: str):
        """Define o tipo de conteúdo para conversão específica"""
        self.content_type = content_type
        
    def detect_language(self, text: str) -> str:
        """
        Detecta o idioma do texto baseado em características linguísticas
        """
        # Contar palavras comuns em cada idioma
        portuguese_words = {
            'para', 'como', 'com', 'que', 'não', 'uma', 'por', 'mais', 'as', 'dos',
            'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos',
            'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela',
            'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas',
            'minha', 'têm', 'naquele', 'neles', 'você', 'dessa', 'nela', 'lhe', 'deles',
            'essa', 'nesses', 'aquelas', 'vocês', 'nelas', 'deste', 'lhes', 'este',
            'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas',
            'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas',
            'deles', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles',
            'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive',
            'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam',
            'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse',
            'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem',
            'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera',
            'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos',
            'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá',
            'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam',
            'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fora', 'fôramos',
            'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for',
            'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria',
            'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'têm', 'tinha',
            'tínhamos', 'tinham', 'tivera', 'tivéramos', 'tenha', 'tenhamos',
            'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos',
            'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos',
            'teriam'
        }
        
        english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
            'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
            'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
            'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
            'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
            'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
            'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'am',
            'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
        
        # Normalizar texto
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Contar palavras de cada idioma
        pt_count = sum(1 for word in words if word in portuguese_words)
        en_count = sum(1 for word in words if word in english_words)
        
        # Verificar padrões específicos
        pt_patterns = [
            r'\b(para|como|com|que|não|uma|por|mais|as|dos)\b',
            r'\b(tem|à|seu|sua|ou|ser|quando|muito|há|nos)\b',
            r'\b(já|está|eu|também|só|pelo|pela|até|isso|ela)\b'
        ]
        
        en_patterns = [
            r'\b(the|be|to|of|and|a|in|that|have|i)\b',
            r'\b(it|for|not|on|with|he|as|you|do|at)\b',
            r'\b(this|but|his|by|from|they|we|say|her|she)\b'
        ]
        
        pt_pattern_count = sum(len(re.findall(pattern, text_lower)) for pattern in pt_patterns)
        en_pattern_count = sum(len(re.findall(pattern, text_lower)) for pattern in en_patterns)
        
        # Calcular score
        pt_score = pt_count + pt_pattern_count * 2
        en_score = en_count + en_pattern_count * 2
        
        # Decidir idioma
        if pt_score > en_score and pt_score > 10:
            return 'pt'
        elif en_score > pt_score and en_score > 10:
            return 'en'
        else:
            return 'en'  # Default to English
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte dados extraídos para formato Markdown"""
        print(f"[MarkdownConversion] Processando com idioma: {self.language}, tipo: {self.content_type}")
        
        # Usar idioma configurado pelo pipeline
        if self.language == 'auto':
            # Fallback: detectar idioma se necessário
            text = data.get('text', '') or data.get('raw_text', '') or data.get('cleaned_text', '')
            if text:
                self.language = self.detect_language(text)
                print(f"[MarkdownConversion] Idioma detectado: {self.language}")
            else:
                self.language = 'en'  # Default para inglês
        
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
        
        # Aplicar otimização de parágrafos
        final_markdown = self._optimize_paragraphs(final_markdown)
        
        # Aplicar pós-processamento de linhas isoladas
        final_markdown = self._post_process_isolated_lines(final_markdown)
        
        # MELHORIA: Aplicar formatação de URLs e referências
        final_markdown = self._format_urls_and_references(final_markdown)
        
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
        
        # Aplicar otimização de parágrafos
        result = self._optimize_paragraphs(result)
        
        # Aplicar pós-processamento para remover linhas isoladas problemáticas
        result = self._post_process_isolated_lines(result)
        
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
        Detecta se uma linha de texto é um título baseado em análise linguística e estrutural
        """
        if not text or not text.strip():
            return False
        
        text_stripped = text.strip()
        words = text_stripped.split()
        word_count = len(words)
        text_lower = text_stripped.lower()
        
        # Se tem menos de 2 palavras, provavelmente não é título
        if word_count < 2:
            return False
        
        # Se tem mais de 15 palavras, provavelmente é texto corrido
        if word_count > 15:
            return False
        
        # Verificar seções baseado no idioma e tipo de conteúdo
        if self.content_type == 'article':
            if self.language == 'pt-br':
                academic_sections = [
                    'resumo', 'introdução', 'métodos', 'materiais', 'resultados', 'discussão',
                    'conclusão', 'conclusões', 'referências', 'bibliografia', 'agradecimentos',
                    'apêndice', 'apêndices', 'método', 'resultado', 'abstract', 'introduction',
                    'methods', 'materials', 'results', 'conclusion', 'references'
                ]
            else:
                academic_sections = [
                    'abstract', 'introduction', 'methods', 'materials', 'results', 'discussion',
                    'conclusion', 'conclusions', 'references', 'bibliography', 'acknowledgments',
                    'appendix', 'appendices', 'method', 'result', 'acknowledgements',
                    'resumo', 'introdução', 'métodos', 'materiais', 'resultados', 'discussão',
                    'conclusão', 'conclusões', 'referências', 'bibliografia', 'agradecimentos'
                ]
        elif self.content_type == 'book':
            if self.language == 'pt-br':
                academic_sections = [
                    'capítulo', 'parte', 'seção', 'apêndice', 'índice', 'bibliografia',
                    'chapter', 'part', 'section', 'appendix', 'index', 'bibliography'
                ]
            else:
                academic_sections = [
                    'chapter', 'part', 'section', 'appendix', 'index', 'bibliography',
                    'capítulo', 'parte', 'seção', 'apêndice', 'índice', 'bibliografia'
                ]
        else:
            # Auto-detection - incluir ambos
            if self.language == 'pt-br':
                academic_sections = [
                    'resumo', 'introdução', 'métodos', 'materiais', 'resultados', 'discussão',
                    'conclusão', 'conclusões', 'referências', 'bibliografia', 'agradecimentos',
                    'apêndice', 'apêndices', 'método', 'resultado', 'capítulo', 'parte', 'seção',
                    'abstract', 'introduction', 'methods', 'materials', 'results', 'conclusion', 'references'
                ]
            else:
                academic_sections = [
                    'abstract', 'introduction', 'methods', 'materials', 'results', 'discussion',
                    'conclusion', 'conclusions', 'references', 'bibliography', 'acknowledgments',
                    'appendix', 'appendices', 'method', 'result', 'acknowledgements', 'chapter', 'part', 'section',
                    'resumo', 'introdução', 'métodos', 'materiais', 'resultados', 'discussão',
                    'conclusão', 'conclusões', 'referências', 'bibliografia', 'agradecimentos'
                ]
        
        if text_lower in academic_sections:
            return True
        
        # Verificar padrões de títulos de livros baseado no idioma
        if self.language == 'pt-br':
            book_patterns = [
                r'^capítulo\s+\d+',
                r'^chapter\s+\d+',
                r'^\d+\.\s+',
                r'^[IVX]+\.\s+',
                r'^apêndice\s+[A-Z]',
                r'^appendix\s+[A-Z]',
                r'^índice$',
                r'^index$',
                r'^bibliografia$',
                r'^bibliography$',
                r'^parte\s+\d+',
                r'^seção\s+\d+'
            ]
        else:
            book_patterns = [
                r'^chapter\s+\d+',
                r'^capítulo\s+\d+',
                r'^\d+\.\s+',
                r'^[IVX]+\.\s+',
                r'^appendix\s+[A-Z]',
                r'^apêndice\s+[A-Z]',
                r'^index$',
                r'^índice$',
                r'^bibliography$',
                r'^bibliografia$',
                r'^part\s+\d+',
                r'^section\s+\d+'
            ]
        
        for pattern in book_patterns:
            if re.match(pattern, text_lower):
                return True
        
        # Verificar se contém verbos conjugados (indica frase, não título)
        if self._has_conjugated_verb(text_stripped):
            return False
        
        # Verificar se é uma frase comum
        if self._is_common_sentence(text_stripped):
            return False
        
        # Verificar se parece continuação de texto
        if self._looks_like_continuation(text_stripped):
            return False
        
        # Verificar formatação (Title Case)
        if self._is_title_case(text_stripped):
            return True
        
        # Verificar se termina com pontuação de frase
        if text_stripped.endswith(('.', '!', '?')):
            return False
        
        # Verificar se contém palavras muito comuns no início
        common_starters = ['the', 'a', 'an', 'this', 'that', 'these', 'those', 'o', 'a', 'os', 'as', 'um', 'uma']
        if words[0].lower() in common_starters and word_count < 5:
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
        # Padrões de verbos conjugados baseado no idioma
        if self.language == 'pt-br':
            verb_patterns = [
                # Verbos em português
                r'\b(é|são|era|eram|foi|foram|está|estão|estava|estavam)\b',  # Ser/Estar
                r'\b(tem|têm|tinha|tinham|terá|terão|teria|teriam)\b',  # Ter
                r'\b(faz|fazem|fez|fizeram|fará|farão|faria|fariam)\b',  # Fazer
                r'\b(pode|podem|podia|podiam|poderá|poderão|poderia|poderiam)\b',  # Poder
                r'\b(deve|devem|devia|deviam|deverá|deverão|deveria|deveriam)\b',  # Dever
                r'\b(estuda|estudam|estudou|estudaram|estudará|estudarão)\b',
                r'\b(analisa|analisam|analisou|analisaram|analisará|analisarão)\b',
                r'\b(investiga|investigam|investigou|investigaram)\b',
                r'\b(examina|examinam|examinou|examinaram)\b',
                r'\b(avalia|avaliam|avaliou|avaliaram)\b',
                r'\b(revisa|revisam|revisou|revisaram)\b',
                r'\b(pesquisa|pesquisam|pesquisou|pesquisaram)\b',
                r'\b(testa|testam|testou|testaram)\b',
                r'\b(desenvolve|desenvolvem|desenvolveu|desenvolveram)\b',
                r'\b(implementa|implementam|implementou|implementaram)\b',
                r'\b(aplica|aplicam|aplicou|aplicaram)\b',
                r'\b(compara|comparam|comparou|compararam)\b',
                # Verbos em inglês também
                r'\b(is|are|was|were|be|been|being)\b',
                r'\b(have|has|had|having)\b',
                r'\b(do|does|did|doing)\b',
                r'\b(can|could|will|would|should|may|might|must)\b'
            ]
        else:
            verb_patterns = [
                # Verbos em inglês
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
                r'\b(develops|developed|developing)\b',
                r'\b(implements|implemented|implementing)\b',
                r'\b(applies|applied|applying)\b',
                r'\b(compares|compared|comparing)\b',
                r'\b(effects|effected|effecting)\b',
                r'\b(impacts|impacted|impacting)\b',
                r'\b(influences|influenced|influencing)\b',
                r'\b(relates|related|relating)\b',
                r'\b(correlates|correlated|correlating)\b',
                r'\b(associates|associated|associating)\b',
                # Verbos em português também
                r'\b(é|são|era|eram|está|estão|tem|têm|faz|fazem)\b'
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
    
    def _is_common_sentence(self, text: str) -> bool:
        """
        Verifica se o texto é uma frase comum (não título)
        """
        text_lower = text.lower()
        
        # Frases comuns que não são títulos baseado no idioma
        if self.language == 'pt-br':
            common_phrases = [
                'este estudo examina', 'encontramos que', 'a análise mostra',
                'em conclusão', 'como resultado', 'por exemplo', 'além disso',
                'além do mais', 'no entanto', 'por outro lado', 'em contraste',
                'similarmente', 'da mesma forma', 'dessa forma', 'assim sendo',
                'portanto', 'logo', 'entretanto', 'contudo', 'todavia',
                'this study examines', 'we found that', 'the analysis shows',
                'in conclusion', 'as a result', 'for example', 'in addition'
            ]
        else:
            common_phrases = [
                'this study examines', 'we found that', 'the analysis shows',
                'in conclusion', 'as a result', 'for example', 'in addition',
                'furthermore', 'moreover', 'however', 'nevertheless',
                'on the other hand', 'in contrast', 'similarly', 'likewise',
                'este estudo examina', 'encontramos que', 'a análise mostra',
                'em conclusão', 'como resultado', 'por exemplo', 'além disso'
            ]
        
        for phrase in common_phrases:
            if phrase in text_lower:
                return True
        
        # Verificar se começa com preposições comuns
        prepositions = ['in', 'on', 'at', 'by', 'for', 'with', 'em', 'no', 'na', 'por', 'para', 'com']
        words = text_lower.split()
        if words and words[0] in prepositions and len(words) > 3:
            return True
        
        # Verificar se é uma frase que começa com verbo
        verb_starters = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'do', 'does', 'did',
                        'é', 'são', 'era', 'eram', 'tem', 'têm', 'tinha', 'faz', 'fazem', 'fez']
        if words and words[0] in verb_starters:
            return True
        
        return False
    
    def _looks_like_continuation(self, text: str) -> bool:
        """
        Verifica se o texto parece ser continuação de uma frase anterior
        """
        text_stripped = text.strip()
        
        # Se é muito curto, pode ser continuação
        if len(text_stripped) < 20:
            return True
        
        # Se não começa com maiúscula, é continuação
        if text_stripped and not text_stripped[0].isupper():
            return True
        
        # Indicadores de continuação baseado no idioma
        if self.language == 'pt-br':
            continuation_indicators = [
                'e', 'ou', 'mas', 'no entanto', 'portanto', 'assim', 'logo',
                'também', 'além disso', 'além do mais', 'ademais', 'entretanto',
                'contudo', 'todavia', 'porém', 'então', 'dessa forma', 'deste modo',
                'and', 'or', 'but', 'however', 'therefore', 'thus', 'hence'
            ]
        else:
            continuation_indicators = [
                'and', 'or', 'but', 'however', 'therefore', 'thus', 'hence',
                'also', 'furthermore', 'moreover', 'in addition', 'besides',
                'e', 'ou', 'mas', 'no entanto', 'portanto', 'assim', 'logo'
            ]
        
        words = text_stripped.lower().split()
        if words and words[0] in continuation_indicators:
            return True
        
        # Verificar padrões de pronomes e artigos no início baseado no idioma
        if self.language == 'pt-br':
            pronoun_patterns = ['este', 'esse', 'essa', 'isso', 'isto', 'aquilo', 'aquela', 'aquele', 'estes', 'esses', 'essas', 'aqueles', 'aquelas', 'this', 'that', 'these', 'those', 'it', 'they']
        else:
            pronoun_patterns = ['this', 'that', 'these', 'those', 'it', 'they', 'este', 'esse', 'essa', 'isso', 'isto', 'aquilo']
        if words and words[0] in pronoun_patterns:
            return True
        
        # Frases muito curtas e sem capitalização
        if len(text_stripped) < 30 and not text_stripped.isupper():
            return True
        
        return False

    def _post_process_isolated_lines(self, markdown_content: str) -> str:
        """
        Remove linhas isoladas problemáticas e melhora a estrutura do documento
        """
        if not markdown_content:
            return markdown_content
        
        lines = markdown_content.split('\n')
        processed_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Pular linhas vazias
            if not line:
                processed_lines.append('')
                continue
            
            # Se é um título, manter
            if line.startswith('#'):
                processed_lines.append(line)
                continue
            
            # Se é lista, manter
            if line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line):
                processed_lines.append(line)
                continue
            
            # Verificar se é linha isolada problemática
            if self._is_problematic_isolated_line(line, lines, i):
                # Tentar juntar com linha anterior ou próxima
                if i > 0 and processed_lines and not processed_lines[-1].startswith('#'):
                    # Juntar com linha anterior
                    processed_lines[-1] = processed_lines[-1] + ' ' + line
                elif i < len(lines) - 1 and not lines[i + 1].strip().startswith('#'):
                    # Juntar com próxima linha (será processada na próxima iteração)
                    continue
                else:
                    # Se não conseguir juntar, manter como está
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _is_problematic_isolated_line(self, line: str, all_lines: list, current_index: int) -> bool:
        """
        Verifica se uma linha é problemática e deve ser juntada
        """
        # Linhas muito curtas que parecem fragmentos
        if len(line) < 20 and not line.endswith(('.', '!', '?', ':', ';')):
            return True
        
        # Linhas que são apenas iniciais ou abreviações
        if re.match(r'^[A-Z]\s+[A-Z]\s+[A-Z]', line):
            return True
        
        # Linhas que são apenas números ou símbolos
        if re.match(r'^[\d\s\.]+$', line):
            return True
        
        # Linhas que parecem ser continuação de texto anterior
        if line and not line[0].isupper() and len(line) < 50:
            return True
        
        # Verificar se a linha anterior termina com vírgula ou não tem pontuação final
        if current_index > 0:
            prev_line = all_lines[current_index - 1].strip()
            if prev_line and not prev_line.endswith(('.', '!', '?')):
                return True
        
        # Verificar fragmentos específicos problemáticos
        problematic_fragments = [
            r'^[A-Z]\s+[A-Z]\s+[A-Z]\s+[A-Z]',  # Múltiplas iniciais
            r'^[A-Z][a-z]+\s+[A-Z]\s+[A-Z][a-z]+\s+[A-Z]\s+[A-Z][a-z]+',  # Nome Inicial Nome Inicial Nome
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+,\s+[A-Z]',  # Nome Nome Nome, Instituição
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # Nome Nome Nome Nome
        ]
        
        for pattern in problematic_fragments:
            if re.match(pattern, line):
                return True
        
        return False

    def _format_urls_and_references(self, markdown_content: str) -> str:
        """
        Melhora a formatação de URLs e referências no texto
        """
        if not markdown_content:
            return markdown_content
        
        # Padrões de URLs e referências para melhorar
        patterns = [
            # URLs simples
            (r'https?://[^\s<>]+', lambda m: f'[{m.group(0)}]({m.group(0)})'),
            
            # URLs entre <> (já formatadas)
            (r'<https?://[^>]+>', lambda m: m.group(0)),
            
            # Referências bibliográficas simples
            (r'\(([A-Z][a-z]+ [A-Z][a-z]+, \d{4})\)', lambda m: f'({m.group(1)})'),
            
            # Números de página
            (r'p\. (\d+)', lambda m: f'p. {m.group(1)}'),
            (r'pp\. (\d+)-(\d+)', lambda m: f'pp. {m.group(1)}-{m.group(2)}'),
            
            # Referências com números
            (r'(\d+)\)', lambda m: f'{m.group(1)})'),
            
            # Melhorar formatação de emails
            (r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', lambda m: f'[{m.group(1)}](mailto:{m.group(1)})'),
        ]
        
        # Aplicar cada padrão
        for pattern, replacement in patterns:
            markdown_content = re.sub(pattern, replacement, markdown_content)
        
        # Melhorar quebras de linha em URLs longas
        lines = markdown_content.split('\n')
        improved_lines = []
        
        for line in lines:
            # Se a linha contém URL muito longa, quebrar adequadamente
            if len(line) > 100 and 'http' in line:
                # Quebrar antes de URLs longas
                line = re.sub(r'([^\s])(https?://)', r'\1\n\2', line)
            
            improved_lines.append(line)
        
        return '\n'.join(improved_lines)

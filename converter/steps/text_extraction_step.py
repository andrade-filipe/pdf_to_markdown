"""Passo de extração de texto do PDF"""

import fitz  # PyMuPDF
from typing import Dict, Any, List
from .base_step import BaseStep
import re


class TextExtractionStep(BaseStep):
    """Passo responsável por extrair texto do PDF com informações de fonte"""
    
    def __init__(self):
        super().__init__("TextExtraction")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai texto do PDF com informações de fonte e posição"""
        pdf_path = data.get('pdf_path')
        if not pdf_path:
            raise ValueError("pdf_path é obrigatório")
        
        # Verificar se é um PDF digitalizado (apenas imagem)
        if self._is_scanned_pdf(pdf_path):
            self.log_warning(f"PDF detectado como digitalizado (apenas imagem): {pdf_path}")
            self.log_warning("Este algoritmo não extrai texto de PDFs digitalizados. Arquivo será ignorado.")
            data['is_scanned_pdf'] = True
            data['extraction_warning'] = "PDF digitalizado detectado - extração de texto não suportada"
            return data
        
        # Abrir o PDF
        doc = fitz.open(pdf_path)
        extracted_data = {
            'text_blocks': [],
            'font_info': [],
            'total_pages': len(doc),
            'raw_text': "",
            'is_scanned_pdf': False
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Usar método dict como padrão para melhor controle
            page_text = self._extract_text_with_dict_method(page, page_num)
            
            if page_text.strip():
                # Limpar o texto da página antes de adicionar
                cleaned_page_text = self._clean_text(page_text)
                if cleaned_page_text.strip():
                    extracted_data['raw_text'] += cleaned_page_text + "\n\n"
            
            # Extrair informações de fonte para detecção de títulos
            self._extract_font_info(page, page_num, extracted_data)
        
        doc.close()
        
        # Adicionar dados extraídos ao contexto
        data.update(extracted_data)
        return data
    
    def _is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Detecta se um PDF é digitalizado (apenas imagem) baseado em:
        1. Baixa densidade de texto
        2. Alta proporção de imagens
        3. Falta de informações de fonte
        4. Texto muito fragmentado ou inexistente
        """
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            if total_pages == 0:
                return True
            
            # Analisar as primeiras páginas para determinar o tipo
            pages_to_check = min(3, total_pages)
            text_density = 0
            image_density = 0
            font_info_count = 0
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                
                # Extrair texto
                text = page.get_text()
                text_density += len(text.strip())
                
                # Contar imagens
                image_list = page.get_images()
                image_density += len(image_list)
                
                # Verificar informações de fonte
                try:
                    blocks = page.get_text("dict")
                    for block in blocks.get("blocks", []):
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    if span.get('text', '').strip():
                                        font_info_count += 1
                except:
                    pass
            
            doc.close()
            
            # Calcular densidades médias
            avg_text_density = text_density / pages_to_check
            avg_image_density = image_density / pages_to_check
            avg_font_info = font_info_count / pages_to_check
            
            # Critérios para detectar PDF digitalizado
            is_scanned = False
            
            # Critério 1: Muito pouco texto (< 100 caracteres por página)
            if avg_text_density < 100:
                is_scanned = True
            
            # Critério 2: Muitas imagens (> 2 por página) e pouco texto
            elif avg_image_density > 2 and avg_text_density < 500:
                is_scanned = True
            
            # Critério 3: Poucas informações de fonte (< 5 por página)
            elif avg_font_info < 5 and avg_text_density < 1000:
                is_scanned = True
            
            # Critério 4: Texto muito fragmentado (muitos caracteres isolados)
            if avg_text_density > 0:
                # Se há texto mas é muito fragmentado, pode ser OCR de baixa qualidade
                if avg_font_info > 0 and avg_text_density / avg_font_info < 10:
                    is_scanned = True
            
            return is_scanned
            
        except Exception as e:
            self.log_info(f"Erro ao detectar tipo de PDF {pdf_path}: {e}")
            # Em caso de erro, assumir que não é digitalizado
            return False
    
    def _extract_text_with_dict_method(self, page, page_num: int) -> str:
        """Extrai texto usando método dict com junção inteligente de spans"""
        try:
            blocks = page.get_text("dict")
            page_text = ""
            
            for block in blocks.get("blocks", []):
                if block.get("type") == 0:  # texto
                    block_text = self._process_text_block(block)
                    if block_text:
                        page_text += block_text + "\n"
            
            return page_text.strip()
        except Exception as e:
            self.log_info(f"Erro na extração dict da página {page_num + 1}: {e}")
            # Fallback para método simples
            return page.get_text()
    
    def _process_text_block(self, block) -> str:
        """Processa um bloco de texto juntando spans inteligentemente"""
        if "lines" not in block:
            return ""
        
        block_lines = []
        
        for line in block["lines"]:
            line_text = self._join_spans_intelligently(line["spans"])
            if line_text.strip():
                block_lines.append(line_text)
        
        return " ".join(block_lines)
    
    def _join_spans_intelligently(self, spans: List[Dict]) -> str:
        """Junta spans de forma inteligente preservando espaçamento natural"""
        if not spans:
            return ""

        # Usar algoritmo básico e robusto para estabilidade
        return self._join_spans_basic(spans)
    
    def _join_spans_basic(self, spans: List[Dict]) -> str:
        """Algoritmo básico e robusto para junção de spans"""
        if not spans:
            return ""
        
        joined_text = ""
        for span in spans:
            text = span.get('text', '').strip()
            if text:
                # Adicionar espaço se necessário
                if joined_text and not joined_text.endswith(' ') and not joined_text.endswith('\n'):
                    joined_text += ' '
                joined_text += text
        
        return joined_text
    
    def _merge_broken_words(self, spans: List[Dict]) -> List[Dict]:
        """Junta spans que fazem parte da mesma palavra quebrada"""
        if len(spans) < 2:
            return spans
        
        merged = []
        i = 0
        
        while i < len(spans):
            current_span = spans[i]
            current_text = current_span.get('text', '')
            current_bbox = current_span.get('bbox', [0, 0, 0, 0])
            
            # Verificar se o próximo span faz parte da mesma palavra
            if i + 1 < len(spans):
                next_span = spans[i + 1]
                next_text = next_span.get('text', '')
                next_bbox = next_span.get('bbox', [0, 0, 0, 0])
                
                # Verificar se são parte da mesma palavra quebrada
                if self._is_broken_word(current_text, next_text, current_bbox, next_bbox):
                    # Juntar os spans
                    merged_text = current_text + next_text
                    merged_bbox = [
                        min(current_bbox[0], next_bbox[0]),
                        min(current_bbox[1], next_bbox[1]),
                        max(current_bbox[2], next_bbox[2]),
                        max(current_bbox[3], next_bbox[3])
                    ]
                    
                    merged_span = {
                        'text': merged_text,
                        'bbox': merged_bbox,
                        'font': current_span.get('font', ''),
                        'size': current_span.get('size', 0),
                        'flags': current_span.get('flags', 0)
                    }
                    
                    merged.append(merged_span)
                    i += 2  # Pular o próximo span
                    continue
            
            # Se não juntou, adicionar o span atual
            merged.append(current_span)
            i += 1
        
        return merged
    
    def _is_broken_word(self, text1: str, text2: str, bbox1: List[float], bbox2: List[float]) -> bool:
        """Verifica se dois textos fazem parte da mesma palavra quebrada"""
        # Verificar distância horizontal
        distance = bbox2[0] - bbox1[2]
        
        # Se estão muito próximos horizontalmente
        if distance < 5.0:
            # Verificar se são parte de uma palavra válida
            combined = text1 + text2
            
            # Regras para identificar palavras quebradas
            # 1. Se a primeira parte termina com hífen
            if text1.endswith('-'):
                return True
            
            # 2. Se a segunda parte começa com minúscula
            if text2 and text2[0].islower():
                return True
            
            # 3. Se a combinação forma uma palavra válida
            if self._is_valid_word_combination(text1, text2):
                return True
            
            # 4. Se são muito próximos e fazem sentido juntos
            if distance < 2.0 and len(combined) <= 20:
                return True
        
        return False
    
    def _is_valid_word_combination(self, word1: str, word2: str) -> bool:
        """Verifica se a combinação de duas palavras faz sentido"""
        combined = word1 + word2
        
        # Regras básicas para validar combinação
        # 1. Não pode ser muito longa
        if len(combined) > 25:
            return False
        
        # 2. Não pode ter consoantes duplas estranhas
        import re
        if re.search(r'([bcdfghjklmnpqrstvwxz])\1{3,}', combined):
            return False
        
        # 3. Não pode ter vogais duplas estranhas
        if re.search(r'([aeiou])\1{4,}', combined):
            return False
        
        # 4. Deve ter pelo menos uma vogal
        if not re.search(r'[aeiou]', combined):
            return False
        
        # 5. Verificar padrões comuns de palavras quebradas
        common_patterns = [
            r'^[a-z]+[a-z]$',  # palavra normal
            r'^[A-Z][a-z]+[a-z]$',  # palavra com inicial maiúscula
            r'^[a-z]+[0-9]+$',  # palavra com números
            r'^[A-Z]+[a-z]+$',  # sigla seguida de palavra
        ]
        
        for pattern in common_patterns:
            if re.match(pattern, combined):
                return True
        
        return False
    
    def _should_join_without_space(self, prev_span: Dict, current_span: Dict) -> bool:
        """Verifica se dois spans devem ser juntados sem espaço"""
        prev_text = prev_span.get('text', '')
        current_text = current_span.get('text', '')
        
        # Casos onde não deve ter espaço
        # 1. Se o texto anterior termina com hífen
        if prev_text.endswith('-'):
            return True
        
        # 2. Se o texto atual começa com minúscula e o anterior não termina com pontuação
        if (current_text and current_text[0].islower() and 
            not prev_text.endswith(('.', '!', '?', ':', ';', ','))):
            return True
        
        # 3. Se são parte de uma expressão matemática ou técnica
        if self._is_technical_expression(prev_text, current_text):
            return True
        
        return False
    
    def _is_technical_expression(self, text1: str, text2: str) -> bool:
        """Verifica se os textos fazem parte de uma expressão técnica"""
        combined = text1 + text2
        
        # Padrões comuns em expressões técnicas
        technical_patterns = [
            r'[A-Z][a-z]+\s*[=<>]\s*$',  # Variável = valor
            r'[a-z]+\s*[=<>]\s*$',       # variável = valor
            r'[0-9]+\s*[+\-*/]\s*$',     # Número + operador
            r'[A-Z]{2,}\s*$',            # Siglas
            r'[a-z]+\s*\([^)]*$',        # Função(
            r'[A-Z][a-z]+\s*:\s*$',      # Título:
        ]
        
        import re
        for pattern in technical_patterns:
            if re.search(pattern, text1):
                return True
        
        return False
    
    def _is_page_number(self, text: str) -> bool:
        """Verifica se o texto é um número de página"""
        # Padrões comuns de numeração de página
        patterns = [
            r'^\d+$',  # Apenas números
            r'^\d+\.?$',  # Número com ponto opcional
            r'^p\.?\s*\d+',  # p. 123 ou p123
            r'^\d+\s*/\s*\d+$',  # 123 / 456
            r'^\d+\s*-\s*\d+$',  # 123 - 456
        ]
        
        for pattern in patterns:
            if re.match(pattern, text.strip()):
                return True
        
        return False
    
    def _is_header_footer(self, text: str) -> bool:
        """Verifica se o texto é cabeçalho ou rodapé repetitivo"""
        text = text.strip()
        
        # Se muito curto, provavelmente é cabeçalho/rodapé
        if len(text) < 3:
            return True
        
        # Padrões de cabeçalho/rodapé comuns
        header_footer_patterns = [
            r'^\d+$',  # Apenas números
            r'^[A-Z][a-z]*\s+\d+$',  # Janeiro 2023
            r'^©|©.*$',  # Copyright
            r'^Confidential|Proprietary|Draft$',  # Marcadores
            r'^[A-Z]{1,3}$',  # Siglas curtas
        ]
        
        for pattern in header_footer_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def _remove_excessive_word_repetitions(self, text: str) -> str:
        """Remove palavras que se repetem excessivamente"""
        lines = text.split('\n')
        cleaned_lines = []
        
        # Analisar frequência de palavras em todo o texto
        word_freq = {}
        all_words = []
        
        for line in lines:
            words = line.split()
            all_words.extend(words)
        
        # Contar frequência de palavras
        for word in all_words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) > 2:  # Ignorar palavras muito curtas
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Identificar palavras excessivamente repetidas (mais conservador)
        excessive_words = {word: count for word, count in word_freq.items() if count > 500}
        
        if excessive_words:
            # Reconstruir texto removendo ou substituindo palavras excessivas
            for line in lines:
                words = line.split()
                new_words = []
                
                for word in words:
                    clean_word = re.sub(r'[^\w]', '', word.lower())
                    
                    if clean_word in excessive_words:
                        # Substituir por uma versão mais curta ou remover
                        if len(word) > 5:
                            # Manter apenas as primeiras letras
                            new_word = word[:3] + "."
                        else:
                            # Pular palavras muito curtas e muito repetidas
                            continue
                    else:
                        new_word = word
                    
                    new_words.append(new_word)
                
                if new_words:  # Só adicionar linha se tiver conteúdo
                    cleaned_lines.append(' '.join(new_words))
        else:
            # Se não há palavras excessivamente repetidas, manter original
            cleaned_lines = lines
        
        return '\n'.join(cleaned_lines)
    
    def _extract_font_info(self, page, page_num: int, extracted_data: Dict):
        """Extrai informações de fonte para detecção de títulos"""
        try:
            blocks = page.get_text("dict")
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Filtrar texto muito pequeno ou vazio
                            if len(span['text'].strip()) > 0 and span['size'] > 6:
                                font_info = {
                                    'text': span['text'],
                                    'tamanho': span['size'],
                                    'posicao': (span['bbox'][0], span['bbox'][1]),
                                    'pagina': page_num + 1,
                                    'fonte': span['font']
                                }
                                extracted_data['font_info'].append(font_info)
                                extracted_data['text_blocks'].append(span['text'])
        except Exception as e:
            self.log_info(f"Erro na extração de informações de fonte da página {page_num + 1}: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Limpa o texto extraído removendo caracteres problemáticos e repetições"""
        # Remover caracteres de controle exceto quebras de linha
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Normalizar espaços múltiplos
        text = re.sub(r' +', ' ', text)
        
        # Remover quebras de linha múltiplas
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remover repetições excessivas de linhas
        text = self._remove_repetitive_lines(text)
        
        # Remover padrões repetitivos de cabeçalho/rodapé
        text = self._remove_header_footer_patterns(text)
        
        # Remover palavras excessivamente repetidas
        text = self._remove_excessive_word_repetitions(text)
        
        return text.strip()
    
    def _remove_repetitive_lines(self, text: str) -> str:
        """Remove linhas que se repetem excessivamente"""
        lines = text.split('\n')
        cleaned_lines = []
        line_count = {}
        
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:
                # Contar ocorrências da linha
                line_count[stripped_line] = line_count.get(stripped_line, 0) + 1
                
                # Se a linha aparece mais de 3 vezes, provavelmente é repetitiva
                if line_count[stripped_line] <= 3:
                    cleaned_lines.append(line)
            else:
                # Preservar linhas vazias
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _remove_header_footer_patterns(self, text: str) -> str:
        """Remove padrões repetitivos de cabeçalho e rodapé"""
        lines = text.split('\n')
        cleaned_lines = []
        header_footer_patterns = [
            r'^Proceedings of the International Conference on',
            r'^©.*Cedarville University',
            r'^Volume \d+ Article \d+',
            r'^Print Reference: \d+-\d+ \d{4}',
            r'^Cronologia Bíblica.*$',  # Cabeçalho específico do arquivo problemático
        ]
        
        for line in lines:
            should_keep = True
            stripped_line = line.strip()
            
            for pattern in header_footer_patterns:
                if re.match(pattern, stripped_line, re.IGNORECASE):
                    should_keep = False
                    break
            
            if should_keep:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

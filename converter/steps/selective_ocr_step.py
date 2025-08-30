"""Passo de OCR seletivo para melhorar precisão"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import numpy as np
from typing import Dict, Any, List, Tuple
from itertools import zip_longest
from .base_step import BaseStep
import re
import tempfile
import os


class SelectiveOCRStep(BaseStep):
    """Passo que aplica OCR seletivamente apenas em páginas problemáticas"""
    
    def __init__(self):
        super().__init__("SelectiveOCR")
        self.quality_threshold = 0.6  # Se a qualidade < 60%, usar OCR (menos sensível)
        self.max_ocr_pages = 10  # Reduzir para 10 páginas máximo (menos agressivo)
        self.ocr_quality_mode = "ultra_precise"  # Modo ultra-preciso
        self.enable_multiple_attempts = True  # Múltiplas tentativas de OCR
        self.enable_post_processing = True  # Pós-processamento avançado
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o PDF usando OCR seletivo"""
        pdf_path = data.get('pdf_path')
        if not pdf_path:
            return data
        
        # Se já temos texto extraído, analisar qualidade
        raw_text = data.get('raw_text', '')
        
        # Analisar qualidade do texto extraído
        quality_analysis = self._analyze_text_quality(raw_text)
        
        if quality_analysis['needs_ocr']:
            self.log_info(f"Texto de baixa qualidade detectado. Aplicando OCR seletivo...")
            
            # Aplicar OCR seletivo
            ocr_text = self._apply_selective_ocr(pdf_path)
            
            # Combinar resultados
            combined_text = self._combine_text_methods(raw_text, ocr_text, quality_analysis)
            
            data['raw_text'] = combined_text
            data['ocr_applied'] = True
            data['ocr_pages_processed'] = len(quality_analysis['problematic_pages'])
        else:
            data['ocr_applied'] = False
            data['ocr_pages_processed'] = 0
        
        return data
    
    def _analyze_text_quality(self, text: str) -> Dict[str, Any]:
        """Analisa a qualidade do texto extraído"""
        lines = text.split('\n')
        
        # Métricas de qualidade
        total_lines = len(lines)
        non_empty_lines = len([l for l in lines if l.strip()])
        
        # 1. Densidade de conteúdo
        content_density = non_empty_lines / total_lines if total_lines > 0 else 0
        
        # 2. Comprimento médio das linhas
        line_lengths = [len(l.strip()) for l in lines if l.strip()]
        avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
        
        # 3. Detectar linhas muito curtas (provavelmente fragmentadas)
        short_lines = len([l for l in line_lengths if l < 10])
        short_line_ratio = short_lines / len(line_lengths) if line_lengths else 0
        
        # 4. Detectar caracteres estranhos ou corrompidos
        strange_chars = len(re.findall(r'[^\w\s\.,;:!?()\[\]{}"\'-]', text))
        strange_char_ratio = strange_chars / len(text) if text else 0
        
        # 5. Detectar repetições excessivas
        word_freq = {}
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        max_word_freq = max(word_freq.values()) if word_freq else 0
        
        # Calcular score de qualidade
        quality_score = 0.0
        
        # Densidade de conteúdo (0-40 pontos)
        quality_score += content_density * 40
        
        # Comprimento médio das linhas (0-30 pontos)
        quality_score += min(30, avg_line_length / 5)
        
        # Penalizar linhas muito curtas (0-20 pontos)
        quality_score += (1 - short_line_ratio) * 20
        
        # Penalizar caracteres estranhos (0-10 pontos)
        quality_score += (1 - min(1, strange_char_ratio * 100)) * 10
        
        # Penalizar repetições excessivas (mais severo)
        if max_word_freq > 50:  # Reduzido de 100 para 50
            quality_score -= 30  # Aumentado de 20 para 30
        elif max_word_freq > 20:  # Nova penalização para repetições moderadas
            quality_score -= 15
        
        # Penalizar duplicação de conteúdo
        if len(text) > 30000:  # Texto muito longo pode indicar duplicação
            quality_score -= 25
        
        # Penalizar padrões repetitivos de cabeçalho
        if text.count('Cronologia Bíblica') > 3:
            quality_score -= 20
        
        quality_score = max(0, quality_score)
        
        # Log da análise para debug
        self.log_info(f"Análise de qualidade: score={quality_score:.1f}, "
                     f"densidade={content_density:.3f}, "
                     f"avg_line_length={avg_line_length:.1f}, "
                     f"repetitions={max_word_freq}")
        
        needs_ocr = quality_score < (self.quality_threshold * 100)
        
        return {
            'quality_score': quality_score,
            'needs_ocr': needs_ocr,
            'content_density': content_density,
            'avg_line_length': avg_line_length,
            'short_line_ratio': short_line_ratio,
            'strange_char_ratio': strange_char_ratio,
            'max_word_freq': max_word_freq,
            'problematic_pages': self._identify_problematic_pages(text)
        }
    
    def _identify_problematic_pages(self, text: str) -> List[int]:
        """Identifica páginas problemáticas para OCR"""
        # Dividir texto em páginas (assumindo que cada página termina com quebra dupla)
        pages = text.split('\n\n')
        problematic_pages = []
        
        for i, page_text in enumerate(pages):
            if len(page_text.strip()) < 50:  # Página muito pequena
                problematic_pages.append(i)
            elif self._has_poor_quality(page_text):
                problematic_pages.append(i)
        
        # Limitar número de páginas para OCR
        return problematic_pages[:self.max_ocr_pages]
    
    def _has_poor_quality(self, text: str) -> bool:
        """Verifica se o texto tem baixa qualidade"""
        lines = text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        if len(non_empty_lines) < 3:
            return True
        
        # Verificar se há muitas linhas muito curtas
        short_lines = len([l for l in non_empty_lines if len(l.strip()) < 10])
        if short_lines / len(non_empty_lines) > 0.7:  # 70% das linhas são muito curtas
            return True
        
        # Verificar se há caracteres estranhos
        strange_chars = len(re.findall(r'[^\w\s\.,;:!?()\[\]{}"\'-]', text))
        if strange_chars / len(text) > 0.1:  # 10% de caracteres estranhos
            return True
        
        return False
    
    def _analyze_specific_problems(self, text: str) -> Dict[str, Any]:
        """Analisa problemas específicos no texto normal"""
        lines = text.split('\n')
        
        # Contar repetições de palavras
        word_freq = {}
        all_words = []
        for line in lines:
            if line.strip():
                words = line.strip().split()
                all_words.extend([w.lower() for w in words if len(w) > 2])
        
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        max_word_repetition = max(word_freq.values()) if word_freq else 0
        
        # Detectar repetições de linhas
        line_freq = {}
        for line in lines:
            if line.strip():
                normalized = line.strip().lower()
                line_freq[normalized] = line_freq.get(normalized, 0) + 1
        
        repeated_lines = sum(1 for count in line_freq.values() if count > 1)
        max_line_repetition = max(line_freq.values()) if line_freq else 0
        
        # Detectar padrões problemáticos
        problematic_patterns = [
            'cronologia bíblica', 'proceedings of the international conference',
            'mount st helens', 'catastrophism', 'geology'
        ]
        
        pattern_counts = {}
        for pattern in problematic_patterns:
            pattern_counts[pattern] = text.lower().count(pattern)
        
        # Determinar severidade dos problemas (mais sensível)
        severe_repetitions = max_word_repetition > 50 or max_line_repetition > 20  # Reduzido
        high_duplication = len(text) > 30000  # Reduzido
        
        return {
            'max_word_repetition': max_word_repetition,
            'repeated_lines': repeated_lines,
            'max_line_repetition': max_line_repetition,
            'pattern_counts': pattern_counts,
            'severe_repetitions': severe_repetitions,
            'high_duplication': high_duplication,
            'total_words': len(all_words)
        }
    
    def _analyze_ocr_quality(self, ocr_text: str) -> Dict[str, Any]:
        """Analisa a qualidade do texto OCR"""
        lines = ocr_text.split('\n')
        
        # Contar linhas válidas
        valid_lines = [l for l in lines if l.strip() and len(l.strip()) > 10]
        valid_line_ratio = len(valid_lines) / len(lines) if lines else 0
        
        # Analisar caracteres estranhos
        strange_chars = len(re.findall(r'[^\w\s\.,;:!?()\[\]{}"\'-]', ocr_text))
        strange_char_ratio = strange_chars / len(ocr_text) if ocr_text else 0
        
        # Analisar estrutura de parágrafos
        paragraph_breaks = ocr_text.count('\n\n')
        avg_line_length = sum(len(l) for l in valid_lines) / len(valid_lines) if valid_lines else 0
        
        # Calcular score de qualidade do OCR
        quality_score = 0
        
        # Proporção de linhas válidas (0-40 pontos)
        quality_score += valid_line_ratio * 40
        
        # Qualidade dos caracteres (0-30 pontos)
        quality_score += (1 - min(1, strange_char_ratio * 20)) * 30
        
        # Estrutura de parágrafos (0-20 pontos)
        if paragraph_breaks > 5 and avg_line_length > 50:
            quality_score += 20
        elif paragraph_breaks > 2 and avg_line_length > 30:
            quality_score += 15
        elif paragraph_breaks > 0 and avg_line_length > 20:
            quality_score += 10
        
        # Comprimento do texto (0-10 pontos)
        if len(ocr_text) > 1000:
            quality_score += 10
        elif len(ocr_text) > 500:
            quality_score += 5
        
        quality_score = min(100, max(0, quality_score))
        
        return {
            'quality_score': quality_score,
            'valid_line_ratio': valid_line_ratio,
            'strange_char_ratio': strange_char_ratio,
            'paragraph_breaks': paragraph_breaks,
            'avg_line_length': avg_line_length,
            'total_length': len(ocr_text)
        }
    
    def _clean_combined_text(self, primary_text: str, secondary_text: str, strategy: str) -> str:
        """Limpa e combina textos usando estratégia específica"""
        if strategy == "normal_preferred":
            # Usar principalmente texto normal, complementar com OCR
            combined = primary_text
            
            # Adicionar informações do OCR que não estão no texto normal
            ocr_lines = secondary_text.split('\n')
            normal_lines = set(line.strip().lower() for line in primary_text.split('\n') if line.strip())
            
            for ocr_line in ocr_lines:
                if len(ocr_line.strip()) > 20:  # Linha significativa
                    if ocr_line.strip().lower() not in normal_lines:
                        combined += f"\n{ocr_line.strip()}"
        
        elif strategy == "ocr_preferred":
            # Usar principalmente OCR, complementar com texto normal
            combined = primary_text
            
            # Adicionar informações do texto normal que não estão no OCR
            normal_lines = primary_text.split('\n')
            ocr_lines = set(line.strip().lower() for line in secondary_text.split('\n') if line.strip())
            
            for normal_line in normal_lines:
                if len(normal_line.strip()) > 20:  # Linha significativa
                    if normal_line.strip().lower() not in ocr_lines:
                        combined += f"\n{normal_line.strip()}"
        
        # Aplicar limpeza final
        return self._final_cleaning(combined)
    
    def _advanced_combine(self, normal_text: str, ocr_text: str, 
                         normal_problems: Dict, ocr_quality: Dict) -> str:
        """Combinação avançada baseada em análise detalhada"""
        
        # Dividir em seções para análise mais granular
        normal_sections = self._split_into_sections(normal_text)
        ocr_sections = self._split_into_sections(ocr_text)
        
        combined_sections = []
        
        # Para cada seção, escolher o melhor texto
        for i, (normal_section, ocr_section) in enumerate(zip_longest(normal_sections, ocr_sections, fillvalue="")):
            
            if not normal_section and not ocr_section:
                continue
            
            if not normal_section:
                combined_sections.append(ocr_section)
                continue
            
            if not ocr_section:
                combined_sections.append(normal_section)
                continue
            
            # Analisar qualidade da seção específica
            normal_section_quality = self._analyze_section_quality(normal_section)
            ocr_section_quality = self._analyze_section_quality(ocr_section)
            
            # Escolher a seção com melhor qualidade
            if ocr_section_quality['score'] > normal_section_quality['score'] + 10:
                combined_sections.append(ocr_section)
            elif normal_section_quality['score'] > ocr_section_quality['score'] + 10:
                combined_sections.append(normal_section)
            else:
                # Combinação híbrida da seção
                combined_sections.append(self._combine_section(normal_section, ocr_section))
        
        combined_text = "\n\n".join(combined_sections)
        
        # Limpeza final agressiva
        return self._final_cleaning(combined_text)
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Divide o texto em seções baseadas em quebras de parágrafo"""
        sections = text.split('\n\n')
        
        # Juntar seções muito pequenas
        merged_sections = []
        current_section = ""
        
        for section in sections:
            if len(section.strip()) < 50:  # Seção muito pequena
                current_section += f"\n\n{section}"
            else:
                if current_section:
                    merged_sections.append(current_section.strip())
                current_section = section
        
        if current_section:
            merged_sections.append(current_section.strip())
        
        return merged_sections
    
    def _analyze_section_quality(self, section: str) -> Dict[str, Any]:
        """Analisa a qualidade de uma seção específica"""
        lines = section.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Métricas básicas
        line_count = len(non_empty_lines)
        avg_line_length = sum(len(l) for l in non_empty_lines) / line_count if line_count > 0 else 0
        
        # Detectar repetições
        line_freq = {}
        for line in non_empty_lines:
            normalized = line.strip().lower()
            line_freq[normalized] = line_freq.get(normalized, 0) + 1
        
        repeated_lines = sum(1 for count in line_freq.values() if count > 1)
        
        # Calcular score
        score = 0
        
        # Número de linhas (0-30 pontos)
        if line_count >= 5:
            score += 30
        elif line_count >= 3:
            score += 20
        elif line_count >= 1:
            score += 10
        
        # Comprimento médio das linhas (0-40 pontos)
        if avg_line_length >= 80:
            score += 40
        elif avg_line_length >= 50:
            score += 30
        elif avg_line_length >= 30:
            score += 20
        elif avg_line_length >= 10:
            score += 10
        
        # Penalizar repetições (0-30 pontos)
        repetition_penalty = min(30, repeated_lines * 5)
        score -= repetition_penalty
        
        return {
            'score': max(0, score),
            'line_count': line_count,
            'avg_line_length': avg_line_length,
            'repeated_lines': repeated_lines
        }
    
    def _combine_section(self, normal_section: str, ocr_section: str) -> str:
        """Combina duas seções de forma inteligente"""
        normal_lines = [l.strip() for l in normal_section.split('\n') if l.strip()]
        ocr_lines = [l.strip() for l in ocr_section.split('\n') if l.strip()]
        
        # Juntar linhas únicas de ambas as fontes
        all_lines = []
        seen_lines = set()
        
        # Alternar entre fontes para manter ordem natural
        max_lines = max(len(normal_lines), len(ocr_lines))
        
        for i in range(max_lines):
            if i < len(normal_lines):
                line = normal_lines[i]
                normalized = line.lower()
                if normalized not in seen_lines and len(line) > 10:
                    all_lines.append(line)
                    seen_lines.add(normalized)
            
            if i < len(ocr_lines):
                line = ocr_lines[i]
                normalized = line.lower()
                if normalized not in seen_lines and len(line) > 10:
                    all_lines.append(line)
                    seen_lines.add(normalized)
        
        return '\n'.join(all_lines)
    
    def _final_cleaning(self, text: str) -> str:
        """Limpeza final agressiva do texto combinado"""
        
        # Remover linhas muito repetidas
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            if line:
                normalized = line.lower()
                
                # Pular apenas linhas muito curtas
                if len(line) < 3:
                    continue
                
                # Para linhas repetidas, ser mais conservador
                if normalized in seen_lines:
                    # Contar quantas vezes já vimos esta linha
                    repeat_count = sum(1 for prev_line in cleaned_lines if prev_line.strip().lower() == normalized)
                    
                    # Permitir até 2 repetições para linhas importantes
                    if repeat_count < 2:
                        cleaned_lines.append(line)
                    else:
                        # Verificar se é uma linha importante que deveria ser mantida
                        important_keywords = ['chapter', 'section', 'figure', 'table', 'reference', 'introduction', 'conclusion']
                        if any(keyword in normalized for keyword in important_keywords):
                            cleaned_lines.append(line)
                else:
                    seen_lines.add(normalized)
                    cleaned_lines.append(line)
        
        # Remover palavras excessivamente repetidas
        all_text = ' '.join(cleaned_lines)
        words = all_text.split()
        word_freq = {}
        
        for word in words:
            word_lower = word.lower()
            if len(word_lower) > 2:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # Identificar palavras muito repetidas (apenas palavras específicas problemáticas)
        problematic_words = set()
        for word, count in word_freq.items():
            # Apenas palavras muito repetidas E específicas (não artigos/pronomes básicos)
            if count > 100 and len(word) > 3 and word not in ['the', 'and', 'for', 'this', 'that']:
                problematic_words.add(word)
        
        if problematic_words:
            self.log_info(f"Reduzindo palavras excessivamente repetidas: {problematic_words}")
            
            # Reduzir essas palavras (não remover completamente)
            
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
        
    def _apply_final_cleaning(self, text: str, aggressive: bool = False) -> str:
        """Aplica limpeza final garantida no texto"""
        self.log_info(f"Aplicando limpeza {'agressiva' if aggressive else 'conservadora'}")
        
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            normalized = line.lower()
            
            # Limpeza baseada na agressividade
            if aggressive:
                # Limpeza agressiva: remover mais repetições
                if normalized in seen_lines:
                    repeat_count = sum(1 for prev_line in cleaned_lines if prev_line.strip().lower() == normalized)
                    if repeat_count >= 1:  # Permitir apenas 1 repetição
                        important_keywords = ['chapter', 'section', 'figure', 'table', 'reference', 'introduction', 'conclusion']
                        if not any(keyword in normalized for keyword in important_keywords):
                            continue
                    seen_lines.add(normalized)
                else:
                    seen_lines.add(normalized)
                cleaned_lines.append(line)
            else:
                # Limpeza conservadora: manter mais conteúdo
                if normalized in seen_lines:
                    repeat_count = sum(1 for prev_line in cleaned_lines if prev_line.strip().lower() == normalized)
                    if repeat_count >= 3:  # Permitir até 3 repetições
                        continue
                    seen_lines.add(normalized)
                else:
                    seen_lines.add(normalized)
                cleaned_lines.append(line)
        
        # Limpeza de palavras excessivamente repetidas (apenas se agressivo)
        if aggressive:
            combined_text = ' '.join(cleaned_lines)
            words = combined_text.split()
            word_freq = {}
            
            for word in words:
                word_lower = word.lower()
                if len(word_lower) > 3:
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            # Identificar palavras muito repetidas
            excessive_words = {word for word, count in word_freq.items() 
                             if count > 200 and word not in ['the', 'and', 'for', 'this', 'that', 'genesis']}
            
            if excessive_words:
                self.log_info(f"Removendo palavras excessivamente repetidas: {excessive_words}")
                
                # Reduzir essas palavras drasticamente
                for word in excessive_words:
                    pattern = r'\b{}\b'.format(re.escape(word))
                    matches = list(re.finditer(pattern, combined_text, flags=re.IGNORECASE))
                    
                    if len(matches) > 50:
                        # Manter apenas 5% das ocorrências
                        keep_count = max(1, len(matches) // 20)
                        
                        text_parts = []
                        last_end = 0
                        
                        for i, match in enumerate(matches):
                            if i < keep_count:
                                text_parts.append(combined_text[last_end:match.end()])
                                last_end = match.end()
                        
                        text_parts.append(combined_text[last_end:])
                        combined_text = ''.join(text_parts)
            
            # Normalizar espaços
            cleaned_text = re.sub(r'\s+', ' ', combined_text).strip()
            
            # Reorganizar em linhas
            sentences = re.split(r'[.!?]+', cleaned_text)
            final_lines = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:
                    final_lines.append(sentence + '.')
            
            return '\n'.join(final_lines)
        else:
            return '\n'.join(cleaned_lines)
    
    def _apply_selective_ocr(self, pdf_path: str) -> str:
        """Aplica OCR ultra-preciso nas páginas problemáticas"""
        doc = fitz.open(pdf_path)
        all_ocr_results = {}
        
        try:
            # Identificar páginas problemáticas
            problematic_pages = self._detect_problematic_pages_from_pdf(doc)
            
            self.log_info(f"Aplicando OCR ultra-preciso em {len(problematic_pages)} páginas...")
            
            for page_num in problematic_pages:
                if page_num >= len(doc):
                    continue
                
                try:
                    page = doc.load_page(page_num)
                    
                    # Múltiplas tentativas de OCR com diferentes configurações
                    page_results = self._ocr_multiple_attempts(page, page_num)
                    
                    # Escolher o melhor resultado para esta página
                    best_result = self._select_best_ocr_result(page_results)
                    
                    if best_result:
                        all_ocr_results[page_num] = best_result
                        self.log_info(f"Página {page_num + 1}: OCR concluído com qualidade {best_result['confidence']:.1f}%")
                    
                except Exception as e:
                    self.log_info(f"Erro no OCR da página {page_num + 1}: {e}")
                    continue
            
            # Combinar todos os resultados com formatação superior
            combined_text = self._combine_ocr_results_with_formatting(all_ocr_results, doc)
            
            return combined_text
        
        finally:
            doc.close()
    
    def _ocr_multiple_attempts(self, page, page_num: int) -> List[Dict]:
        """Executa múltiplas tentativas de OCR com diferentes configurações"""
        results = []
        
        # Configurações de renderização (otimizadas)
        render_configs = [
            {'zoom': 2.5, 'colorspace': 'rgb'},  # Configuração balanceada
            {'zoom': 3.0, 'colorspace': 'gray'},  # Alta qualidade para casos difíceis
        ]
        
        # Configurações do Tesseract (otimizadas)
        tesseract_configs = [
            '--psm 6 --oem 1',  # Bloco uniforme, LSTM (melhor para artigos)
            '--psm 3 --oem 1',  # Automático, LSTM (fallback)
        ]
        
        for render_config in render_configs:
            # Renderizar página com alta qualidade
            mat = fitz.Matrix(render_config['zoom'], render_config['zoom'])
            pix = page.get_pixmap(matrix=mat)
            
            # Converter para imagem
            img_data = pix.tobytes("png")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(img_data)
                tmp_file_path = tmp_file.name
            
            try:
                # Tentar diferentes configurações do Tesseract
                for i, tesseract_config in enumerate(tesseract_configs):
                    try:
                        # OCR com configuração específica
                        ocr_result = pytesseract.image_to_string(
                            Image.open(tmp_file_path),
                            lang='eng',
                            config=tesseract_config
                        )
                        
                        # Obter dados estruturados do OCR
                        ocr_data = pytesseract.image_to_data(
                            Image.open(tmp_file_path),
                            lang='eng',
                            config=tesseract_config,
                            output_type=pytesseract.Output.DICT
                        )
                        
                        # Calcular confiança média
                        confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                        
                        # Processar e avaliar resultado
                        processed_text = self._process_ocr_result_advanced(ocr_result, ocr_data)
                        quality_score = self._evaluate_ocr_quality(processed_text, ocr_data)
                        
                        results.append({
                            'text': processed_text,
                            'confidence': avg_confidence,
                            'quality_score': quality_score,
                            'render_config': render_config,
                            'tesseract_config': tesseract_config,
                            'attempt': f"{render_config['zoom']}x_{tesseract_config.split()[1]}"
                        })
                        
                        self.log_info(f"  Tentativa {len(results)}: conf={avg_confidence:.1f}%, qual={quality_score:.1f}")
                        
                    except Exception as e:
                        self.log_info(f"  Erro na tentativa {i+1}: {e}")
                        continue
                
            finally:
                os.unlink(tmp_file_path)
        
        return results
    
    def _select_best_ocr_result(self, results: List[Dict]) -> Dict:
        """Seleciona o melhor resultado de OCR baseado em múltiplos critérios"""
        if not results:
            return None
        
        # Pontuação ponderada: 60% confiança + 40% qualidade
        for result in results:
            weighted_score = (result['confidence'] * 0.6) + (result['quality_score'] * 0.4)
            result['weighted_score'] = weighted_score
        
        # Ordenar por pontuação ponderada
        results.sort(key=lambda x: x['weighted_score'], reverse=True)
        
        best_result = results[0]
        self.log_info(f"Melhor resultado: {best_result['attempt']} (score: {best_result['weighted_score']:.1f})")
        
        return best_result
    
    def _evaluate_ocr_quality(self, text: str, ocr_data: Dict) -> float:
        """Avalia a qualidade do resultado do OCR"""
        quality_score = 0.0
        
        # 1. Proporção de palavras válidas (0-30 pontos)
        words = text.split()
        valid_words = [w for w in words if len(w) > 2 and w.isalpha()]
        if words:
            word_validity = len(valid_words) / len(words)
            quality_score += word_validity * 30
        
        # 2. Comprimento médio das linhas (0-25 pontos)
        lines = [l for l in text.split('\n') if l.strip()]
        if lines:
            avg_line_length = sum(len(l) for l in lines) / len(lines)
            quality_score += min(25, avg_line_length / 4)
        
        # 3. Estrutura de parágrafos (0-25 pontos)
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 3:
            quality_score += 25
        elif len(paragraphs) > 1:
            quality_score += 15
        
        # 4. Caracteres estranhos (0-20 pontos)
        strange_chars = len(re.findall(r'[^\w\s\.,;:!?()\[\]{}"\'-]', text))
        if text:
            strange_ratio = strange_chars / len(text)
            quality_score += (1 - min(1, strange_ratio * 10)) * 20
        
        return quality_score
    
    def _combine_ocr_results_with_formatting(self, all_ocr_results: Dict, doc) -> str:
        """Combina resultados do OCR com formatação Markdown superior"""
        if not all_ocr_results:
            return ""
        
        self.log_info("Combinando resultados do OCR com formatação superior...")
        
        # Ordenar páginas por número
        sorted_pages = sorted(all_ocr_results.keys())
        
        # Estrutura final do documento
        document_sections = []
        
        # Adicionar cabeçalho do documento
        document_sections.append("# Documento Processado com OCR Ultra-Preciso\n")
        
        # Processar cada página
        for page_num in sorted_pages:
            result = all_ocr_results[page_num]
            
            # Cabeçalho da página
            page_header = f"## Página {page_num + 1}\n"
            page_header += f"*Qualidade do OCR: {result['confidence']:.1f}% | Método: {result['attempt']}*\n\n"
            
            # Conteúdo da página com formatação aprimorada
            formatted_content = self._format_page_content(result['text'], page_num)
            
            page_section = page_header + formatted_content
            document_sections.append(page_section)
        
        # Combinar todas as seções
        final_document = '\n\n'.join(document_sections)
        
        # Aplicar limpeza final inteligente
        final_document = self._apply_intelligent_cleaning(final_document)
        
        return final_document
    
    def _format_page_content(self, text: str, page_num: int) -> str:
        """Formata o conteúdo de uma página com estrutura superior"""
        lines = text.split('\n')
        formatted_lines = []
        
        # Detectar e formatar seções
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_section:
                    formatted_lines.extend(current_section)
                    formatted_lines.append("")  # Linha em branco para separar
                    current_section = []
                continue
            
            # Detectar cabeçalhos
            if self._is_markdown_header(line):
                if current_section:
                    formatted_lines.extend(current_section)
                    formatted_lines.append("")
                    current_section = []
                formatted_lines.append(line)
            # Detectar listas
            elif line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                if current_section and not current_section[-1].startswith(('-', '•', '*')):
                    formatted_lines.extend(current_section)
                    current_section = []
                formatted_lines.append(line)
            # Parágrafos normais
            else:
                current_section.append(line)
        
        # Adicionar última seção
        if current_section:
            formatted_lines.extend(current_section)
        
        return '\n'.join(formatted_lines)
    
    def _is_markdown_header(self, line: str) -> bool:
        """Verifica se uma linha é um cabeçalho Markdown"""
        # Já formatado como cabeçalho
        if line.startswith('#'):
            return True
        
        # Verificar se parece um cabeçalho
        text_lower = line.lower()
        header_indicators = [
            'chapter', 'section', 'introduction', 'conclusion', 'abstract',
            'summary', 'appendix', 'references', 'bibliography', 'index'
        ]
        
        return any(indicator in text_lower for indicator in header_indicators)
    
    def _apply_intelligent_cleaning(self, text: str) -> str:
        """Aplica limpeza inteligente mantendo a formatação"""
        lines = text.split('\n')
        cleaned_lines = []
        
        # Remover linhas duplicadas consecutivas
        last_line = None
        for line in lines:
            if line.strip() != last_line:
                cleaned_lines.append(line)
                last_line = line.strip()
        
        # Remover seções muito pequenas (provavelmente ruído)
        sections = []
        current_section = []
        
        for line in cleaned_lines:
            if line.startswith('#') and current_section:
                # Finalizar seção anterior
                if len(current_section) > 2:  # Seção deve ter pelo menos 2 linhas
                    sections.append(current_section)
                current_section = []
            
            current_section.append(line)
        
        # Adicionar última seção
        if len(current_section) > 2:
            sections.append(current_section)
        
        # Reconstruir texto
        final_lines = []
        for section in sections:
            final_lines.extend(section)
            final_lines.append("")  # Separador entre seções
        
        return '\n'.join(final_lines)
    
    def _detect_problematic_pages_from_pdf(self, doc) -> List[int]:
        """Detecta páginas problemáticas analisando o PDF diretamente"""
        problematic_pages = []
        
        # Verificar se há problemas no texto geral (indicador para aplicar OCR)
        total_pages = len(doc)
        pages_to_analyze = min(total_pages, 10)  # Analisar primeiras 10 páginas
        
        self.log_info(f"Analisando {pages_to_analyze} páginas para detecção de problemas...")
        
        for page_num in range(pages_to_analyze):
            try:
                page = doc.load_page(page_num)
                
                # Extrair texto da página
                page_text = page.get_text()
                
                # Critérios para considerar página problemática
                is_problematic = False
                
                # 1. Página com pouco texto
                if len(page_text.strip()) < 50:
                    self.log_info(f"Página {page_num + 1}: pouco texto ({len(page_text.strip())} chars)")
                    is_problematic = True
                
                # 2. Texto de baixa qualidade
                elif self._has_poor_quality(page_text):
                    self.log_info(f"Página {page_num + 1}: baixa qualidade detectada")
                    is_problematic = True
                
                # 3. Muitas imagens
                image_list = page.get_images()
                if len(image_list) > 2:  # Reduzido de 3 para 2
                    self.log_info(f"Página {page_num + 1}: muitas imagens ({len(image_list)})")
                    is_problematic = True
                
                # 4. Caracteres estranhos ou corrompidos
                strange_chars = len(re.findall(r'[^\w\s\.,;:!?()\[\]{}"\'-]', page_text))
                if len(page_text) > 0 and (strange_chars / len(page_text)) > 0.1:
                    self.log_info(f"Página {page_num + 1}: muitos caracteres estranhos")
                    is_problematic = True
                
                if is_problematic:
                    problematic_pages.append(page_num)
                    
            except Exception as e:
                self.log_info(f"Erro ao analisar página {page_num}: {e}")
                continue
        
        # Se não encontrou páginas específicas problemáticas, mas há problemas gerais,
        # aplicar OCR em algumas páginas estratégicas
        if not problematic_pages and doc.metadata.get('title', '').lower().find('genesis') != -1:
            # Para documentos relacionados ao Genesis, aplicar OCR em páginas estratégicas
            strategic_pages = [0, 1, 2, 3, 4]  # Primeiras 5 páginas
            problematic_pages = strategic_pages[:5]
            self.log_info("Aplicando OCR em páginas estratégicas (primeiras 5 páginas)")
        
        self.log_info(f"Páginas problemáticas detectadas: {problematic_pages}")
        return problematic_pages[:self.max_ocr_pages]
    
    def _process_ocr_result_advanced(self, ocr_text: str, ocr_data: Dict) -> str:
        """Processamento avançado do resultado do OCR com dados estruturados"""
        # Usar dados estruturados para melhor processamento
        if ocr_data and 'text' in ocr_data:
            structured_lines = self._reconstruct_from_ocr_data(ocr_data)
            if structured_lines:
                return self._enhance_text_formatting(structured_lines)
        
        # Fallback para processamento básico
        return self._process_ocr_result_basic(ocr_text)
    
    def _reconstruct_from_ocr_data(self, ocr_data: Dict) -> List[Dict]:
        """Reconstrói texto usando dados estruturados do OCR"""
        if not ocr_data or 'text' not in ocr_data:
            return []
        
        # Agrupar palavras por linha baseado na posição Y
        line_groups = {}
        
        for i, text in enumerate(ocr_data['text']):
            if text.strip():
                y_pos = ocr_data['top'][i]
                confidence = int(ocr_data['conf'][i])
                
                # Agrupar por posição Y (com tolerância)
                y_group = None
                for group_y in line_groups.keys():
                    if y_group is not None and abs(y_group - y_pos) < 10:  # 10px de tolerância
                        y_group = group_y
                        break
                
                if y_group is None:
                    y_group = y_pos
                
                if y_group not in line_groups:
                    line_groups[y_group] = []
                
                line_groups[y_group].append({
                    'text': text,
                    'x': ocr_data['left'][i],
                    'y': y_pos,
                    'confidence': confidence,
                    'width': ocr_data['width'][i],
                    'height': ocr_data['height'][i]
                })
        
        # Ordenar linhas por posição Y
        sorted_lines = []
        for y_pos in sorted(line_groups.keys()):
            line_words = line_groups[y_pos]
            # Ordenar palavras na linha por posição X
            line_words.sort(key=lambda w: w['x'])
            
            sorted_lines.append({
                'y_pos': y_pos,
                'words': line_words,
                'text': ' '.join(w['text'] for w in line_words),
                'avg_confidence': sum(w['confidence'] for w in line_words) / len(line_words)
            })
        
        return sorted_lines
    
    def _enhance_text_formatting(self, structured_lines: List[Dict]) -> str:
        """Aprimora a formatação usando dados estruturados"""
        formatted_lines = []
        
        for i, line in enumerate(structured_lines):
            text = line['text'].strip()
            if not text:
                continue
            
            # Detectar cabeçalhos baseado em posição e tamanho
            if self._is_header_line(line, structured_lines):
                formatted_lines.append(f"# {text}")
            # Detectar subcabeçalhos
            elif self._is_subheader_line(line, structured_lines):
                formatted_lines.append(f"## {text}")
            # Detectar listas
            elif text.startswith(('•', '-', '*', '1.', '2.', '3.')):
                formatted_lines.append(f"- {text}")
            # Detectar parágrafos
            else:
                # Verificar se deve criar nova seção
                if i > 0 and self._should_create_new_section(line, structured_lines[i-1]):
                    formatted_lines.append("")  # Linha em branco para separar seções
                formatted_lines.append(text)
        
        return '\n'.join(formatted_lines)
    
    def _is_header_line(self, line: Dict, all_lines: List[Dict]) -> bool:
        """Detecta se uma linha é um cabeçalho principal"""
        text = line['text'].lower()
        
        # Palavras-chave de cabeçalho
        header_keywords = ['chapter', 'section', 'introduction', 'conclusion', 'abstract', 'summary']
        if any(keyword in text for keyword in header_keywords):
            return True
        
        # Verificar tamanho relativo das palavras (cabeçalhos costumam ter palavras maiores)
        word_sizes = [w['width'] for w in line['words'] if w['width'] > 0]
        if word_sizes:
            avg_word_size = sum(word_sizes) / len(word_sizes)
            # Cabeçalhos costumam ter palavras maiores
            if avg_word_size > 50:
                return True
        
        return False
    
    def _is_subheader_line(self, line: Dict, all_lines: List[Dict]) -> bool:
        """Detecta se uma linha é um subcabeçalho"""
        text = line['text'].lower()
        
        # Palavras-chave de subcabeçalho
        subheader_keywords = ['subsection', 'subchapter', 'part', 'topic']
        if any(keyword in text for keyword in subheader_keywords):
            return True
        
        return False
    
    def _should_create_new_section(self, current_line: Dict, previous_line: Dict) -> bool:
        """Determina se deve criar uma nova seção"""
        # Espaçamento vertical grande indica nova seção
        y_spacing = current_line['y_pos'] - previous_line['y_pos']
        if y_spacing > 50:  # Mais de 50px de espaçamento
            return True
        
        return False
    
    def _process_ocr_result_basic(self, ocr_text: str) -> str:
        """Processamento básico do resultado do OCR"""
        # Remover caracteres estranhos
        ocr_text = re.sub(r'[^\w\s\.,;:!?()\[\]{}"\'-]', '', ocr_text)
        
        # Normalizar espaços
        ocr_text = re.sub(r'\s+', ' ', ocr_text)
        
        # Corrigir quebras de linha
        lines = ocr_text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Juntar linhas muito curtas
                if len(line) < 10 and processed_lines:
                    processed_lines[-1] += ' ' + line
                else:
                    processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _combine_text_methods(self, normal_text: str, ocr_text: str, quality_analysis: Dict) -> str:
        """Combina texto normal com OCR de forma inteligente e otimizada"""
        if not ocr_text:
            return self._apply_final_cleaning(normal_text)
        
        self.log_info(f"Combinando textos: normal={len(normal_text)} chars, OCR={len(ocr_text)} chars")
        
        # Analisar problemas específicos do texto normal
        normal_problems = self._analyze_specific_problems(normal_text)
        ocr_quality = self._analyze_ocr_quality(ocr_text)
        
        self.log_info(f"Problemas no texto normal: repetições={normal_problems['max_word_repetition']}, "
                     f"linhas repetidas={normal_problems['repeated_lines']}")
        self.log_info(f"Qualidade do OCR: {ocr_quality['quality_score']:.1f}/100")
        
        # Verificar se há duplicações graves no texto normal
        if normal_problems['severe_repetitions'] or normal_problems['high_duplication']:
            self.log_info("Problemas graves detectados - aplicando limpeza agressiva e considerando OCR")
            
            # Se o OCR tem qualidade significativamente melhor, usar OCR
            if ocr_quality['quality_score'] > 70:
                self.log_info("Usando OCR como base devido à alta qualidade")
                combined_text = ocr_text
            else:
                # Aplicar limpeza agressiva no texto normal
                combined_text = self._apply_final_cleaning(normal_text, aggressive=True)
        else:
            self.log_info("Problemas leves - aplicando limpeza conservadora")
            # Usar texto normal com limpeza conservadora
            combined_text = self._apply_final_cleaning(normal_text, aggressive=False)
        
        # Aplicar limpeza final para remover duplicações
        final_text = self._remove_duplications(combined_text)
        
        return final_text
    
    def _smart_combine(self, normal_text: str, ocr_text: str) -> str:
        """Combina os dois textos de forma inteligente"""
        # Para páginas problemáticas, preferir OCR
        # Para o resto, manter texto normal
        
        combined_lines = []
        
        # Dividir em páginas (aproximação)
        normal_pages = normal_text.split('\n\n')
        ocr_pages = ocr_text.split('\n\n')
        
        for i, normal_page in enumerate(normal_pages):
            if i < len(ocr_pages) and self._is_page_problematic(normal_page):
                # Usar OCR para páginas problemáticas
                combined_lines.append(ocr_pages[i])
            else:
                # Manter texto normal
                combined_lines.append(normal_page)
        
        return '\n\n'.join(combined_lines)
    
    def _is_page_problematic(self, page_text: str) -> bool:
        """Verifica se uma página é problemática"""
        lines = page_text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        if len(non_empty_lines) < 3:
            return True
        
        # Verificar qualidade da página
        short_lines = len([l for l in non_empty_lines if len(l.strip()) < 10])
        if short_lines / len(non_empty_lines) > 0.5:
            return True
        
        return False

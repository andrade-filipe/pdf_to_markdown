"""Step de Análise Estatística Avançada para Estruturação de Conteúdo"""

import re
import math
from collections import Counter, defaultdict
from typing import Dict, Any, List, Tuple, Optional
from .base_step import BaseStep


class StatisticalAnalysisStep(BaseStep):
    """Step que usa análise estatística para estruturar e otimizar conteúdo"""
    
    def __init__(self):
        super().__init__("StatisticalAnalysis")
        self.title_patterns = self._load_title_patterns()
        self.section_keywords = self._load_section_keywords()
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo usando análise estatística"""
        self.log_info("Iniciando análise estatística")
        
        # Tentar diferentes campos de conteúdo
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            markdown_content = data.get('raw_text', '')
        if not markdown_content:
            markdown_content = data.get('text', '')
        
        if not markdown_content:
            self.log_warning("Nenhum conteúdo encontrado para análise")
            return data
        
        try:
            # Análise estatística do conteúdo
            structured_content = self._analyze_and_structure(markdown_content)
            
            if structured_content:
                data['markdown_content'] = structured_content
                data['statistical_analysis_stats'] = {
                    'original_lines': markdown_content.count('\n') + 1,
                    'final_lines': structured_content.count('\n') + 1,
                    'titles_detected': structured_content.count('#'),
                    'paragraphs_formed': structured_content.count('\n\n'),
                    'improvement_ratio': len(structured_content) / len(markdown_content) if markdown_content else 1.0
                }
                
                self.log_info(f"Análise estatística concluída")
                self.log_info(f"Títulos detectados: {data['statistical_analysis_stats']['titles_detected']}")
                self.log_info(f"Parágrafos formados: {data['statistical_analysis_stats']['paragraphs_formed']}")
            else:
                self.log_warning("Análise estatística não retornou conteúdo estruturado")
                
        except Exception as e:
            self.log_error(f"Erro na análise estatística: {e}")
        
        return data
    
    def _analyze_and_structure(self, content: str) -> Optional[str]:
        """Analisa e estrutura o conteúdo usando estatísticas"""
        
        # Dividir em linhas
        lines = content.split('\n')
        
        # Análise estatística das linhas
        line_stats = self._analyze_line_statistics(lines)
        
        # Detectar títulos baseado em estatísticas
        title_lines = self._detect_titles_statistically(lines, line_stats)
        
        # Agrupar parágrafos baseado em similaridade
        paragraphs = self._group_paragraphs_statistically(lines, line_stats)
        
        # Estruturar conteúdo
        structured_lines = self._structure_content(lines, title_lines, paragraphs)
        
        return '\n'.join(structured_lines)
    
    def _analyze_line_statistics(self, lines: List[str]) -> Dict[str, Any]:
        """Analisa estatísticas das linhas"""
        stats = {
            'lengths': [],
            'word_counts': [],
            'capitalization_ratios': [],
            'punctuation_counts': [],
            'digit_counts': [],
            'special_char_counts': [],
            'position_scores': []
        }
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Comprimento da linha
            stats['lengths'].append(len(line))
            
            # Contagem de palavras
            words = line.split()
            stats['word_counts'].append(len(words))
            
            # Razão de capitalização
            if line:
                caps = sum(1 for c in line if c.isupper())
                stats['capitalization_ratios'].append(caps / len(line))
            
            # Contagem de pontuação
            punct = sum(1 for c in line if c in '.,;:!?')
            stats['punctuation_counts'].append(punct)
            
            # Contagem de dígitos
            digits = sum(1 for c in line if c.isdigit())
            stats['digit_counts'].append(digits)
            
            # Contagem de caracteres especiais
            special = sum(1 for c in line if c in '()[]{}<>-_=+@#$%^&*')
            stats['special_char_counts'].append(special)
            
            # Score de posição (linhas no início têm mais chance de serem títulos)
            position_score = 1.0 - (i / len(lines))
            stats['position_scores'].append(position_score)
        
        # Calcular médias e desvios padrão
        stats_copy = stats.copy()
        for key in stats_copy:
            if stats_copy[key]:
                stats[f'{key}_mean'] = sum(stats_copy[key]) / len(stats_copy[key])
                stats[f'{key}_std'] = self._calculate_std(stats_copy[key])
        
        return stats
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calcula desvio padrão"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    def _detect_titles_statistically(self, lines: List[str], stats: Dict[str, Any]) -> List[int]:
        """Detecta títulos usando análise estatística"""
        title_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Calcular score de título
            title_score = self._calculate_title_score(line, i, stats)
            
            # Se score alto, é provavelmente um título
            if title_score > 0.7:
                title_lines.append(i)
        
        return title_lines
    
    def _calculate_title_score(self, line: str, line_index: int, stats: Dict[str, Any]) -> float:
        """Calcula score de probabilidade de ser título"""
        score = 0.0
        
        # 1. Padrões de regex
        for pattern in self.title_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                score += 0.3
                break
        
        # 2. Palavras-chave de seção
        line_lower = line.lower()
        for keyword in self.section_keywords:
            if keyword in line_lower:
                score += 0.4
                break
        
        # 3. Características estatísticas
        if len(line) < 100:  # Títulos são geralmente curtos
            score += 0.2
        
        if line.isupper() and len(line) < 80:  # Títulos em maiúsculas
            score += 0.3
        
        # 4. Posição no documento (usar stats se disponível)
        if 'position_scores' in stats and line_index < len(stats['position_scores']):
            position_score = stats['position_scores'][line_index]
            score += position_score * 0.1
        else:
            # Fallback simples
            score += 0.1
        
        # 5. Capitalização
        if line:
            caps_ratio = sum(1 for c in line if c.isupper()) / len(line)
            if caps_ratio > 0.5:
                score += 0.2
        
        # 6. Ausência de pontuação final
        if line and not line[-1] in '.!?':
            score += 0.1
        
        return min(score, 1.0)
    
    def _group_paragraphs_statistically(self, lines: List[str], stats: Dict[str, Any]) -> List[List[int]]:
        """Agrupa linhas em parágrafos usando análise estatística"""
        paragraphs = []
        current_paragraph = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                    current_paragraph = []
                continue
            
            # Verificar se deve começar novo parágrafo
            if self._should_start_new_paragraph(line, i, lines, stats):
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                    current_paragraph = []
            
            current_paragraph.append(i)
        
        if current_paragraph:
            paragraphs.append(current_paragraph)
        
        return paragraphs
    
    def _should_start_new_paragraph(self, line: str, line_index: int, all_lines: List[str], stats: Dict[str, Any]) -> bool:
        """Determina se deve começar novo parágrafo"""
        
        # Se é um título, sempre começa novo parágrafo
        if self._calculate_title_score(line, line_index, stats) > 0.7:
            return True
        
        # Se linha anterior estava vazia
        if line_index > 0 and not all_lines[line_index - 1].strip():
            return True
        
        # Se há mudança significativa no comprimento
        if line_index > 0:
            prev_line = all_lines[line_index - 1].strip()
            if prev_line:
                length_diff = abs(len(line) - len(prev_line))
                if length_diff > 50:  # Mudança significativa
                    return True
        
        # Se há mudança na capitalização
        if line_index > 0:
            prev_line = all_lines[line_index - 1].strip()
            if prev_line:
                prev_caps = sum(1 for c in prev_line if c.isupper()) / len(prev_line)
                curr_caps = sum(1 for c in line if c.isupper()) / len(line)
                if abs(curr_caps - prev_caps) > 0.3:
                    return True
        
        return False
    
    def _structure_content(self, lines: List[str], title_lines: List[int], paragraphs: List[List[int]]) -> List[str]:
        """Estrutura o conteúdo final"""
        structured_lines = []
        
        for paragraph in paragraphs:
            if not paragraph:
                continue
            
            # Verificar se parágrafo contém título
            has_title = any(i in title_lines for i in paragraph)
            
            if has_title:
                # Processar título
                for line_idx in paragraph:
                    line = lines[line_idx].strip()
                    if line_idx in title_lines:
                        # Formatar título
                        title_level = self._determine_title_level(line, line_idx, lines)
                        structured_lines.append(f"{'#' * title_level} {line}")
                        structured_lines.append("")
                    else:
                        # Conteúdo do parágrafo
                        if line:
                            structured_lines.append(line)
                
                structured_lines.append("")
            else:
                # Parágrafo normal
                paragraph_text = []
                for line_idx in paragraph:
                    line = lines[line_idx].strip()
                    if line:
                        paragraph_text.append(line)
                
                if paragraph_text:
                    structured_lines.append(" ".join(paragraph_text))
                    structured_lines.append("")
        
        return structured_lines
    
    def _determine_title_level(self, line: str, line_index: int, all_lines: List[str]) -> int:
        """Determina o nível do título (1, 2, 3)"""
        
        # Títulos principais (primeiros 20% do documento)
        if line_index < len(all_lines) * 0.2:
            return 1
        
        # Títulos de seção (palavras-chave específicas)
        line_lower = line.lower()
        main_sections = ['introduction', 'methods', 'results', 'discussion', 'conclusion', 
                        'introdução', 'métodos', 'resultados', 'discussão', 'conclusão']
        
        for section in main_sections:
            if section in line_lower:
                return 2
        
        # Títulos numerados
        if re.match(r'^\d+\.', line):
            return 2
        
        # Títulos em maiúsculas
        if line.isupper() and len(line) < 80:
            return 2
        
        # Outros títulos
        return 3
    
    def _load_title_patterns(self) -> List[str]:
        """Carrega padrões de regex para detecção de títulos"""
        return [
            r'^\d+\.\s+[A-Z]',  # 1. Título
            r'^[A-Z][A-Z\s]+$',  # TÍTULO EM MAIÚSCULAS
            r'^[A-Z][a-z\s]+$',  # Título Capitalizado
            r'^Abstract$', r'^Introduction$', r'^Conclusion$',
            r'^Resumo$', r'^Introdução$', r'^Conclusão$',
            r'^References$', r'^Bibliography$',
            r'^Referências$', r'^Bibliografia$'
        ]
    
    def _load_section_keywords(self) -> List[str]:
        """Carrega palavras-chave de seções"""
        return [
            'abstract', 'introduction', 'methods', 'materials', 'results', 
            'discussion', 'conclusion', 'references', 'bibliography', 'acknowledgments',
            'appendix', 'figure', 'table', 'chapter', 'section',
            'resumo', 'introdução', 'métodos', 'materiais', 'resultados',
            'discussão', 'conclusão', 'referências', 'bibliografia', 'agradecimentos',
            'apêndice', 'figura', 'tabela', 'capítulo', 'seção'
        ]

#!/usr/bin/env python3
"""
Passo de Spell Checking e Correção Ortográfica
"""

import re
from difflib import SequenceMatcher
from .base_step import BaseStep

class SpellCheckingStep(BaseStep):
    def __init__(self):
        super().__init__("SpellChecking")
        
        # Dicionário de palavras comuns em inglês e português
        self.common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'o', 'a', 'os', 'as', 'um', 'uma', 'e', 'ou', 'mas', 'em', 'no', 'na', 'nos', 'nas',
            'para', 'por', 'com', 'sem', 'sob', 'sobre', 'entre', 'contra', 'desde', 'até',
            'é', 'são', 'era', 'eram', 'foi', 'foram', 'ser', 'estar', 'ter', 'haver',
            'fazer', 'dizer', 'ver', 'dar', 'vir', 'saber', 'poder', 'dever', 'querer',
            'science', 'research', 'study', 'analysis', 'method', 'result', 'conclusion',
            'ciência', 'pesquisa', 'estudo', 'análise', 'método', 'resultado', 'conclusão'
        }
        
        # Palavras científicas comuns
        self.scientific_words = {
            # Inglês
            'evolution', 'creation', 'geology', 'biology', 'chemistry', 'physics',
            'fossil', 'sediment', 'strata', 'formation', 'analysis', 'methodology',
            'hypothesis', 'theory', 'experiment', 'observation', 'conclusion',
            'research', 'study', 'investigation', 'examination', 'evaluation',
            'assessment', 'measurement', 'calculation', 'computation', 'simulation',
            'modeling', 'prediction', 'forecast', 'estimation', 'approximation',
            
            # Português
            'evolução', 'criação', 'geologia', 'biologia', 'química', 'física',
            'fóssil', 'sedimento', 'estrato', 'formação', 'análise', 'metodologia',
            'hipótese', 'teoria', 'experimento', 'observação', 'conclusão',
            'pesquisa', 'estudo', 'investigação', 'exame', 'avaliação',
            'medição', 'cálculo', 'computação', 'simulação', 'modelagem',
            'predição', 'previsão', 'estimativa', 'aproximação'
        }
        
        self.common_words.update(self.scientific_words)
    
    def process(self, context):
        """Aplica correção ortográfica ao texto"""
        self.log_info("Iniciando correção ortográfica...")
        
        if 'markdown_content' not in context:
            self.log_info("Nenhum conteúdo Markdown encontrado para correção")
            return context
        
        original_content = context['markdown_content']
        corrected_content, corrections = self.correct_spelling(original_content)
        
        # Salvar estatísticas de correção
        context['spell_corrections'] = {
            'total_corrections': corrections['corrected_words'],
            'corrections_made': corrections['corrections']
        }
        
        # Atualizar conteúdo
        context['markdown_content'] = corrected_content
        
        self.log_info(f"Correção ortográfica concluída: {corrections['corrected_words']} palavras corrigidas")
        
        return context
    
    def correct_spelling(self, text):
        """Corrige erros ortográficos no texto"""
        corrections = {
            'corrected_words': 0,
            'corrections': []
        }
        
        # Dividir em palavras preservando a estrutura
        lines = text.split('\n')
        corrected_lines = []
        
        for line in lines:
            # Preservar títulos e formatação
            if line.startswith('#') or line.startswith('!') or line.startswith('|'):
                corrected_lines.append(line)
                continue
            
            # Corrigir palavras na linha
            words = re.findall(r'\b\w+\b', line)
            corrected_words = []
            
            for word in words:
                original_word = word
                corrected_word = word
                
                # Verificar se precisa de correção
                if len(word) > 2 and word.lower() not in self.common_words:
                    best_match = self.find_best_match(word)
                    if best_match:
                        corrected_word = best_match
                        corrections['corrected_words'] += 1
                        corrections['corrections'].append({
                            'original': original_word,
                            'corrected': corrected_word
                        })
                
                corrected_words.append(corrected_word)
            
            # Reconstruir a linha
            corrected_line = line
            for i, word in enumerate(words):
                corrected_line = corrected_line.replace(word, corrected_words[i], 1)
            
            corrected_lines.append(corrected_line)
        
        corrected_text = '\n'.join(corrected_lines)
        return corrected_text, corrections
    
    def find_best_match(self, word):
        """Encontra a melhor correspondência para uma palavra"""
        word_lower = word.lower()
        best_match = None
        best_similarity = 0
        
        # Verificar palavras comuns
        for common_word in self.common_words:
            if len(common_word) > 3:
                similarity = SequenceMatcher(None, word_lower, common_word).ratio()
                if similarity > best_similarity and similarity > 0.85:  # Mais conservador
                    best_similarity = similarity
                    best_match = common_word
        
        return best_match

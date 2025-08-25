"""Passo avançado de conversão Markdown com múltiplos métodos"""

import re
from typing import Dict, Any, List, Tuple
from .base_step import BaseStep


class AdvancedMarkdownConversionStep(BaseStep):
    """Passo responsável por conversão Markdown avançada com múltiplos métodos"""
    
    def __init__(self):
        super().__init__("AdvancedMarkdownConversion")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo com múltiplos métodos e escolhe o melhor"""
        # Pular processamento se for relatório Quantum (já tem etapa específica)
        if data.get('document_type') == 'quantum_report':
            return data
            
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            return data
        
        # Verificar se o conteúdo é muito grande (> 1MB)
        content_size = len(markdown_content.encode('utf-8'))
        if content_size > 1024 * 1024:  # 1MB
            self.log_info(f"Conteúdo grande detectado ({content_size / 1024 / 1024:.1f}MB), aplicando otimizações")
            # Para PDFs muito grandes, usar apenas métodos mais eficientes
            methods = {
                'compact': self._method_compact(markdown_content),
                'clean': self._method_clean(markdown_content),
                'minimal': self._method_minimal(markdown_content)
            }
        else:
            # Para PDFs menores, usar todos os métodos
            methods = {
                'current': self._method_current(markdown_content),
                'intelligent': self._method_intelligent(markdown_content),
                'structured': self._method_structured(markdown_content),
                'compact': self._method_compact(markdown_content),
                'clean': self._method_clean(markdown_content),
                'academic': self._method_academic(markdown_content),
                'minimal': self._method_minimal(markdown_content)
            }
        
        # Avaliar e escolher o melhor método
        best_method, best_content = self._evaluate_and_choose_best(methods, data)
        
        print(f"🎯 Método escolhido: {best_method}")
        
        # Atualizar o conteúdo
        data['markdown_content'] = best_content
        data['conversion_method'] = best_method
        data['all_methods'] = methods
        
        return data
    
    def _method_current(self, content: str) -> str:
        """Método atual (conservador)"""
        return content
    
    def _method_intelligent(self, content: str) -> str:
        """Método inteligente - agrupa por contexto"""
        lines = content.split('\n')
        formatted_lines = []
        current_section = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_section:
                    formatted_lines.extend(self._format_section(current_section))
                    current_section = []
                continue
            
            # Se é um título, processar seção anterior e começar nova
            if line.startswith('#'):
                if current_section:
                    formatted_lines.extend(self._format_section(current_section))
                    current_section = []
                formatted_lines.append(line)
            else:
                current_section.append(line)
        
        # Processar última seção
        if current_section:
            formatted_lines.extend(self._format_section(current_section))
        
        return '\n'.join(formatted_lines)
    
    def _method_structured(self, content: str) -> str:
        """Método estruturado - foca em seções acadêmicas"""
        lines = content.split('\n')
        formatted_lines = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_paragraph:
                    formatted_lines.append(self._join_paragraph(current_paragraph))
                    current_paragraph = []
                continue
            
            # Se é um título, processar parágrafo anterior
            if line.startswith('#'):
                if current_paragraph:
                    formatted_lines.append(self._join_paragraph(current_paragraph))
                    current_paragraph = []
                formatted_lines.append(line)
            else:
                current_paragraph.append(line)
        
        # Processar último parágrafo
        if current_paragraph:
            formatted_lines.append(self._join_paragraph(current_paragraph))
        
        return '\n\n'.join(formatted_lines)
    
    def _method_compact(self, content: str) -> str:
        """Método compacto - remove quebras desnecessárias"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Se é um título, consolidar títulos consecutivos
            if line.startswith('#'):
                # Se o último item também é um título, juntar
                if formatted_lines and formatted_lines[-1].startswith('#'):
                    # Juntar títulos consecutivos
                    last_title = formatted_lines[-1]
                    clean_last = re.sub(r'^#+\s*', '', last_title)
                    clean_current = re.sub(r'^#+\s*', '', line)
                    combined_title = f"# {clean_last} {clean_current}".strip()
                    formatted_lines[-1] = combined_title
                else:
                    formatted_lines.append(line)
            else:
                # Juntar linhas que fazem parte do mesmo contexto
                if formatted_lines and not formatted_lines[-1].startswith('#'):
                    # Se a linha anterior não termina com pontuação, juntar
                    if not re.search(r'[.!?]$', formatted_lines[-1]):
                        formatted_lines[-1] += ' ' + line
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
        
        return '\n\n'.join(formatted_lines)
    
    def _method_clean(self, content: str) -> str:
        """Método clean - remove repetições e texto desnecessário"""
        # Primeiro, verificar se há texto corrompido
        if self._detect_corrupted_text(content):
            content = self._clean_corrupted_text(content)
        
        lines = content.split('\n')
        formatted_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Se é um título, processar
            if line.startswith('#'):
                # Remover duplicatas de títulos
                clean_title = re.sub(r'^#+\s*', '', line)
                if clean_title not in seen_lines:
                    formatted_lines.append(line)
                    seen_lines.add(clean_title)
            else:
                # Para texto normal, remover linhas muito repetitivas
                # Normalizar a linha para comparação
                normalized = re.sub(r'\s+', ' ', line).lower()
                # Remover caracteres especiais para melhor comparação
                normalized = re.sub(r'[^\w\s]', '', normalized)
                
                if len(normalized) > 10 and normalized not in seen_lines:
                    formatted_lines.append(line)
                    seen_lines.add(normalized)
        
        # Juntar linhas que fazem parte do mesmo contexto
        result_lines = []
        current_paragraph = []
        
        for line in formatted_lines:
            if line.startswith('#'):
                # Se temos um parágrafo acumulado, juntá-lo
                if current_paragraph:
                    result_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                result_lines.append(line)
            else:
                current_paragraph.append(line)
        
        # Processar último parágrafo
        if current_paragraph:
            result_lines.append(' '.join(current_paragraph))
        
        return '\n\n'.join(result_lines)
    
    def _method_academic(self, content: str) -> str:
        """Método acadêmico - otimizado para artigos científicos"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar seções acadêmicas comuns
            if re.match(r'^(abstract|introduction|conclusion|references|bibliography|methods?|results?|discussion|background|materials?|acknowledgments?|appendix)', line.lower()):
                # Converter para título de seção
                formatted_lines.append(f"## {line.title()}")
            elif line.startswith('#'):
                # Manter títulos existentes
                formatted_lines.append(line)
            else:
                # Parágrafo normal
                formatted_lines.append(line)
        
        # Juntar parágrafos consecutivos
        result_lines = []
        current_paragraph = []
        
        for line in formatted_lines:
            if line.startswith('#'):
                # Se temos um parágrafo acumulado, juntá-lo
                if current_paragraph:
                    result_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                result_lines.append(line)
            else:
                current_paragraph.append(line)
        
        # Processar último parágrafo
        if current_paragraph:
            result_lines.append(' '.join(current_paragraph))
        
        return '\n\n'.join(result_lines)
    
    def _method_minimal(self, content: str) -> str:
        """Método minimal - foco em simplicidade e legibilidade"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remover linhas muito curtas ou repetitivas
            if len(line) < 10:
                continue
            
            # Detectar títulos simples
            if re.match(r'^[A-Z][A-Z\s]+$', line) and len(line) < 50:
                # Título em maiúsculas
                formatted_lines.append(f"## {line.title()}")
            elif line.startswith('#'):
                # Manter títulos existentes
                formatted_lines.append(line)
            else:
                # Parágrafo normal
                formatted_lines.append(line)
        
        # Juntar parágrafos consecutivos de forma mais agressiva
        result_lines = []
        current_paragraph = []
        
        for line in formatted_lines:
            if line.startswith('#'):
                # Se temos um parágrafo acumulado, juntá-lo
                if current_paragraph:
                    result_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                result_lines.append(line)
            else:
                # Só quebrar se a linha terminar com pontuação forte
                if line.endswith(('.', '!', '?')):
                    current_paragraph.append(line)
                    result_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                else:
                    current_paragraph.append(line)
        
        # Processar último parágrafo
        if current_paragraph:
            result_lines.append(' '.join(current_paragraph))
        
        return '\n\n'.join(result_lines)
    
    def _format_section(self, section_lines: List[str]) -> List[str]:
        """Formata uma seção de texto"""
        if not section_lines:
            return []
        
        # Juntar linhas que fazem parte do mesmo contexto
        joined_text = ' '.join(section_lines)
        
        # Limpar espaços extras
        joined_text = re.sub(r'\s+', ' ', joined_text).strip()
        
        # Dividir em parágrafos baseado em pontuação
        paragraphs = re.split(r'(?<=[.!?])\s+', joined_text)
        
        # Filtrar parágrafos vazios e muito curtos
        valid_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if len(para) > 10:  # Parágrafos com pelo menos 10 caracteres
                valid_paragraphs.append(para)
        
        return valid_paragraphs
    
    def _join_paragraph(self, lines: List[str]) -> str:
        """Junta linhas em um parágrafo bem formatado"""
        if not lines:
            return ""
        
        # Juntar linhas
        text = ' '.join(lines)
        
        # Limpar espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remover quebras de linha desnecessárias
        text = re.sub(r'\s*\n\s*', ' ', text)
        
        return text
    
    def _evaluate_and_choose_best(self, methods: Dict[str, str], data: Dict[str, Any]) -> Tuple[str, str]:
        """Avalia e escolhe o melhor método"""
        scores = {}
        
        for method_name, content in methods.items():
            score = self._calculate_quality_score(content)
            
            # Bônus especial para o método 'clean' quando há muitas repetições
            if method_name == 'clean':
                repetition_count = self._count_repetitions(content)
                print(f"🔍 Repetições detectadas em 'clean': {repetition_count}")
                if repetition_count > 10:  # Se há muitas repetições
                    score += 10  # Bônus maior de 10 pontos
                    print(f"🎯 Bônus aplicado: +10 pontos")
                elif repetition_count > 5:  # Se há algumas repetições
                    score += 5  # Bônus de 5 pontos
                    print(f"🎯 Bônus aplicado: +5 pontos")
            
            scores[method_name] = score
            print(f"📊 {method_name}: {score:.2f}")
        
        # Escolher o método com maior pontuação
        best_method = max(scores, key=scores.get)
        
        # Salvar o método escolhido nos dados
        data['method_chosen'] = best_method
        
        return best_method, methods[best_method]
    
    def _count_repetitions(self, content: str) -> int:
        """Conta o número de repetições no conteúdo"""
        lines = content.split('\n')
        seen_lines = set()
        repeated_lines = 0
        
        for line in lines:
            line = line.strip()
            if line:
                # Normalizar linha para comparação
                normalized = re.sub(r'\s+', ' ', line).lower()
                # Remover caracteres especiais para melhor comparação
                normalized = re.sub(r'[^\w\s]', '', normalized)
                
                if normalized in seen_lines:
                    repeated_lines += 1
                else:
                    seen_lines.add(normalized)
        
        return repeated_lines
    
    def _detect_corrupted_text(self, content: str) -> bool:
        """Detecta se o texto contém caracteres corrompidos"""
        # Caracteres que indicam texto corrompido
        corrupted_patterns = [
            r'[^\x00-\x7F]',  # Caracteres não-ASCII
            r'[\uFFFD]',  # Caracteres de substituição Unicode
            r'[^\w\s\.,!?;:()\[\]{}"\'-]',  # Caracteres estranhos
        ]
        
        for pattern in corrupted_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _clean_corrupted_text(self, content: str) -> str:
        """Limpa texto corrompido"""
        # Remover caracteres problemáticos
        content = re.sub(r'[^\x00-\x7F]', '', content)  # Manter apenas ASCII
        content = re.sub(r'[\uFFFD]', '', content)  # Remover caracteres de substituição Unicode
        
        # Limpar espaços extras
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calcula a pontuação de qualidade do conteúdo"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        score = 0.0
        
        # Pontuação baseada no número de linhas (menos é melhor, mas menos penalização)
        line_count = len([l for l in lines if l.strip()])
        score += max(0, 15 - line_count / 200)  # Ajustado: menos penalização por linhas
        
        # Pontuação baseada na presença de títulos (mais valor)
        title_count = len([l for l in lines if l.startswith('#')])
        score += min(15, title_count * 2)  # Aumentado: mais valor para títulos
        
        # Pontuação baseada na legibilidade (parágrafos bem formados)
        paragraphs = content.split('\n\n')
        well_formed_paragraphs = 0
        for para in paragraphs:
            para = para.strip()
            if len(para) > 30 and not para.startswith('#'):  # Reduzido: parágrafos menores também contam
                well_formed_paragraphs += 1
        
        score += min(20, well_formed_paragraphs * 2)  # Aumentado: mais valor para parágrafos
        
        # Pontuação baseada na ausência de quebras desnecessárias
        unnecessary_breaks = len(re.findall(r'\n\s*\n\s*\n', content))
        score += max(0, 10 - unnecessary_breaks)  # Aumentado: mais valor para evitar quebras
        
        # Pontuação baseada na estrutura acadêmica (mais palavras-chave)
        academic_keywords = [
            'abstract', 'introduction', 'conclusion', 'references', 'bibliography',
            'analysis', 'study', 'research', 'method', 'result', 'data', 'evidence',
            'figure', 'table', 'discussion', 'materials', 'methods', 'background'
        ]
        keyword_count = sum(1 for keyword in academic_keywords if keyword.lower() in content.lower())
        score += keyword_count * 1.5  # Aumentado: mais valor para palavras-chave acadêmicas
        
        # Pontuação baseada na ausência de repetições (penalização mais severa)
        seen_lines = set()
        repeated_lines = 0
        for line in lines:
            line = line.strip()
            if line:
                normalized = re.sub(r'\s+', ' ', line).lower()
                if normalized in seen_lines:
                    repeated_lines += 1
                else:
                    seen_lines.add(normalized)
        
        # Penalizar repetições mais severamente
        repetition_penalty = min(15, repeated_lines * 2)  # Aumentado: penalização mais severa
        score -= repetition_penalty
        
        # Bônus para conteúdo bem estruturado
        if title_count > 5:  # Muitos títulos indicam boa estrutura
            score += 10
        if well_formed_paragraphs > 10:  # Muitos parágrafos bem formados
            score += 10
        
        return score

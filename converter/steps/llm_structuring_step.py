"""Step de Estruturação usando Large Language Models"""

import time
import json
from typing import Dict, Any, Optional
from .base_step import BaseStep


class LLMStructuringStep(BaseStep):
    """Step que usa LLMs para reestruturar e otimizar conteúdo Markdown"""
    
    def __init__(self):
        super().__init__("LLMStructuring")
        self.llm_providers = {
            'openai': self._call_openai,
            'anthropic': self._call_anthropic,
            'local': self._call_local_llm,
            'mock': self._call_mock_llm  # Para testes
        }
        self.current_provider = 'mock'  # Padrão para testes
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo usando LLM para estruturação"""
        self.log_info("Iniciando estruturação com LLM")
        
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            self.log_warning("Nenhum conteúdo Markdown encontrado")
            return data
        
        start_time = time.time()
        
        try:
            # Estruturar conteúdo usando LLM
            structured_content = self._structure_with_llm(markdown_content)
            
            if structured_content:
                data['markdown_content'] = structured_content
                data['llm_structuring_stats'] = {
                    'processing_time': time.time() - start_time,
                    'provider': self.current_provider,
                    'original_length': len(markdown_content),
                    'final_length': len(structured_content),
                    'improvement_ratio': len(structured_content) / len(markdown_content) if markdown_content else 1.0
                }
                
                self.log_info(f"Estruturação LLM concluída em {time.time() - start_time:.2f}s")
                self.log_info(f"Provedor: {self.current_provider}")
                self.log_info(f"Melhoria: {data['llm_structuring_stats']['improvement_ratio']:.2f}x")
            else:
                self.log_warning("LLM não retornou conteúdo estruturado")
                
        except Exception as e:
            self.log_error(f"Erro na estruturação LLM: {e}")
        
        return data
    
    def _structure_with_llm(self, content: str) -> Optional[str]:
        """Estrutura conteúdo usando LLM"""
        
        # Prompt otimizado para conversão PDF-Markdown
        prompt = self._create_structuring_prompt(content)
        
        # Chamar LLM
        provider_func = self.llm_providers.get(self.current_provider)
        if not provider_func:
            self.log_error(f"Provedor LLM não encontrado: {self.current_provider}")
            return None
        
        try:
            response = provider_func(prompt)
            return self._parse_llm_response(response)
        except Exception as e:
            self.log_error(f"Erro ao chamar LLM: {e}")
            return None
    
    def _create_structuring_prompt(self, content: str) -> str:
        """Cria prompt otimizado para estruturação"""
        
        # Limitar tamanho do conteúdo para evitar tokens excessivos
        max_chars = 8000  # Aproximadamente 2000 tokens
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Conteúdo truncado...]"
        
        prompt = f"""
Você é um especialista em conversão de PDF para Markdown. Sua tarefa é reestruturar e otimizar o seguinte conteúdo extraído de um PDF, convertendo-o para Markdown bem formatado.

REGRAS IMPORTANTES:
1. Identifique e marque títulos usando #, ##, ### baseado na hierarquia
2. Agrupe parágrafos relacionados em blocos coesos
3. Formate listas corretamente (usando - ou 1. 2. 3.)
4. Preserve a estrutura hierárquica do documento
5. Remova linhas vazias desnecessárias
6. Mantenha apenas o conteúdo relevante
7. Corrija formatação quebrada ou mal estruturada
8. Preserve citações e referências
9. Mantenha tabelas se existirem
10. Use formatação Markdown apropriada (negrito, itálico, etc.)

CONTEÚDO PARA ESTRUTURAR:
{content}

Retorne APENAS o Markdown estruturado, sem explicações adicionais.
"""
        return prompt
    
    def _parse_llm_response(self, response: str) -> Optional[str]:
        """Parse a resposta do LLM"""
        if not response:
            return None
        
        # Limpar resposta
        response = response.strip()
        
        # Remover possíveis marcadores de código
        if response.startswith('```markdown'):
            response = response[11:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        
        return response.strip()
    
    def _call_openai(self, prompt: str) -> str:
        """Chama OpenAI GPT-4"""
        # Implementação real seria:
        # import openai
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=4000,
        #     temperature=0.3
        # )
        # return response.choices[0].message.content
        
        # Mock para demonstração
        return self._mock_llm_response(prompt)
    
    def _call_anthropic(self, prompt: str) -> str:
        """Chama Anthropic Claude"""
        # Implementação real seria:
        # import anthropic
        # client = anthropic.Anthropic()
        # response = client.messages.create(
        #     model="claude-3-sonnet-20240229",
        #     max_tokens=4000,
        #     temperature=0.3,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.content[0].text
        
        # Mock para demonstração
        return self._mock_llm_response(prompt)
    
    def _call_local_llm(self, prompt: str) -> str:
        """Chama LLM local (Ollama, etc.)"""
        # Implementação real seria:
        # import requests
        # response = requests.post("http://localhost:11434/api/generate", json={
        #     "model": "llama2",
        #     "prompt": prompt,
        #     "stream": False
        # })
        # return response.json()["response"]
        
        # Mock para demonstração
        return self._mock_llm_response(prompt)
    
    def _call_mock_llm(self, prompt: str) -> str:
        """Mock LLM para testes"""
        return self._mock_llm_response(prompt)
    
    def _mock_llm_response(self, prompt: str) -> str:
        """Gera resposta mock baseada no prompt"""
        # Simular processamento LLM
        time.sleep(0.1)  # Simular latência
        
        # Extrair conteúdo do prompt
        if "CONTEÚDO PARA ESTRUTURAR:" in prompt:
            content = prompt.split("CONTEÚDO PARA ESTRUTURAR:")[1].strip()
        else:
            content = prompt
        
        # Aplicar algumas melhorias básicas
        lines = content.split('\n')
        improved_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detectar títulos
            if self._is_likely_title(line):
                if line.isupper() and len(line) < 100:
                    improved_lines.append(f"# {line.title()}")
                elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    improved_lines.append(f"## {line[3:].strip()}")
                elif len(line) < 80 and line[0].isupper():
                    improved_lines.append(f"### {line}")
                else:
                    improved_lines.append(line)
            else:
                improved_lines.append(line)
        
        # Agrupar linhas em parágrafos
        result = []
        current_paragraph = []
        
        for line in improved_lines:
            if line.startswith('#'):
                if current_paragraph:
                    result.append(' '.join(current_paragraph))
                    result.append('')
                    current_paragraph = []
                result.append(line)
                result.append('')
            else:
                current_paragraph.append(line)
        
        if current_paragraph:
            result.append(' '.join(current_paragraph))
        
        return '\n'.join(result)
    
    def _is_likely_title(self, line: str) -> bool:
        """Detecta se uma linha provavelmente é um título"""
        # Linhas muito curtas
        if len(line) < 30:
            return True
        
        # Linhas em maiúsculas
        if line.isupper() and len(line) < 100:
            return True
        
        # Linhas que começam com números
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            return True
        
        # Palavras-chave de títulos
        title_keywords = [
            'abstract', 'introduction', 'conclusion', 'references', 'bibliography',
            'methods', 'results', 'discussion', 'acknowledgments', 'appendix',
            'resumo', 'introdução', 'conclusão', 'referências', 'bibliografia',
            'métodos', 'resultados', 'discussão', 'agradecimentos', 'apêndice'
        ]
        
        line_lower = line.lower()
        for keyword in title_keywords:
            if keyword in line_lower:
                return True
        
        return False
    
    def set_provider(self, provider: str):
        """Define o provedor LLM a ser usado"""
        if provider in self.llm_providers:
            self.current_provider = provider
            self.log_info(f"Provedor LLM alterado para: {provider}")
        else:
            self.log_error(f"Provedor LLM inválido: {provider}")
    
    def get_available_providers(self) -> list:
        """Retorna lista de provedores disponíveis"""
        return list(self.llm_providers.keys())

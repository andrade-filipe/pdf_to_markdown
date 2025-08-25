# Guia do Desenvolvedor - Conversor PDF para Markdown

## Índice

1. [Introdução](#introdução)
2. [Configuração do Ambiente](#configuração-do-ambiente)
3. [Estrutura do Código](#estrutura-do-código)
4. [Padrões de Código](#padrões-de-código)
5. [Como Contribuir](#como-contribuir)
6. [Testes](#testes)
7. [Debugging](#debugging)
8. [Extensões](#extensões)
9. [Performance](#performance)
10. [Troubleshooting](#troubleshooting)

## Introdução

Este guia é destinado a desenvolvedores que desejam contribuir para o projeto ou entender como o código funciona internamente. O projeto utiliza uma arquitetura modular baseada no padrão Pipeline, com foco em qualidade, testabilidade e extensibilidade.

## Configuração do Ambiente

### Pré-requisitos

- Python 3.8+
- pip
- Git

### Setup Inicial

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd pdf_to_markdown

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Verificar instalação
python3 -m pytest tests/ -v
```

### Dependências de Desenvolvimento

```bash
# Para desenvolvimento adicional
pip install black flake8 mypy pytest-cov
```

## Estrutura do Código

### Visão Geral da Arquitetura

```
converter/
├── __init__.py                    # Pacote principal
├── converter.py                   # Funções básicas
├── pipeline.py                    # Pipeline principal
└── steps/                         # Passos do pipeline
    ├── __init__.py
    ├── base_step.py               # Classe base abstrata
    ├── text_extraction_step.py    # Extração de texto
    ├── table_extraction_step.py   # Extração de tabelas
    ├── cleanup_step.py            # Limpeza de texto
    ├── image_extraction_step.py   # Extração de imagens
    ├── markdown_conversion_step.py # Conversão básica
    └── advanced_markdown_conversion_step.py # Conversão avançada
```

### Fluxo de Dados

```python
# 1. Inicialização
data = {'pdf_path': 'arquivo.pdf'}

# 2. TextExtractionStep
data = {
    'pdf_path': 'arquivo.pdf',
    'text_blocks': [...],
    'font_info': [...],
    'raw_text': '...',
    'total_pages': 10
}

# 3. TableExtractionStep
data['tables'] = [...]

# 4. CleanupStep
data['cleaned_text'] = '...'

# 5. ImageExtractionStep
data['images'] = [...]

# 6. MarkdownConversionStep
data['markdown_content'] = '...'

# 7. AdvancedMarkdownConversionStep
data['markdown_content'] = '...'  # Versão final otimizada
data['method_chosen'] = 'academic'
```

## Padrões de Código

### 1. PEP 8 Compliance

```python
# ✅ Correto
def extract_text_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """Extrai texto de um arquivo PDF.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        
    Returns:
        Dicionário com dados extraídos
    """
    pass

# ❌ Incorreto
def extractTextFromPDF(pdfPath):
    pass
```

### 2. Type Hints

```python
from typing import Dict, List, Any, Optional, Tuple

def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Processa dados com type hints."""
    pass

def extract_tables(pdf_path: str) -> List[List[str]]:
    """Extrai tabelas retornando lista de listas."""
    pass
```

### 3. Docstrings

```python
def calculate_quality_score(content: str) -> float:
    """Calcula pontuação de qualidade do conteúdo Markdown.
    
    Args:
        content: Conteúdo Markdown a ser avaliado
        
    Returns:
        Pontuação de qualidade (0.0 a 100.0)
        
    Raises:
        ValueError: Se o conteúdo estiver vazio
    """
    if not content:
        raise ValueError("Conteúdo não pode estar vazio")
    
    # Lógica de cálculo
    return score
```

### 4. Error Handling

```python
def safe_extract_text(pdf_path: str) -> str:
    """Extrai texto com tratamento de erros robusto."""
    try:
        with fitz.open(pdf_path) as doc:
            return doc.get_text()
    except fitz.FileDataError:
        print(f"⚠️  PDF corrompido: {pdf_path}")
        return ""
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return ""
```

## Como Contribuir

### 1. Fork e Clone

```bash
# 1. Fork no GitHub
# 2. Clone seu fork
git clone https://github.com/seu-usuario/pdf_to_markdown.git
cd pdf_to_markdown

# 3. Adicionar upstream
git remote add upstream https://github.com/original/pdf_to_markdown.git
```

### 2. Criar Branch

```bash
# Criar branch para feature
git checkout -b feature/nova-funcionalidade

# Ou para bugfix
git checkout -b fix/correcao-bug
```

### 3. Desenvolvimento

```bash
# 1. Fazer alterações
# 2. Executar testes
python3 -m pytest tests/ -v

# 3. Verificar qualidade do código
black converter/ tests/
flake8 converter/ tests/
mypy converter/

# 4. Commit
git add .
git commit -m "feat: adiciona nova funcionalidade X"
```

### 4. Pull Request

```bash
# 1. Push para seu fork
git push origin feature/nova-funcionalidade

# 2. Criar PR no GitHub
# 3. Aguardar review
```

### 5. Convenções de Commit

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: tarefas de manutenção
```

## Testes

### Estrutura de Testes

```python
# tests/test_converter.py
import pytest
from converter.converter import converter_texto, converter_tabela

class TestPDFToMarkdownConverter:
    def setup_method(self):
        """Setup antes de cada teste."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        shutil.rmtree(self.temp_dir)
    
    def test_converte_texto_simples(self):
        """Testa conversão de texto simples."""
        texto = "Este é um parágrafo simples."
        resultado = converter_texto(texto)
        assert resultado == texto
    
    def test_converte_tabela_valida(self):
        """Testa conversão de tabela válida."""
        tabela = [["A", "B"], ["1", "2"]]
        resultado = converter_tabela(tabela)
        assert "| A | B |" in resultado
        assert "| 1 | 2 |" in resultado
```

### Executando Testes

```bash
# Todos os testes
python3 -m pytest tests/ -v

# Teste específico
python3 -m pytest tests/test_converter.py::test_converte_texto_simples -v

# Com cobertura
python3 -m pytest tests/ --cov=converter --cov-report=html

# Testes de integração
python3 -m pytest tests/test_converter.py::test_pipeline_conversao_completa -v
```

### Testes de Performance

```python
import time
import pytest

def test_performance_large_pdf():
    """Testa performance com PDF grande."""
    start_time = time.time()
    
    # Executar conversão
    pipeline = ConversionPipeline()
    result = pipeline.convert("large_file.pdf")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Verificar que não demorou mais de 60 segundos
    assert duration < 60
    assert result.exists()
```

## Debugging

### Logging

```python
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Iniciando função")
    logger.info("Processando dados")
    logger.warning("Aviso importante")
    logger.error("Erro encontrado")
```

### Debug com pdb

```python
import pdb

def complex_function():
    # ... código ...
    pdb.set_trace()  # Breakpoint
    # ... mais código ...
```

### Debug com print

```python
def debug_with_print():
    print(f"🔍 DEBUG: Valor da variável: {variavel}")
    print(f"📊 DEBUG: Tamanho da lista: {len(lista)}")
```

### Modo Verbose

```python
# Usar --verbose para debug
python3 main.py arquivo.pdf --verbose
```

## Extensões

### Adicionando Novo Passo

```python
# converter/steps/custom_step.py
from .base_step import BaseStep
from typing import Any

class CustomStep(BaseStep):
    def __init__(self):
        super().__init__("CustomStep")
    
    def process(self, data: Any) -> Any:
        """Processa dados personalizados."""
        # Sua lógica aqui
        processed_data = self._custom_processing(data)
        data['custom_result'] = processed_data
        return data
    
    def _custom_processing(self, data: Any) -> Any:
        """Lógica personalizada de processamento."""
        # Implementar lógica
        return processed_data
```

### Adicionando ao Pipeline

```python
# converter/pipeline.py
from .steps.custom_step import CustomStep

class ConversionPipeline:
    def __init__(self, output_dir: str = "."):
        # ... código existente ...
        self.steps = [
            TextExtractionStep(),
            TableExtractionStep(),
            CleanupStep(),
            ImageExtractionStep(),
            MarkdownConversionStep(),
            CustomStep(),  # Novo passo
            AdvancedMarkdownConversionStep()
        ]
```

### Adicionando Novo Método de Conversão

```python
# converter/steps/advanced_markdown_conversion_step.py
def _method_custom(self, content: str) -> str:
    """Método personalizado de conversão."""
    # Implementar lógica personalizada
    processed_content = self._custom_logic(content)
    return processed_content

def _custom_logic(self, content: str) -> str:
    """Lógica personalizada de processamento."""
    # Sua implementação
    return processed_content
```

### Adicionando Métrica de Qualidade

```python
def _calculate_quality_score(self, content: str) -> float:
    score = 0.0
    
    # Métricas existentes...
    
    # Nova métrica personalizada
    custom_score = self._calculate_custom_metric(content)
    score += custom_score
    
    return score

def _calculate_custom_metric(self, content: str) -> float:
    """Calcula métrica personalizada."""
    # Implementar cálculo
    return score
```

## Performance

### Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Função a ser analisada
    pipeline = ConversionPipeline()
    pipeline.convert("arquivo.pdf")
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Otimizações Comuns

```python
# 1. Cache de resultados
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(data: str) -> str:
    # Cálculo custoso
    return result

# 2. Processamento em lotes
def process_batch(items: List[str]) -> List[str]:
    results = []
    batch_size = 100
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = process_batch_items(batch)
        results.extend(batch_results)
    
    return results

# 3. Lazy loading
class LazyLoader:
    def __init__(self, loader_func):
        self._loader_func = loader_func
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            self._data = self._loader_func()
        return self._data
```

### Monitoramento de Memória

```python
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"Uso de memória: {memory_info.rss / 1024 / 1024:.2f} MB")
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Importação

```bash
# Problema: ModuleNotFoundError
# Solução: Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. Erro de Permissão

```bash
# Problema: PermissionError
# Solução: Verificar permissões
chmod +x install.sh
chmod +x main.py
```

#### 3. Erro de Dependência

```bash
# Problema: ImportError
# Solução: Reinstalar dependências
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

#### 4. Erro de Memória

```python
# Problema: MemoryError
# Solução: Processar em chunks
def process_large_file(file_path: str):
    chunk_size = 1024 * 1024  # 1MB
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            process_chunk(chunk)
```

### Debug de Pipeline

```python
def debug_pipeline():
    pipeline = ConversionPipeline()
    
    # Debug cada passo
    for step in pipeline.steps:
        print(f"🔍 Executando: {step.name}")
        try:
            pipeline.current_data = step.process(pipeline.current_data)
            print(f"✅ Sucesso: {step.name}")
        except Exception as e:
            print(f"❌ Erro em {step.name}: {e}")
            raise
```

### Validação de Dados

```python
def validate_data(data: Dict[str, Any]) -> bool:
    """Valida estrutura de dados."""
    required_keys = ['pdf_path', 'text_blocks', 'font_info']
    
    for key in required_keys:
        if key not in data:
            print(f"❌ Chave obrigatória ausente: {key}")
            return False
    
    return True
```

## Conclusão

Este guia fornece as ferramentas necessárias para contribuir efetivamente com o projeto. Lembre-se de:

1. **Seguir padrões**: PEP 8, type hints, docstrings
2. **Testar**: Sempre escrever testes para novas funcionalidades
3. **Documentar**: Atualizar documentação quando necessário
4. **Comunicar**: Usar mensagens de commit claras e descritivas
5. **Iterar**: Melhorar continuamente baseado em feedback

Para dúvidas específicas, consulte a documentação da arquitetura ou abra uma issue no repositório.

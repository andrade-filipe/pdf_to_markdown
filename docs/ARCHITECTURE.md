# Arquitetura do Conversor PDF para Markdown

## Visão Geral

O conversor utiliza uma arquitetura baseada no padrão **Pipeline (Chain of Responsibility)** para processar PDFs de forma modular e extensível. Cada etapa do pipeline é responsável por uma funcionalidade específica, permitindo fácil manutenção e extensão.

## Diagrama da Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input PDF     │───▶│  ConversionPipeline │───▶│  Output Markdown │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Pipeline Steps                           │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│TextExtraction   │TableExtraction  │CleanupStep      │ImageExtract│
│Step             │Step             │                 │ionStep    │
├─────────────────┼─────────────────┼─────────────────┼───────────┤
│MarkdownConversion│AdvancedMarkdown │                 │           │
│Step             │ConversionStep   │                 │           │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

## Componentes Principais

### 1. ConversionPipeline

**Arquivo**: `converter/pipeline.py`

**Responsabilidade**: Orquestra a execução sequencial de todos os passos do pipeline.

**Funcionalidades**:
- Inicializa e executa os passos na ordem correta
- Gerencia o fluxo de dados entre os passos
- Coleta estatísticas de conversão
- Trata erros e exceções

**Fluxo de Execução**:
```python
def convert(self, pdf_path: str, output_filename: str = None) -> Path:
    # 1. Inicializar dados
    data = {'pdf_path': pdf_path}
    
    # 2. Executar cada passo sequencialmente
    for step in self.steps:
        self.current_data = step.process(self.current_data)
    
    # 3. Salvar resultado
    markdown_content = self.current_data.get('markdown_content', '')
    # ... salvar arquivo
```

### 2. BaseStep

**Arquivo**: `converter/steps/base_step.py`

**Responsabilidade**: Classe abstrata que define a interface para todos os passos.

**Interface**:
```python
class BaseStep(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Processa os dados e retorna o resultado"""
        pass
```

## Passos do Pipeline

### 1. TextExtractionStep

**Arquivo**: `converter/steps/text_extraction_step.py`

**Responsabilidade**: Extrai texto e informações de fonte do PDF.

**Estratégias de Extração**:
1. **Método Simples**: `page.get_text()`
2. **Método HTML**: `page.get_text("html")` com limpeza de tags
3. **Método por Blocos**: `page.get_text("dict")` com processamento manual
4. **Fallback pdfplumber**: Para PDFs problemáticos

**Detecção de Texto Corrompido**:
```python
def _is_text_corrupted(self, text: str) -> bool:
    # Conta caracteres estranhos (>127, exceto acentos)
    strange_chars = sum(1 for char in text 
                       if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
    return strange_chars / len(text) > 0.15
```

**Dados Extraídos**:
- `text_blocks`: Lista de blocos de texto
- `font_info`: Informações de fonte (tamanho, posição, família)
- `raw_text`: Texto bruto extraído
- `total_pages`: Número total de páginas

### 2. TableExtractionStep

**Arquivo**: `converter/steps/table_extraction_step.py`

**Responsabilidade**: Extrai tabelas usando pdfplumber.

**Processo**:
1. Abre PDF com pdfplumber
2. Itera por todas as páginas
3. Extrai tabelas com `page.extract_tables()`
4. Converte para formato Markdown

**Formato de Saída**:
```markdown
| Coluna A | Coluna B |
|---|---|
| Dado 1 | Dado 2 |
| Dado 3 | Dado 4 |
```

### 3. CleanupStep

**Arquivo**: `converter/steps/cleanup_step.py`

**Responsabilidade**: Remove cabeçalhos, rodapés e texto desnecessário.

**Padrões de Limpeza**:
```python
patterns = [
    r'^\d+\s*$',           # Números soltos
    r'^[-–—]\s*$',         # Linhas com traços
    r'^\s*Page\s+\d+\s*$', # Números de página
    r'^\s*-\s*\d+\s*-\s*$' # Separadores de página
]
```

### 4. ImageExtractionStep

**Arquivo**: `converter/steps/image_extraction_step.py`

**Responsabilidade**: Extrai e salva imagens do PDF.

**Processo**:
1. Itera por todas as páginas
2. Extrai imagens com `page.get_images()`
3. Converte para Pixmap
4. Salva como PNG usando Pillow
5. Organiza em diretório `images/`

**Estrutura de Diretórios**:
```
output/
├── artigo.md
└── images/
    ├── imagem_p1_1.png
    ├── imagem_p2_1.png
    └── ...
```

### 5. MarkdownConversionStep

**Arquivo**: `converter/steps/markdown_conversion_step.py`

**Responsabilidade**: Converte dados extraídos para Markdown básico.

**Estratégias**:
1. **Prioridade**: Usa `font_info` para detecção de títulos
2. **Fallback 1**: Usa `raw_text` se não houver font_info
3. **Fallback 2**: Usa `cleaned_text` como último recurso

**Detecção de Títulos**:
```python
def _is_title(self, text: str) -> bool:
    patterns = [
        r'^\d+\.\s+[A-Z]',  # 1. Título
        r'^[A-Z][A-Z\s]+$', # TÍTULO EM MAIÚSCULAS
        r'^Abstract$', r'^Introduction$', r'^Conclusion$'
    ]
    return any(re.match(pattern, text.strip()) for pattern in patterns)
```

### 6. AdvancedMarkdownConversionStep

**Arquivo**: `converter/steps/advanced_markdown_conversion_step.py`

**Responsabilidade**: Aplica múltiplos métodos de conversão e escolhe o melhor.

## Sistema de Métodos de Conversão

### Métodos Disponíveis

#### 1. current
**Descrição**: Conversão básica atual
**Características**: Mantém estrutura original sem modificações

#### 2. intelligent
**Descrição**: Organização inteligente de parágrafos
**Características**: Agrupa linhas relacionadas em parágrafos

#### 3. structured
**Descrição**: Estrutura hierárquica rigorosa
**Características**: Força estrutura de títulos e seções

#### 4. compact
**Descrição**: Formatação compacta
**Características**: Remove quebras desnecessárias

#### 5. clean
**Descrição**: Limpeza agressiva de repetições e texto corrompido
**Características**: Remove duplicatas e caracteres problemáticos

#### 6. academic
**Descrição**: Otimizado para artigos científicos
**Características**: Detecta seções acadêmicas comuns

#### 7. minimal
**Descrição**: Foco na simplicidade e legibilidade
**Características**: Remove linhas curtas e repetitivas

### Sistema de Pontuação de Qualidade

**Arquivo**: `converter/steps/advanced_markdown_conversion_step.py`

**Métricas Avaliadas**:

#### 1. Número de Linhas
```python
line_count = len([l for l in lines if l.strip()])
score += max(0, 15 - line_count / 200)  # Menos linhas = melhor
```

#### 2. Presença de Títulos
```python
title_count = len([l for l in lines if l.startswith('#')])
score += min(15, title_count * 2)  # Mais títulos = melhor
```

#### 3. Parágrafos Bem Formados
```python
well_formed_paragraphs = 0
for para in paragraphs:
    if len(para) > 30 and not para.startswith('#'):
        well_formed_paragraphs += 1
score += min(20, well_formed_paragraphs * 2)
```

#### 4. Ausência de Quebras Desnecessárias
```python
unnecessary_breaks = len(re.findall(r'\n\s*\n\s*\n', content))
score += max(0, 10 - unnecessary_breaks)
```

#### 5. Palavras-chave Acadêmicas
```python
academic_keywords = [
    'abstract', 'introduction', 'conclusion', 'references',
    'analysis', 'study', 'research', 'method', 'result'
]
keyword_count = sum(1 for keyword in academic_keywords 
                   if keyword.lower() in content.lower())
score += keyword_count * 1.5
```

#### 6. Ausência de Repetições
```python
seen_lines = set()
repeated_lines = 0
for line in lines:
    normalized = line.strip().lower()
    if normalized in seen_lines:
        repeated_lines += 1
    else:
        seen_lines.add(normalized)
repetition_penalty = min(15, repeated_lines * 2)
score -= repetition_penalty
```

### Seleção Automática do Método

```python
def _evaluate_and_choose_best(self, methods: Dict[str, str], data: Dict[str, Any]) -> Tuple[str, str]:
    scores = {}
    
    for method_name, content in methods.items():
        score = self._calculate_quality_score(content)
        
        # Bônus especial para método 'clean' com repetições
        if method_name == 'clean':
            repetition_count = self._count_repetitions(content)
            if repetition_count > 10:
                score += 10
            elif repetition_count > 5:
                score += 5
        
        scores[method_name] = score
    
    # Escolher método com maior pontuação
    best_method = max(scores, key=scores.get)
    best_content = methods[best_method]
    
    # Salvar método escolhido nos dados
    data['method_chosen'] = best_method
    
    return best_method, best_content
```

## Sistema de Estatísticas

### Coleta de Dados

**Arquivo**: `converter/pipeline.py`

**Métricas Coletadas**:
- `total_pages`: Número total de páginas
- `text_blocks`: Quantidade de blocos de texto extraídos
- `tables`: Número de tabelas extraídas
- `images`: Número de imagens extraídas
- `font_info_entries`: Entradas de informação de fonte
- `raw_text_length`: Tamanho do texto bruto
- `cleaned_text_length`: Tamanho do texto limpo
- `markdown_length`: Tamanho do Markdown final
- `markdown_lines`: Número de linhas no Markdown
- `method_chosen`: Método de conversão escolhido

### Exibição de Estatísticas

**Arquivo**: `main.py`

```python
if args.verbose:
    stats = pipeline.get_statistics()
    print(f"\n📊 Estatísticas:")
    print(f"   - Páginas processadas: {stats['total_pages']}")
    print(f"   - Blocos de texto: {stats['text_blocks']}")
    # ... outras métricas
```

## Tratamento de Erros

### Estratégias de Fallback

1. **Texto Corrompido**: Fallback para pdfplumber
2. **Imagens Não Suportadas**: Skip com warning
3. **Tabelas Vazias**: Ignora tabelas vazias
4. **PDF Inválido**: Validação inicial

### Logging e Debug

```python
print(f"⚠️  Texto corrompido detectado, tentando método alternativo...")
print(f"🔍 Repetições detectadas em 'clean': {repetition_count}")
print(f"📊 {method_name}: {score:.2f}")
```

## Otimizações de Performance

### Para PDFs Grandes (>1MB)

```python
content_size = len(markdown_content.encode('utf-8'))
if content_size > 1024 * 1024:  # 1MB
    # Usar apenas métodos mais eficientes
    methods = {
        'compact': self._method_compact(markdown_content),
        'clean': self._method_clean(markdown_content),
        'minimal': self._method_minimal(markdown_content)
    }
```

### Filtros de Fonte

```python
# Filtrar texto muito pequeno ou vazio
if len(span['text'].strip()) > 0 and span['size'] > 6:
    # Processar apenas texto relevante
```

## Extensibilidade

### Adicionando Novos Passos

1. Criar nova classe herdando de `BaseStep`
2. Implementar método `process()`
3. Adicionar ao pipeline em `ConversionPipeline.__init__()`

### Adicionando Novos Métodos de Conversão

1. Implementar novo método em `AdvancedMarkdownConversionStep`
2. Adicionar ao dicionário de métodos
3. Ajustar sistema de pontuação se necessário

### Exemplo de Extensão

```python
class CustomStep(BaseStep):
    def __init__(self):
        super().__init__("CustomStep")
    
    def process(self, data: Any) -> Any:
        # Lógica personalizada
        return data
```

## Padrões de Design Utilizados

### 1. Pipeline (Chain of Responsibility)
- **Vantagem**: Separação de responsabilidades
- **Flexibilidade**: Fácil adição/remoção de passos
- **Testabilidade**: Cada passo pode ser testado isoladamente

### 2. Strategy (implícito)
- **Vantagem**: Múltiplos algoritmos de conversão
- **Flexibilidade**: Seleção automática do melhor método
- **Extensibilidade**: Fácil adição de novos métodos

### 3. Factory (implícito)
- **Vantagem**: Criação dinâmica de passos
- **Flexibilidade**: Configuração flexível do pipeline

## Considerações de Performance

### Complexidade Temporal
- **TextExtractionStep**: O(n) onde n = número de páginas
- **TableExtractionStep**: O(n) onde n = número de páginas
- **AdvancedMarkdownConversionStep**: O(m) onde m = número de métodos

### Complexidade Espacial
- **Armazenamento**: O(t) onde t = tamanho do texto
- **Cache**: Informações de fonte mantidas em memória
- **Imagens**: Salvas em disco, referências em memória

### Otimizações Implementadas
1. **Filtros de fonte**: Remove texto irrelevante
2. **Métodos seletivos**: Para PDFs grandes
3. **Limpeza eficiente**: Regex otimizadas
4. **Cache de dados**: Evita reprocessamento

## Testabilidade

### Estrutura de Testes

```
tests/
├── __init__.py
├── test_converter.py          # Testes unitários
└── test_integration.py        # Testes de integração
```

### Cobertura de Testes

- **Funções básicas**: 100% cobertura
- **Pipeline completo**: Teste de integração
- **Casos extremos**: PDFs problemáticos
- **Performance**: PDFs grandes

### Mocking e Stubs

```python
def setup_method(self):
    self.temp_dir = tempfile.mkdtemp()
    self.test_pdf = self.create_test_pdf()

def teardown_method(self):
    shutil.rmtree(self.temp_dir)
```

## Conclusões

A arquitetura modular baseada em Pipeline oferece:

1. **Manutenibilidade**: Código organizado e bem estruturado
2. **Extensibilidade**: Fácil adição de novas funcionalidades
3. **Testabilidade**: Componentes isolados e testáveis
4. **Robustez**: Múltiplos fallbacks e tratamento de erros
5. **Performance**: Otimizações específicas para diferentes cenários

O sistema de múltiplos métodos com pontuação automática garante alta qualidade de conversão, enquanto a coleta detalhada de estatísticas permite monitoramento e melhoria contínua.

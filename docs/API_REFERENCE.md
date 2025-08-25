# Referência da API - Conversor PDF para Markdown

## Índice

1. [Visão Geral](#visão-geral)
2. [Classes Principais](#classes-principais)
3. [Passos do Pipeline](#passos-do-pipeline)
4. [Funções Utilitárias](#funções-utilitárias)
5. [Tipos de Dados](#tipos-de-dados)
6. [Exceções](#exceções)
7. [Constantes](#constantes)

## Visão Geral

Esta documentação descreve a API completa do conversor PDF para Markdown, incluindo todas as classes, métodos e funções disponíveis para desenvolvedores.

## Classes Principais

### ConversionPipeline

**Arquivo**: `converter/pipeline.py`

**Descrição**: Classe principal que orquestra o processo de conversão de PDF para Markdown.

#### Construtor

```python
ConversionPipeline(output_dir: str = ".")
```

**Parâmetros**:
- `output_dir` (str): Diretório de saída para arquivos gerados (padrão: diretório atual)

#### Métodos

##### convert()

```python
def convert(self, pdf_path: str, output_filename: str = None) -> Path
```

**Descrição**: Executa a conversão completa de um PDF para Markdown.

**Parâmetros**:
- `pdf_path` (str): Caminho para o arquivo PDF de entrada
- `output_filename` (str, opcional): Nome do arquivo de saída (padrão: nome do PDF + .md)

**Retorna**:
- `Path`: Caminho para o arquivo Markdown gerado

**Exemplo**:
```python
pipeline = ConversionPipeline()
result = pipeline.convert("documento.pdf", "saida.md")
print(f"Arquivo gerado: {result}")
```

##### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

**Descrição**: Retorna estatísticas detalhadas da última conversão.

**Retorna**:
- `Dict[str, Any]`: Dicionário com métricas de conversão

**Exemplo**:
```python
stats = pipeline.get_statistics()
print(f"Páginas processadas: {stats['total_pages']}")
print(f"Tabelas extraídas: {stats['tables']}")
```

#### Atributos

- `steps`: Lista de passos do pipeline
- `output_dir`: Diretório de saída
- `current_data`: Dados da conversão atual

### BaseStep

**Arquivo**: `converter/steps/base_step.py`

**Descrição**: Classe abstrata base para todos os passos do pipeline.

#### Construtor

```python
BaseStep(name: str)
```

**Parâmetros**:
- `name` (str): Nome identificador do passo

#### Métodos Abstratos

##### process()

```python
@abstractmethod
def process(self, data: Any) -> Any
```

**Descrição**: Método abstrato que deve ser implementado por todas as subclasses.

**Parâmetros**:
- `data` (Any): Dados de entrada para processamento

**Retorna**:
- `Any`: Dados processados

#### Métodos

##### __str__()

```python
def __str__(self) -> str
```

**Retorna**: Representação string do passo

## Passos do Pipeline

### TextExtractionStep

**Arquivo**: `converter/steps/text_extraction_step.py`

**Descrição**: Extrai texto e informações de fonte do PDF.

#### Construtor

```python
TextExtractionStep()
```

#### Métodos

##### process()

```python
def process(self, data: Dict[str, Any]) -> Dict[str, Any]
```

**Descrição**: Extrai texto e informações de fonte do PDF.

**Parâmetros**:
- `data` (Dict[str, Any]): Dados contendo caminho do PDF

**Retorna**:
- `Dict[str, Any]`: Dados com texto extraído e informações de fonte

**Dados Adicionados**:
- `text_blocks`: Lista de blocos de texto
- `font_info`: Informações de fonte (tamanho, posição, família)
- `raw_text`: Texto bruto extraído
- `total_pages`: Número total de páginas

##### _is_text_corrupted()

```python
def _is_text_corrupted(self, text: str) -> bool
```

**Descrição**: Detecta se o texto está corrompido.

**Parâmetros**:
- `text` (str): Texto a ser analisado

**Retorna**:
- `bool`: True se o texto estiver corrompido

##### _extract_with_pdfplumber()

```python
def _extract_with_pdfplumber(self, pdf_path: str) -> str
```

**Descrição**: Extrai texto usando pdfplumber como fallback.

**Parâmetros**:
- `pdf_path` (str): Caminho do PDF

**Retorna**:
- `str`: Texto extraído

### TableExtractionStep

**Arquivo**: `converter/steps/table_extraction_step.py`

**Descrição**: Extrai tabelas do PDF.

#### Construtor

```python
TableExtractionStep()
```

#### Métodos

##### process()

```python
def process(self, data: Dict[str, Any]) -> Dict[str, Any]
```

**Descrição**: Extrai tabelas do PDF.

**Parâmetros**:
- `data` (Dict[str, Any]): Dados contendo caminho do PDF

**Retorna**:
- `Dict[str, Any]`: Dados com tabelas extraídas

**Dados Adicionados**:
- `tables`: Lista de tabelas extraídas

### CleanupStep

**Arquivo**: `converter/steps/cleanup_step.py`

**Descrição**: Remove cabeçalhos, rodapés e texto desnecessário.

#### Construtor

```python
CleanupStep()
```

#### Métodos

##### process()

```python
def process(self, data: Dict[str, Any]) -> Dict[str, Any]
```

**Descrição**: Limpa o texto extraído.

**Parâmetros**:
- `data` (Dict[str, Any]): Dados com texto bruto

**Retorna**:
- `Dict[str, Any]`: Dados com texto limpo

**Dados Adicionados**:
- `cleaned_text`: Texto limpo

##### _clean_text()

```python
def _clean_text(self, text: str) -> str
```

**Descrição**: Aplica padrões de limpeza ao texto.

**Parâmetros**:
- `text` (str): Texto a ser limpo

**Retorna**:
- `str`: Texto limpo

### ImageExtractionStep

**Arquivo**: `converter/steps/image_extraction_step.py`

**Descrição**: Extrai e salva imagens do PDF.

#### Construtor

```python
ImageExtractionStep()
```

#### Métodos

##### process()

```python
def process(self, data: Dict[str, Any]) -> Dict[str, Any]
```

**Descrição**: Extrai imagens do PDF.

**Parâmetros**:
- `data` (Dict[str, Any]): Dados contendo caminho do PDF

**Retorna**:
- `Dict[str, Any]`: Dados com imagens extraídas

**Dados Adicionados**:
- `images`: Lista de imagens extraídas

### MarkdownConversionStep

**Arquivo**: `converter/steps/markdown_conversion_step.py`

**Descrição**: Converte dados extraídos para Markdown básico.

#### Construtor

```python
MarkdownConversionStep()
```

#### Métodos

##### process()

```python
def process(self, data: Dict[str, Any]) -> Dict[str, Any]
```

**Descrição**: Converte dados para Markdown.

**Parâmetros**:
- `data` (Dict[str, Any]): Dados extraídos

**Retorna**:
- `Dict[str, Any]`: Dados com Markdown gerado

**Dados Adicionados**:
- `markdown_content`: Conteúdo Markdown

##### _process_font_info()

```python
def _process_font_info(self, font_info: List[Dict[str, Any]]) -> str
```

**Descrição**: Processa informações de fonte para detectar títulos.

**Parâmetros**:
- `font_info` (List[Dict[str, Any]]): Lista de informações de fonte

**Retorna**:
- `str`: Markdown com títulos detectados

##### _process_raw_text()

```python
def _process_raw_text(self, raw_text: str) -> str
```

**Descrição**: Processa texto bruto para Markdown.

**Parâmetros**:
- `raw_text` (str): Texto bruto

**Retorna**:
- `str`: Markdown processado

##### _is_title()

```python
def _is_title(self, text: str) -> bool
```

**Descrição**: Detecta se um texto é um título.

**Parâmetros**:
- `text` (str): Texto a ser analisado

**Retorna**:
- `bool`: True se for um título

### AdvancedMarkdownConversionStep

**Arquivo**: `converter/steps/advanced_markdown_conversion_step.py`

**Descrição**: Aplica múltiplos métodos de conversão e escolhe o melhor.

#### Construtor

```python
AdvancedMarkdownConversionStep()
```

#### Métodos

##### process()

```python
def process(self, data: Dict[str, Any]) -> Dict[str, Any]
```

**Descrição**: Aplica múltiplos métodos de conversão.

**Parâmetros**:
- `data` (Dict[str, Any]): Dados com Markdown básico

**Retorna**:
- `Dict[str, Any]`: Dados com Markdown otimizado

**Dados Modificados**:
- `markdown_content`: Markdown otimizado
- `method_chosen`: Método escolhido

##### _evaluate_and_choose_best()

```python
def _evaluate_and_choose_best(self, methods: Dict[str, str], data: Dict[str, Any]) -> Tuple[str, str]
```

**Descrição**: Avalia e escolhe o melhor método de conversão.

**Parâmetros**:
- `methods` (Dict[str, str]): Dicionário de métodos e seus resultados
- `data` (Dict[str, Any]): Dados da conversão

**Retorna**:
- `Tuple[str, str]`: (método_escolhido, conteúdo_otimizado)

##### _calculate_quality_score()

```python
def _calculate_quality_score(self, content: str) -> float
```

**Descrição**: Calcula pontuação de qualidade do conteúdo.

**Parâmetros**:
- `content` (str): Conteúdo Markdown

**Retorna**:
- `float`: Pontuação de qualidade

#### Métodos de Conversão

##### _method_current()

```python
def _method_current(self, content: str) -> str
```

**Descrição**: Método de conversão atual (básico).

##### _method_intelligent()

```python
def _method_intelligent(self, content: str) -> str
```

**Descrição**: Organização inteligente de parágrafos.

##### _method_structured()

```python
def _method_structured(self, content: str) -> str
```

**Descrição**: Estrutura hierárquica rigorosa.

##### _method_compact()

```python
def _method_compact(self, content: str) -> str
```

**Descrição**: Formatação compacta.

##### _method_clean()

```python
def _method_clean(self, content: str) -> str
```

**Descrição**: Limpeza agressiva de repetições e texto corrompido.

##### _method_academic()

```python
def _method_academic(self, content: str) -> str
```

**Descrição**: Otimizado para artigos científicos.

##### _method_minimal()

```python
def _method_minimal(self, content: str) -> str
```

**Descrição**: Foco na simplicidade e legibilidade.

## Funções Utilitárias

### converter.py

**Arquivo**: `converter/converter.py`

#### converter_texto()

```python
def converter_texto(texto: str) -> str
```

**Descrição**: Converte texto simples para Markdown.

**Parâmetros**:
- `texto` (str): Texto a ser convertido

**Retorna**:
- `str`: Texto em formato Markdown

#### converter_tabela()

```python
def converter_tabela(tabela_pdf: List[List[str]]) -> str
```

**Descrição**: Converte tabela para formato Markdown.

**Parâmetros**:
- `tabela_pdf` (List[List[str]]): Tabela em formato de lista de listas

**Retorna**:
- `str`: Tabela em formato Markdown

#### limpar_texto()

```python
def limpar_texto(texto: str) -> str
```

**Descrição**: Remove caracteres especiais e formata texto.

**Parâmetros**:
- `texto` (str): Texto a ser limpo

**Retorna**:
- `str`: Texto limpo

#### detectar_titulos()

```python
def detectar_titulos(font_info: List[Dict[str, Any]]) -> List[str]
```

**Descrição**: Detecta títulos baseado em informações de fonte.

**Parâmetros**:
- `font_info` (List[Dict[str, Any]]): Informações de fonte

**Retorna**:
- `List[str]`: Lista de títulos detectados

#### processar_imagem()

```python
def processar_imagem(imagem_path: str, output_dir: str) -> str
```

**Descrição**: Processa e salva imagem.

**Parâmetros**:
- `imagem_path` (str): Caminho da imagem
- `output_dir` (str): Diretório de saída

**Retorna**:
- `str`: Caminho da imagem processada

## Tipos de Dados

### FontInfo

```python
FontInfo = Dict[str, Any]
```

**Estrutura**:
```python
{
    'text': str,           # Texto extraído
    'tamanho': float,      # Tamanho da fonte
    'posicao': Tuple[float, float],  # Posição (x, y)
    'pagina': int,         # Número da página
    'fonte': str           # Nome da fonte
}
```

### TableData

```python
TableData = List[List[str]]
```

**Descrição**: Tabela representada como lista de linhas, onde cada linha é uma lista de células.

### ImageInfo

```python
ImageInfo = Dict[str, Any]
```

**Estrutura**:
```python
{
    'path': str,           # Caminho da imagem salva
    'page': int,           # Página de origem
    'index': int,          # Índice na página
    'bbox': Tuple[float, float, float, float]  # Bounding box
}
```

### ConversionData

```python
ConversionData = Dict[str, Any]
```

**Estrutura**:
```python
{
    'pdf_path': str,                    # Caminho do PDF
    'text_blocks': List[str],           # Blocos de texto
    'font_info': List[FontInfo],        # Informações de fonte
    'raw_text': str,                    # Texto bruto
    'total_pages': int,                 # Total de páginas
    'tables': List[TableData],          # Tabelas extraídas
    'cleaned_text': str,                # Texto limpo
    'images': List[ImageInfo],          # Imagens extraídas
    'markdown_content': str,            # Conteúdo Markdown
    'method_chosen': str                # Método escolhido
}
```

### Statistics

```python
Statistics = Dict[str, Any]
```

**Estrutura**:
```python
{
    'total_pages': int,                 # Total de páginas
    'text_blocks': int,                 # Blocos de texto
    'tables': int,                      # Tabelas extraídas
    'images': int,                      # Imagens extraídas
    'font_info_entries': int,           # Entradas de fonte
    'raw_text_length': int,             # Tamanho texto bruto
    'cleaned_text_length': int,         # Tamanho texto limpo
    'markdown_length': int,             # Tamanho Markdown
    'markdown_lines': int,              # Linhas Markdown
    'method_chosen': str                # Método escolhido
}
```

## Exceções

### PDFProcessingError

```python
class PDFProcessingError(Exception):
    """Exceção base para erros de processamento de PDF."""
    pass
```

### TextExtractionError

```python
class TextExtractionError(PDFProcessingError):
    """Exceção para erros de extração de texto."""
    pass
```

### TableExtractionError

```python
class TableExtractionError(PDFProcessingError):
    """Exceção para erros de extração de tabelas."""
    pass
```

### ImageExtractionError

```python
class ImageExtractionError(PDFProcessingError):
    """Exceção para erros de extração de imagens."""
    pass
```

### MarkdownConversionError

```python
class MarkdownConversionError(PDFProcessingError):
    """Exceção para erros de conversão para Markdown."""
    pass
```

## Constantes

### Padrões de Limpeza

```python
CLEANUP_PATTERNS = [
    r'^\d+\s*$',           # Números soltos
    r'^[-–—]\s*$',         # Linhas com traços
    r'^\s*Page\s+\d+\s*$', # Números de página
    r'^\s*-\s*\d+\s*-\s*$' # Separadores de página
]
```

### Palavras-chave Acadêmicas

```python
ACADEMIC_KEYWORDS = [
    'abstract', 'introduction', 'conclusion', 'references',
    'analysis', 'study', 'research', 'method', 'result',
    'data', 'evidence', 'figure', 'table', 'discussion',
    'materials', 'methods', 'background'
]
```

### Padrões de Título

```python
TITLE_PATTERNS = [
    r'^\d+\.\s+[A-Z]',  # 1. Título
    r'^[A-Z][A-Z\s]+$', # TÍTULO EM MAIÚSCULAS
    r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
    r'^Abstract$', r'^Introduction$', r'^Conclusion$',
    r'^References$', r'^Bibliography$', r'^Appendix$'
]
```

### Configurações de Performance

```python
LARGE_FILE_THRESHOLD = 1024 * 1024  # 1MB
MIN_FONT_SIZE = 6
CORRUPTION_THRESHOLD = 0.15
```

## Exemplos de Uso

### Conversão Básica

```python
from converter.pipeline import ConversionPipeline

# Criar pipeline
pipeline = ConversionPipeline()

# Converter PDF
result = pipeline.convert("documento.pdf")

# Obter estatísticas
stats = pipeline.get_statistics()
print(f"Páginas: {stats['total_pages']}")
```

### Conversão com Opções

```python
from converter.pipeline import ConversionPipeline

# Pipeline com diretório personalizado
pipeline = ConversionPipeline(output_dir="/caminho/saida")

# Converter com nome personalizado
result = pipeline.convert("documento.pdf", "saida_personalizada.md")
```

### Uso de Passos Individuais

```python
from converter.steps.text_extraction_step import TextExtractionStep

# Usar passo individual
step = TextExtractionStep()
data = {'pdf_path': 'documento.pdf'}
result = step.process(data)

print(f"Texto extraído: {result['raw_text'][:100]}...")
```

### Acesso a Métodos de Conversão

```python
from converter.steps.advanced_markdown_conversion_step import AdvancedMarkdownConversionStep

# Usar método específico
step = AdvancedMarkdownConversionStep()
content = "# Título\n\nParágrafo de exemplo."

# Aplicar método específico
result = step._method_academic(content)
print(result)
```

## Considerações de Performance

### Complexidade Temporal

- **TextExtractionStep**: O(n) onde n = número de páginas
- **TableExtractionStep**: O(n) onde n = número de páginas  
- **AdvancedMarkdownConversionStep**: O(m) onde m = número de métodos

### Complexidade Espacial

- **Armazenamento**: O(t) onde t = tamanho do texto
- **Cache**: Informações de fonte mantidas em memória
- **Imagens**: Salvas em disco, referências em memória

### Otimizações

- Filtros de fonte para remover texto irrelevante
- Métodos seletivos para PDFs grandes
- Limpeza eficiente com regex otimizadas
- Cache de dados para evitar reprocessamento

# PDF to Markdown Converter

Um conversor robusto e inteligente de PDF para Markdown, especialmente otimizado para artigos científicos. Desenvolvido em Python com foco na qualidade da conversão e usabilidade.

## ✨ Características Principais

### 🎯 Funcionalidades Core
- **Extração Digital**: Prioriza conteúdo digital (sem OCR)
- **Alta Fidelidade**: Preserva estrutura de títulos, tabelas e listas
- **Múltiplos Métodos**: 7 estratégias diferentes de conversão Markdown
- **Seleção Inteligente**: Escolhe automaticamente o melhor método baseado em qualidade
- **Extração de Imagens**: Salva imagens organizadas localmente
- **Detecção de Títulos**: Identifica títulos por tamanho de fonte e padrões acadêmicos
- **Limpeza Inteligente**: Remove cabeçalhos, rodapés e texto corrompido

### 🚀 Funcionalidades Avançadas
- **Sistema de Pontuação**: Avalia qualidade automaticamente
- **Fallback Robusto**: Múltiplas estratégias de extração de texto
- **Performance Otimizada**: Otimizado para PDFs grandes (>1MB)
- **Estatísticas Detalhadas**: Métricas completas de conversão
- **Relatórios JSON**: Análise detalhada de qualidade
- **CLI Intuitivo**: Interface de linha de comando flexível

## 📦 Instalação

### Opção 1: Instalação Automatizada (Recomendada)
```bash
# Baixar o projeto
git clone <repository-url>
cd pdf_to_markdown

# Executar script de instalação
chmod +x install.sh
./install.sh
```

### Opção 2: Instalação Manual
```bash
# Instalar dependências do sistema (se necessário)
sudo apt update
sudo apt install python3-pip python3-full python3-venv

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Opção 3: Instalação Direta (Fallback)
```bash
# Instalar diretamente no sistema
python3 -m pip install --break-system-packages -r requirements.txt
```

## 🎮 Como Usar

### Uso Básico
```bash
# Converter um PDF
python3 main.py arquivo.pdf

# Especificar diretório de saída
python3 main.py arquivo.pdf --output-dir /caminho/saida

# Ver estatísticas detalhadas
python3 main.py arquivo.pdf --verbose
```

### Exemplos Práticos
```bash
# Converter artigo científico
python3 main.py artigo.pdf --output-dir ~/Documentos/Markdown

# Converter com nome personalizado
python3 main.py documento.pdf --output documento_convertido.md

# Ver todas as estatísticas
python3 main.py relatorio.pdf --verbose
```

### Opções Disponíveis
- `--output-dir`: Diretório de saída (padrão: diretório atual)
- `--output`: Nome do arquivo de saída (padrão: nome do PDF + .md)
- `--verbose`: Mostrar estatísticas detalhadas
- `--help`: Mostrar ajuda

## 🏗️ Arquitetura

### Padrão Pipeline (Chain of Responsibility)
```
ConversionPipeline
├── TextExtractionStep (PyMuPDF + fallback pdfplumber)
├── TableExtractionStep (pdfplumber)
├── CleanupStep (regex patterns)
├── ImageExtractionStep (PyMuPDF + Pillow)
└── AdvancedMarkdownConversionStep (7 métodos)
```

### Métodos de Conversão Markdown
1. **current**: Conversão básica atual
2. **intelligent**: Organização inteligente de parágrafos
3. **structured**: Estrutura hierárquica rigorosa
4. **compact**: Formatação compacta
5. **clean**: Limpeza agressiva de repetições e texto corrompido
6. **academic**: Otimizado para artigos científicos
7. **minimal**: Foco na simplicidade e legibilidade

### Sistema de Pontuação de Qualidade
O conversor avalia automaticamente cada método baseado em:
- **Número de linhas** (menos é melhor)
- **Presença de títulos** (mais é melhor)
- **Parágrafos bem formados**
- **Ausência de quebras desnecessárias**
- **Palavras-chave acadêmicas**
- **Ausência de repetições**

## 📊 Estatísticas e Relatórios

### Estatísticas no Terminal (--verbose)
```
📊 Estatísticas:
   - Páginas processadas: 15
   - Blocos de texto: 234
   - Tabelas extraídas: 3
   - Imagens extraídas: 8
   - Entradas de fonte: 156
   - Tamanho texto bruto: 45,678 chars
   - Tamanho texto limpo: 42,123 chars
   - Tamanho Markdown: 38,901 chars
   - Linhas Markdown: 1,234
   - Método escolhido: academic
```

### Relatório JSON Detalhado
```json
{
  "total_files": 20,
  "successful_conversions": 19,
  "success_rate": 95.0,
  "method_distribution": {
    "academic": 8,
    "clean": 6,
    "minimal": 3,
    "structured": 2
  },
  "average_stats": {
    "pages": 12.3,
    "text_blocks": 189.5,
    "tables": 2.1,
    "images": 4.8
  }
}
```

## 🧪 Testes e Validação

### Executar Testes
```bash
# Testes unitários
python3 -m pytest tests/

# Teste de integração
python3 -m pytest tests/test_converter.py::test_pipeline_conversao_completa

# Validação com múltiplos PDFs
python3 advanced_test.py
```

### Cobertura de Testes
- ✅ Testes unitários para funções básicas
- ✅ Teste de integração do pipeline completo
- ✅ Testes de robustez com múltiplos PDFs
- ✅ Validação de qualidade do Markdown gerado

## 📁 Estrutura do Projeto

```
pdf_to_markdown/
├── main.py                          # CLI principal
├── converter/                       # Módulo principal
│   ├── __init__.py
│   ├── converter.py                 # Funções básicas
│   ├── pipeline.py                  # Pipeline de conversão
│   └── steps/                       # Passos do pipeline
│       ├── __init__.py
│       ├── base_step.py             # Classe base
│       ├── text_extraction_step.py  # Extração de texto
│       ├── table_extraction_step.py # Extração de tabelas
│       ├── cleanup_step.py          # Limpeza de texto
│       ├── image_extraction_step.py # Extração de imagens
│       ├── markdown_conversion_step.py # Conversão básica
│       └── advanced_markdown_conversion_step.py # Conversão avançada
├── tests/                           # Testes
│   ├── __init__.py
│   └── test_converter.py
├── context/                         # Documentação da AI
│   ├── AI_DOCS.md
│   └── TRUTH.md
├── docs/                            # Documentação técnica
├── requirements.txt                 # Dependências
├── install.sh                       # Script de instalação
├── advanced_test.py                 # Testes avançados
└── README.md                        # Este arquivo
```

## 🔧 Dependências

### Principais
- **PyMuPDF (fitz)**: Extração de texto e imagens com informações de fonte
- **pdfplumber**: Extração especializada de tabelas e fallback de texto
- **Pillow**: Processamento e salvamento de imagens
- **pytest**: Framework de testes

### Versões Recomendadas
```
PyMuPDF>=1.26.0
pdfplumber>=0.11.0
pytest>=8.0.0
Pillow>=10.0.0
```

## 🎯 Casos de Uso

### Artigos Científicos
- Detecção automática de seções (Abstract, Introduction, etc.)
- Preservação de estrutura hierárquica
- Extração de tabelas e figuras
- Limpeza de cabeçalhos/rodapés acadêmicos

### Documentos Técnicos
- Conversão de manuais e documentação
- Preservação de listas e enumerações
- Extração de diagramas e gráficos
- Formatação consistente

### Relatórios
- Conversão de relatórios empresariais
- Preservação de estrutura de dados
- Extração de gráficos e tabelas
- Formatação profissional

## 🚨 Troubleshooting

### Problemas Comuns

#### Erro de Instalação
```bash
# Se houver erro de ambiente gerenciado
python3 -m pip install --break-system-packages -r requirements.txt
```

#### Texto Corrompido
- O conversor detecta automaticamente texto corrompido
- Usa fallback para pdfplumber quando necessário
- Limpa caracteres problemáticos automaticamente

#### PDFs Muito Grandes
- Otimização automática para PDFs >1MB
- Usa métodos mais eficientes para arquivos grandes
- Processamento otimizado de memória

#### Falha na Conversão
```bash
# Verificar se o PDF é válido
python3 -c "import fitz; fitz.open('arquivo.pdf')"

# Tentar com verbose para mais detalhes
python3 main.py arquivo.pdf --verbose
```

## 📈 Performance

### Métricas Típicas
- **PDFs pequenos (<1MB)**: 2-5 segundos
- **PDFs médios (1-10MB)**: 5-15 segundos
- **PDFs grandes (10-50MB)**: 15-60 segundos
- **Taxa de sucesso**: ~95% em PDFs científicos

### Otimizações
- Processamento otimizado para PDFs grandes
- Seleção inteligente de métodos de conversão
- Cache de informações de fonte
- Limpeza eficiente de texto

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente seguindo TDD
4. Execute os testes
5. Envie um Pull Request

### Padrões de Código
- Seguir PEP 8
- Documentar funções e classes
- Adicionar testes para novas funcionalidades
- Manter compatibilidade com Python 3.8+

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🎉 Agradecimentos

- **PyMuPDF**: Extração robusta de conteúdo PDF
- **pdfplumber**: Extração especializada de tabelas
- **Pillow**: Processamento de imagens
- **pytest**: Framework de testes confiável

---

**Desenvolvido com ❤️ para a comunidade científica**

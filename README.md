# Conversor de PDF para Markdown

Uma ferramenta robusta e estruturada para converter artigos científicos em formato PDF para Markdown, priorizando a extração de conteúdo digital com alta fidelidade estrutural.

## 🎯 Características

- **Extração de Texto Inteligente**: Detecta títulos automaticamente por tamanho de fonte e posicionamento
- **Preservação de Tabelas**: Extrai e converte tabelas mantendo a estrutura original
- **Gestão de Imagens**: Extrai imagens e organiza em diretórios por artigo
- **Limpeza Automática**: Remove cabeçalhos e rodapés automaticamente
- **Pipeline Modular**: Arquitetura baseada em padrão Strategy/Pipeline para fácil extensão
- **CLI Robusta**: Interface de linha de comando com validação e tratamento de erros

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- pip

### Instalação das Dependências

#### Opção 1: Instalação Automática (Recomendada)
```bash
# Executar script de instalação
./install.sh
```

#### Opção 2: Instalação Manual
```bash
# Instalar dependências do sistema (se necessário)
sudo apt install python3-full python3-venv

# Instalar dependências Python
python3 -m pip install --break-system-packages -r requirements.txt
```

#### Opção 3: Ambiente Virtual (Alternativa)
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## 📦 Dependências

- **PyMuPDF (fitz)**: Extração de texto com informações de fonte
- **pdfplumber**: Extração de tabelas
- **Pillow**: Processamento de imagens
- **pytest**: Framework de testes

## 🛠️ Uso

### Uso Básico

```bash
python main.py artigo.pdf
```

### Opções Avançadas

```bash
# Especificar nome do arquivo de saída
python main.py artigo.pdf -o artigo_convertido.md

# Especificar diretório de saída
python main.py artigo.pdf -d output/personalizado

# Modo verboso (mais informações)
python main.py artigo.pdf -v

# Ver ajuda
python main.py --help
```

### Exemplos de Uso

```bash
# Conversão simples
python main.py papers/artigo_cientifico.pdf

# Conversão com saída personalizada
python main.py papers/artigo_cientifico.pdf -o artigo_final.md -d output/convertidos

# Conversão com debug
python main.py papers/artigo_cientifico.pdf -v
```

## 📁 Estrutura do Projeto

```
pdf_to_markdown/
├── main.py                 # Script principal da CLI
├── requirements.txt        # Dependências do projeto
├── README.md              # Esta documentação
├── converter/             # Módulo principal
│   ├── __init__.py
│   ├── converter.py       # Funções básicas de conversão
│   ├── pipeline.py        # Pipeline principal
│   └── steps/            # Passos do pipeline
│       ├── __init__.py
│       ├── base_step.py   # Classe base para passos
│       ├── text_extraction_step.py
│       ├── table_extraction_step.py
│       ├── cleanup_step.py
│       ├── image_extraction_step.py
│       └── markdown_conversion_step.py
├── tests/                # Testes unitários
│   ├── __init__.py
│   └── test_converter.py
├── context/              # Documentação interna
│   ├── AI_DOCS.md
│   └── TRUTH.md
└── output/               # Diretório de saída (criado automaticamente)
    ├── artigo.md
    └── images/
        ├── imagem_p1_1.png
        └── ...
```

## 🔧 Arquitetura

### Padrão Pipeline (Chain of Responsibility)

O projeto utiliza o padrão Pipeline para organizar o processo de conversão em etapas sequenciais:

1. **TextExtractionStep**: Extrai texto com informações de fonte usando PyMuPDF
2. **TableExtractionStep**: Extrai tabelas usando pdfplumber
3. **CleanupStep**: Remove cabeçalhos e rodapés
4. **ImageExtractionStep**: Extrai e salva imagens
5. **MarkdownConversionStep**: Converte tudo para Markdown

### Detecção de Títulos

A ferramenta detecta títulos automaticamente baseando-se em:
- **Tamanho da fonte**: Fontes ≥ 14pt são consideradas títulos
- **Posicionamento**: Ordenação por posição Y na página
- **Padrões acadêmicos**: Números de seção (1., 2., etc.)

## 🧪 Testes

### Executar Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar testes específicos
python -m pytest tests/test_converter.py::TestPDFToMarkdownConverter::test_converte_titulo_e_paragrafo -v

# Executar com cobertura
python -m pytest tests/ --cov=converter --cov-report=html
```

### Testes Implementados

- ✅ Conversão de títulos e parágrafos
- ✅ Conversão de tabelas simples
- ✅ Remoção de cabeçalhos/rodapés
- ✅ Extração e referência de imagens
- ✅ Detecção de títulos por tamanho de fonte
- ✅ Pipeline completo de conversão

## 📊 Funcionalidades

### Extração de Texto
- Extração com preservação de estrutura
- Informações de fonte (tamanho, família)
- Posicionamento preciso

### Conversão de Tabelas
- Detecção automática de tabelas
- Preservação de estrutura de colunas
- Conversão para formato Markdown

### Gestão de Imagens
- Extração automática de imagens
- Organização por artigo
- Referências relativas no Markdown

### Limpeza de Texto
- Remoção de cabeçalhos/rodapés
- Padrões configuráveis
- Preservação de conteúdo relevante

## 🔍 Exemplos de Saída

### Markdown Gerado

```markdown
# 1. Introdução

Este é o primeiro parágrafo do artigo científico.

## Tabela 1 (Página 2)

| Coluna A | Coluna B |
|---|---|
| Dado 1 | Dado 2 |
| Dado 3 | Dado 4 |

## Imagem 1 (Página 3)

![imagem_p3_1.png](./images/imagem_p3_1.png)
```

## 🚨 Tratamento de Erros

A ferramenta inclui tratamento robusto de erros:

- **Validação de entrada**: Verifica se o arquivo PDF existe
- **Tratamento de dependências**: Verifica bibliotecas necessárias
- **Graceful degradation**: Continua processamento mesmo com erros em imagens
- **Logging detalhado**: Informações de debug em modo verboso

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:

1. Verifique a documentação
2. Execute com `-v` para mais informações de debug
3. Abra uma issue no repositório

## 🔄 Roadmap

- [ ] Suporte a múltiplos idiomas
- [ ] Detecção de listas numeradas
- [ ] Extração de metadados (autores, abstract)
- [ ] Interface web
- [ ] Processamento em lote
- [ ] Configuração via arquivo YAML

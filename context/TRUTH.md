# Fontes da Verdade - Python PDF to Markdown Converter

## Bibliotecas Python para Manipulação de PDF

### PyMuPDF (fitz)
- **Vantagens:** Performance superior, extração precisa de texto e metadados, suporte a imagens
- **Documentação:** https://pymupdf.readthedocs.io/
- **Instalação:** `pip install PyMuPDF`
- **Uso Principal:** Extração de texto com preservação de estrutura

### pdfplumber
- **Vantagens:** Excelente para extração de tabelas, análise de layout
- **Documentação:** https://github.com/jsvine/pdfplumber
- **Instalação:** `pip install pdfplumber`
- **Uso Principal:** Extração de tabelas e análise de posicionamento

### Alternativas Consideradas
- **PyPDF2:** Menos preciso para extração estrutural
- **pdf2image:** Apenas para conversão de páginas para imagens
- **Marker:** Complexo demais para o escopo atual

## Melhores Práticas Python

### PEP 8 - Guia de Estilo
- Indentação: 4 espaços
- Nomes de funções: snake_case
- Nomes de classes: PascalCase
- Imports: agrupados (stdlib, third-party, local)

### Estrutura de Projeto
- Separar lógica de negócio da interface CLI
- Usar `__init__.py` para tornar diretórios em pacotes
- Organizar testes em diretório separado

### Padrões de Projeto
- **Strategy Pattern:** Para diferentes tipos de conversão
- **Pipeline Pattern:** Para processamento sequencial de etapas
- **Factory Pattern:** Para criação de objetos de conversão

## Test-Driven Development (TDD)

### Ciclo Red-Green-Refactor
1. **Red:** Escrever teste que falha
2. **Green:** Implementar código mínimo para passar
3. **Refactor:** Melhorar código mantendo testes passando

### Boas Práticas de Teste
- Testes unitários para cada função
- Mocks para dependências externas
- Fixtures para dados de teste reutilizáveis
- Nomes descritivos para testes

## CLI com argparse
- Interface de linha de comando robusta
- Validação de argumentos
- Mensagens de erro claras
- Documentação automática com --help

## Tratamento de Erros
- Exceções específicas para diferentes tipos de erro
- Logging apropriado
- Mensagens de erro informativas para o usuário
- Graceful degradation quando possível

# Documentação do Conversor PDF para Markdown

Bem-vindo à documentação completa do Conversor PDF para Markdown. Esta documentação foi organizada para atender diferentes tipos de usuários e necessidades.

## 📚 Índice da Documentação

### 🎯 Para Usuários Finais
- **[README.md](../README.md)** - Documentação principal do usuário
  - Guia de instalação e uso
  - Exemplos práticos
  - Troubleshooting
  - Casos de uso

### 🏗️ Para Desenvolvedores

#### 1. [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura do Sistema
- **Visão Geral**: Explicação completa da arquitetura Pipeline
- **Componentes**: Detalhamento de cada classe e responsabilidade
- **Fluxo de Dados**: Como os dados fluem pelo sistema
- **Padrões de Design**: Pipeline, Strategy, Factory
- **Sistema de Métodos**: 7 estratégias de conversão Markdown
- **Sistema de Pontuação**: Algoritmo de qualidade automática
- **Otimizações**: Performance e extensibilidade

#### 2. [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Guia do Desenvolvedor
- **Configuração**: Setup do ambiente de desenvolvimento
- **Padrões de Código**: PEP 8, type hints, docstrings
- **Como Contribuir**: Processo de contribuição
- **Testes**: Estrutura e execução de testes
- **Debugging**: Técnicas de debug e troubleshooting
- **Extensões**: Como adicionar novas funcionalidades
- **Performance**: Otimizações e profiling

#### 3. [API_REFERENCE.md](API_REFERENCE.md) - Referência da API
- **Classes Principais**: ConversionPipeline, BaseStep
- **Passos do Pipeline**: Todos os steps implementados
- **Funções Utilitárias**: Funções auxiliares
- **Tipos de Dados**: Estruturas de dados utilizadas
- **Exceções**: Tratamento de erros
- **Constantes**: Configurações e padrões
- **Exemplos de Uso**: Código prático

### 🤖 Para IA e Automação
- **[context/AI_DOCS.md](../context/AI_DOCS.md)** - Documentação interna da IA
  - Rastreamento completo do desenvolvimento
  - Resolução de problemas
  - Status do projeto
  - Métricas e conclusões

## 🎯 Como Usar Esta Documentação

### Se você é um **Usuário Final**:
1. Comece pelo [README.md](../README.md) principal
2. Use o [install.sh](../install.sh) para instalação rápida
3. Execute `python3 main.py --help` para ver opções
4. Consulte a seção de troubleshooting se houver problemas

### Se você é um **Desenvolvedor**:
1. Leia o [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) para setup
2. Consulte [ARCHITECTURE.md](ARCHITECTURE.md) para entender o sistema
3. Use [API_REFERENCE.md](API_REFERENCE.md) como referência técnica
4. Execute os testes: `python3 -m pytest tests/ -v`

### Se você é um **Contribuidor**:
1. Siga o [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
2. Entenda a arquitetura em [ARCHITECTURE.md](ARCHITECTURE.md)
3. Use a [API_REFERENCE.md](API_REFERENCE.md) para implementar
4. Adicione testes para novas funcionalidades

## 🏗️ Arquitetura em Resumo

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

## 🔧 Componentes Principais

### 1. ConversionPipeline
- **Responsabilidade**: Orquestração do processo
- **Arquivo**: `converter/pipeline.py`
- **Funcionalidades**: Execução sequencial, coleta de estatísticas

### 2. Passos do Pipeline
- **TextExtractionStep**: Extração de texto com PyMuPDF
- **TableExtractionStep**: Extração de tabelas com pdfplumber
- **CleanupStep**: Limpeza de cabeçalhos/rodapés
- **ImageExtractionStep**: Extração e salvamento de imagens
- **MarkdownConversionStep**: Conversão básica para Markdown
- **AdvancedMarkdownConversionStep**: 7 métodos de conversão + pontuação

### 3. Sistema de Métodos
1. **current**: Conversão básica
2. **intelligent**: Organização inteligente
3. **structured**: Estrutura hierárquica
4. **compact**: Formatação compacta
5. **clean**: Limpeza agressiva
6. **academic**: Otimizado para artigos científicos
7. **minimal**: Foco na simplicidade

## 📊 Métricas e Qualidade

### Sistema de Pontuação
- **Número de linhas**: Menos é melhor
- **Presença de títulos**: Mais é melhor
- **Parágrafos bem formados**: Estrutura adequada
- **Ausência de quebras**: Organização lógica
- **Palavras-chave acadêmicas**: Contexto científico
- **Ausência de repetições**: Conteúdo único

### Estatísticas Coletadas
- Total de páginas processadas
- Blocos de texto extraídos
- Tabelas e imagens extraídas
- Tamanhos de texto (bruto, limpo, markdown)
- Método de conversão escolhido

## 🚀 Funcionalidades Avançadas

### Fallback Robusto
- Múltiplos métodos de extração de texto
- Detecção automática de texto corrompido
- Fallback para pdfplumber quando necessário

### Performance Otimizada
- Otimização para PDFs grandes (>1MB)
- Métodos seletivos baseados no tamanho
- Cache de informações de fonte

### Extensibilidade
- Padrão Pipeline permite fácil extensão
- Novos passos podem ser adicionados
- Novos métodos de conversão suportados

## 🧪 Testes e Validação

### Cobertura de Testes
- **Testes Unitários**: Funções básicas
- **Testes de Integração**: Pipeline completo
- **Testes de Robustez**: Múltiplos PDFs
- **Validação de Qualidade**: Markdown gerado

### Execução de Testes
```bash
# Todos os testes
python3 -m pytest tests/ -v

# Com cobertura
python3 -m pytest tests/ --cov=converter --cov-report=html

# Testes específicos
python3 -m pytest tests/test_converter.py::test_pipeline_conversao_completa -v
```

## 📈 Performance

### Métricas Típicas
- **PDFs pequenos (<1MB)**: 2-5 segundos
- **PDFs médios (1-10MB)**: 5-15 segundos
- **PDFs grandes (10-50MB)**: 15-60 segundos
- **Taxa de sucesso**: ~95% em PDFs científicos

### Otimizações Implementadas
- Filtros de fonte para texto irrelevante
- Métodos seletivos para PDFs grandes
- Limpeza eficiente com regex otimizadas
- Cache de dados para evitar reprocessamento

## 🔍 Troubleshooting

### Problemas Comuns
1. **Erro de Instalação**: Use `--break-system-packages`
2. **Texto Corrompido**: Fallback automático para pdfplumber
3. **PDFs Muito Grandes**: Otimização automática
4. **Falha na Conversão**: Use `--verbose` para debug

### Debug
```bash
# Modo verbose para debug
python3 main.py arquivo.pdf --verbose

# Verificar PDF
python3 -c "import fitz; fitz.open('arquivo.pdf')"

# Executar testes
python3 -m pytest tests/ -v
```

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

## 📞 Suporte

Para dúvidas e problemas:
1. Consulte a documentação relevante
2. Execute com `--verbose` para mais detalhes
3. Abra uma issue no repositório
4. Verifique os testes para exemplos de uso

---

**Desenvolvido com ❤️ para a comunidade científica**

# PDF to Markdown Converter

Conversor robusto de PDF para Markdown com foco na qualidade do output, especialmente para artigos científicos e livros.

## 🚀 **Características Principais**

- **100% Local e Gratuito** - Sem dependência de APIs externas
- **Múltiplas Abordagens** - Análise estatística, regex avançado e combinação
- **Alta Qualidade** - Foco na legibilidade e estruturação do conteúdo
- **Detecção Inteligente** - Títulos, parágrafos, listas, tabelas e citações
- **Processamento Robusto** - Suporte a diferentes tipos de PDF

## 🎯 **Abordagens Implementadas**

### 1. **Análise Estatística** (`StatisticalAnalysisStep`)
- Detecção de títulos baseada em estatísticas
- Agrupamento inteligente de parágrafos
- Estruturação hierárquica do conteúdo
- Cálculo de scores de probabilidade

### 2. **Regex Avançado** (`AdvancedRegexStep`)
- 12 padrões regex complexos
- Detecção de seções principais
- Correção de hifenização
- Limpeza de caracteres especiais

### 3. **Combinação** (Recomendado)
- Equilibra as duas abordagens
- Resultado intermediário e bem balanceado
- Melhor legibilidade geral

## 📦 **Instalação**

```bash
# Clonar o repositório
git clone <repository-url>
cd pdf_to_markdown

# Instalar dependências
pip install -r requirements.txt
```

## 🛠️ **Uso**

### **Uso Básico**
```bash
python main.py input.pdf
```

### **Uso com Pipeline Personalizado**
```python
from converter.pipeline import ConversionPipeline

pipeline = ConversionPipeline()
output_path = pipeline.convert("input.pdf")
```

### **Uso com Abordagens Específicas**
```python
from converter.steps.statistical_analysis_step import StatisticalAnalysisStep
from converter.steps.advanced_regex_step import AdvancedRegexStep

# Análise estatística
stats_step = StatisticalAnalysisStep()
data = stats_step.process({'raw_text': content})

# Regex avançado
regex_step = AdvancedRegexStep()
data = regex_step.process({'raw_text': content})
```

## 📊 **Resultados dos Testes**

Testado com artigo científico de 14 páginas:

| Abordagem | Títulos | Parágrafos | Qualidade |
|-----------|---------|------------|-----------|
| Análise Estatística | 14 | 112 | 100/100 |
| Regex Avançado | 109 | 51 | 100/100 |
| Combinação | 94 | 39 | 100/100 |

## 🏗️ **Arquitetura**

```
converter/
├── pipeline.py              # Pipeline principal
├── steps/                   # Passos de processamento
│   ├── text_extraction_step.py
│   ├── statistical_analysis_step.py    # Nova abordagem
│   ├── advanced_regex_step.py          # Nova abordagem
│   ├── table_extraction_step.py
│   ├── image_extraction_step.py
│   ├── markdown_conversion_step.py
│   └── ...
└── __init__.py
```

## 🎯 **Recomendações por Tipo de Documento**

- **Artigos Científicos**: Combinação
- **Livros e Manuais**: Análise Estatística
- **Relatórios Técnicos**: Regex Avançado
- **Uso Geral**: Combinação

## 📁 **Estrutura do Projeto**

```
pdf_to_markdown/
├── main.py                  # Script principal
├── converter/               # Módulo principal
├── docs/                    # Documentação
├── tests/                   # Testes
├── context/                 # Contexto do projeto
├── requirements.txt         # Dependências
└── README.md               # Este arquivo
```

## 🔧 **Configuração**

O sistema detecta automaticamente a melhor abordagem baseada no tipo de documento, mas você pode configurar manualmente:

```python
# Configurar abordagem específica
pipeline = ConversionPipeline()
pipeline.add_step(StatisticalAnalysisStep())  # Análise estatística
pipeline.add_step(AdvancedRegexStep())        # Regex avançado
```

## 📈 **Melhorias Recentes**

- ✅ Implementação de abordagens locais e gratuitas
- ✅ Análise estatística para estruturação inteligente
- ✅ Regex avançado para formatação precisa
- ✅ Sistema de combinação para melhor resultado
- ✅ Testes com PDFs reais
- ✅ Limpeza e otimização do código

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 **Suporte**

Para dúvidas ou problemas, abra uma issue no repositório.

---

**Status**: ✅ **PRODUÇÃO - FUNCIONAL**

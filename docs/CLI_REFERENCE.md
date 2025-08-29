# CLI Reference - PDF to Markdown Converter

## Visão Geral

O PDF to Markdown Converter oferece uma interface de linha de comando robusta para conversão de artigos científicos de PDF para Markdown, com análise linguística avançada e detecção inteligente de estruturas.

## Instalação e Configuração

### Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt

# Instalar Tesseract OCR (para funcionalidade OCR)
sudo apt install tesseract-ocr tesseract-ocr-eng
```

### Uso Básico

```bash
# Usar o script wrapper (recomendado)
./pdf2md [comando] [opções]

# Ou usar diretamente
python main.py [comando] [opções]
```

## Comandos Principais

### 1. Conversão de PDFs

#### Converter um único PDF

```bash
# Conversão básica
./pdf2md convert single documento.pdf

# Com diretório de saída personalizado
./pdf2md convert single documento.pdf --output ./markdown/

# Modo verboso
./pdf2md convert single documento.pdf --output ./markdown/ --verbose
```

#### Converter todos os PDFs de um diretório

```bash
# Conversão em lote
./pdf2md convert batch ./pdfs/

# Com diretório de saída personalizado
./pdf2md convert batch ./pdfs/ --output ./markdown/

# Modo verboso
./pdf2md convert batch ./pdfs/ --output ./markdown/ --verbose
```

### 2. Análise Crítica com Fidelidade

```bash
# Análise completa com métricas de fidelidade
./pdf2md analyze ./pdfs/ --output ./markdown/ --verbose

# Com relatório JSON
./pdf2md analyze ./pdfs/ --output ./markdown/ --report relatorio.json --verbose
```

**Métricas de Fidelidade:**
- **EXCELENTE (≥95%)**: Conversão de alta qualidade
- **BOM (85-94%)**: Conversão satisfatória
- **REGULAR (70-84%)**: Conversão aceitável com melhorias necessárias
- **POBRE (<70%)**: Conversão com problemas significativos

### 3. Testes e Validações

#### Testar Detecção de Títulos

```bash
# Teste padrão
./pdf2md test titles --verbose

# Teste com casos específicos
./pdf2md test titles --cases "Abstract,Introduction,Methods,do,da,de" --verbose

# Salvar resultado em JSON
./pdf2md test titles --output resultado_titulos.json --verbose
```

## Opções Globais

### Modo Verboso (`--verbose`, `-v`)

Ativa saída detalhada com informações de progresso, métricas e estatísticas.

### Diretório de Saída (`--output`, `-o`)

Especifica o diretório onde os arquivos Markdown serão salvos.

### Relatórios (`--report`, `-r`)

Salva relatórios detalhados em formato JSON para análise posterior.

## Exemplos de Uso

### Exemplo 1: Conversão Simples

```bash
# Converter um artigo científico
./pdf2md convert single artigo.pdf --output ./artigos/ --verbose
```

**Saída:**
```
🔄 Convertendo: artigo.pdf
✅ Conversão concluída: ./artigos/artigo.md
📊 Tamanho: 15,432 caracteres
```

### Exemplo 2: Processamento em Lote com Análise

```bash
# Processar todos os artigos com análise crítica
./pdf2md analyze ./artigos_pdf/ --output ./artigos_md/ --report analise.json --verbose
```

**Saída:**
```
📁 Encontrados 44 PDFs em ./artigos_pdf/

[1/44] 🔍 ANÁLISE CRÍTICA: artigo1.pdf
  📊 Fidelidade: 92.3% - BOM
  📏 Tamanho: 15,432 chars
  📋 Linhas: 234
  🏷️  Headers: 8
  ✅ Sem problemas críticos
  💾 Salvo: ./artigos_md/artigo1.md

...

🎯 RESULTADOS DA ANÁLISE CRÍTICA
================================================================================
📁 Total processado: 44/44
⏱️  Tempo total: 127.3 segundos
🎯 Fidelidade média: 87.2%

📈 DISTRIBUIÇÃO DE QUALIDADE:
  🎉 EXCELENTE (≥95%): 12 arquivos
  👍 BOM (85-94%): 18 arquivos
  ⚠️  REGULAR (70-84%): 10 arquivos
  ❌ POBRE (<70%): 2 arquivos
  💥 FALHAS: 2 arquivos
```

### Exemplo 3: Teste de Detecção de Títulos

```bash
# Testar algoritmo de detecção
./pdf2md test titles --verbose
```

**Saída:**
```
🔍 TESTE DE DETECÇÃO DE TÍTULOS
============================================================
✅ TÍTULO: 'Abstract'
✅ TÍTULO: 'Introduction'
✅ TÍTULO: 'Methods'
✅ TÍTULO: 'Results'
✅ TÍTULO: 'Discussion'
✅ TÍTULO: 'Conclusion'
❌ REJEITADO: 'do'
❌ REJEITADO: 'da'
❌ REJEITADO: 'de'
❌ REJEITADO: 'Davi'
❌ REJEITADO: 'Saul'

📊 RESULTADOS:
   Títulos detectados: 12
   Títulos rejeitados: 31
   Acurácia estimada: 100.0%
```

## Estrutura de Arquivos de Saída

### Arquivos Markdown

Os arquivos Markdown gerados seguem a estrutura:

```markdown
# Título Principal

## Abstract

Conteúdo do resumo...

## Introduction

Conteúdo da introdução...

## Methods

Descrição dos métodos...

## Results

Resultados obtidos...

## Discussion

Discussão dos resultados...

## Conclusion

Conclusões...

## References

Lista de referências...
```

### Relatórios JSON

Os relatórios JSON contêm:

```json
{
  "total_files": 44,
  "processed": 42,
  "failures": 2,
  "excellent": 12,
  "good": 18,
  "regular": 10,
  "poor": 2,
  "total_fidelity_score": 3662.4,
  "elapsed_time": 127.3,
  "results": {
    "artigo1.pdf": {
      "fidelity_score": 92.3,
      "status": "BOM",
      "total_chars": 15432,
      "total_lines": 234,
      "headers_count": 8,
      "empty_ratio": 0.15,
      "critical_issues": []
    }
  }
}
```

## Troubleshooting

### Problemas Comuns

1. **Erro: PDF não encontrado**
   ```bash
   # Verificar se o arquivo existe
   ls -la documento.pdf
   ```

2. **Erro: Nenhum PDF encontrado**
   ```bash
   # Verificar se há PDFs no diretório
   ls -la *.pdf
   ```

3. **Erro de permissão**
   ```bash
   # Dar permissão de execução
   chmod +x pdf2md
   ```

4. **Erro de dependências**
   ```bash
   # Reinstalar dependências
   pip install -r requirements.txt
   ```

### Logs e Debug

Use o modo verboso para obter informações detalhadas:

```bash
./pdf2md convert single documento.pdf --verbose
```

## Integração com Outras Ferramentas

### Scripts de Automação

```bash
#!/bin/bash
# Script para processar novos artigos

INPUT_DIR="./novos_artigos"
OUTPUT_DIR="./artigos_processados"
REPORT_FILE="relatorio_$(date +%Y%m%d_%H%M%S).json"

./pdf2md analyze "$INPUT_DIR" --output "$OUTPUT_DIR" --report "$REPORT_FILE" --verbose

# Enviar relatório por email
mail -s "Relatório de Conversão" usuario@exemplo.com < "$REPORT_FILE"
```

### Integração com Git

```bash
# Processar artigos e commitar mudanças
./pdf2md convert batch ./artigos/ --output ./markdown/
git add ./markdown/
git commit -m "Atualizar conversões de artigos"
```

## Performance e Otimização

### Dicas de Performance

1. **Processamento em lote**: Use `convert batch` para múltiplos arquivos
2. **Diretório de saída**: Especifique um diretório SSD para melhor performance
3. **Modo não-verboso**: Use sem `--verbose` para processamento mais rápido

### Monitoramento de Recursos

```bash
# Monitorar uso de CPU e memória
top -p $(pgrep -f "python.*main.py")

# Monitorar uso de disco
watch -n 1 "du -sh ./markdown/"
```

## Suporte e Contribuição

Para reportar bugs ou solicitar funcionalidades:

1. Verifique a documentação
2. Use o modo verboso para coletar logs
3. Inclua exemplos de PDFs problemáticos
4. Descreva o comportamento esperado vs. atual

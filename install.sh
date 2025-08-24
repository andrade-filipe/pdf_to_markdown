#!/bin/bash
# Script de instalação para o Conversor de PDF para Markdown

echo "🚀 Instalando Conversor de PDF para Markdown..."

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verificar se pip está disponível
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip não encontrado. Tentando instalar..."
    sudo apt update
    sudo apt install python3-pip python3-full python3-venv
fi

echo "✅ pip encontrado: $(python3 -m pip --version)"

# Instalar dependências
echo "📦 Instalando dependências..."

# Tentar instalar com --break-system-packages se necessário
if python3 -m pip install -r requirements.txt &> /dev/null; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "⚠️  Tentando instalar com --break-system-packages..."
    python3 -m pip install --break-system-packages -r requirements.txt
    echo "✅ Dependências instaladas com sucesso!"
fi

# Testar se tudo está funcionando
echo "🧪 Testando instalação..."
if python3 -c "import fitz, pdfplumber, PIL; print('✅ Todas as dependências estão funcionando!')" 2>/dev/null; then
    echo "✅ Instalação concluída com sucesso!"
    echo ""
    echo "📖 Para usar o conversor:"
    echo "   python3 main.py arquivo.pdf"
    echo ""
    echo "📖 Para ver a ajuda:"
    echo "   python3 main.py --help"
else
    echo "❌ Erro na instalação. Verifique as dependências."
    exit 1
fi

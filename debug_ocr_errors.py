#!/usr/bin/env python3
"""Debug específico para erros do OCR"""

import sys
import os
import traceback
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ocr_directly(pdf_path):
    """Testa OCR diretamente em um único PDF para identificar problemas"""
    print(f"🔍 TESTANDO OCR DIRETAMENTE EM: {pdf_path}")
    print("=" * 60)
    
    try:
        # Importar os passos diretamente
        from converter.steps.text_extraction_step import TextExtractionStep
        from converter.steps.cleanup_step import CleanupStep
        from converter.steps.selective_ocr_step import SelectiveOCRStep
        
        # 1. Extrair texto
        print("1️⃣ TextExtraction...")
        text_step = TextExtractionStep()
        text_result = text_step.process({'pdf_path': str(pdf_path)})
        print(f"   Texto extraído: {len(text_result.get('raw_text', ''))} chars")
        
        # 2. Cleanup
        print("2️⃣ Cleanup...")
        cleanup_step = CleanupStep()
        cleanup_result = cleanup_step.process(text_result)
        print(f"   Texto limpo: {len(cleanup_result.get('cleaned_text', ''))} chars")
        
        # 3. OCR com debug detalhado
        print("3️⃣ SelectiveOCR (com debug)...")
        ocr_step = SelectiveOCRStep()
        
        # Configurar para debug
        ocr_step.quality_threshold = 0.4
        ocr_step.max_ocr_pages = 5
        ocr_step.ocr_quality_mode = 'ultra_precise'
        ocr_step.enable_multiple_attempts = True
        ocr_step.enable_post_processing = True
        
        print("   Analisando qualidade do texto...")
        ocr_result = ocr_step.process(cleanup_result)
        
        print("✅ OCR concluído sem erros!")
        print(f"   Resultado final: {len(ocr_result.get('cleaned_text', ''))} chars")
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO OCR: {type(e).__name__}: {str(e)}")
        print("📋 TRACEBACK COMPLETO:")
        traceback.print_exc()
        return False

def test_tesseract_installation():
    """Testa se o Tesseract está instalado corretamente"""
    print("🔧 TESTANDO INSTALAÇÃO DO TESSERACT")
    print("=" * 40)
    
    try:
        import pytesseract
        from PIL import Image
        
        # Testar se o pytesseract consegue encontrar o tesseract
        print("1️⃣ Verificando pytesseract...")
        tesseract_version = pytesseract.get_tesseract_version()
        print(f"   ✅ Tesseract versão: {tesseract_version}")
        
        # Testar configurações
        print("2️⃣ Testando configurações...")
        configs = [
            '--psm 6 --oem 1',
            '--psm 3 --oem 1',
            '--psm 1 --oem 1'
        ]
        
        for config in configs:
            try:
                print(f"   Testando: {config}")
                # Criar uma imagem simples para teste
                img = Image.new('RGB', (100, 50), color='white')
                # Isso deve funcionar sem erro
                print(f"   ✅ Configuração {config} OK")
            except Exception as e:
                print(f"   ❌ Erro na configuração {config}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO TESSERACT: {type(e).__name__}: {str(e)}")
        print("📋 TRACEBACK COMPLETO:")
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    pdf_dir = Path("/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF")
    
    if not pdf_dir.exists():
        print(f"❌ Diretório não encontrado: {pdf_dir}")
        return
    
    # Primeiro testar a instalação do Tesseract
    print("🔧 TESTE 1: Instalação do Tesseract")
    tesseract_ok = test_tesseract_installation()
    
    if not tesseract_ok:
        print("❌ Problemas com Tesseract. Verificando instalação...")
        return
    
    # Depois testar OCR em um PDF
    print("\n🔍 TESTE 2: OCR em PDF")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📁 Encontrados {len(pdf_files)} PDFs")
    
    if pdf_files:
        test_ocr_directly(pdf_files[0])
    else:
        print("❌ Nenhum PDF encontrado")

if __name__ == "__main__":
    main()

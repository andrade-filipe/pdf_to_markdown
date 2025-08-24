"""Passo de extração de texto do PDF"""

import fitz  # PyMuPDF
from typing import Dict, Any, List
from .base_step import BaseStep


class TextExtractionStep(BaseStep):
    """Passo responsável por extrair texto do PDF com informações de fonte"""
    
    def __init__(self):
        super().__init__("TextExtraction")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai texto do PDF com informações de fonte e posição"""
        pdf_path = data.get('pdf_path')
        if not pdf_path:
            raise ValueError("pdf_path é obrigatório")
        
        # Abrir o PDF
        doc = fitz.open(pdf_path)
        extracted_data = {
            'text_blocks': [],
            'font_info': [],
            'total_pages': len(doc),
            'raw_text': ""
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Tentar diferentes métodos de extração
            page_text = ""
            
            # Método 1: Extração simples
            try:
                page_text = page.get_text()
            except:
                pass
            
            # Método 2: Extração com HTML (às vezes funciona melhor)
            if not page_text.strip():
                try:
                    page_text = page.get_text("html")
                    # Limpar tags HTML
                    import re
                    page_text = re.sub(r'<[^>]+>', '', page_text)
                except:
                    pass
            
            # Método 3: Extração por blocos
            if not page_text.strip():
                try:
                    blocks = page.get_text("dict")
                    page_text = ""
                    for block in blocks.get("blocks", []):
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    page_text += span['text'] + " "
                except:
                    pass
            
            if page_text.strip():
                extracted_data['raw_text'] += page_text + "\n\n"
            
            # Extrair informações de fonte para detecção de títulos
            try:
                blocks = page.get_text("dict")
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                # Filtrar texto muito pequeno ou vazio
                                if len(span['text'].strip()) > 0 and span['size'] > 6:
                                    font_info = {
                                        'text': span['text'],
                                        'tamanho': span['size'],
                                        'posicao': (span['bbox'][0], span['bbox'][1]),
                                        'pagina': page_num + 1,
                                        'fonte': span['font']
                                    }
                                    extracted_data['font_info'].append(font_info)
                                    extracted_data['text_blocks'].append(span['text'])
            except:
                pass
        
        doc.close()
        
        # Verificar se o texto extraído está muito corrompido
        if extracted_data['raw_text'] and self._is_text_corrupted(extracted_data['raw_text']):
            print(f"⚠️  Texto corrompido detectado, tentando método alternativo...")
            # Tentar método alternativo usando pdfplumber
            extracted_data['raw_text'] = self._extract_with_pdfplumber(pdf_path)
        
        # Adicionar dados extraídos ao contexto
        data.update(extracted_data)
        return data
    
    def _is_text_corrupted(self, text: str) -> bool:
        """Detecta se o texto está corrompido"""
        if not text:
            return True
        
        # Contar caracteres estranhos
        strange_chars = sum(1 for char in text if ord(char) > 127 and char not in 'áéíóúâêîôûãõçàèìòùäëïöüñ')
        total_chars = len(text)
        
        # Se mais de 15% dos caracteres são estranhos, considerar corrompido
        return strange_chars / total_chars > 0.15 if total_chars > 0 else True
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extrai texto usando pdfplumber como fallback"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            return text
        except Exception as e:
            print(f"⚠️  Erro no fallback pdfplumber: {e}")
            return ""

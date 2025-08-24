"""Passo de extração de imagens do PDF"""

import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path
from typing import Dict, Any, List
from .base_step import BaseStep


class ImageExtractionStep(BaseStep):
    """Passo responsável por extrair imagens do PDF"""
    
    def __init__(self, output_dir: str):
        super().__init__("ImageExtraction")
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai imagens do PDF e salva em diretório local"""
        pdf_path = data.get('pdf_path')
        if not pdf_path:
            raise ValueError("pdf_path é obrigatório")
        
        extracted_images = []
        
        # Abrir o PDF
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extrair imagens da página
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Obter dados da imagem
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # Verifica se é RGB ou CMYK
                        # Converter para RGB se necessário
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    
                    # Converter para PIL Image
                    img_data = pix.tobytes("png")
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Salvar imagem
                    img_filename = f"imagem_p{page_num+1}_{img_index+1}.png"
                    img_path = self.images_dir / img_filename
                    pil_image.save(img_path)
                    
                    # Adicionar informações da imagem
                    image_info = {
                        'pagina': page_num + 1,
                        'numero': img_index + 1,
                        'caminho': str(img_path),
                        'caminho_relativo': f"./images/{img_filename}",
                        'nome_arquivo': img_filename
                    }
                    extracted_images.append(image_info)
                    
                    pix = None  # Liberar memória
                    
                except Exception as e:
                    print(f"Erro ao extrair imagem {img_index} da página {page_num + 1}: {e}")
                    continue
        
        doc.close()
        
        # Adicionar imagens extraídas ao contexto
        data['images'] = extracted_images
        return data

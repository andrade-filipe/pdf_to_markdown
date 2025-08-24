import pytest
import os
import tempfile
from pathlib import Path

# Importações das funções de conversão
from converter.converter import (
    converter_texto,
    converter_tabela,
    limpar_texto,
    processar_imagem,
    detectar_titulos
)

# Importações do pipeline
from converter.pipeline import ConversionPipeline
from converter.steps.text_extraction_step import TextExtractionStep
from converter.steps.table_extraction_step import TableExtractionStep
from converter.steps.cleanup_step import CleanupStep
from converter.steps.image_extraction_step import ImageExtractionStep


class TestPDFToMarkdownConverter:
    """Testes para o conversor de PDF para Markdown"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_converte_titulo_e_paragrafo(self):
        """Teste de conversão de títulos e parágrafos"""
        # Simule o texto extraído de um PDF
        texto_pdf = "1. Introdução\nEste é o primeiro parágrafo."
        resultado_esperado = "# 1. Introdução\n\nEste é o primeiro parágrafo."
        
        resultado = converter_texto(texto_pdf)
        assert resultado == resultado_esperado
    
    def test_converte_tabela_simples(self):
        """Teste de conversão de tabela simples"""
        # Simule uma tabela extraída
        tabela_pdf = [["Coluna A", "Coluna B"], ["Dado 1", "Dado 2"], ["Dado 3", "Dado 4"]]
        resultado_esperado = "| Coluna A | Coluna B |\n|---|---|\n| Dado 1 | Dado 2 |\n| Dado 3 | Dado 4 |"
        
        resultado = converter_tabela(tabela_pdf)
        assert resultado == resultado_esperado
    
    def test_remove_cabecalho_rodape(self):
        """Teste de remoção de cabeçalho/rodapé"""
        texto_pagina = "Conteúdo principal da página.\n\nNome do Artigo - Página 5"
        resultado_esperado = "Conteúdo principal da página."
        
        resultado = limpar_texto(texto_pagina)
        assert resultado == resultado_esperado
    
    def test_extrai_e_referencia_imagem(self):
        """Teste de extração e referência de imagem"""
        # Simule a extração de uma imagem de um PDF
        caminho_imagem_salva = "output/images/imagem_1.png"
        resultado_esperado = "![imagem_1.png](./images/imagem_1.png)"
        
        resultado = processar_imagem(caminho_imagem_salva)
        assert resultado == resultado_esperado
    
    def test_detecta_titulo_por_tamanho_fonte(self):
        """Teste de detecção de título por tamanho da fonte"""
        # Simule dados de fonte extraídos
        dados_fonte = [
            {"texto": "Introdução", "tamanho": 16, "posicao": (50, 100)},
            {"texto": "Este é um parágrafo", "tamanho": 12, "posicao": (50, 150)}
        ]
        resultado_esperado = "# Introdução\n\nEste é um parágrafo"
        
        resultado = detectar_titulos(dados_fonte)
        assert resultado == resultado_esperado
    
    def test_pipeline_conversao_completa(self):
        """Teste do pipeline completo de conversão"""
        # Criar um arquivo PDF de teste simples
        import fitz
        
        # Criar PDF de teste
        pdf_path = self.output_dir / "teste.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "1. Introdução", fontsize=16)
        page.insert_text((50, 100), "Este é o primeiro parágrafo.", fontsize=12)
        doc.save(str(pdf_path))
        doc.close()
        
        # Testar pipeline
        pipeline = ConversionPipeline(str(self.output_dir))
        resultado = pipeline.convert(str(pdf_path))
        
        assert resultado.exists()
        assert resultado.suffix == ".md"
        
        # Verificar conteúdo
        with open(resultado, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Introdução" in content


if __name__ == "__main__":
    pytest.main([__file__])

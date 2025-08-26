#!/usr/bin/env python3
"""
Script para analisar detalhadamente o conflito de processamento
"""

import os
import sys
from pathlib import Path
import re

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from converter.pipeline import ConversionPipeline

def analyze_processing_steps():
    """Analisa cada step do processamento para identificar conflitos"""
    
    # Arquivo para testar
    pdf_path = "/home/andrade/Documentos/Meus Ebooks/Genesis: The Correct Timeline/Referencias em PDF/Mount St. Helens and Catastrophism.pdf"
    test_output_dir = "/tmp/analyze_conflict"
    
    print("🔍 ANÁLISE DETALHADA DO PROCESSAMENTO")
    print("="*60)
    
    # Criar pipeline
    pipeline = ConversionPipeline(test_output_dir)
    
    # Interceptar dados entre cada step para análise
    original_data = pipeline.current_data.copy()
    
    print(f"\n📄 ARQUIVO DE TESTE: {Path(pdf_path).name}")
    print(f"📁 DIRETÓRIO DE TESTE: {test_output_dir}")
    
    # Simular execução step por step
    pipeline.current_data = {
        'pdf_path': pdf_path,
        'output_dir': test_output_dir
    }
    
    print(f"\n🔄 SIMULANDO PROCESSAMENTO STEP POR STEP:")
    print("-" * 40)
    
    for i, step in enumerate(pipeline.steps):
        print(f"\n{i+1}. Executando: {step.name}")
        
        try:
            # Executar step
            pipeline.current_data = step.process(pipeline.current_data)
            
            # Analisar dados após o step
            analyze_step_output(step.name, pipeline.current_data)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            break

def analyze_step_output(step_name, data):
    """Analisa a saída de cada step"""
    
    print(f"   📊 Dados após {step_name}:")
    
    if step_name == "MarkdownConversion":
        # Analisar otimização de parágrafos
        markdown_content = data.get('markdown_content', '')
        if markdown_content:
            lines = markdown_content.split('\n')
            empty_lines = len([l for l in lines if not l.strip()])
            total_lines = len(lines)
            
            print(f"      - Linhas totais: {total_lines}")
            print(f"      - Linhas vazias: {empty_lines}")
            print(f"      - Taxa de linhas vazias: {empty_lines/total_lines*100:.1f}%")
            
            # Mostrar amostra
            sample = markdown_content[:300] + "..." if len(markdown_content) > 300 else markdown_content
            print(f"      - Amostra: {sample}")
    
    elif step_name == "AdvancedMarkdownConversion":
        # Analisar seleção de método
        method_chosen = data.get('method_chosen', 'unknown')
        all_methods = data.get('all_methods', {})
        
        print(f"      - Método escolhido: {method_chosen}")
        print(f"      - Métodos disponíveis: {list(all_methods.keys())}")
        
        # Analisar conteúdo final
        markdown_content = data.get('markdown_content', '')
        if markdown_content:
            lines = markdown_content.split('\n')
            empty_lines = len([l for l in lines if not l.strip()])
            total_lines = len(lines)
            
            print(f"      - Linhas finais: {total_lines}")
            print(f"      - Linhas vazias finais: {empty_lines}")
            print(f"      - Taxa final de linhas vazias: {empty_lines/total_lines*100:.1f}%")
            
            # Mostrar amostra final
            sample = markdown_content[:300] + "..." if len(markdown_content) > 300 else markdown_content
            print(f"      - Amostra final: {sample}")

def analyze_method_compact():
    """Analisa especificamente o método compact"""
    
    print(f"\n🔍 ANÁLISE ESPECÍFICA DO MÉTODO COMPACT")
    print("-" * 40)
    
    # Simular entrada típica
    sample_input = """# Título 1
Título 1

Texto da primeira linha que deveria ser juntado
com a segunda linha relacionada.

# Título 2
Outro parágrafo que também deveria ser otimizado
mas está sendo quebrado desnecessariamente.

Lista de itens:
- Item 1
- Item 2
- Item 3"""
    
    print("📥 ENTRADA SIMULADA:")
    print(sample_input)
    print("-" * 40)
    
    # Simular método compact
    result = simulate_method_compact(sample_input)
    
    print("📤 SAÍDA DO MÉTODO COMPACT:")
    print(result)
    print("-" * 40)
    
    # Analisar diferenças
    input_lines = [l for l in sample_input.split('\n') if l.strip()]
    output_lines = [l for l in result.split('\n') if l.strip()]
    input_empty = len([l for l in sample_input.split('\n') if not l.strip()])
    output_empty = len([l for l in result.split('\n') if not l.strip()])
    
    print("📊 COMPARAÇÃO:")
    print(f"   - Linhas de entrada: {len(input_lines)}")
    print(f"   - Linhas de saída: {len(output_lines)}")
    print(f"   - Linhas vazias entrada: {input_empty}")
    print(f"   - Linhas vazias saída: {output_empty}")
    print(f"   - Mudança: {(len(output_lines) - len(input_lines)):+d} linhas, {(output_empty - input_empty):+d} vazias")

def simulate_method_compact(content):
    """Simula o método compact para análise"""
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Se é um título, consolidar títulos consecutivos
        if line.startswith('#'):
            # Se o último item também é um título, juntar
            if formatted_lines and formatted_lines[-1].startswith('#'):
                # Juntar títulos consecutivos
                last_title = formatted_lines[-1]
                import re
                clean_last = re.sub(r'^#+\s*', '', last_title)
                clean_current = re.sub(r'^#+\s*', '', line)
                combined_title = f"# {clean_last} {clean_current}".strip()
                formatted_lines[-1] = combined_title
            else:
                formatted_lines.append(line)
        else:
            # Juntar linhas que fazem parte do mesmo contexto
            if formatted_lines and not formatted_lines[-1].startswith('#'):
                # Se a linha anterior não termina com pontuação, juntar
                import re
                if not re.search(r'[.!?]$', formatted_lines[-1]):
                    formatted_lines[-1] += ' ' + line
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
    
    return '\n\n'.join(formatted_lines)

def propose_solutions():
    """Propõe soluções para os problemas identificados"""
    
    print(f"\n💡 SOLUÇÕES PROPOSTAS")
    print("="*60)
    
    print(f"\n🎯 PROBLEMA 1: CONFLITO DE PROCESSAMENTO")
    print("-" * 40)
    print("O método compact está sobrescrevendo as otimizações do MarkdownConversionStep")
    print("\n💡 SOLUÇÃO 1A: Modificar método compact para preservar otimizações")
    print("   - Adicionar verificação se linhas já foram otimizadas")
    print("   - Pular re-processamento se otimização já aplicada")
    print("   - Manter estrutura de parágrafos otimizada")
    
    print(f"\n💡 SOLUÇÃO 1B: Mover otimização para depois da seleção de método")
    print("   - Aplicar otimização de parágrafos após escolha do melhor método")
    print("   - Evitar processamento duplo")
    print("   - Garantir que otimizações sejam preservadas")
    
    print(f"\n💡 SOLUÇÃO 1C: Melhorar pontuação para métodos que preservam otimizações")
    print("   - Adicionar métrica de 'preservação de otimizações'")
    print("   - Penalizar métodos que quebram estrutura otimizada")
    print("   - Dar bônus para métodos que mantêm melhorias")
    
    print(f"\n🎯 PROBLEMA 2: PONTUAÇÃO DE QUALIDADE INCORRETA")
    print("-" * 40)
    print("Método compact recebe score alto mas não melhora conteúdo real")
    
    print(f"\n💡 SOLUÇÃO 2A: Adicionar métrica de densidade de conteúdo")
    print("   - Calcular taxa de linhas vazias vs linhas com conteúdo")
    print("   - Penalizar métodos que geram muitas linhas vazias")
    print("   - Considerar preservação de conteúdo na pontuação")
    
    print(f"\n💡 SOLUÇÃO 2B: Implementar teste de qualidade antes/depois")
    print("   - Comparar métricas antes e depois do processamento")
    print("   - Penalizar métodos que pioram métricas de qualidade")
    print("   - Ajustar pontuação baseado em melhorias reais")
    
    print(f"\n🎯 PROBLEMA 3: PRESERVAÇÃO DE CONTEÚDO")
    print("-" * 40)
    print("Taxa de preservação de 47.7% para palavras no caso problemático")
    
    print(f"\n💡 SOLUÇÃO 3A: Investigar perda de conteúdo na extração")
    print("   - Comparar texto extraído vs texto original do PDF")
    print("   - Identificar onde conteúdo é perdido")
    print("   - Melhorar algoritmo de extração para casos específicos")
    
    print(f"\n💡 SOLUÇÃO 3B: Implementar fallback para textos com baixa preservação")
    print("   - Detectar quando preservação < 50%")
    print("   - Usar métodos alternativos de extração")
    print("   - Aplicar OCR se necessário")

def recommend_best_approach():
    """Recomenda a melhor abordagem baseada na análise"""
    
    print(f"\n🎯 RECOMENDAÇÃO DE ABORDAGEM")
    print("="*60)
    
    print(f"\n🥇 ABORDAGEM RECOMENDADA: Solução 1B + 2A")
    print("-" * 40)
    print("1. Mover otimização para depois da seleção de método")
    print("2. Adicionar métrica de densidade de conteúdo na pontuação")
    print("3. Testar com casos específicos antes de aplicar globalmente")
    
    print(f"\n✅ VANTAGENS:")
    print("- Evita processamento duplo e conflitante")
    print("- Preserva melhorias em todos os métodos")
    print("- Pontuação reflete qualidade real do conteúdo")
    print("- Menor risco de quebrar código existente")
    
    print(f"\n⚠️ RISCOS:")
    print("- Pode afetar a seleção de métodos existente")
    print("- Requer testes extensivos")
    print("- Pode impactar performance")
    
    print(f"\n📋 PLANO DE IMPLEMENTAÇÃO:")
    print("1. Implementar métrica de densidade de conteúdo")
    print("2. Mover otimização para após seleção de método")
    print("3. Testar com Mount St. Helens (caso problemático)")
    print("4. Validar com outros casos conhecidos")
    print("5. Aplicar globalmente se validado")

def main():
    """Função principal"""
    print("🔬 ANÁLISE CRÍTICA DE CONFLITOS DE PROCESSAMENTO")
    print("="*60)
    
    # Análises
    analyze_processing_steps()
    analyze_method_compact()
    propose_solutions()
    recommend_best_approach()
    
    print(f"\n🎉 ANÁLISE CONCLUÍDA!")
    print("Próximo passo: Implementar solução recomendada")

if __name__ == "__main__":
    main()

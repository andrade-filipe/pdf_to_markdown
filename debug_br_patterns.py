#!/usr/bin/env python3
import fitz
import re

def debug_br_patterns(pdf_path):
    """Debuga os padrões exatos das regras de negócio"""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for i in range(len(doc)):
            page = doc[i]
            full_text += page.get_text()
        doc.close()
        
        print(f"\n🔍 Debugando {pdf_path}")
        
        # Procurar por padrões BR
        lines = full_text.split('\n')
        br_lines = []
        
        for i, line in enumerate(lines):
            if '_BR_' in line:
                br_lines.append((i+1, line.strip()))
        
        print(f"Linhas com '_BR_': {len(br_lines)}")
        
        if br_lines:
            print("Primeiras 10 linhas com BR:")
            for i, (line_num, line) in enumerate(br_lines[:10]):
                print(f"  {line_num}: {line}")
        
        # Verificar padrão específico que estamos procurando
        pattern = r'^(.+?)\((.+_BR_\d+)\)\[(.+)\]$'
        matches = []
        
        for line in lines:
            match = re.match(pattern, line.strip())
            if match:
                matches.append(match.groups())
        
        print(f"Matches com padrão atual: {len(matches)}")
        if matches:
            print("Primeiros 5 matches:")
            for i, (name, id, impact) in enumerate(matches[:5]):
                print(f"  {i+1}. Nome: '{name}', ID: '{id}', Impacto: '{impact}'")
        
        # Verificar se há outros padrões
        alternative_patterns = [
            r'(.+?)_BR_(\d+)',
            r'(.+?)\s*\((.+?)_BR_(\d+)\)',
            r'(.+?)\s*\[(.+?)_BR_(\d+)\]',
            r'(.+?)_BR_(\d+)\s*\[(.+?)\]',
            r'(.+?)\s*\((.+?)_BR_(\d+)\)\s*\[(.+?)\]'
        ]
        
        for i, pattern in enumerate(alternative_patterns):
            matches = re.findall(pattern, full_text)
            if matches:
                print(f"Padrão alternativo {i+1}: {len(matches)} encontrados")
                if len(matches) <= 3:
                    for match in matches:
                        print(f"  - {match}")
                else:
                    print(f"  - Primeiros 3: {matches[:3]}")
        
        return full_text
        
    except Exception as e:
        print(f"Erro: {e}")
        return ""

# Testar com um PDF que não está sendo detectado
debug_br_patterns("/home/andrade/Documentos/quantum/pdf/quantum-dominio.pdf")

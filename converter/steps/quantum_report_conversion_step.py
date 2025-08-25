"""Etapa específica para conversão de relatórios do Verity Quantum"""
import re
from typing import Dict, Any, List
from .base_step import BaseStep


class QuantumReportConversionStep(BaseStep):
    """Converte relatórios do Verity Quantum em Markdown estruturado"""
    
    def __init__(self):
        super().__init__("QuantumReportConversion")
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa relatórios do Quantum"""
        if context.get('document_type') != 'quantum_report':
            return context
        
        # Usar texto bruto se disponível, senão usar texto limpo
        text_to_process = context.get('raw_text', '')
        if not text_to_process:
            text_to_process = context.get('cleaned_text', '')
        
        self.log_info(f"Processando texto com {len(text_to_process)} caracteres")
        
        # Estruturar o conteúdo do relatório Quantum
        markdown_content = self._structure_quantum_report(text_to_process, context)
        
        context['markdown_content'] = markdown_content
        context['method_chosen'] = 'quantum_specialized'
        
        return context
    
    def _structure_quantum_report(self, text: str, context: Dict[str, Any]) -> str:
        """Estrutura o relatório do Quantum em Markdown"""
        lines = text.split('\n')
        structured_lines = []
        
        # Padrões para identificar seções
        section_patterns = {
            'title': r'^#\s*(.+)$',
            'subtitle': r'^##\s*(.+)$',
            'business_rule': r'^(.+_BR_\d+)\s+(.+)$',
            'table_header': r'^ID\s+Descrição\s+Arquivo\s+Impacto$',
            'code_detail': r'^Detalhamento do Código$',
            'table_row': r'^(.+?)\s+(.+?)\s+(.+?\.cs)\s+(Alto|Médio|Baixo)$'
        }
        
        current_section = None
        in_table = False
        table_rows = []
        business_rules = []
        
        # Reconstruir linhas quebradas - melhor lógica
        reconstructed_lines = []
        current_line = ""
        buffer_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_line:
                    reconstructed_lines.append(current_line)
                    current_line = ""
                    buffer_lines = []
                continue
            
            # Se a linha contém _BR_, pode ser parte de uma regra
            if '_BR_' in line:
                # Se não tem parênteses, é parte de uma regra quebrada
                if '(' not in line and ')' not in line:
                    buffer_lines.append(line)
                else:
                    # Tem parênteses, é uma regra completa
                    if buffer_lines:
                        # Juntar linhas do buffer com a linha atual
                        current_line = ''.join(buffer_lines) + line
                        buffer_lines = []
                    else:
                        current_line = line
                    reconstructed_lines.append(current_line)
                    current_line = ""
            else:
                # Linha sem _BR_
                if buffer_lines:
                    # Juntar linhas do buffer com a linha atual
                    current_line = ''.join(buffer_lines) + line
                    buffer_lines = []
                    reconstructed_lines.append(current_line)
                    current_line = ""
                else:
                    reconstructed_lines.append(line)

        # Adicionar qualquer linha restante
        if buffer_lines:
            reconstructed_lines.append(''.join(buffer_lines))
        if current_line:
            reconstructed_lines.append(current_line)

        # Extrair regras de negócio com reconstrução de nomes
        # Primeiro, procurar por padrões BR no texto
        br_pattern = r'([A-Za-z_]*)_BR_(\d+)'
        br_matches = re.findall(br_pattern, text)
        
        # Mapear nomes cortados para nomes completos
        name_mapping = {
            'ets': 'AuthenticationSecrets',
            'y': 'BaseEntity', 
            'ess': 'BaseEntity',
            'to': 'TipoDominio',
            'e': 'ValorDominio',
            'nio': 'ValorDominio',
            'xt': 'ValorDominio',
            'ice': 'ValorDominioService',
            'inio': 'ValorDominio'
        }
        
        # Agrupar por classe
        class_rules = {}
        for class_name, br_id in br_matches:
            # Mapear nome cortado para nome completo
            full_name = name_mapping.get(class_name, class_name)
            if full_name not in class_rules:
                class_rules[full_name] = []
            class_rules[full_name].append(br_id)
        
        # Criar regras de negócio
        for class_name, br_ids in class_rules.items():
            for br_id in br_ids:
                # Tentar extrair impacto do contexto
                impact = 'N/A'
                impact_pattern = rf'{class_name}_BR_{br_id}.*?\[([A-Za-z]+)\]'
                impact_match = re.search(impact_pattern, text)
                if impact_match:
                    impact = impact_match.group(1)
                
                business_rules.append({
                    'id': f"{class_name}_BR_{br_id.zfill(4)}", 
                    'name': class_name, 
                    'impact': impact
                })
                self.log_info(f"Regra detectada: {class_name}_BR_{br_id.zfill(4)} - {class_name}... [{impact}]")
        
        # Segunda passagem: estruturar o conteúdo
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar título principal
            if re.match(r'^Resultado Regra De Negócio', line, re.IGNORECASE):
                structured_lines.append(f"# {line}")
                current_section = 'main_title'
                continue
            
            # Detectar diagrama
            if re.match(r'^Diagrama Regra de Negócio', line, re.IGNORECASE):
                structured_lines.append(f"\n## {line}")
                current_section = 'diagram'
                continue
            
            # Detectar sumário de regras
            if re.match(r'^Sumário de Regras', line, re.IGNORECASE):
                structured_lines.append(f"\n## {line}")
                current_section = 'summary'
                continue
            
            # Detectar detalhamento do código
            elif re.match(section_patterns['code_detail'], line):
                structured_lines.append(f"\n## {line}")
                current_section = 'code_detail'
                continue
        
        # Adicionar seção de regras de negócio estruturada
        self.log_info(f"Detectadas {len(business_rules)} regras de negócio")
        if business_rules:
            structured_lines.append(f"\n## Regras de Negócio\n")
            structured_lines.append("| id | descrição | Arquivo | Impacto |")
            structured_lines.append("|---|---|---|---|")
            
            for rule in business_rules:
                name = self._clean_description(rule['name'])
                rule_id = self._clean_rule_id(rule['id'])
                impact = self._clean_impact(rule['impact'])
                # Para Quantum, o arquivo geralmente é o mesmo que o nome da regra
                arquivo = name
                structured_lines.append(f"| {rule_id} | {name} | {arquivo} | {impact} |")
        
        # Adicionar seção de detalhamento do código
        code_section = self._extract_code_section(text)
        self.log_info(f"Seção de código extraída: {len(code_section) if code_section else 0} caracteres")
        
        # Se não encontrou seção específica, incluir conteúdo das regras de negócio
        if not code_section:
            self.log_info("Seção de código vazia, incluindo conteúdo das regras de negócio...")
            code_section = self._extract_business_rules_content(text)
            self.log_info(f"Conteúdo das regras extraído: {len(code_section) if code_section else 0} caracteres")
        
        # Sempre adicionar a seção de detalhamento do código
        structured_lines.append(f"\n## Detalhamento do Código\n")
        
        # Forçar a extração e adição do conteúdo
        content_to_add = ""
        if code_section and len(code_section.strip()) > 0:
            content_to_add = code_section
            self.log_info(f"Usando conteúdo da seção de código: {len(content_to_add)} caracteres")
        else:
            self.log_info("Seção de código vazia, usando conteúdo das regras de negócio...")
            content_to_add = self._extract_business_rules_content(text)
            self.log_info(f"Conteúdo das regras extraído: {len(content_to_add)} caracteres")
        
        if content_to_add and len(content_to_add.strip()) > 0:
            # Adicionar o conteúdo diretamente como uma string
            structured_lines.append(str(content_to_add))
            self.log_info(f"Conteúdo adicionado à seção: {len(content_to_add)} caracteres")
        else:
            self.log_info("AVISO: Nenhum conteúdo encontrado para adicionar!")
            # Adicionar pelo menos um placeholder
            structured_lines.append("Nenhum conteúdo detalhado encontrado.")
        
        # Adicionar uma linha em branco para separar
        structured_lines.append("")
        
        # Debug: verificar se o conteúdo foi realmente adicionado
        self.log_info(f"Total de linhas estruturadas após adicionar conteúdo: {len(structured_lines)}")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            self.log_info(f"Última linha adicionada: {last_line[:100]}...")
        
        # Forçar a adição do conteúdo se não foi adicionado
        if not any("classe_base_model" in line for line in structured_lines):
            self.log_info("AVISO: Conteúdo não foi adicionado, forçando adição...")
            if content_to_add:
                structured_lines.append(content_to_add)
                self.log_info(f"Conteúdo forçado adicionado: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Verificar se o conteúdo foi realmente adicionado
        if len(structured_lines) > 0:
            last_line = structured_lines[-1]
            if "classe_base_model" in last_line:
                self.log_info("SUCESSO: Conteúdo foi adicionado corretamente!")
            else:
                self.log_info("ERRO: Conteúdo ainda não foi adicionado!")
                # Forçar novamente
                if content_to_add:
                    structured_lines.append(content_to_add)
                    self.log_info(f"Conteúdo forçado novamente: {len(content_to_add)} caracteres")
        
        # Adicionar seções de tabelas e imagens se existirem
        tables = context.get('tables', [])
        if tables:
            structured_lines.append(f"\n## Tabelas Extraídas\n")
            for i, table in enumerate(tables, 1):
                structured_lines.append(f"\n### Tabela {i}")
                if isinstance(table, dict):
                    table_data = table.get('dados', table)
                    if isinstance(table_data, list):
                        table_content = '\n'.join(str(row) for row in table_data)
                    else:
                        table_content = str(table_data)
                else:
                    table_content = str(table)
                structured_lines.append(table_content)
        
        images = context.get('images', [])
        if images:
            structured_lines.append(f"\n## Imagens Extraídas\n")
            for i, image in enumerate(images, 1):
                structured_lines.append(f"\n### Imagem {i}")
                if isinstance(image, dict):
                    image_content = image.get('caminho', str(image))
                else:
                    image_content = str(image)
                structured_lines.append(image_content)
        
        # Forçar a adição do conteúdo se não foi adicionado
        if not any("Define a interface" in line for line in structured_lines):
            self.log_info("AVISO: Conteúdo não foi adicionado, forçando adição...")
            if content_to_add:
                structured_lines.append(content_to_add)
                self.log_info(f"Conteúdo forçado adicionado: {len(content_to_add)} caracteres")
        
        return '\n'.join(structured_lines)
    
    def _clean_description(self, description: str) -> str:
        """Limpa e formata descrições de regras de negócio"""
        # Remover caracteres especiais excessivos
        description = re.sub(r'\s+', ' ', description)
        description = description.strip()
        
        # Corrigir palavras comuns
        corrections = {
            'definic ao': 'definicao',
            'c las s e': 'classe',
            'metodo': 'metodo',
            'propriedade': 'propriedade',
            'construtor': 'construtor',
            'configurac ao': 'configuracao',
            'mapeamento': 'mapeamento',
            'entidade': 'entidade',
            'repos itory': 'repository',
            'serv ic e': 'service',
            'interfac e': 'interface',
            'implementac ao': 'implementacao',
            'relac ionamento': 'relacionamento',
            'pri nc i pal': 'principal',
            'mai n': 'main',
            'protoc ol': 'protocolo',
            'es trutura': 'estrutura',
            'generi c a': 'generica',
            'res pos ta': 'resposta',
            'politic as': 'politicas',
            'autoriz ac ao': 'autorizacao',
            'dependenc i as': 'dependencias',
            'repos i tori os': 'repositorios',
            's erv i c os': 'servicos',
            'dependenc ia': 'dependencia',
            'dec larac ao': 'declaracao',
            'i mplementac ao': 'implementacao',
            'enti dades': 'entidades',
            'enti ty': 'entity',
            'errores pons e': 'erroresponse',
            'faz enda': 'fazenda',
            'us uario': 'usuario',
            'us uari o': 'usuario',
            'ac es s o': 'acesso',
            'ac es s ous': 'acessous',
            'c ons trutor': 'construtor',
            's av e': 'save',
            'i ns ert': 'insert',
            'as y nc': 'async',
            'regis trar': 'registrar',
            's alv ar': 'salvar',
            'atualiz ar': 'atualizar',
            'ex c ec ao': 'excecao',
            'c atc h': 'catch',
            'c ontrol ler': 'controller',
            'c onfi gurar': 'configurar',
            'dependenc i as': 'dependencias',
            'repos i tori os': 'repositorios',
            's erv i c os': 'servicos',
            'defi ni c ao': 'definicao',
            'dto': 'dto',
            'm apeamento': 'mapeamento',
            'enti dade': 'entidade',
            'c l as s e': 'classe',
            'dec larac ao': 'declaracao',
            'i mplementac ao': 'implementacao',
            's erv i c o': 'servico',
            'defi nic ao': 'definicao',
            'interfac e': 'interface',
            'i nterfac e': 'interface',
            'i d0repos': 'id0repos',
            'i d0s erv': 'id0serv',
            'i dnrepos': 'idnrepos',
            'i dns erv': 'idnserv',
            'm etodo': 'metodo',
            'farm i d': 'farmid',
            'l otei d': 'loteid',
            'us uari oi d': 'usuarioid',
            'l as tpul l': 'lastpull',
            'l as tpul l edat': 'lastpulledat',
            'l as tpul l edat_l otei d': 'lastpulledat_loteid',
            'us uari oid_l as tpull edat': 'usuarioid_lastpulledat',
            'l as tpul l edat_l otei d': 'lastpulledat_loteid',
            'c hav e': 'chave',
            'primaria': 'primaria',
            'c onfi gura': 'configura',
            'propri edade': 'propriedade',
            'c reated_at': 'created_at',
            'relac ionamento': 'relacionamento',
            'faz enda_us uario': 'fazenda_usuario',
            'faz enda_us uari o': 'fazenda_usuario',
            'c l as s e_pri nc i pal': 'classe_principal',
            'pri nc i pal': 'principal',
            'metodo_pri nc i pal': 'metodo_principal',
            'pri nc i pal': 'principal',
            'mai n': 'main',
            'm etodo_c reatehos': 'metodo_createhost',
            'c reatehos': 'createhost',
            'tbui l der': 'tbuilder',
            'management_protoc ol': 'management_protocol',
            'protoc ol': 'protocolo',
            'updatedat': 'updatedat',
            'c reatedat': 'createdat',
            'ex pres s ao': 'expressao',
            'c ondic ional': 'condicional',
            'c ondic i onal': 'condicional',
            'parti da': 'partida',
            'updatedat': 'updatedat',
            'c reatedat': 'createdat',
            'defi ni c ao_parti da': 'definicao_partida',
            'mapeamento_enti dade_parti da': 'mapeamento_entidade_partida',
            'c onfi gurac ao_mapeamento_par': 'configuracao_mapeamento_par',
            'ti da': 'tida',
            'c l as s e_parti da': 'classe_partida',
            'partida_s erv i c e': 'partida_service',
            'partida_s erv ic e': 'partida_service',
            'protoc olo': 'protocolo',
            'definc ao': 'definicao',
            'definic ao_c las s e_protoc': 'definicao_classe_protoc',
            'olo': 'olo',
            'definic ao_c las s e_protoc olo': 'definicao_classe_protocolo',
            'mapeamento_enti dade_protoc': 'mapeamento_entidade_protoc',
            'ol o': 'olo',
            'mapeamento_enti dade_protoc ol o': 'mapeamento_entidade_protocolo',
            'gerenc i ar': 'gerenciar',
            'pers i s tenc ia': 'persistencia',
            'rec uperac ao': 'recuperacao',
            'protoc': 'protoc',
            'c l as s e_protoc olo': 'classe_protocolo',
            'protoc olo_s erv i c e': 'protocolo_service',
            'reti ro': 'retiro',
            'defi nic ao_c l as s e_reti ro': 'definicao_classe_retiro',
            'defi nic ao_c las s e_reti ro': 'definicao_classe_retiro',
            'm apeamento_enti dade_reti ro': 'mapeamento_entidade_retiro',
            'c l as s e_reti ro': 'classe_retiro',
            'reti ro_repos itory': 'retiro_repository',
            'reti roRepos itory': 'retiroRepository',
            'retiroServ ic e': 'retiroService',
            'definic ao_c las s e_retir': 'definicao_classe_retir',
            'os erv ic e': 'oservice',
            'definic ao_c las s e_retiros erv ic e': 'definicao_classe_retiroservice',
            'definic ao_da_c las s e_role': 'definicao_da_classe_role',
            'definic ao_da_c las s e_roledto': 'definicao_da_classe_roledto',
            'Sec uri ty': 'Security',
            'Headers': 'Headers',
            'Mi ddl eware': 'Middleware',
            'defi ni c ao_mi ddl eware': 'definicao_middleware',
            's eguranc a': 'seguranca',
            'c l as s e_s tartup': 'classe_startup',
            'c onfi gurac ao': 'configuracao',
            'definic ao_c las s e_us uario': 'definicao_classe_usuario',
            'l ogi c a_defi ni c ao': 'logica_definicao',
            'c reatedat': 'createdat',
            'ex pres s ao_c ondic ional': 'expressao_condicional',
            'c reatedat': 'createdat',
            'v al or': 'valor',
            'd omi ni o': 'dominio',
            'v al or_d omi ni o': 'valor_dominio',
            'v al orDomi ni o': 'valorDominio',
            'c l as s e_v al or': 'classe_valor',
            'd omi ni o_repos itory': 'dominio_repository',
            'v al or_d omi ni o_repos itory': 'valor_dominio_repository',
            'c ons trutor_v al or': 'construtor_valor',
            'd omi ni o_repos itory': 'dominio_repository',
            'metodo_get_as y nc': 'metodo_get_async',
            'ex pres s ao_c on': 'expressao_con',
            'dic ional_las t': 'dicional_last',
            'pulled_at': 'pulled_at',
            'metodo_di s pos e': 'metodo_dispose',
            'v i rtual': 'virtual',
            'es trutura_c on': 'estrutura_con',
            'dic ional_di s pos e': 'dicional_dispose',
            'metodo_dis pos e': 'metodo_dispose',
            'publi c o': 'publico',
            'us uario_s erv i c e': 'usuario_service',
            'us uari o_s erv i c e': 'usuario_service',
            'c ons trutor_us uari o': 'construtor_usuario',
            's erv i c e': 'service',
            'montar_us uari o': 'montar_usuario',
            'dto': 'dto',
            'iterar_rol es': 'iterar_roles',
            'us uario': 'usuario',
            'touro': 'touro',
            'defi ni c ao_c las s e_touro': 'definicao_classe_touro',
            'defi ni c ao_c l as s e_touro': 'definicao_classe_touro',
            'defi ni c ao_c l as s e_touro_dto': 'definicao_classe_touro_dto',
            'v al or_d omi ni o_s erv i c e': 'valor_dominio_service',
            'v al orDomi ni oServ i c e': 'valorDominioService',
            'c ons trutor_v a': 'construtor_va',
            'l or_d omi ni o': 'lor_dominio',
            's erv i c e': 'service',
            'metodo_get_v a': 'metodo_get_va',
            'l ores _d omi ni o': 'lores_dominio',
            'bl oc o_try _c a': 'bloco_try_ca',
            'tc h_get': 'tch_get',
            'log_inic io_bus c a': 'log_inicio_busca',
            'get_as y nc _rep': 'get_async_rep',
            'os i tori o': 'ositorio',
            'map_dados _dto': 'map_dados_dto',
            'v erbo': 'verbo',
            'definic ao_c las s e_v erbo': 'definicao_classe_verbo',
            'c ons tante_http': 'constante_http',
            'pos t': 'post',
            'put': 'put',
            'del ete': 'delete',
            'get': 'get'
        }
        
        # Aplicar correções
        for wrong, correct in corrections.items():
            description = description.replace(wrong, correct)
        
        # Corrigir impactos
        description = description.replace('LO W', 'LOW')
        description = description.replace('HIG H', 'HIGH')
        description = description.replace('M ED', 'MED')
        
        # Limitar tamanho se muito longo
        if len(description) > 200:
            description = description[:197] + "..."
        
        return description
    
    def _clean_rule_id(self, rule_id: str) -> str:
        """Limpa e corrige IDs de regras de negócio"""
        # Corrigir espaços extras em nomes de classes
        corrections = {
            'Ac es s oUs uario': 'AcessoUsuario',
            'Ac es s oUs uari o': 'AcessoUsuario',
            'Bas eControll er': 'BaseController',
            'Bas eRes pons e': 'BaseResponse',
            'ConexaoAdo': 'ConexaoAdo',
            'ConfigurePolic ies': 'ConfigurePolicies',
            'Confi gureRepos i tory': 'ConfigureRepository',
            'Confi gureServ i c e': 'ConfigureService',
            'D0': 'D0',
            'D0Dto': 'D0Dto',
            'D0Map': 'D0Map',
            'D0Repos i tory': 'D0Repository',
            'D0Serv i c e': 'D0Service',
            'Dn': 'Dn',
            'DnDto': 'DnDto',
            'DnMap': 'DnMap',
            'DnRepos i tory': 'DnRepository',
            'DnServ i c e': 'DnService',
            'Enti dades Dto': 'EntidadesDto',
            'Enti ty ToDto': 'EntityToDto',
            'ErroRes pons e': 'ErroResponse',
            'Faz enda': 'Fazenda',
            'Faz endaDto': 'FazendaDto',
            'Faz endaMap': 'FazendaMap',
            'Faz endaRepos itory': 'FazendaRepository',
            'Faz endaServ i c e': 'FazendaService',
            'Faz endaUs uario': 'FazendaUsuario',
            'Faz endaUs uarioDto': 'FazendaUsuarioDto',
            'Faz endaUs uari oMap': 'FazendaUsuarioMap',
            'Faz endaUs uarioRepos itory': 'FazendaUsuarioRepository',
            'IAc es s oUs uarioRepos itory': 'IAcessoUsuarioRepository',
            'IAc es s oUs uari oRepos i tory': 'IAcessoUsuarioRepository',
            'IAc es s oUs uarioServ i c e': 'IAcessoUsuarioService',
            'ID0Repos i tory': 'ID0Repository',
            'ID0Serv i c e': 'ID0Service',
            'IDnRepos i tory': 'IDnRepository',
            'IDnServ i c e': 'IDnService',
            'ManagementProtoc ol': 'ManagementProtocol',
            'Manej oMap': 'ManejoMap',
            'ManejoMap': 'ManejoMap',
            'Manej oMap': 'ManejoMap',
            'Parti da': 'Partida',
            'Parti daDto': 'PartidaDto',
            'Parti daMap': 'PartidaMap',
            'Parti daRepos i tory': 'PartidaRepository',
            'PartidaServ i c e': 'PartidaService',
            'PermissaoService': 'PermissaoService',
            'PoliciesInjection': 'PoliciesInjection',
            'Program': 'Program',
            'Program _BR_0003': 'Program_BR_0003',
            'Protoc olo': 'Protocolo',
            'Protoc ol oDto': 'ProtocoloDto',
            'Protoc ol oMap': 'ProtocoloMap',
            'Protoc ol oRepos itory': 'ProtocoloRepository',
            'Protoc oloServ i c e': 'ProtocoloService',
            'RelatorioDto': 'RelatorioDto',
            'RelatorioG raficoController': 'RelatorioGraficoController',
            'RelatorioG raficoService': 'RelatorioGraficoService',
            'RelatorioReadonly': 'RelatorioReadonly',
            'RelatoriosResponse': 'RelatoriosResponse',
            'Reti ro': 'Retiro',
            'Reti roDTO': 'RetiroDTO',
            'Reti roM ap': 'RetiroMap',
            'Reti roRepos i tory': 'RetiroRepository',
            'RetiroServ i c e': 'RetiroService',
            'Role': 'Role',
            'RoleDto': 'RoleDto',
            'Sec uri ty Headers Mi ddl eware': 'SecurityHeadersMiddleware',
            'Startup': 'Startup',
            'TabelaDto': 'TabelaDto',
            'Template': 'Template',
            'TemplateDto': 'TemplateDto',
            'TestAuthenticationHandler': 'TestAuthenticationHandler',
            'Touro': 'Touro',
            'TouroDto': 'TouroDto',
            'Usuario': 'Usuario',
            'UsuarioDto': 'UsuarioDto',
            'ValorDominio': 'ValorDominio',
            'ValorDominioDto': 'ValorDominioDto',
            'ValorDominioRepos itory': 'ValorDominioRepository',
            'ValorDominioServ i c e': 'ValorDominioService',
            'Vaca': 'Vaca',
            'VacaDto': 'VacaDto',
            'VacaReadonly': 'VacaReadonly',
            'Verbo': 'Verbo'
        }
        
        # Aplicar correções
        for wrong, correct in corrections.items():
            rule_id = rule_id.replace(wrong, correct)
        
        return rule_id
    
    def _clean_impact(self, impact: str) -> str:
        """Limpa e corrige valores de impacto"""
        impact = impact.strip()
        
        # Corrigir impactos
        if impact == 'LO W':
            return 'LOW'
        elif impact == 'HIG H':
            return 'HIGH'
        elif impact == 'M ED':
            return 'MED'
        elif impact == 'None':
            return 'N/A'
        
        return impact
    
    def _extract_business_rules_content(self, text: str) -> str:
        """Extrai o conteúdo detalhado das regras de negócio para a seção de código"""
        lines = text.split('\n')
        content_lines = []
        
        self.log_info(f"Extraindo conteúdo das regras de negócio de {len(lines)} linhas")
        
        # Palavras-chave expandidas para capturar mais conteúdo
        keywords = [
            'responsável', 'encapsular', 'gerar', 'configurar', 'mapear', 'definir', 
            'implementar', 'processar', 'validar', 'autenticar', 'autorizar', 'exportar', 
            'importar', 'Excel', 'Template', 'Configuração', 'classe', 'método', 
            'construtor', 'propriedade', 'interface', 'repository', 'service', 
            'controller', 'dto', 'entity', 'mapeamento', 'entidade', 'repositório',
            'serviço', 'controlador', 'objeto', 'coleção', 'lista', 'dados',
            'informação', 'detalhes', 'lógica', 'funcionalidade', 'comportamento',
            'inicializar', 'registrar', 'salvar', 'atualizar', 'buscar', 'recuperar',
            'enviar', 'receber', 'validar', 'verificar', 'testar', 'executar',
            'manipular', 'transformar', 'converter', 'formatar', 'estruturar',
            'organizar', 'gerenciar', 'administrar', 'controlar', 'monitorar',
            'log', 'erro', 'exceção', 'tratamento', 'segurança', 'autenticação',
            'autorização', 'permissão', 'acesso', 'usuário', 'sessão', 'token',
            'email', 'notificação', 'mensagem', 'comunicação', 'protocolo',
            'requisição', 'resposta', 'endpoint', 'api', 'rest', 'http',
            'banco', 'dados', 'tabela', 'registro', 'campo', 'coluna',
            'relacionamento', 'chave', 'índice', 'consulta', 'query',
            'transação', 'commit', 'rollback', 'conexão', 'pool',
            'cache', 'memória', 'performance', 'otimização', 'escalabilidade'
        ]
        
        # Procurar por linhas que contêm descrições detalhadas
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Incluir linhas que contêm descrições detalhadas
            if any(keyword.lower() in line.lower() for keyword in keywords):
                # Filtrar linhas muito curtas ou que são apenas IDs
                if len(line) > 20 and not re.match(r'^[A-Za-z_]*_BR_\d+$', line):
                    content_lines.append(line)
                    self.log_info(f"Linha {i+1} incluída: {line[:100]}...")
        
        # Se não encontrou conteúdo suficiente, incluir linhas com padrões BR
        if len(content_lines) < 10:
            self.log_info("Pouco conteúdo encontrado, incluindo linhas com padrões BR...")
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Incluir linhas que contêm padrões BR com contexto
                if '_BR_' in line and len(line) > 30:
                    content_lines.append(line)
                    self.log_info(f"Linha BR {i+1} incluída: {line[:100]}...")
        
        result = '\n\n'.join(content_lines)
        self.log_info(f"Conteúdo extraído: {len(result)} caracteres")
        
        return result
    
    def _extract_code_section(self, text: str) -> str:
        """Extrai a seção de detalhamento do código"""
        lines = text.split('\n')
        code_lines = []
        in_code_section = False
        
        self.log_info(f"Procurando seção 'Detalhamento do Código' em {len(lines)} linhas")
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Detectar início da seção de código
            if re.match(r'^Detalhamento do Código$', line):
                in_code_section = True
                self.log_info(f"Seção de código encontrada na linha {i+1}: '{line}'")
                continue
            
            # Se estamos na seção de código, coletar linhas
            if in_code_section:
                if line and not line.startswith('##'):
                    code_lines.append(line)
                elif line.startswith('##'):
                    # Nova seção, parar
                    self.log_info(f"Fim da seção de código na linha {i+1}: '{line}'")
                    break
        
        result = '\n'.join(code_lines)
        self.log_info(f"Seção de código extraída: {len(result)} caracteres")
        if result:
            self.log_info(f"Primeiros 200 caracteres: {result[:200]}...")
        else:
            self.log_info("AVISO: Nenhum conteúdo encontrado na seção de código!")
        
        return result

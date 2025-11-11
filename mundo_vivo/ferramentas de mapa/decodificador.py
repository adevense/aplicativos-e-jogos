import json
import os

# --- Configurações de Arquivo ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))

NOME_ARQUIVO_CODIFICADO = os.path.join(CAMINHO_SCRIPT, 'mapa_bd.json')
NOME_ARQUIVO_DECODIFICADO = os.path.join(CAMINHO_SCRIPT, 'mapa_bd_decodificado.json')

# Modelo de chaves e sua ordem para garantir a estrutura exata na saída
CELL_TEMPLATE_KEYS = [
    "x", "y", "terreno", "ambiente", "local_atual", "npcs_presentes",
    "grupos_presentes", "players_presentes", "valor_movimentacao",
    "valor_estabilidade", "descricao"
]

def decodificar_json_estrutura_exata(nome_arquivo_entrada, nome_arquivo_saida):
    """
    Carrega o JSON codificado e recria a estrutura detalhada de objetos 
    de célula na ORDEM e com todos os NOMES de chaves especificados.
    """
    if not os.path.exists(nome_arquivo_entrada):
        print(f"❌ ERRO: O arquivo de entrada codificado '{nome_arquivo_entrada}' não foi encontrado.")
        return

    # 1. Carregamento dos Dados
    try:
        with open(nome_arquivo_entrada, 'r') as f:
            dados_codificados = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERRO de decodificação no JSON de entrada: {e}")
        return
    
    metadata = dados_codificados.get("metadata", {})
    
    # 2. Extração dos Mapas de Decodificação
    terrenos_map = metadata.get("terrenos_map", {})
    ambientes_map = metadata.get("ambientes_map", {})
    
    # 3. Preparação dos Dados Codificados (Garantindo valores padrão)
    mapa_terreno = dados_codificados.get("terreno", [])
    mapa_ambiente = dados_codificados.get("ambiente", [])
    mapa_movimentacao = dados_codificados.get("valor_movimentacao", [])
    mapa_estabilidade = dados_codificados.get("valor_estabilidade", [])
    
    num_rows = len(mapa_terreno)
    if num_rows == 0:
        print("❌ ERRO: O array de terreno está vazio.")
        return

    # 4. Decodificação e Reconstrução do Mapa Detalhado
    mapa_decodificado_detalhado = []
    
    print(f"Iniciando decodificação de {num_rows} linhas...")

    for y in range(num_rows):
        row_detalhada = []
        num_cols = len(mapa_terreno[y])
        
        for x in range(num_cols):
            # Obtém os códigos/valores
            terreno_code = str(mapa_terreno[y][x])
            ambiente_code = str(mapa_ambiente[y][x])
            
            movimentacao_val = mapa_movimentacao[y][x]
            estabilidade_val = mapa_estabilidade[y][x]
            
            # Converte o código de volta para a string
            terreno_nome = terrenos_map.get(terreno_code, "DESCONHECIDO")
            ambiente_nome = ambientes_map.get(ambiente_code, "DESCONHECIDO")
            
            # --- Montagem da Célula Usando o Template (Garantindo a Ordem) ---
            
            # 1. Cria o objeto com os valores dinâmicos
            cell_data = {
                "x": x,
                "y": y,
                "terreno": terreno_nome,
                "ambiente": ambiente_nome,
                "valor_movimentacao": movimentacao_val,
                "valor_estabilidade": estabilidade_val,
                
                # Valores fixos/padrão que você não codificou, mas quer manter na saída
                "local_atual": None,
                "npcs_presentes": [],
                "grupos_presentes": [],
                "players_presentes": [],
                "descricao": f"Terreno: {terreno_nome}, Ambiente: {ambiente_nome}" # Mantendo o exemplo de descrição
            }
            
            # 2. Cria o objeto final na ordem exata (OrderedDict não é necessário,
            # mas garante o uso da ordem das chaves do template)
            cell_objeto = {}
            for key in CELL_TEMPLATE_KEYS:
                # Usa .get() para pegar o valor do dicionário recém-criado
                cell_objeto[key] = cell_data.get(key) 

            row_detalhada.append(cell_objeto)
            
        mapa_decodificado_detalhado.append(row_detalhada)

    # 5. Monta a Estrutura Final e Salva
    estrutura_final = {
        "mapa": mapa_decodificado_detalhado
    }

    try:
        with open(nome_arquivo_saida, 'w') as f:
            # json.dump em Python 3.7+ mantém a ordem de inserção do dicionário.
            json.dump(estrutura_final, f, indent=4) 

        print("\n✅ Decodificação concluída com sucesso!")
        print(f"O novo mapa detalhado e com estrutura idêntica foi salvo como: {nome_arquivo_saida}")
        
    except Exception as e:
        print(f"❌ ERRO ao salvar o arquivo de saída: {e}")

# --- Execução do Decodificador ---
decodificar_json_estrutura_exata(NOME_ARQUIVO_CODIFICADO, NOME_ARQUIVO_DECODIFICADO)
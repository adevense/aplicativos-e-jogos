import json
import os

# --- Configurações de Arquivo ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))

NOME_ARQUIVO_CODIFICADO = os.path.join(CAMINHO_SCRIPT, 'mapa_bd.json')
NOME_ARQUIVO_DECODIFICADO = os.path.join(CAMINHO_SCRIPT, 'mapa_bd_decodificado.json')


# Modelo de chaves e sua ordem EXATA para a saída
CELL_TEMPLATE_KEYS = [
    "x", "y", "terreno", "ambiente", "local_atual", "npcs_presentes",
    "grupos_presentes", "players_presentes", "valor_movimentacao",
    "valor_estabilidade", "descricao"
]

def decodificar_json_estrutura_exata(nome_arquivo_entrada, nome_arquivo_saida):
    if not os.path.exists(nome_arquivo_entrada):
        print(f"❌ ERRO: O arquivo de entrada codificado '{nome_arquivo_entrada}' não foi encontrado.")
        return

    # 1. Carregamento dos Dados
    try:
        with open(nome_arquivo_entrada, 'r') as f:
            dados_codificados = json.load(f)
    except Exception as e:
        print(f"❌ ERRO ao ler ou decodificar o JSON codificado: {e}")
        return
    
    metadata = dados_codificados.get("metadata", {})
    
    # 2. Extração dos Mapas de Decodificação
    terrenos_map = metadata.get("terrenos_map", {})
    ambientes_map = metadata.get("ambientes_map", {})
    # *** NOVO: Carrega o mapa de local_atual ***
    local_atual_map = metadata.get("local_atual_map", {}) 
    
    # 3. Preparação dos Dados Codificados
    mapa_terreno = dados_codificados.get("terreno", [])
    mapa_ambiente = dados_codificados.get("ambiente", [])
    mapa_movimentacao = dados_codificados.get("valor_movimentacao", [])
    mapa_estabilidade = dados_codificados.get("valor_estabilidade", [])
    # *** NOVO: Carrega o array de local_atual ***
    mapa_local_atual = dados_codificados.get("local_atual", [])
    
    num_rows = len(mapa_terreno)
    if num_rows == 0:
        print("❌ ERRO: O array de terreno está vazio.")
        return

    # 4. Decodificação e Reconstrução
    mapa_decodificado_detalhado = []
    
    for y in range(num_rows):
        row_detalhada = []
        num_cols = len(mapa_terreno[y])
        
        for x in range(num_cols):
            # Obtém e converte o código de volta para a string
            terreno_code = str(mapa_terreno[y][x])
            ambiente_code = str(mapa_ambiente[y][x])
            # *** NOVO: Decodifica o local_atual ***
            local_atual_code = str(mapa_local_atual[y][x])
            
            terreno_nome = terrenos_map.get(terreno_code, "DESCONHECIDO")
            ambiente_nome = ambientes_map.get(ambiente_code, "DESCONHECIDO")
            # *** NOVO: Obtém o valor real (None ou "acampamento") ***
            local_atual_val = local_atual_map.get(local_atual_code, None) 
            
            movimentacao_val = mapa_movimentacao[y][x]
            estabilidade_val = mapa_estabilidade[y][x]

            # --- Montagem da Célula (Garantindo a Ordem e todos os campos) ---
            cell_data = {
                "x": x,
                "y": y,
                "terreno": terreno_nome,
                "ambiente": ambiente_nome,
                "valor_movimentacao": movimentacao_val,
                "valor_estabilidade": estabilidade_val,
                "local_atual": local_atual_val, # *** ATUALIZADO ***
                "npcs_presentes": [],
                "grupos_presentes": [],
                "players_presentes": [],
                "descricao": f"Terreno: {terreno_nome}, Ambiente: {ambiente_nome}" 
            }
            
            cell_objeto = {}
            for key in CELL_TEMPLATE_KEYS:
                cell_objeto[key] = cell_data.get(key) 

            row_detalhada.append(cell_objeto)
            
        mapa_decodificado_detalhado.append(row_detalhada)

    # 5. Salvamento
    estrutura_final = {"mapa": mapa_decodificado_detalhado}

    try:
        with open(nome_arquivo_saida, 'w') as f:
            json.dump(estrutura_final, f, indent=4) 

        print(f"\n✅ Decodificação (com acampamentos) concluída! Arquivo salvo como: {nome_arquivo_saida}")
        
    except Exception as e:
        print(f"❌ ERRO ao salvar o arquivo decodificado: {e}")

# --- EXECUÇÃO ---
decodificar_json_estrutura_exata(NOME_ARQUIVO_CODIFICADO, NOME_ARQUIVO_DECODIFICADO)
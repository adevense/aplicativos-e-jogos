import json
import os

# Nome do seu arquivo JSON original com a estrutura detalhada
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))


NOME_ARQUIVO_ORIGINAL = os.path.join(CAMINHO_SCRIPT, 'mapa_bd_decodificado.json')
NOME_ARQUIVO_CODIFICADO = os.path.join(CAMINHO_SCRIPT, 'mapa_bd.json')




def codificar_json_mapa_final(nome_arquivo_entrada, nome_arquivo_saida):
    if not os.path.exists(nome_arquivo_entrada):
        print(f"❌ ERRO: O arquivo de entrada '{nome_arquivo_entrada}' não foi encontrado.")
        return

    try:
        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as f:
            dados_detalhados = json.load(f)
    except Exception as e:
        print(f"❌ ERRO ao ler ou decodificar o JSON de entrada: {e}")
        return
    
    mapa_detalhado = dados_detalhados.get("mapa")
    if not mapa_detalhado:
        print("❌ ERRO: A chave 'mapa' não foi encontrada ou está vazia.")
        return

    # --- Inicialização ---
    terreno_map = {}
    ambiente_map = {}
    
    # *** NOVO: Mapa para local_atual (Provavelmente só 0=None, 1="acampamento") ***
    local_atual_map = {} 
    
    encoded_data = {
        "terreno": [], "ambiente": [], "valor_movimentacao": [], "valor_estabilidade": [],
        "local_atual": [] # *** NOVO ARRAY ***
    }
    
    terreno_counter = 0
    ambiente_counter = 0
    local_atual_counter = 0 # *** NOVO CONTADOR ***
    
    print(f"Iniciando codificação de um mapa com {len(mapa_detalhado)} linhas...")

    # --- Processamento ---
    for row in mapa_detalhado:
        row_encoded = {key: [] for key in encoded_data.keys()}
        
        for cell in row:
            # 1. Terreno
            terreno_val = cell.get("terreno")
            if terreno_val not in terreno_map:
                terreno_map[terreno_val] = terreno_counter
                terreno_counter += 1
            row_encoded["terreno"].append(terreno_map[terreno_val])
            
            # 2. Ambiente
            ambiente_val = cell.get("ambiente")
            if ambiente_val not in ambiente_map:
                ambiente_map[ambiente_val] = ambiente_counter
                ambiente_counter += 1
            row_encoded["ambiente"].append(ambiente_map[ambiente_val])

            # 3. *** NOVO: Codificação do local_atual ***
            local_val = cell.get("local_atual") # Pode ser None (null) ou "acampamento"
            if local_val not in local_atual_map:
                local_atual_map[local_val] = local_atual_counter
                local_atual_counter += 1
            row_encoded["local_atual"].append(local_atual_map[local_val])
            
            # 4. Valores Numéricos
            row_encoded["valor_movimentacao"].append(cell.get("valor_movimentacao", 0))
            row_encoded["valor_estabilidade"].append(cell.get("valor_estabilidade", 0))

        for key, row_list in row_encoded.items():
            encoded_data[key].append(row_list)
            
    # --- Montagem da Saída ---
    terreno_map_revertido = {str(v): k for k, v in terreno_map.items()}
    ambiente_map_revertido = {str(v): k for k, v in ambiente_map.items()}
    # *** NOVO: Mapa de local_atual revertido ***
    local_atual_map_revertido = {str(v): k for k, v in local_atual_map.items()}
    
    nova_estrutura = {
        "metadata": {
            "num_rows": len(mapa_detalhado),
            "num_cols": len(mapa_detalhado[0]) if mapa_detalhado and len(mapa_detalhado[0]) > 0 else 0,
            "terrenos_map": terreno_map_revertido,
            "ambientes_map": ambiente_map_revertido,
            "local_atual_map": local_atual_map_revertido # *** NOVO MAPA DE METADADOS ***
        },
        **encoded_data 
    }
    
    # --- Salvamento ---
    try:
        with open(nome_arquivo_saida, 'w') as f:
            json.dump(nova_estrutura, f, separators=(',', ':')) 

        print(f"\n✅ Codificação (com acampamentos) concluída! Arquivo salvo como: {nome_arquivo_saida}")
        
    except Exception as e:
        print(f"❌ ERRO ao salvar o arquivo codificado: {e}")

# --- EXECUÇÃO ---
codificar_json_mapa_final(NOME_ARQUIVO_ORIGINAL, NOME_ARQUIVO_CODIFICADO)
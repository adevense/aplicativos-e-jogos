import json
import os

# Nome do seu arquivo JSON original com a estrutura detalhada
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))


NOME_ARQUIVO_ORIGINAL = os.path.join(CAMINHO_SCRIPT, 'mapa_final_200x86.json')
NOME_ARQUIVO_CODIFICADO = os.path.join(CAMINHO_SCRIPT, 'mapa_bd.json')

def codificar_json_mapa(nome_arquivo_entrada, nome_arquivo_saida):
    """
    Carrega o JSON detalhado e o converte para uma estrutura codificada
    com arrays de inteiros e um dicionário de mapeamento (metadata).
    """
    if not os.path.exists(nome_arquivo_entrada):
        print(f"ERRO: O arquivo de entrada '{nome_arquivo_entrada}' não foi encontrado.")
        print("Certifique-se de que o nome do arquivo está correto.")
        return

    # 1. Carregamento dos Dados
    try:
        with open(nome_arquivo_entrada, 'r') as f:
            dados_detalhados = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERRO ao decodificar o JSON: {e}")
        return
    
    # Assumindo que a estrutura principal do mapa está em "mapa"
    if "mapa" not in dados_detalhados or not dados_detalhados["mapa"]:
        print("ERRO: A estrutura 'mapa' não foi encontrada ou está vazia no JSON.")
        return

    mapa_detalhado = dados_detalhados["mapa"]
    
    # 2. Inicialização dos Mapeamentos e Arrays de Saída
    terreno_map = {}
    ambiente_map = {}
    
    # Arrays para armazenar os códigos numéricos, eliminando a repetição de chaves
    terreno_encoded = []
    ambiente_encoded = []
    movimentacao_encoded = []
    estabilidade_encoded = []
    
    terreno_counter = 0
    ambiente_counter = 0
    
    print(f"Iniciando codificação de um mapa com {len(mapa_detalhado)} linhas...")

    # 3. Processamento e Codificação Célula por Célula
    for row in mapa_detalhado:
        
        terreno_row = []
        ambiente_row = []
        movimentacao_row = []
        estabilidade_row = []
        
        for cell in row:
            # --- Codificação de Terreno ---
            terreno_val = cell["terreno"]
            if terreno_val not in terreno_map:
                terreno_map[terreno_val] = terreno_counter
                terreno_counter += 1
            terreno_row.append(terreno_map[terreno_val])
            
            # --- Codificação de Ambiente ---
            ambiente_val = cell["ambiente"]
            if ambiente_val not in ambiente_map:
                ambiente_map[ambiente_val] = ambiente_counter
                ambiente_counter += 1
            ambiente_row.append(ambiente_map[ambiente_val])
            
            # --- Codificação de Valores Numéricos (copia os valores) ---
            movimentacao_row.append(cell.get("valor_movimentacao", 0))
            estabilidade_row.append(cell.get("valor_estabilidade", 0))

        terreno_encoded.append(terreno_row)
        ambiente_encoded.append(ambiente_row)
        movimentacao_encoded.append(movimentacao_row)
        estabilidade_encoded.append(estabilidade_row)

    # 4. Inverte os Mapas (Código -> Nome) para a Metadados
    terreno_map_revertido = {v: k for k, v in terreno_map.items()}
    ambiente_map_revertido = {v: k for k, v in ambiente_map.items()}
    
    # 5. Monta a Nova Estrutura JSON Codificada
    nova_estrutura = {
        "metadata": {
            "num_rows": len(mapa_detalhado),
            "num_cols": len(mapa_detalhado[0]) if mapa_detalhado else 0,
            "terrenos_map": terreno_map_revertido,
            "ambientes_map": ambiente_map_revertido,
            # Se você tiver dados de NPCs/Players/Locais que não são atributos fixos
            # da célula, eles devem ser processados aqui (como uma lista de coordenadas).
        },
        "terreno": terreno_encoded,
        "ambiente": ambiente_encoded,
        "valor_movimentacao": movimentacao_encoded,
        "valor_estabilidade": estabilidade_encoded,
    }
    
    # 6. Salvamento
    with open(nome_arquivo_saida, 'w') as f:
        # Usamos `indent=4` para que o novo JSON seja legível, mas para a máxima
        # eficiência e leveza, você deve usar `indent=None` em produção.
        json.dump(nova_estrutura, f, indent=4)

    print("\n✅ Codificação concluída com sucesso!")
    print(f"O novo mapa codificado foi salvo como: {nome_arquivo_saida}")
    print("Agora este arquivo é muito mais leve e eficiente para carregar!")

# --- Execução do Codificador ---
codificar_json_mapa(NOME_ARQUIVO_ORIGINAL, NOME_ARQUIVO_CODIFICADO)
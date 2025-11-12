import json
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import sys

# --- 1. Configurações de Caminho ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_bd.json') 
OUTPUT_IMAGE_COMPLETO = os.path.join(CAMINHO_SCRIPT, 'mapa_completo.png')

WIDTH = 200
HEIGHT = 86

# --- 2. Definição de Cores e Mapeamento (Lógica de Visualização) ---
# Mapeia as STRINGS (decodificadas) para CORES

COLOR_MAP_RGB = {
    "agua": (0.2, 0.4, 0.6),        # Azul Escuro (Água)
    "gelo": (1.0, 1.0, 1.0),        # Branco (Gelo)
    "rochoso": (0.4, 0.2, 0.0),     # Marrom Escuro (Rochoso)
    "vegetacao_escuro": (0.0, 0.5, 0.0), # Verde Escuro (Terra/Floresta)
    "vegetacao_claro": (0.6, 0.8, 0.2), # Verde Claro (Vegetação/Campo)
    "vazio": (0.0, 0.0, 0.0),       # Preto (Vazio/Não Mapeado)
    "acampamento": (1.0, 0.0, 0.0), # Vermelho (Acampamento)
}

# Lista de cores na ordem dos ÍNDICES (0-6)
colors = [
    COLOR_MAP_RGB["agua"],
    COLOR_MAP_RGB["gelo"],
    COLOR_MAP_RGB["rochoso"],
    COLOR_MAP_RGB["vegetacao_escuro"],
    COLOR_MAP_RGB["vegetacao_claro"],
    COLOR_MAP_RGB["vazio"],
    COLOR_MAP_RGB["acampamento"],
]
labels = ["Água", "Gelo", "Rochoso", "Floresta", "Vegetação", "Vazio", "Acampamentos"]
cmap = ListedColormap(colors)

# Mapeia as STRINGS (lidas do JSON) para o ÍNDICE DE COR (0-6)
CLASSIFICATION_TO_INDEX = {
    # (Terreno, Ambiente) -> Índice de Cor
    ("agua", "oceano"): 0,      
    ("agua", "rio"): 0,         
    ("gelo", "geleira"): 1,     
    ("rochoso", "montanha"): 2, 
    ("gramado", "floresta"): 3, # "gramado" é o terreno lido do JSON
    ("gramado", "campo"): 4,    
    ("vazio", "vazio"): 5,      
    ("acampamento", "acampamento"): 6, 
}

# --- 3. Funções de Classificação e Carregamento ---

def get_classification_index_from_strings(terreno, ambiente, local_atual):
    """
    Recebe as strings decodificadas e retorna o ÍNDICE DE COR (0-6)
    para o Matplotlib.
    """
    if local_atual and local_atual != "None" and local_atual != "null": 
        return CLASSIFICATION_TO_INDEX.get(("acampamento", "acampamento"), 6)
    
    key = (terreno, ambiente)
    if key in CLASSIFICATION_TO_INDEX:
        return CLASSIFICATION_TO_INDEX[key]
            
    if terreno == "gramado":
        return CLASSIFICATION_TO_INDEX.get(("gramado", "campo"), 4)
    if terreno == "agua":
        return CLASSIFICATION_TO_INDEX.get(("agua", "oceano"), 0)
            
    return CLASSIFICATION_TO_INDEX.get(("vazio", "vazio"), 5)

def load_codified_map(json_path):
    """Carrega o arquivo JSON codificado."""
    try:
        with open(json_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON codificado não encontrado em {json_path}.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o arquivo JSON em {json_path}.")
        return None

# --- 4. Função Principal de Plotagem ---

def plot_map_codified(data):
    """Gera a imagem do mapa completo a partir dos dados codificados."""
    try:
        metadata = data["metadata"]
        terrenos_map = metadata["terrenos_map"]
        ambientes_map = metadata["ambientes_map"]
        local_atual_map = metadata.get("local_atual_map", {})
        
        mapa_terreno = data["terreno"]
        mapa_ambiente = data["ambiente"]
        mapa_local_atual = data.get("local_atual", [])

        map_matrix = np.full((HEIGHT, WIDTH), 5, dtype=int) 
        
        for y in range(HEIGHT):
            for x in range(WIDTH):
                # Decodifica os valores
                terreno_code = str(mapa_terreno[y][x])
                ambiente_code = str(mapa_ambiente[y][x])
                
                local_atual_val = None
                if mapa_local_atual:
                    local_atual_code = str(mapa_local_atual[y][x])
                    local_atual_val = local_atual_map.get(local_atual_code)

                terreno_str = terrenos_map.get(terreno_code, "vazio")
                ambiente_str = ambientes_map.get(ambiente_code, "vazio")
                
                # Re-classifica para o índice de cor
                map_matrix[y, x] = get_classification_index_from_strings(terreno_str, ambiente_str, local_atual_val)

        # Plotar
        fig, ax = plt.subplots(figsize=(12, 6))
        # vmin/vmax garantem que os índices 0-6 correspondam às cores 0-6
        ax.imshow(map_matrix, cmap=cmap, interpolation='nearest', vmin=0, vmax=len(colors)-1)
        
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.set_title("Visualização do Mapa Codificado (200x86)")
        ax.set_xlabel("Coluna (X)"); ax.set_ylabel("Linha (Y)")
        ax.set_xticks(np.arange(0, WIDTH, 3)); ax.set_yticks(np.arange(0, HEIGHT, 3))
        
        legend_elements = [Patch(facecolor=colors[i], edgecolor='black', label=labels[i]) for i in range(len(labels))]
        ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

        plt.tight_layout()
        plt.savefig(OUTPUT_IMAGE_COMPLETO, dpi=100)
        plt.close(fig)
        
        print(f"Sucesso: Imagem do mapa completo salva em {OUTPUT_IMAGE_COMPLETO}")

    except Exception as e:
        print(f"Erro ao plotar mapa completo: {e}")

# --- 5. Execução ---
if __name__ == "__main__":
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("O Matplotlib não está instalado. Tentando instalar...")
        os.system(f"{sys.executable} -m pip install matplotlib")
        import matplotlib.pyplot as plt
        
    data = load_codified_map(INPUT_JSON_PATH)
    if data:
        plot_map_codified(data)
    else:
        print("Não foi possível carregar os dados do mapa para visualização.")
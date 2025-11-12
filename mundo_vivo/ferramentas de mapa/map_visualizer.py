import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

# --- 1. Definições ---
WIDTH = 200
HEIGHT = 86
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Caminho para o seu arquivo JSON DETALHADO ORIGINAL
INPUT_JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_bd_decodificado.json') 
OUTPUT_IMAGE_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_completo.png')

# --- 2. Definição de Cores e Mapeamento (Sincronizado) ---
# Esta é a definição principal. A ordem aqui (Índices 0-6) 
# deve ser a mesma dos rótulos e da lógica de classificação.

# Cores em RGB (0.0 a 1.0) baseadas na sua legenda (imagem e710e8.png)
COLOR_MAP_RGB = {
    "agua": (0.2, 0.4, 0.6),        # Azul Escuro (Água)
    "gelo": (1.0, 1.0, 1.0),        # Branco (Gelo)
    "rochoso": (0.4, 0.2, 0.0),     # Marrom Escuro (Rochoso)
    "vegetacao_escuro": (0.0, 0.5, 0.0), # Verde Escuro (Terra/Floresta)
    "vegetacao_claro": (0.6, 0.8, 0.2), # Verde Claro (Vegetação/Campo)
    "vazio": (0.0, 0.0, 0.0),       # Preto (Vazio/Não Mapeado)
    "acampamento": (1.0, 0.0, 0.0), # Vermelho (Acampamento)
}

# 3. Lista de Cores e Rótulos (A ORDEM DEVE CORRESPONDER AOS ÍNDICES 0-6)
# Índice 0: Água
# Índice 1: Gelo
# Índice 2: Rochoso
# Índice 3: Terra
# Índice 4: Vegetação
# Índice 5: Vazio
# Índice 6: Acampamentos

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

# 4. Mapeamento de Classificação (JSON -> ÍNDICE 0-6)
CLASSIFICATION_TO_INDEX = {
    ("agua", "oceano"): 0,      
    ("agua", "rio"): 0,         
    ("gelo", "geleira"): 1,     
    ("rochoso", "montanha"): 2, 
    ("gramado", "floresta"): 3, # Gramado/Floresta = Terra
    ("gramado", "campo"): 4,    # Gramado/Campo = Vegetação
    ("vazio", "vazio"): 5,      
    ("acampamento", "acampamento"): 6, 
}

# 5. Função de Classificação Robusta (Índices 0-6)
def get_classification_index(field):
    terreno = field.get("terreno")
    ambiente = field.get("ambiente")
    local_atual = field.get("local_atual") # Pode ser None, "None", "null", "", ou "acampamento"

    # Prioridade 1: Acampamento (Índice 6)
    # Verifica se local_atual não é Nulo (None) E não é uma string vazia ("")
    # E não é a string "None" (que seu log mostrou)
    if local_atual and local_atual != "None" and local_atual != "null": 
        return CLASSIFICATION_TO_INDEX[("acampamento", "acampamento")]
    
    # Prioridade 2: Mapeamento Direto
    key = (terreno, ambiente)
    if key in CLASSIFICATION_TO_INDEX:
        return CLASSIFICATION_TO_INDEX[key]
            
    # Prioridade 3: Fallbacks Genéricos (Se o ambiente não estiver mapeado)
    if terreno == "gramado":
        return CLASSIFICATION_TO_INDEX[("gramado", "campo")] # Default (4)
    if terreno == "agua":
        return CLASSIFICATION_TO_INDEX[("agua", "oceano")] # Default (0)
            
    # Fallback Final: Vazio (Índice 5)
    return CLASSIFICATION_TO_INDEX.get(("vazio", "vazio"), 5)

# 6. Função de Plotagem
def plot_map():
    try:
        with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
        return

    mapa_data = data.get("mapa")
    if not mapa_data:
        print("Erro: A chave 'mapa' não foi encontrada no JSON.")
        return

    # Inicializa a matriz com o índice de 'Vazio' (5), não 'Água' (0)
    map_matrix = np.full((HEIGHT, WIDTH), 5, dtype=int) 
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            map_matrix[y, x] = get_classification_index(mapa_data[y][x]) 

    # Plotar
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 🚨 CORREÇÃO CRÍTICA (vmin/vmax) 🚨
    # Força o Matplotlib a usar nossos índices (0 a 6) sem normalização.
    # O valor 0 será a cor 0 (Água), o 4 será a cor 4 (Vegetação), o 6 será a cor 6 (Vermelho).
    im = ax.imshow(map_matrix, cmap=cmap, interpolation='nearest', vmin=0, vmax=len(colors)-1)
    
    ax.tick_params(axis='both', which='major', labelsize=5)
    ax.set_title("Visualização do Mapa por Tipo de Terreno (Grade 200x86)")
    ax.set_xlabel("Coluna (X)")
    ax.set_ylabel("Linha (Y)")
    
    # Ticks (Mantidos do seu código original)
    ax.set_xticks(np.arange(0, WIDTH, 3))
    ax.set_yticks(np.arange(0, HEIGHT, 3))
    
    # Legenda (Baseada nos índices 0-6)
    legend_elements = [Patch(facecolor=colors[i], edgecolor='black', label=labels[i]) for i in range(len(labels))]
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE_PATH, dpi=100)
    plt.close(fig)
    
    print(f"\n✅ Sucesso: O arquivo PNG visual foi gerado em {OUTPUT_IMAGE_PATH}")
    print("Verifique a imagem. As cores devem estar corretas agora.")

# 7. Execução
if __name__ == "__main__":
    plot_map()
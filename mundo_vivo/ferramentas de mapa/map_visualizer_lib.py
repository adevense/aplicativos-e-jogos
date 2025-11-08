import os
#import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import json

# Definições do mapa
WIDTH = 200
HEIGHT = 86
# O caminho para o JSON deve ser ajustado para onde o seu arquivo JSON está
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_final_200x86.json')
OUTPUT_IMAGE_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_visualizado_final.png')

# Mapeamento de Classificações para Cores e Rótulos (Baseado na Imagem de Referência)

# 1. Definição das Cores e Rótulos da Legenda (Estilo Matplotlib)
# As cores são aproximadas das cores da imagem de referência.
COLOR_MAP_MATPLOTLIB = {
    "agua": (0.2, 0.4, 0.6),        # Azul Escuro (Água)
    "gelo": (1.0, 1.0, 1.0),        # Branco (Gelo)
    "rochoso": (0.4, 0.2, 0.0),     # Marrom Escuro (Rochoso)
    "vegetacao_escuro": (0.0, 0.5, 0.0), # Verde Escuro (Terra/Floresta)
    "vegetacao_claro": (0.6, 0.8, 0.2), # Verde Claro (Vegetação/Campo)
    "vazio": (0.0, 0.0, 0.0),       # Preto (Vazio/Não Mapeado)
    "acampamento": (1.0, 0.0, 0.0), # Vermelho (Acampamento)
}

# 2. Mapeamento de Classificação do JSON para o ID da Cor
# Usaremos IDs de 1 a 7 para mapear as cores.
CLASSIFICATION_TO_ID = {
    ("agua", "oceano"): 1,
    ("agua", "rio"): 1,
    ("gelo", "geleira"): 2,
    ("rochoso", "montanha"): 3,
    ("gramado", "floresta"): 4, # Vegetação Escuro (Terra)
    ("gramado", "campo"): 5,    # Vegetação Claro (Vegetação)
    ("vazio", "vazio"): 6,      # Fallback para Vazio
    ("acampamento", "acampamento"): 7, # Acampamento
}

# 3. Definição da Matriz de Cores
# A ordem é importante para a legenda
colors = [
    COLOR_MAP_MATPLOTLIB["agua"],
    COLOR_MAP_MATPLOTLIB["gelo"],
    COLOR_MAP_MATPLOTLIB["rochoso"],
    COLOR_MAP_MATPLOTLIB["vegetacao_escuro"],
    COLOR_MAP_MATPLOTLIB["vegetacao_claro"],
    COLOR_MAP_MATPLOTLIB["vazio"],
    COLOR_MAP_MATPLOTLIB["acampamento"],
]
cmap = ListedColormap(colors)

# 4. Definição dos Rótulos da Legenda
labels = ["Água", "Gelo", "Rochoso", "Terra", "Vegetação", "Vazio", "Acampamentos"]

def get_classification_id(field):
    terreno = field.get("terreno")
    ambiente = field.get("ambiente")
    local_atual = field.get("local_atual")
    
    # Prioridade para Acampamento (Vermelho)
    if local_atual == "acampamento":
        return CLASSIFICATION_TO_ID[("acampamento", "acampamento")]
    
    # Classificações principais
    key = (terreno, ambiente)
    if key in CLASSIFICATION_TO_ID:
        return CLASSIFICATION_TO_ID[key]
        
    # Classificações de gramado (para mapear para as duas cores de vegetação)
    if terreno == "gramado":
        if ambiente == "floresta":
            return CLASSIFICATION_TO_ID[("gramado", "floresta")]
        else: # Campo ou qualquer outro gramado
            return CLASSIFICATION_TO_ID[("gramado", "campo")]
            
    # Classificações de água (para mapear para a cor de água)
    if terreno == "agua":
        return CLASSIFICATION_TO_ID[("agua", "oceano")]
        
    # Fallback para Vazio/Não Mapeado
    return CLASSIFICATION_TO_ID[("vazio", "vazio")]

def plot_map():
    try:
        with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em {INPUT_JSON_PATH}")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
        return

    mapa_data = data.get("mapa")
    if not mapa_data:
        print("Erro: A chave 'mapa' não foi encontrada no JSON.")
        return

    # Converter o JSON para uma matriz numpy de IDs de classificação
    map_matrix = np.zeros((HEIGHT, WIDTH), dtype=int)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            map_matrix[y, x] = get_classification_id(mapa_data[y][x])

    # Plotar com Matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Usar imshow para plotar a matriz
    im = ax.imshow(map_matrix, cmap=cmap, interpolation='nearest')
    ax.tick_params(axis='both', which='major', labelsize=5) # Diminuindo o tamanho da fonte

    # Configurar Título e Eixos
    ax.set_title("Visualização do Mapa por Tipo de Terreno (Grade 200x86)")
    ax.set_xlabel("Coluna (X)")
    ax.set_ylabel("Linha (Y)")
    
    # Configurar Ticks (para 200x86)
    ax.set_xticks(np.arange(0, WIDTH, 3))
    ax.set_yticks(np.arange(0, HEIGHT, 3))
    
    # Configurar a Legenda
    # Criar patches para a legenda
    legend_elements = [Patch(facecolor=colors[i], edgecolor='black', label=labels[i]) for i in range(len(labels))]
    
    # Adicionar a legenda
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    # Salvar a imagem
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE_PATH, dpi=100)
    plt.close(fig)
    
    print(f"Sucesso: O arquivo PNG visual foi gerado em {OUTPUT_IMAGE_PATH}")

if __name__ == "__main__":
    plot_map()
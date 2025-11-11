import json
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Patch
import sys

# --- Configurações de Caminho e Constantes ---
WIDTH = 200
HEIGHT = 86
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_final_200x86.json')
OUTPUT_IMAGE_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_visualizado_final.png')

# Terrenos e Ambientes Válidos (para edição)
TERRENOS_VALIDOS = ["agua", "gelo", "rochoso", "gramado", "vazio"]
AMBIENTES_VALIDOS = ["oceano", "rio", "geleira", "montanha", "terreno_rochoso", "floresta", "campo", "vazio"]

# 1. Definição das Cores (RGB)
COLOR_MAP_MATPLOTLIB = {
    "agua": (0.2, 0.4, 0.6),        # ID 0: Azul
    "gelo": (1.0, 1.0, 1.0),        # ID 1: Branco
    "rochoso": (0.4, 0.2, 0.0),     # ID 2: Marrom
    "vegetacao_escuro": (0.0, 0.5, 0.0), # ID 3: Verde escuro (Terra/Floresta)
    "vegetacao_claro": (0.6, 0.8, 0.2),  # ID 4: Verde claro (Vegetação/Campo)
    "vazio": (0.0, 0.0, 0.0),       # ID 5: Preto
    "acampamento": (1.0, 0.0, 0.0), # ID 6: Vermelho
}

# 2. Mapeamento de Classificação para ID (0 a 6)
CLASSIFICATION_TO_ID = {
    ("agua", "oceano"): 0,
    ("agua", "rio"): 0,
    ("gelo", "geleira"): 1,
    ("rochoso", "montanha"): 2,
    ("gramado", "floresta"): 3, 
    ("gramado", "campo"): 4, 
    ("vazio", "vazio"): 5, 
    ("acampamento", "acampamento"): 6, 
}

# 3. Definição da Matriz de Cores (ORDEM CRUCIAL: ID 0 a ID 6)
# Usamos a ordem garantida pelo ID para construir a paleta
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

# 4. Definição dos Rótulos da Legenda (Corresponde à ordem 0-6)
labels = ["Água", "Gelo", "Rochoso", "Terra", "Vegetação", "Vazio", "Acampamentos"]


def get_classification_id(field):
    terreno = field.get("terreno")
    ambiente = field.get("ambiente")
    local_atual = field.get("local_atual")
    
    # Prioridade para Acampamento (ID 6 - Vermelho)
    if local_atual == "acampamento":
        return CLASSIFICATION_TO_ID.get(("acampamento", "acampamento"), 6)
    
    # Classificações principais
    key = (terreno, ambiente)
    if key in CLASSIFICATION_TO_ID:
        return CLASSIFICATION_TO_ID[key]
        
    # Fallback por Terreno: 
    if terreno == "gramado":
        return CLASSIFICATION_TO_ID.get(("gramado", "campo"), 4)
    if terreno == "agua":
        return CLASSIFICATION_TO_ID.get(("agua", "oceano"), 0)
    if terreno == "gelo":
        return CLASSIFICATION_TO_ID.get(("gelo", "geleira"), 1)
    if terreno == "rochoso":
        return CLASSIFICATION_TO_ID.get(("rochoso", "montanha"), 2)
        
    # Fallback final para Vazio/Não Mapeado (ID 5 - Preto)
    return CLASSIFICATION_TO_ID.get(("vazio", "vazio"), 5)


def plot_map():
    try:
        data = load_map(INPUT_JSON_PATH)
        if not data or not data.get("mapa"):
            return

        mapa_data = data["mapa"]
        map_matrix = np.zeros((HEIGHT, WIDTH), dtype=int)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                map_matrix[y, x] = get_classification_id(mapa_data[y][x]) 

        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 🛑 Aplicar vmin/vmax também na visualização completa
        ax.imshow(map_matrix, cmap=cmap, interpolation='nearest', vmin=0, vmax=6)
        
        ax.tick_params(axis='both', which='major', labelsize=5) 

        ax.set_title("Visualização do Mapa por Tipo de Terreno (Grade 200x86)")
        ax.set_xlabel("Coluna (X)")
        ax.set_ylabel("Linha (Y)")
        
        ax.set_xticks(np.arange(0, WIDTH, 3))
        ax.set_yticks(np.arange(0, HEIGHT, 3))
        
        legend_elements = [Patch(facecolor=colors[i], edgecolor='black', label=labels[i]) for i in range(len(labels))]
        ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

        plt.tight_layout()
        plt.savefig(OUTPUT_IMAGE_PATH, dpi=100)
        plt.close(fig)
        
        print(f"Sucesso: O arquivo PNG visual foi gerado em {OUTPUT_IMAGE_PATH}")

    except Exception as e:
        print(f"Erro na plotagem do mapa: {e}")

# ... (Mantenha as funções load_map, save_map, get_valid_input e edit_map como na última versão) ...

# --- Funções de Visualização ---

def visualize_focus_area(mapa, q_focus, r_focus, output_image_path="mapa_visualizado_foco.png"):
    FOCUS_SIZE = 5
    q_min = max(0, q_focus - FOCUS_SIZE)
    q_max = min(WIDTH, q_focus + FOCUS_SIZE + 1)
    r_min = max(0, r_focus - FOCUS_SIZE)
    r_max = min(HEIGHT, r_focus + FOCUS_SIZE + 1)
    
    focus_matrix = np.zeros((r_max - r_min, q_max - q_min), dtype=int)
    
    for r_idx, r in enumerate(range(r_min, r_max)):
        for q_idx, q in enumerate(range(q_min, q_max)):
            focus_matrix[r_idx, q_idx] = get_classification_id(mapa[r][q]) 

    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 🛑 CORREÇÃO FINAL: Definir vmin e vmax para forçar o mapeamento de 0 a 6
    # Isso garante que o ID 0 use a primeira cor e o ID 6 use a última cor.
    ax.imshow(focus_matrix, cmap=cmap, interpolation='nearest', vmin=0, vmax=6)
    
    focus_q_rel = q_focus - q_min
    focus_r_rel = r_focus - r_min
    
    rect = Rectangle((focus_q_rel - 0.5, focus_r_rel - 0.5), 1, 1, 
                     edgecolor='magenta', facecolor='none', linewidth=3)
    ax.add_patch(rect)
    
    ax.set_xticks(np.arange(q_max - q_min))
    ax.set_xticklabels(np.arange(q_min, q_max))
    ax.set_yticks(np.arange(r_max - r_min))
    ax.set_yticklabels(np.arange(r_min, r_max))
    
    ax.set_title(f"Foco em ({q_focus}, {r_focus})")
    
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=100)
    plt.close(fig)
    
    print(f"Sucesso: Visualização de foco gerada em {output_image_path}")

# --- Funções de Edição (Adição do Debug Crucial) ---

def load_map(json_path):
    # ... (mesma função) ...
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em {json_path}.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o arquivo JSON em {json_path}.")
        return None

def save_map(data, json_path):
    # ... (mesma função) ...
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nMapa salvo em {json_path}")

def get_valid_input(prompt, valid_options):
    # ... (mesma função) ...
    while True:
        user_input = input(prompt).lower().strip()
        if user_input in valid_options:
            return user_input
        print(f"Entrada inválida. As opções válidas são: {', '.join(valid_options)}")

def edit_map():
    data = load_map(INPUT_JSON_PATH)
    if not data:
        return

    mapa = data["mapa"]
    num_rows = len(mapa)
    num_cols = len(mapa[0])
    
    while True:
        print("-" * 50)
        print("Editor de Célula Específica")
        
        try:
            q = int(input(f"Digite a Coluna X (0 a {num_cols - 1}): "))
            r = int(input(f"Digite a Linha Y (0 a {num_rows - 1}): "))
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")
            continue

        if not (0 <= q < num_cols and 0 <= r < num_rows):
            print("Coordenadas fora dos limites do mapa.")
            continue

        cell = mapa[r][q]
        
        print("-" * 50)
        
        # 🛑 DIAGNÓSTICO CRUCIAL: Exibe os dados brutos da célula antes de plotar
        print("🛑 DADOS BRUTOS DO JSON NA CÉLULA ANTES DA EDIÇÃO:")
        print(f"   Terreno: {cell.get('terreno')}")
        print(f"   Ambiente: {cell.get('ambiente')}")
        print(f"   Local Atual: {cell.get('local_atual')}")
        calculated_id = get_classification_id(cell)
        print(f"   ID Calculado: {calculated_id} (Deveria ser a cor no índice {calculated_id} da lista 'colors')")
        print("-" * 50)
        
        # Gera a visualização de foco
        visualize_focus_area(mapa, q, r)
        
        print(f"Célula em foco: ({q}, {r}) - Terreno Atual: {cell.get('terreno')}, Ambiente Atual: {cell.get('ambiente')}")
        
        confirmar = input("A célula está correta para edição? (s/n): ").lower().strip()
        if confirmar != 's':
            print("Edição cancelada. Escolha outra célula.")
            continue
            
        novo_terreno = get_valid_input(f"Novo Terreno ({'/'.join(TERRENOS_VALIDOS)}): ", TERRENOS_VALIDOS)
        novo_ambiente = get_valid_input(f"Novo Ambiente ({'/'.join(AMBIENTES_VALIDOS)}): ", AMBIENTES_VALIDOS)
        
        cell["terreno"] = novo_terreno
        cell["ambiente"] = novo_ambiente
        cell["descricao"] = f"Terreno: {novo_terreno.capitalize()}, Ambiente: {novo_ambiente.capitalize()} (Corrigido Manualmente)"
        
        save_map(data, INPUT_JSON_PATH)
        
        plot_map()
        
        continuar = input("Pressione ENTER para editar outra célula, ou 's' para sair: ").lower().strip()
        if continuar == 's':
            break

    print("\nEdição manual concluída.")

if __name__ == "__main__":
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("O Matplotlib não está instalado. Tentando instalar...")
        os.system(f"{sys.executable} -m pip install matplotlib")
        import matplotlib.pyplot as plt
        
    edit_map()
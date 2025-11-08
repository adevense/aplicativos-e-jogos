import json
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle # Usar Rectangle para compatibilidade

# --- Configurações de Caminho ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_final_200x86.json')

# Terrenos e Ambientes Válidos
TERRENOS_VALIDOS = ["agua", "gelo", "rochoso", "gramado", "vazio"]
AMBIENTES_VALIDOS = ["oceano", "rio", "geleira", "montanha", "terreno_rochoso", "floresta", "campo", "vazio"]

# --- Funções de Plotagem ---
WIDTH = 200
HEIGHT = 86

COLOR_MAP_MATPLOTLIB = {
    "agua": (0.2, 0.4, 0.6),
    "gelo": (1.0, 1.0, 1.0),
    "rochoso": (0.4, 0.2, 0.0),
    "vegetacao_escuro": (0.0, 0.5, 0.0),
    "vegetacao_claro": (0.6, 0.8, 0.2),
    "vazio": (0.0, 0.0, 0.0),
    "acampamento": (1.0, 0.0, 0.0),
}

CLASSIFICATION_TO_ID = {
    ("agua", "oceano"): 1,
    ("agua", "rio"): 1,
    ("gelo", "geleira"): 2,
    ("rochoso", "montanha"): 3,
    ("gramado", "floresta"): 4,
    ("gramado", "campo"): 5,
    ("vazio", "vazio"): 6,
    ("acampamento", "acampamento"): 7,
}

colors = [
    COLOR_MAP_MATPLOTLIB["agua"], COLOR_MAP_MATPLOTLIB["gelo"], COLOR_MAP_MATPLOTLIB["rochoso"],
    COLOR_MAP_MATPLOTLIB["vegetacao_escuro"], COLOR_MAP_MATPLOTLIB["vegetacao_claro"],
    COLOR_MAP_MATPLOTLIB["vazio"], COLOR_MAP_MATPLOTLIB["acampamento"],
]
cmap = ListedColormap(colors)
labels = ["Água", "Gelo", "Rochoso", "Terra", "Vegetação", "Vazio", "Acampamentos"]

def get_classification_id(field):
    terreno = field.get("terreno")
    ambiente = field.get("ambiente")
    local_atual = field.get("local_atual")
    
    # 1. Prioridade para Acampamento (vermelho)
    if local_atual == "acampamento":
        # Retorna o ID 7 (Acampamento) APENAS se houver acampamento
        return CLASSIFICATION_TO_ID[("acampamento", "acampamento")]
    
    # 2. Mapeamento Exato
    key = (terreno, ambiente)
    if key in CLASSIFICATION_TO_ID:
        return CLASSIFICATION_TO_ID[key]
        
    # 3. Fallback por Terreno (para garantir que a cor base esteja correta)
    if terreno == "gramado":
        # Se não for floresta (ID 4), assume campo (ID 5)
        return CLASSIFICATION_TO_ID.get(("gramado", "campo"), 5)
    if terreno == "agua":
        # Se não for rio (ID 1), assume oceano (ID 1)
        return CLASSIFICATION_TO_ID.get(("agua", "oceano"), 1)
    if terreno == "gelo":
        return CLASSIFICATION_TO_ID.get(("gelo", "geleira"), 2)
    if terreno == "rochoso":
        return CLASSIFICATION_TO_ID.get(("rochoso", "montanha"), 3)
        
    # 4. Fallback final para Vazio (preto)
    # O ID 7 (vermelho) não é usado como fallback em nenhuma circunstância.
    return CLASSIFICATION_TO_ID.get(("vazio", "vazio"), 6)

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
    ax.imshow(focus_matrix, cmap=cmap, interpolation='nearest')
    
    focus_q_rel = q_focus - q_min
    focus_r_rel = r_focus - r_min
    
    rect = Rectangle((focus_q_rel - 0.5, focus_r_rel - 0.5), 1, 1, 
                     edgecolor='magenta', facecolor='none', linewidth=3) # Cor alterada para magenta
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

def visualize_map_final(json_path, output_image_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erro ao ler JSON para visualização: {e}")
        return

    mapa_data = data.get("mapa")
    map_matrix = np.zeros((HEIGHT, WIDTH), dtype=int)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            map_matrix[y, x] = get_classification_id(mapa_data[y][x])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(map_matrix, cmap=cmap, interpolation='nearest')
    ax.tick_params(axis='both', which='major', labelsize=5)

    ax.set_title("Visualização do Mapa por Tipo de Terreno (Grade 200x86)")
    ax.set_xlabel("Coluna (X)")
    ax.set_ylabel("Linha (Y)")
    
    ax.set_xticks(np.arange(0, WIDTH, 3))
    ax.set_yticks(np.arange(0, HEIGHT, 3))
    
    legend_elements = [Rectangle((0, 0), 1, 1, facecolor=colors[i], edgecolor='black', label=labels[i]) for i in range(len(labels))]
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    plt.tight_layout()
    plt.savefig(output_image_path, dpi=100)
    plt.close(fig)
    
    print(f"Sucesso: O arquivo PNG visual foi gerado em {output_image_path}")

def load_map():
    try:
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em {JSON_PATH}.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o arquivo JSON em {JSON_PATH}.")
        return None

def save_map(data):
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nMapa salvo em {JSON_PATH}")

def get_valid_input(prompt, valid_options):
    while True:
        user_input = input(prompt).lower().strip()
        if user_input in valid_options:
            return user_input
        print(f"Entrada inválida. As opções válidas são: {', '.join(valid_options)}")

def edit_map():
    data = load_map()
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
        
        visualize_focus_area(mapa, q, r)
        
        print(f"Célula em foco: ({q}, {r}) - Terreno Atual: {cell['terreno']}, Ambiente Atual: {cell['ambiente']}")
        
        confirmar = input("A célula está correta para edição? (s/n): ").lower().strip()
        if confirmar != 's':
            print("Edição cancelada. Escolha outra célula.")
            continue
            
        novo_terreno = get_valid_input(f"Novo Terreno ({'/'.join(TERRENOS_VALIDOS)}): ", TERRENOS_VALIDOS)
        novo_ambiente = get_valid_input(f"Novo Ambiente ({'/'.join(AMBIENTES_VALIDOS)}): ", AMBIENTES_VALIDOS)
        
        cell["terreno"] = novo_terreno
        cell["ambiente"] = novo_ambiente
        cell["descricao"] = f"Terreno: {novo_terreno.capitalize()}, Ambiente: {novo_ambiente.capitalize()} (Corrigido Manualmente)"
        
        save_map(data)
        
        visualize_map_final(json_path=JSON_PATH, output_image_path="mapa_visualizado_final.png")
        
        continuar = input("Pressione ENTER para editar outra célula, ou 's' para sair: ").lower().strip()
        if continuar == 's':
            break

    print("\nEdição manual concluída.")

if __name__ == "__main__":
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Instalando matplotlib...")
        os.system("pip3 install matplotlib")
        import matplotlib.pyplot as plt
        
    edit_map()
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Patch
import sys

# --- 1. Configurações de Caminho ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_codificado.json') 
OUTPUT_IMAGE_FOCO = os.path.join(CAMINHO_SCRIPT, 'mapa_foco.png')
OUTPUT_IMAGE_COMPLETO = os.path.join(CAMINHO_SCRIPT, 'mapa_completo.png')

WIDTH = 200
HEIGHT = 86

# --- 2. Definição de Cores e Mapeamento (Lógica de Visualização) ---
COLOR_MAP_RGB = {
    "agua": (0.2, 0.4, 0.6),        # Azul Escuro (Água)
    "gelo": (1.0, 1.0, 1.0),        # Branco (Gelo)
    "rochoso": (0.4, 0.2, 0.0),     # Marrom Escuro (Rochoso)
    "vegetacao_escuro": (0.0, 0.5, 0.0), # Verde Escuro (Terra/Floresta)
    "vegetacao_claro": (0.6, 0.8, 0.2), # Verde Claro (Vegetação/Campo)
    "vazio": (0.0, 0.0, 0.0),       # Preto (Vazio/Não Mapeado)
    "acampamento": (1.0, 0.0, 0.0), # Vermelho (Acampamento)
}
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

# --- 3. Funções de Classificação (Lógica de Visualização) ---
def get_classification_index_from_strings(terreno, ambiente, local_atual):
    if local_atual and local_atual != "None" and local_atual != "null": 
        return CLASSIFICATION_TO_INDEX.get(("acampamento", "acampamento"), 6)
    key = (terreno, ambiente)
    if key in CLASSIFICATION_TO_INDEX: return CLASSIFICATION_TO_INDEX[key]
    if terreno == "gramado": return CLASSIFICATION_TO_INDEX.get(("gramado", "campo"), 4)
    if terreno == "agua": return CLASSIFICATION_TO_INDEX.get(("agua", "oceano"), 0)
    return CLASSIFICATION_TO_INDEX.get(("vazio", "vazio"), 5)

# --- 4. Funções de Visualização (Usadas pelo Editor) ---
def plot_map_codified(data):
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
                terreno_code = str(mapa_terreno[y][x])
                ambiente_code = str(mapa_ambiente[y][x])
                local_atual_val = None
                if mapa_local_atual:
                    local_atual_code = str(mapa_local_atual[y][x])
                    local_atual_val = local_atual_map.get(local_atual_code)
                terreno_str = terrenos_map.get(terreno_code, "vazio")
                ambiente_str = ambientes_map.get(ambiente_code, "vazio")
                map_matrix[y, x] = get_classification_index_from_strings(terreno_str, ambiente_str, local_atual_val)

        fig, ax = plt.subplots(figsize=(12, 6))
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
        print(f"Sucesso: Imagem do mapa completo atualizada em {OUTPUT_IMAGE_COMPLETO}")
    except Exception as e:
        print(f"Erro ao plotar mapa completo: {e}")

def visualize_focus_codified(data, q_focus, r_focus):
    try:
        metadata = data["metadata"]
        terrenos_map = metadata["terrenos_map"]
        ambientes_map = metadata["ambientes_map"]
        local_atual_map = metadata.get("local_atual_map", {})
        mapa_terreno = data["terreno"]
        mapa_ambiente = data["ambiente"]
        mapa_local_atual = data.get("local_atual", [])

        FOCUS_SIZE = 5
        q_min = max(0, q_focus - FOCUS_SIZE)
        q_max = min(WIDTH, q_focus + FOCUS_SIZE + 1)
        r_min = max(0, r_focus - FOCUS_SIZE)
        r_max = min(HEIGHT, r_focus + FOCUS_SIZE + 1)
        
        focus_matrix = np.full((r_max - r_min, q_max - q_min), 5, dtype=int)
        
        for r_idx, r in enumerate(range(r_min, r_max)):
            for q_idx, q in enumerate(range(q_min, q_max)):
                terreno_code = str(mapa_terreno[r][q])
                ambiente_code = str(mapa_ambiente[r][q])
                local_atual_val = None
                if mapa_local_atual:
                    local_atual_code = str(mapa_local_atual[r][q])
                    local_atual_val = local_atual_map.get(local_atual_code)
                terreno_str = terrenos_map.get(terreno_code, "vazio")
                ambiente_str = ambientes_map.get(ambiente_code, "vazio")
                focus_matrix[r_idx, q_idx] = get_classification_index_from_strings(terreno_str, ambiente_str, local_atual_val)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(focus_matrix, cmap=cmap, interpolation='nearest', vmin=0, vmax=len(colors)-1)
        focus_q_rel = q_focus - q_min
        focus_r_rel = r_focus - r_min
        rect = Rectangle((focus_q_rel - 0.5, focus_r_rel - 0.5), 1, 1, 
                         edgecolor='magenta', facecolor='none', linewidth=3)
        ax.add_patch(rect)
        ax.set_xticks(np.arange(q_max - q_min)); ax.set_xticklabels(np.arange(q_min, q_max))
        ax.set_yticks(np.arange(r_max - r_min)); ax.set_yticklabels(np.arange(r_min, r_max))
        ax.set_title(f"Foco em ({q_focus}, {r_focus})")
        plt.tight_layout()
        plt.savefig(OUTPUT_IMAGE_FOCO, dpi=100)
        plt.close(fig)
        print(f"Sucesso: Visualização de foco gerada em {OUTPUT_IMAGE_FOCO}")
    except Exception as e:
        print(f"Erro ao plotar foco: {e}")

# --- 5. Funções de Edição ---
def load_codified_map(json_path):
    try:
        with open(json_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON codificado não encontrado em {json_path}.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o arquivo JSON em {json_path}.")
        return None

def save_codified_map(data, json_path):
    try:
        with open(json_path, "w", encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))
        print(f"\nMapa codificado salvo em {json_path}")
    except Exception as e:
        print(f"Erro ao salvar JSON codificado: {e}")

def get_valid_input(prompt, valid_options):
    while True:
        user_input = input(prompt).lower().strip()
        if user_input in valid_options:
            return user_input
        print(f"Entrada inválida. As opções válidas são: {', '.join(valid_options)}")

def edit_map_codified():
    data = load_codified_map(INPUT_JSON_PATH)
    if not data:
        return

    # --- Prepara os mapas de DEcodificação (Código -> String) ---
    metadata = data["metadata"]
    terrenos_decode = metadata["terrenos_map"]
    ambientes_decode = metadata["ambientes_map"]
    local_atual_decode = metadata.get("local_atual_map", {})
    
    # --- Prepara os mapas de ENcodificação (String -> Código) ---
    terrenos_encode = {v: int(k) for k, v in terrenos_decode.items()}
    ambientes_encode = {v: int(k) for k, v in ambientes_decode.items()}
    local_atual_encode = {v if v is not None else None: int(k) for k, v in local_atual_decode.items()}

    valid_terrenos = list(terrenos_encode.keys())
    valid_ambientes = list(ambientes_encode.keys())
    valid_locals_str = [str(k) if k is not None else "nenhum" for k in local_atual_encode.keys()]

    while True:
        print("-" * 50); print("Editor de Célula (Versão Codificada)")
        
        try:
            q = int(input(f"Digite a Coluna X (0 a {WIDTH - 1}): "))
            r = int(input(f"Digite a Linha Y (0 a {HEIGHT - 1}): "))
        except ValueError:
            print("Entrada inválida. Digite um número inteiro."); continue

        if not (0 <= q < WIDTH and 0 <= r < HEIGHT):
            print("Coordenadas fora dos limites do mapa."); continue
        
        # --- Decodifica os valores atuais ---
        terreno_code_atual = str(data["terreno"][r][q])
        ambiente_code_atual = str(data["ambiente"][r][q])
        local_atual_code_atual = str(data["local_atual"][r][q])

        terreno_str = terrenos_decode.get(terreno_code_atual, "vazio")
        ambiente_str = ambientes_decode.get(ambiente_code_atual, "vazio")
        local_atual_val = local_atual_decode.get(local_atual_code_atual, None)
        
        print("-" * 50)
        visualize_focus_codified(data, q, r)
        
        print(f"Célula em foco: ({q}, {r})")
        print(f"   Terreno Atual: {terreno_str}")
        print(f"   Ambiente Atual: {ambiente_str}")
        print(f"   Local Atual: {local_atual_val}")
        
        confirmar = input("A célula está correta para edição? (s/n): ").lower().strip()
        if confirmar != 's':
            print("Edição cancelada. Escolha outra célula."); continue
            
        # --- Obtém Novos Valores (Strings) ---
        print(f"\nOpções de Terreno: {', '.join(valid_terrenos)}")
        novo_terreno_str = get_valid_input("Novo Terreno: ", valid_terrenos)
        
        print(f"\nOpções de Ambiente: {', '.join(valid_ambientes)}")
        novo_ambiente_str = get_valid_input("Novo Ambiente: ", valid_ambientes)

        print(f"\nOpções de Local: {', '.join(valid_locals_str)}")
        novo_local_input = get_valid_input("Novo Local Atual (ou 'nenhum'): ", valid_locals_str)
        
        novo_local_val = None if novo_local_input == "nenhum" else novo_local_input
        
        # --- Re-codifica os valores para Inteiros ---
        new_terreno_code = terrenos_encode[novo_terreno_str]
        new_ambiente_code = ambientes_encode[novo_ambiente_str]
        new_local_code = local_atual_encode[novo_local_val]
        
        # --- Atualiza os arrays no JSON ---
        data["terreno"][r][q] = new_terreno_code
        data["ambiente"][r][q] = new_ambiente_code
        data["local_atual"][r][q] = new_local_code
        
        save_codified_map(data, INPUT_JSON_PATH)
        plot_map_codified(data) 
        
        continuar = input("Pressione ENTER para editar outra célula, ou 's' para sair: ").lower().strip()
        if continuar == 's': break

    print("\nEdição manual concluída.")

# --- 6. Execução ---
if __name__ == "__main__":
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("O Matplotlib não está instalado. Tentando instalar...")
        os.system(f"{sys.executable} -m pip install matplotlib")
        import matplotlib.pyplot as plt
        
    edit_map_codified()
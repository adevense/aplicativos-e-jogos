import json
import os
import matplotlib.pyplot as plt
import numpy as np

# --- Configurações de Caminho ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# O JSON de entrada/saída é o resultado do gap-filling
JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_final_200x86.json') 
OUTPUT_IMAGE_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_visualizado_foco.png')

# --- Mapeamento de Cores para Visualização (Deve ser o mesmo do visualizador) ---
COLOR_MAP = {
    "agua": "#4682B4",          # Azul Aço
    "oceano": "#4682B4",        # Azul Aço
    "gelo": "#F0F8FF",          # Branco Alice
    "geleira": "#F0F8FF",       # Branco Alice
    "rochoso": "#8B4513",       # Cinza Escuro
    "terreno_rochoso": "#8B4513", # Cinza Escuro
    "terra": "#EA00FF",         # Marrom Sela
    "floresta": "#228B22",      # Verde Floresta
    "vegetacao_escassa": "#9ACD32", # Amarelo Verdeado
    "campo": "#ADFF2F",         # Verde Amarelo
    "vazio": "#000000",         # Preto (para células não classificadas)
    "desconhecido": "#FF0000"   # Vermelho (para erros de classificação)
}

# Terrenos e Ambientes Válidos
TERRENOS_VALIDOS = ["agua", "gelo", "rochoso", "terra", "vazio"]
AMBIENTES_VALIDOS = ["oceano", "geleira", "montanha", "terreno_rochoso", "floresta", "vegetacao_escassa", "campo", "vazio"]

def hex_to_rgb(hex_color):
    """Converte uma string de cor hexadecimal para uma tupla RGB (0-1)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def load_map():
    """Carrega o arquivo JSON do mapa."""
    try:
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em {JSON_PATH}. Certifique-se de que o processamento V1 foi concluído.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o arquivo JSON em {JSON_PATH}.")
        return None

def save_map(data):
    """Salva o arquivo JSON do mapa."""
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nMapa salvo em {JSON_PATH}")

def visualize_cell_focus(mapa, r_focus, q_focus):
    """Gera uma visualização do mapa com a célula de foco destacada."""
    
    num_rows = len(mapa)
    num_cols = len(mapa[0])
    image_data = np.zeros((num_rows, num_cols, 3))
    
    for r in range(num_rows):
        for q in range(num_cols):
            cell = mapa[r][q]
            
            # Cor da célula
            key = cell.get("ambiente")
            if key in COLOR_MAP:
                color = hex_to_rgb(COLOR_MAP[key])
            else:
                key = cell.get("terreno")
                if key in COLOR_MAP:
                    color = hex_to_rgb(COLOR_MAP[key])
                else:
                    color = hex_to_rgb(COLOR_MAP.get("vazio", "#000000"))
            
            image_data[r, q] = color

    # Destacar a célula de foco com um quadrado vermelho
    # O Matplotlib plota (y, x) para (linha, coluna)
    # Usamos uma borda de 1 pixel para destacar
    if 0 <= r_focus < num_rows and 0 <= q_focus < num_cols:
        # Cor da borda (vermelho)
        border_color = hex_to_rgb("#FF0000") 
        
        # Desenha a borda (1 pixel ao redor)
        for dr in [-1, 0, 1]:
            for dq in [-1, 0, 1]:
                if abs(dr) + abs(dq) > 0: # Apenas a borda, não o centro
                    br, bq = r_focus + dr, q_focus + dq
                    if 0 <= br < num_rows and 0 <= bq < num_cols:
                        image_data[br, bq] = border_color
        
        # Desenha um ponto vermelho no centro (para ser mais visível)
        image_data[r_focus, q_focus] = hex_to_rgb("#FF0000")

    # Gerar a imagem
    plt.figure(figsize=(num_cols / 10, num_rows / 10))
    plt.imshow(image_data)
    plt.title(f"Foco na Célula ({q_focus}, {r_focus}) - Terreno: {mapa[r_focus][q_focus]['terreno']}")
    plt.axis('off')
    plt.tight_layout()
    
    # Salvar a imagem
    plt.savefig(OUTPUT_IMAGE_PATH, dpi=100)
    plt.close()
    
    print(f"\nVisualização de foco salva em {OUTPUT_IMAGE_PATH}")
    print(f"Abra o arquivo para ver a célula destacada.")

def get_valid_input(prompt, valid_options):
    """Obtém uma entrada válida do usuário."""
    while True:
        user_input = input(prompt).lower().strip()
        if user_input in valid_options:
            return user_input
        print(f"Entrada inválida. As opções válidas são: {', '.join(valid_options)}")

def edit_map():
    """Itera sobre células vazias/desconhecidas e permite edição manual."""
    
    data = load_map()
    if not data:
        return

    mapa = data["mapa"]
    num_rows = len(mapa)
    num_cols = len(mapa[0])
    
    cells_to_edit = []
    for r in range(num_rows):
        for q in range(num_cols):
            cell = mapa[r][q]
            if cell["terreno"] in ["vazio", "desconhecido"]:
                cells_to_edit.append((r, q))

    if not cells_to_edit:
        print("Nenhuma célula 'vazio' ou 'desconhecido' encontrada. O mapa está limpo!")
        return

    print(f"Iniciando edição manual. {len(cells_to_edit)} células para corrigir.")
    
    for r, q in cells_to_edit:
        cell = mapa[r][q]
        
        print("-" * 50)
        print(f"Editando Célula ({q}, {r})")
        print(f"Terreno Atual: {cell['terreno']}, Ambiente Atual: {cell['ambiente']}")
        
        # 1. Gerar visualização de foco
        visualize_cell_focus(mapa, r, q)
        
        # 2. Obter nova classificação
        novo_terreno = get_valid_input(f"Novo Terreno ({'/'.join(TERRENOS_VALIDOS)}): ", TERRENOS_VALIDOS)
        novo_ambiente = get_valid_input(f"Novo Ambiente ({'/'.join(AMBIENTES_VALIDOS)}): ", AMBIENTES_VALIDOS)
        
        # 3. Aplicar e salvar
        cell["terreno"] = novo_terreno
        cell["ambiente"] = novo_ambiente
        cell["descricao"] = f"Terreno: {novo_terreno.capitalize()}, Ambiente: {novo_ambiente.capitalize()} (Corrigido Manualmente)"
        
        save_map(data)
        
        # Pergunta se quer continuar
        continuar = input("Pressione ENTER para continuar para a próxima célula, ou 's' para sair: ").lower().strip()
        if continuar == 's':
            break

    print("\nEdição manual concluída.")

if __name__ == "__main__":
    # Instalar matplotlib se não estiver instalado
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Instalando matplotlib...")
        os.system("pip3 install matplotlib")
        import matplotlib.pyplot as plt
        
    edit_map()

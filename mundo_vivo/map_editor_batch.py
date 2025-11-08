import json
import os
import matplotlib.pyplot as plt
import numpy as np

# --- Configurações de Caminho ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# O JSON de entrada/saída é o resultado do gap-filling
JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_final_200x86.json') 
OUTPUT_IMAGE_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_visualizado_batch.png')

# --- Mapeamento de Cores para Visualização (Deve ser o mesmo do visualizador) ---
COLOR_MAP = {
    "agua": "#FF03E6",          # Azul Aço
    "oceano": "#4682B4",        # Azul Aço
    "gelo": "#F0F8FF",          # Branco Alice
    "geleira": "#F0F8FF",       # Branco Alice
    "rochoso": "#A9A9A9",       # Cinza Escuro
    "terreno_rochoso": "#A9A9A9", # Cinza Escuro
    "terra": "#8B4513",         # Marrom Sela
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

def visualize_batch_focus(mapa, x_start, y_start, x_end, y_end):
    """Gera uma visualização do mapa com a região de foco destacada."""
    
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

    # Destacar a região selecionada com uma borda amarela
    highlight_color = hex_to_rgb("#FFFF00") # Amarelo
    
    # Garantir que as coordenadas estejam dentro dos limites
    y_start = max(0, min(y_start, num_rows - 1))
    y_end = max(0, min(y_end, num_rows - 1))
    x_start = max(0, min(x_start, num_cols - 1))
    x_end = max(0, min(x_end, num_cols - 1))
    
    # Desenhar a borda
    for r in range(y_start, y_end + 1):
        for q in range(x_start, x_end + 1):
            # Desenhar um ponto amarelo no centro da célula
            image_data[r, q] = highlight_color

    # Gerar a imagem
    plt.figure(figsize=(num_cols / 10, num_rows / 10))
    plt.imshow(image_data)
    plt.title(f"Foco na Região ({x_start},{y_start}) a ({x_end},{y_end})")
    plt.axis('off')
    plt.tight_layout()
    
    # Salvar a imagem
    plt.savefig(OUTPUT_IMAGE_PATH, dpi=100)
    plt.close()
    
    print(f"\nVisualização de foco salva em {OUTPUT_IMAGE_PATH}")
    print(f"Abra o arquivo para ver a região destacada.")

def get_valid_input(prompt, valid_options):
    """Obtém uma entrada válida do usuário."""
    while True:
        user_input = input(prompt).lower().strip()
        if user_input in valid_options:
            return user_input
        print(f"Entrada inválida. As opções válidas são: {', '.join(valid_options)}")

def get_valid_coord(prompt, max_val):
    """Obtém uma coordenada numérica válida do usuário."""
    while True:
        try:
            coord = int(input(prompt))
            if 0 <= coord < max_val:
                return coord
            print(f"Coordenada inválida. Deve ser um número inteiro entre 0 e {max_val - 1}.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")

def edit_map_batch():
    """Permite a edição em massa de regiões retangulares."""
    
    data = load_map()
    if not data:
        return

    mapa = data["mapa"]
    num_rows = len(mapa)
    num_cols = len(mapa[0])
    
    print("Iniciando edição em massa por região retangular.")
    print(f"O mapa tem {num_cols} colunas (X: 0 a {num_cols - 1}) e {num_rows} linhas (Y: 0 a {num_rows - 1}).")
    
    while True:
        print("-" * 50)
        
        # 1. Obter coordenadas da região
        print("Defina o canto superior esquerdo (X, Y):")
        x_start = get_valid_coord("X inicial (Coluna): ", num_cols)
        y_start = get_valid_coord("Y inicial (Linha): ", num_rows)
        
        print("Defina o canto inferior direito (X, Y):")
        x_end = get_valid_coord("X final (Coluna): ", num_cols)
        y_end = get_valid_coord("Y final (Linha): ", num_rows)
        
        # Garantir que start <= end
        x_start, x_end = min(x_start, x_end), max(x_start, x_end)
        y_start, y_end = min(y_start, y_end), max(y_start, y_end)
        
        # 2. Gerar visualização de foco
        visualize_batch_focus(mapa, x_start, y_start, x_end, y_end)
        
        # 3. Confirmação
        confirm = input("A região destacada está correta? (s/n): ").lower().strip()
        if confirm != 's':
            print("Região não confirmada. Tente novamente.")
            continue
            
        # 4. Obter nova classificação
        novo_terreno = get_valid_input(f"Novo Terreno ({'/'.join(TERRENOS_VALIDOS)}): ", TERRENOS_VALIDOS)
        novo_ambiente = get_valid_input(f"Novo Ambiente ({'/'.join(AMBIENTES_VALIDOS)}): ", AMBIENTES_VALIDOS)
        
        # 5. Aplicar e salvar
        cells_modified = 0
        for r in range(y_start, y_end + 1):
            for q in range(x_start, x_end + 1):
                cell = mapa[r][q]
                cell["terreno"] = novo_terreno
                cell["ambiente"] = novo_ambiente
                cell["descricao"] = f"Terreno: {novo_terreno.capitalize()}, Ambiente: {novo_ambiente.capitalize()} (Corrigido em Lote)"
                cells_modified += 1
                
        save_map(data)
        print(f"{cells_modified} células modificadas na região ({x_start},{y_start}) a ({x_end},{y_end}).")
        
        # Pergunta se quer continuar
        continuar = input("Pressione ENTER para editar outra região, ou 's' para sair: ").lower().strip()
        if continuar == 's':
            break

    print("\nEdição em massa concluída.")

if __name__ == "__main__":
    # Instalar matplotlib se não estiver instalado
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Instalando matplotlib...")
        os.system("pip3 install matplotlib")
        import matplotlib.pyplot as plt
        
    edit_map_batch()
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from map_visualizer_lib import visualize_map_final

# --- Configurações de Caminho ---
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# O JSON de entrada/saída é o resultado do gap-filling
JSON_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_final_200x86.json') 
# O script de edição em massa não precisa de um OUTPUT_IMAGE_PATH, pois usará o visualize_map_final
# OUTPUT_IMAGE_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_visualizado_batch.png')

TERRENOS_VALIDOS = ["agua", "gelo", "rochoso", "terra", "vazio"]
AMBIENTES_VALIDOS = ["oceano", "geleira", "montanha", "terreno_rochoso", "floresta", "vegetacao_escassa", "campo", "vazio"]

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
    """Gera a visualização final com a região de foco destacada e salva em mapa_visualizado_final.png."""
    
        # 1. Gerar a visualização final
    visualize_map_final(json_path=JSON_PATH, output_image_path="mapa_visualizado_final.png")
        
        # 2. Imprimir as coordenadas de foco
    print(f"\nVisualização final atualizada em mapa_visualizado_final.png")
    print(f"Região em foco: ({x_start},{y_start}) a ({x_end},{y_end})")
    print("Por favor, abra a imagem e use a imagem de referência numerada para confirmar a região.")

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
        
        # 6. Gerar visualização final após a edição
        visualize_map_final(json_path=JSON_PATH, output_image_path="mapa_visualizado_final.png")
        
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
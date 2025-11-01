
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Caminho para o arquivo JSON gerado
INPUT_JSON_PATH = "C:/Users/Sora/Documents/Programação/aplicativos-e-jogos/mundo_vivo/mapa_200x86.json"
OUTPUT_IMAGE_PATH = "C:/Users/Sora/Documents/Programação/aplicativos-e-jogos/mundo_vivo/mapa_visualizado.png"

def visualize_map(json_path, output_path):
    """
    Lê o arquivo JSON e gera uma visualização do mapa, colorindo as células
    de acordo com o tipo de terreno.
    """
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em {json_path}.")
        return
    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o arquivo JSON em {json_path}.")
        return

    map_matrix = data["mapa"]
    num_rows = data["metadata"]["linhas"]
    num_cols = data["metadata"]["colunas"]

    # 1. Mapeamento de Terreno para Cor
    # Definindo um mapeamento de cores para os tipos de terreno identificados
    color_map = {
        "agua": "#4682B4",          # Azul Aço (Oceano)
        "gelo": "#F0F8FF",          # Branco Azulado (Geleira)
        "rochoso": "#8B4513",       # Marrom Sela (Montanha/Rochoso)
        "terra": "#3CB371",         # Verde Médio Primavera (Terra)
        "vazio": "#FFFFFF",         # Branco (Fora do Mapa)
        "desconhecido": "#FF0000"   # Vermelho (Caso de segurança, não deve ocorrer)
    }
    
    # Criando uma matriz de cores para a visualização
    color_array = np.full((num_rows, num_cols), "#FFFFFF", dtype=object)

    # 2. Preenchendo a matriz de cores
    for r in range(num_rows):
        for c in range(num_cols):
            cell = map_matrix[r][c]
            if cell:
                terreno = cell.get("terreno", "desconhecido")
                color_array[r, c] = color_map.get(terreno, color_map["desconhecido"])
            else:
                # Célula nula (não deve acontecer com a grade 200x86)
                color_array[r, c] = color_map["vazio"]

    # 3. Visualização com Matplotlib
    
    # Criando um mapa de cores personalizado para Matplotlib
    unique_colors = list(color_map.values())
    cmap = ListedColormap(unique_colors)
    
    # Mapeando os tipos de terreno para índices numéricos para o imshow
    terreno_to_index = {terreno: i for i, terreno in enumerate(color_map.keys())}
    index_array = np.zeros((num_rows, num_cols), dtype=int)
    
    for r in range(num_rows):
        for c in range(num_cols):
            cell = map_matrix[r][c]
            if cell:
                terreno = cell.get("terreno", "desconhecido")
                index_array[r, c] = terreno_to_index.get(terreno, terreno_to_index["desconhecido"])
            else:
                index_array[r, c] = terreno_to_index["vazio"]

    # Invertendo o eixo Y para que a linha 0 (y=0) fique no topo
    plt.imshow(index_array, cmap=cmap, origin='upper')
    
    # Configurando a legenda
    patches = [plt.plot([],[], marker="s", ms=10, ls="", mec=None, color=color_map[terreno], 
                        label=terreno.capitalize())[0] for terreno in color_map.keys()]
    
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    # Configurações do gráfico
    plt.title("Visualização do Mapa por Tipo de Terreno (Grade 200x86)")
    plt.xlabel("Coluna (X)")
    plt.ylabel("Linha (Y)")
    plt.xticks(np.arange(0, num_cols, 20))
    plt.yticks(np.arange(0, num_rows, 10))
    plt.grid(True, which='both', color='gray', linestyle='-', linewidth=0.5)
    plt.tight_layout()

    # 4. Salvando a imagem
    plt.savefig(output_path)
    print(f"Visualização do mapa salva em {output_path}")

if __name__ == "__main__":
    visualize_map(INPUT_JSON_PATH, OUTPUT_IMAGE_PATH)
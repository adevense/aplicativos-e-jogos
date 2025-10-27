import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# ==============================================================================
# MÓDULO I: DOMÍNIO (CORE) - Lógica de Coordenadas e Células
# O Core não tem dependências de bibliotecas de visualização como Matplotlib.
# ==============================================================================

@dataclass(frozen=True)
class Hex:
    """
    Representa uma coordenada Hexagonal no sistema Cúbico (q, r, s).
    A soma das coordenadas deve ser sempre zero: q + r + s = 0. 
    """
    q: int
    r: int
    s: int = field(init=False)

    def __post_init__(self):
        # Garante a restrição cúbica [1]
        s_val = -(self.q + self.r)
        object.__setattr__(self, 's', s_val)

    def __add__(self, other: 'Hex') -> 'Hex':
        """Permite a adição de coordenadas Hex (vetores)."""
        return Hex(self.q + other.q, self.r + other.r)

    # Vetores de direção usados para encontrar vizinhos diretos [1, 2]
    DIRECTIONS: List['Hex'] = [
        Hex(1, 0), Hex(1, -1), Hex(0, -1),
        Hex(-1, 0), Hex(-1, 1), Hex(0, 1),
    ]

    def neighbors(self) -> List['Hex']:
        """
        Retorna as 6 coordenadas Hex vizinhas. (Implementação completa) [1]
        """
        # Adiciona o Hex de origem a cada um dos 6 vetores de direção
        return

    def distance(self, other: 'Hex') -> int:
        """
        Calcula a Distância Manhattan Hexagonal. [2]
        """
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs(self.s - other.s)) // 2
    
    def __hash__(self):
        """Torna a coordenada hashable para uso como chave de dicionário. [3]"""
        return hash((self.q, self.r))


@dataclass
class HexCell:
    """
    Representa o estado customizável de uma única célula hexagonal.
    Inclui propriedades de lógica (`cost`, `isBlocked`) e dados arbitrários. [2, 4]
    """
    coord: Hex
    # Propriedades de Lógica (para Pathfinding e BFS) [4]
    isBlocked: bool = False
    cost: float = 1.0  # Custo para atravessar (usado em A*)
    
    # Propriedades Customizáveis (dados de domínio: altitude, tipo, etc.) [4]
    attributes: Dict[str, Any] = field(default_factory=dict)

    @property
    def get_color(self) -> str:
        """Determina a cor de visualização com base nos atributos customizados."""
        if self.isBlocked:
            return '#333333'  # Bloqueado (Cinza escuro)
        
        cell_type = self.attributes.get('type', 'Default')
        if cell_type == 'Forest':
            return '#228B22'
        elif cell_type == 'Water':
            return '#00BFFF'
        elif cell_type == 'Mountain':
            return '#A9A9A9'
        elif cell_type == 'Castle':
             return '#FFD700'
        return '#ADFF2F' # Padrão (Grass)


# ==============================================================================
# MÓDULO II: INFRAESTRUTURA (ADAPTERS) - Armazenamento e Visualização
# ==============================================================================

class HexGrid:
    """
    Adaptador de Armazenamento. Gerencia a coleção de HexCells.
    """
    def __init__(self, radius: int):
        self.radius = radius
        # O mapa é um dicionário indexado pelas coordenadas Hex [3]
        self.map_data: Dict[Hex, HexCell] = {}
        self._generate_hex_ring_map()

    def _generate_hex_ring_map(self):
        """Gera um mapa em forma de diamante preenchido (círculo) de raio R."""
        for q in range(-self.radius, self.radius + 1):
            r1 = max(-self.radius, -q - self.radius)
            r2 = min(self.radius, -q + self.radius)
            for r in range(r1, r2 + 1):
                h = Hex(q, r)
                self.map_data[h] = HexCell(h)
    
    def get_cell(self, coord: Hex) -> Optional[HexCell]:
        """Retorna uma célula dado uma coordenada."""
        return self.map_data.get(coord)

    def set_terrain(self, coord: Hex, terrain_type: str, cost: float, isBlocked: bool = False):
        """Método de customização para definir propriedades da célula."""
        cell = self.get_cell(coord)
        if cell:
            cell.set_attribute('type', terrain_type)
            cell.cost = cost
            cell.isBlocked = isBlocked

# Adaptador de Visualização Matplotlib
class HexLayout:
    """
    Responsável pela conversão de coordenadas lógicas (Hex) para coordenadas de pixel (X, Y). 
    """
    def __init__(self, size: float, origin: Tuple[float, float] = (0.0, 0.0)):
        self.size = size  # Distância centro-vértice
        self.origin = origin
        # Matriz de orientação para "pointy-top" (ponta para cima) 
        self.M = (
            math.sqrt(3.0) * size, math.sqrt(3.0) / 2.0 * size,
            0.0 * size, 3.0 / 2.0 * size
        )

    def hex_to_pixel(self, h: Hex) -> Tuple[float, float]:
        """Converte coordenada Hex para coordenada de tela (Pixel)."""
        x = self.M * h.q + self.M[5] * h.r + self.origin
        y = self.M[6] * h.q + self.M[7] * h.r + self.origin[5]
        return (x, y)

    # CORREÇÃO CRÍTICA DE SINTAXE RESOLVIDA: Anotação de tipo correta para Lista de Tuplas
    def hex_corners(self, h: Hex) -> List]:
        """Calcula os 6 vértices do polígono do hexágono no espaço do pixel. """
        center_x, center_y = self.hex_to_pixel(h)
        corners: List] =
        
        # Ângulos para pointy-top: 30, 90, 150, 210, 270, 330 graus
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + self.size * math.cos(angle_rad)
            y = center_y + self.size * math.sin(angle_rad)
            corners.append((x, y))
        return corners

def draw_hex_map(grid: HexGrid, layout: HexLayout):
    """
    Função de visualização que desenha o mapa usando Matplotlib.
    """
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal', adjustable='box')

    for cell in grid.map_data.values():
        # 1. Obter os vértices do hexágono
        vertices = layout.hex_corners(cell.coord)

        # 2. Criar o patch do polígono com cor customizada [8, 9]
        color = cell.get_color
        
        hexagon = Polygon(
            vertices,
            closed=True,
            facecolor=color,
            edgecolor='black',
            linewidth=1.0,
            alpha=0.8
        )
        ax.add_patch(hexagon)

        # 3. Adicionar texto (Rótulos de Coordenadas e Tipo)
        center_x, center_y = layout.hex_to_pixel(cell.coord)
        label = f"({cell.coord.q}, {cell.coord.r})"
        
        if cell.attributes.get('type'):
             label += f"\n{cell.attributes['type']}"
        
        if cell.cost!= 1.0 and not cell.isBlocked:
             label += f" | C: {cell.cost:.1f}"

        # Lógica de cor do texto para legibilidade
        dark_colors = ('#333333', '#00BFFF', '#228B22') 
        text_color = 'white' if color in dark_colors or color == '#A9A9A9' else 'black'

        ax.text(
            center_x, center_y,
            label,
            ha='center', va='center',
            fontsize=8,
            color=text_color,
            zorder=10
        )

    # Configurações finais do gráfico
    ax.autoscale_view()
    ax.axis('off')
    plt.title(f"Mapa Hexagonal Customizável (Raio {grid.radius})")
    plt.show()

# ==============================================================================
# EXEMPLO DE USO: CRIAÇÃO E CUSTOMIZAÇÃO DO MAPA
# ==============================================================================

if __name__ == '__main__':
    # 1. Inicializa a Grade
    GRID_RADIUS = 5
    my_grid = HexGrid(radius=GRID_RADIUS)

    # 2. Customiza Células Específicas
    
    # Montanhas (Alto Custo de Movimento)
    my_grid.set_terrain(Hex(2, -2), 'Mountain', cost=5.0)
    my_grid.set_terrain(Hex(3, -2), 'Mountain', cost=5.0)
    my_grid.set_terrain(Hex(4, -4), 'Mountain', cost=5.0)

    # Água (Bloqueada/Intransitável)
    my_grid.set_terrain(Hex(-1, 0), 'Water', cost=1000.0, isBlocked=True)
    my_grid.set_terrain(Hex(-2, 1), 'Water', cost=1000.0, isBlocked=True)
    my_grid.set_terrain(Hex(-3, 2), 'Water', cost=1000.0, isBlocked=True)
    
    # Floresta (Custo Médio)
    my_grid.set_terrain(Hex(0, -3), 'Forest', cost=3.0)
    my_grid.set_terrain(Hex(1, -3), 'Forest', cost=3.0)
    my_grid.set_terrain(Hex(0, -2), 'Forest', cost=3.0)
    
    # Ponto de Interesse (Castle) - Customização de dados genéricos
    poi_coord = Hex(0, 0)
    my_grid.set_terrain(poi_coord, 'Castle', cost=1.0)
    poi_cell = my_grid.get_cell(poi_coord)
    if poi_cell:
        poi_cell.set_attribute('population', 500)
        poi_cell.set_attribute('owner', 'Player 1')
        

    # 3. Inicializa o Layout de Renderização
    HEX_SIZE = 1.0
    hex_layout = HexLayout(size=HEX_SIZE)

    # 4. Desenha o Mapa Customizado
    draw_hex_map(my_grid, hex_layout)
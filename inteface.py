import json
import os
import random
import math
import heapq
import sys

# Tenta importar bibliotecas externas visuais
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.layout import Layout
    from rich.progress import track
    from rich import print as rprint
except ImportError:
    print("❌ ERRO CRÍTICO: A biblioteca 'rich' não está instalada.")
    print("Para o novo visual funcionar, execute no terminal: pip install rich")
    sys.exit(1)

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
MAPA_CODIFICADO_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_codificado.json')
DADOS_ENTIDADES_PATH = os.path.join(CAMINHO_SCRIPT, 'dados_entidades.json')
OUTPUT_IMAGE_MUNDO = os.path.join(CAMINHO_SCRIPT, 'mapa_status_mundo.png')
OUTPUT_IMAGE_ROTA = os.path.join(CAMINHO_SCRIPT, 'mapa_rota.png')
OUTPUT_IMAGE_INSPECAO = os.path.join(CAMINHO_SCRIPT, 'inspecao_local.png')

WIDTH = 200
HEIGHT = 86
LARGURA_CELULA_KM = 200.0 
AREA_CELULA_KM2 = LARGURA_CELULA_KM * LARGURA_CELULA_KM 
MOVIMENTO_BASE_KM_DIA = 30.0 
PONTOS_DIARIOS_MAX = 50.0 

console = Console()

# --- CONFIGURAÇÕES DE MUNDO ---
DEFAULT_TRANSPORTS = {
    "a_pe": {"speed": 1.0, "restrict": ["oceano"], "cost_mod": 1.0},
    "cavalo": {"speed": 1.8, "restrict": ["oceano", "agua", "montanha", "rochoso"], "cost_mod": 1.0},
    "carroca": {"speed": 0.6, "restrict": ["oceano", "agua", "montanha", "floresta", "rochoso"], "cost_mod": 1.2},
    "barco_rio": {"speed": 1.2, "restrict": ["terra", "vegetacao", "gelo", "rochoso", "oceano"], "cost_mod": 0.5},
    "navio_oceano": {"speed": 1.5, "restrict": ["terra", "vegetacao", "gelo", "rochoso"], "cost_mod": 0.1},
    "voo": {"speed": 3.0, "restrict": [], "cost_mod": 0.1}
}

MOVEMENT_COSTS = {
    "agua": 3.0, "oceano": 10.0, "gelo": 2.5, "rochoso": 3.0,
    "terra": 1.0, "vegetacao": 1.5, "acampamento": 0.5, "vazio": 9999
}

TERRAIN_BEST_MODE = {
    "oceano": "navio_oceano", "agua": "barco_rio", "terra": "cavalo",
    "vegetacao": "a_pe", "rochoso": "a_pe", "gelo": "a_pe", "acampamento": "a_pe", "vazio": "a_pe"
}

# --- VISUALIZAÇÃO ---
COLOR_MAP_RGB = {
    "agua": (0.27, 0.44, 0.61), "gelo": (0.9, 0.9, 1.0), "rochoso": (0.4, 0.3, 0.2),
    "terra": (0.55, 0.7, 0.3), "vegetacao": (0.1, 0.4, 0.1), "vazio": (0.0, 0.0, 0.0),
    "acampamento": (0.8, 0.2, 0.2), "oceano": (0.0, 0.0, 0.4)
}
COLORS_LIST = list(COLOR_MAP_RGB.values())
LABELS_LIST = ["Rio/Lago", "Gelo", "Rochoso", "Terra", "Floresta", "Vazio", "Local", "Oceano"]
CMAP = ListedColormap(COLORS_LIST)
STR_TO_IDX = {"agua": 0, "gelo": 1, "rochoso": 2, "terra": 3, "gramado": 3, "vegetacao": 4, "floresta": 4, "vazio": 5, "acampamento": 6, "oceano": 7}
BASE_ENTITY_COLORS = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#33FFF6', '#FFC300', '#FFFFFF']

# ==============================================================================
# 2. SISTEMA DE DATA E TEMPO
# ==============================================================================

def get_date(ent_data):
    """Retorna Ano, Mês, Dia."""
    # Garante que a chave metadata existe para leitura
    meta = ent_data.get("metadata", {})
    total_days = meta.get("global_time_days", 0)
    
    year = 1 + (total_days // 360)
    month = 1 + ((total_days % 360) // 30)
    day = 1 + (total_days % 30)
    return year, month, day, total_days

def increment_time(ent_data, days):
    # Garante que a chave metadata existe para escrita
    if "metadata" not in ent_data: ent_data["metadata"] = {}
    
    current = ent_data["metadata"].get("global_time_days", 0)
    ent_data["metadata"]["global_time_days"] = current + days
    return get_date(ent_data)

def display_date_header(ent_data):
    y, m, d, t = get_date(ent_data)
    return f"[bold yellow]📅 Data Atual: Ano {y} | Mês {m} | Dia {d} (Total: {t} dias)[/]"

# ==============================================================================
# 3. UTILITÁRIOS DE DADOS
# ==============================================================================

def load_json(path):
    try:
        with open(path, "r", encoding='utf-8') as f: return json.load(f)
    except: return None

def save_json(data, path):
    try:
        with open(path, "w", encoding='utf-8') as f:
            indent = 4 if "entidades" in path else None
            sep = (',', ':') if "entidades" not in path else None
            json.dump(data, f, indent=indent, separators=sep, ensure_ascii=False)
    except Exception as e: console.print(f"[red]Erro ao salvar: {e}[/]")

def get_transport_config(ent_data, mode_name):
    custom = ent_data.get("config", {}).get("custom_transports", {})
    if mode_name in custom: return custom[mode_name]
    return DEFAULT_TRANSPORTS.get(mode_name, DEFAULT_TRANSPORTS["a_pe"])

def generate_unique_color(index=None):
    if index is not None and index < len(BASE_ENTITY_COLORS): return BASE_ENTITY_COLORS[index]
    return f'#{random.randint(50, 255):02x}{random.randint(50, 255):02x}{random.randint(50, 255):02x}'

# ==============================================================================
# 4. LÓGICA DO MUNDO (TERRENO E IA)
# ==============================================================================

def get_terrain_info(map_data, q, r):
    if not (0 <= q < WIDTH and 0 <= r < HEIGHT): return "vazio", "vazio", None
    t_str = map_data["metadata"]["terrenos_map"].get(str(map_data["terreno"][r][q]), "vazio")
    a_str = map_data["metadata"]["ambientes_map"].get(str(map_data["ambiente"][r][q]), "vazio")
    
    if t_str == "agua" and a_str == "oceano": t_str = "oceano"
    elif t_str == "gramado": t_str = "vegetacao" if a_str == "floresta" else "terra"
    
    l_val = None
    if "local_atual" in map_data:
        code = str(map_data["local_atual"][r][q])
        l_val = map_data["metadata"].get("local_atual_map", {}).get(code)
    return t_str, a_str, l_val

def get_visual_idx(t_str, l_val):
    if l_val and l_val not in ["None", "null", "0"]: return 6
    return STR_TO_IDX.get(t_str, 5)

def get_location_coords(map_data, loc_name):
    target = next((k for k, v in map_data["metadata"].get("local_atual_map", {}).items() if v == loc_name), None)
    if target:
        for r in range(HEIGHT):
            for q in range(WIDTH):
                if str(map_data["local_atual"][r][q]) == target: return q, r
    return None, None

def calculate_movement(entity, t_str, ent_data_root):
    modo = entity.get("modo_transporte", "a_pe")
    config = get_transport_config(ent_data_root, modo)
    if t_str in config.get("restrict", []): return 0
    
    custo_terreno = MOVEMENT_COSTS.get(t_str, 9999)
    custo_mod = config.get("cost_mod", 1.0)
    final_custo = custo_terreno * custo_mod
    if final_custo >= 9000: return 0

    vel_km = (MOVIMENTO_BASE_KM_DIA * config.get("speed", 1.0)) / final_custo
    return (vel_km / LARGURA_CELULA_KM) * PONTOS_DIARIOS_MAX

def heuristic(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_path_astar(start, goal, map_data, entity, ent_data_root, limit=1500):
    start_node, goal_node = (start[0], start[1]), (goal[0], goal[1])
    frontier = []; heapq.heappush(frontier, (0, start_node))
    came_from = {start_node: None}; cost_so_far = {start_node: 0}
    
    visited = 0
    while frontier:
        visited += 1
        if visited > limit: break
        _, current = heapq.heappop(frontier)
        if current == goal_node: break

        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nq, nr = current[0]+dx, current[1]+dy
            if not (0 <= nq < WIDTH and 0 <= nr < HEIGHT): continue
            t_next, _, _ = get_terrain_info(map_data, nq, nr)
            pts = calculate_movement(entity, t_next, ent_data_root)
            if pts <= 0.01: continue
            
            new_cost = cost_so_far[current] + (1.0 / (pts + 0.001))
            next_node = (nq, nr)
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                heapq.heappush(frontier, (new_cost + heuristic(goal_node, next_node), next_node))
                came_from[next_node] = current

    if goal_node not in came_from: return None
    path = []
    curr = goal_node
    while curr != start_node:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path

def decide_ia_goal(ent, map_data, ent_data_root):
    if ent.get("home_location") and ent.get("return_freq_days"):
        if ent.get("days_since_home", 0) >= ent["return_freq_days"]:
            hq, hr = get_location_coords(map_data, ent["home_location"])
            if hq is not None:
                return (hq, hr) if (ent["q"] != hq or ent["r"] != hr) else generate_random_goal(ent, map_data, ent_data_root)
    if ent.get("meta_q") is None or (ent["q"] == ent["meta_q"] and ent["r"] == ent["meta_r"]):
        return generate_random_goal(ent, map_data, ent_data_root)
    return ent["meta_q"], ent["meta_r"]

def generate_random_goal(ent, map_data, ent_data_root):
    for _ in range(10): 
        rq, rr = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        t, _, _ = get_terrain_info(map_data, rq, rr)
        if calculate_movement(ent, t, ent_data_root) > 0: return rq, rr
    return ent["q"], ent["r"]

def process_tick(map_data, ent_data, days=1):
    with console.status(f"[bold green]Simulando {days} dias...[/]"):
        for _ in range(days):
            increment_time(ent_data, 1)
            for k in ["npcs", "grupos", "players"]:
                for ent in ent_data.get(k, []):
                    if ent.get("status") == "parado": continue
                    ent["days_since_home"] = ent.get("days_since_home", 0) + 1
                    
                    if ent["tipo"] != "player":
                        nq, nr = decide_ia_goal(ent, map_data, ent_data)
                        ent["meta_q"], ent["meta_r"] = nq, nr
                    
                    if not ent.get("meta_q"): continue
                    
                    path = find_path_astar((ent["q"], ent["r"]), (ent["meta_q"], ent["meta_r"]), map_data, ent, ent_data)
                    if not path:
                        ent["meta_q"] = None; continue

                    next_q, next_r = path[0]
                    t_here, _, _ = get_terrain_info(map_data, ent["q"], ent["r"])
                    pts = calculate_movement(ent, t_here, ent_data)
                    ent["progresso_diario"] = ent.get("progresso_diario", 0) + pts
                    
                    if ent["progresso_diario"] >= PONTOS_DIARIOS_MAX:
                        ent["q"], ent["r"] = next_q, next_r
                        ent["progresso_diario"] -= PONTOS_DIARIOS_MAX

    save_json(ent_data, DADOS_ENTIDADES_PATH)
    console.print(f"[bold green]✅ Simulação concluída.[/] {display_date_header(ent_data)}")
    generate_world_image(map_data, ent_data)

# ==============================================================================
# 5. GERAÇÃO DE IMAGENS (MAIOR RESOLUÇÃO)
# ==============================================================================

def generate_world_image(map_data, ent_data, focus_coords=None, is_route=False, path_points=None):
    """Gera imagem do mundo, foco ou rota. Resolução aumentada para ~2K."""
    mat = np.zeros((HEIGHT, WIDTH), dtype=int)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t, _, l = get_terrain_info(map_data, x, y)
            mat[y, x] = get_visual_idx(t, l)

    # AJUSTE DE RESOLUÇÃO PARA ~2K: figsize e dpi aumentados
    fig = plt.figure(figsize=(20, 15)) # 20 polegadas de largura
    gs = gridspec.GridSpec(2, 2, height_ratios=[6, 1], width_ratios=[6, 1])
    ax_map = fig.add_subplot(gs[0, 0])
    
    ax_map.imshow(mat, cmap=CMAP, interpolation='nearest', vmin=0, vmax=7)
    ax_map.axis('off')

    save_path = OUTPUT_IMAGE_MUNDO
    if focus_coords:
        qx, ry = focus_coords
        ax_map.set_xlim(max(0, qx - 20), min(WIDTH, qx + 20))
        ax_map.set_ylim(min(HEIGHT, ry + 20), max(0, ry - 20))
        ax_map.set_title(f"Foco em ({qx}, {ry})", color='red', fontweight='bold')
        save_path = OUTPUT_IMAGE_INSPECAO
    elif is_route:
        save_path = OUTPUT_IMAGE_ROTA
        ax_map.set_title("Visualização de Rota", color='blue', fontweight='bold')

    legend_elements = {}
    for k in ["players", "grupos", "npcs"]:
        for ent in ent_data.get(k, []):
            cor = ent.get("cor_hex", "#FFFFFF")
            mk = 'o' if k=="grupos" else '*' if k=="npcs" else 'D'
            ax_map.scatter(ent['q'], ent['r'], c=cor, marker=mk, s=80, edgecolors='black', zorder=10)
            ax_map.text(ent['q'], ent['r']+1.5, ent['nome'][:8], color='white', fontsize=6, ha='center', 
                        bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.5))
            if ent['nome'] not in legend_elements: legend_elements[ent['nome']] = (cor, mk)

    if is_route and path_points:
        xs, ys = zip(*path_points)
        ax_map.plot(xs, ys, color='red', linewidth=3, alpha=0.8, zorder=5)

    ax_ter = fig.add_subplot(gs[0, 1]); ax_ter.axis('off')
    tp = [Patch(facecolor=c, edgecolor='black', label=l) for l, c in zip(LABELS_LIST, COLORS_LIST)]
    ax_ter.legend(handles=tp, loc='center left', title="Terrenos")

    plt.tight_layout()
    plt.savefig(save_path, dpi=120) # 120 DPI * 20 polegadas = 2400 pixels de largura
    plt.close(fig)
    if not focus_coords and not is_route:
        console.print(f"[dim]Imagem geral atualizada: {os.path.basename(save_path)}[/]")

# ==============================================================================
# 6. MENUS RICOS (INTERFACE)
# ==============================================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def select_entity_rich(ent_data):
    table = Table(title="Selecione uma Entidade")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Tipo", style="magenta")
    table.add_column("Local", style="green")

    all_ents = []
    count = 1
    for k in ["players", "grupos", "npcs"]:
        for e in ent_data.get(k, []):
            all_ents.append(e)
            table.add_row(str(count), e['nome'], k[:-1].upper(), f"({e['q']},{e['r']})")
            count += 1
    
    console.print(table)
    if not all_ents: return None
    
    choice = IntPrompt.ask("Digite o ID", choices=[str(i) for i in range(1, count)])
    return all_ents[choice-1]

def create_entity_detailed(ent_data, map_data):
    console.print(Panel("[bold green]CRIADOR DE ENTIDADE UNITÁRIO[/]", border_style="green"))
    
    tipo_choices = {"1": "npcs", "2": "grupos", "3": "players"}
    console.print("1. NPC | 2. Grupo | 3. Player")
    tipo_key = tipo_choices[Prompt.ask("Escolha o Tipo", choices=["1","2","3"])]
    
    nome = Prompt.ask("Nome da Entidade")
    desc = Prompt.ask("Descrição (opcional)", default="Sem descrição")
    hp = IntPrompt.ask("Vida (HP)", default=100)
    lvl = IntPrompt.ask("Nível", default=1)
    transp = Prompt.ask("Modo de Transporte Padrão", choices=list(DEFAULT_TRANSPORTS.keys()), default="a_pe")
    tem_navio = Confirm.ask("Possui Navio Oceânico?")
    tem_cavalo = Confirm.ask("Possui Cavalo?")
    
    console.print("[bold]Defina a Localização Inicial:[/]")
    if Confirm.ask("Usar posição aleatória?"):
        q, r = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
    else:
        q = IntPrompt.ask("Largura (X)", show_default=False)
        r = IntPrompt.ask("Altura (Y)", show_default=False)
        q = max(0, min(WIDTH-1, q))
        r = max(0, min(HEIGHT-1, r))

    if tipo_key not in ent_data: ent_data[tipo_key] = []
    
    new_ent = {
        "nome": nome, "descricao": desc, "tipo": tipo_key[:-1],
        "q": q, "r": r, "status": "ativo",
        "hp": hp, "nivel": lvl,
        "modo_transporte": transp,
        "tem_navio": tem_navio, "tem_cavalo": tem_cavalo, "tem_barco_rio": False,
        "cor_hex": generate_unique_color(len(ent_data[tipo_key])),
        "progresso_diario": 0, "meta_q": None, "meta_r": None
    }
    
    ent_data[tipo_key].append(new_ent)
    save_json(ent_data, DADOS_ENTIDADES_PATH)
    console.print(f"[bold green]✅ {nome} criado com sucesso em ({q},{r})![/]")

def inspector_menu(map_data, ent_data):
    clear_screen()
    console.print(Panel("[bold blue]INSPETOR DE COORDENADAS[/]", border_style="blue"))
    q = IntPrompt.ask("Largura (X)", default=WIDTH//2)
    r = IntPrompt.ask("Altura (Y)", default=HEIGHT//2)
    
    if not (0 <= q < WIDTH and 0 <= r < HEIGHT):
        console.print("[red]Coordenada fora do mapa![/]")
        return

    t, a, l = get_terrain_info(map_data, q, r)
    generate_world_image(map_data, ent_data, focus_coords=(q, r))
    
    grid = Table.grid(expand=True)
    grid.add_column(); grid.add_column(justify="right")
    grid.add_row(f"[bold]📍 Coordenada:[/]", f"({q}, {r})")
    grid.add_row(f"[bold]🏔️ Terreno:[/]", t.upper())
    grid.add_row(f"[bold]🌲 Ambiente:[/]", a.upper())
    grid.add_row(f"[bold]🏰 Local:[/]", l if l else "Ermo")
    
    occupants = []
    for k in ["players", "grupos", "npcs"]:
        for e in ent_data.get(k, []):
            if e['q'] == q and e['r'] == r: occupants.append(f"{e['nome']} ({k[:-1]})")
    grid.add_row(f"[bold]👥 Ocupantes:[/]", ", ".join(occupants) if occupants else "Ninguém")
    
    console.print(Panel(grid, title="Relatório de Inspeção"))
    console.print(f"[dim]Imagem de detalhe salva em: {os.path.basename(OUTPUT_IMAGE_INSPECAO)}[/]")
    Prompt.ask("Pressione Enter para voltar")

def reports_menu(map_data, ent_data):
    while True:
        clear_screen()
        console.print(Panel("[bold magenta]RELATÓRIOS E ESTATÍSTICAS[/]", border_style="magenta"))
        console.print("1. Custo de Movimento por Terreno")
        console.print("2. Censo Demográfico (População)")
        console.print("3. Relatório de Velocidades")
        console.print("0. Voltar")
        
        op = Prompt.ask("Escolha", choices=["1", "2", "3", "0"])
        
        if op == '1':
            table = Table(title="Custos de Movimento")
            table.add_column("Terreno", style="cyan")
            table.add_column("Custo Base", style="red")
            for k, v in MOVEMENT_COSTS.items(): table.add_row(k.upper(), str(v))
            console.print(table); Prompt.ask("Enter...")
        elif op == '2':
            table = Table(title="Censo Demográfico")
            table.add_column("Tipo", style="yellow")
            table.add_column("Quantidade", style="green")
            total = 0
            for k in ["players", "grupos", "npcs"]:
                qtd = len(ent_data.get(k, []))
                total += qtd
                table.add_row(k.upper(), str(qtd))
            table.add_row("[bold]TOTAL[/]", str(total))
            console.print(table); Prompt.ask("Enter...")
        elif op == '3':
            table = Table(title="Relatório de Logística")
            table.add_column("Entidade")
            table.add_column("Modo Atual")
            table.add_column("Equipamento")
            all_ents = [e for k in ["players", "grupos", "npcs"] for e in ent_data.get(k, [])]
            for e in all_ents:
                equip = []
                if e.get('tem_cavalo'): equip.append("Cavalo")
                if e.get('tem_navio'): equip.append("Navio")
                table.add_row(e['nome'], e.get('modo_transporte', 'a_pe'), ", ".join(equip) or "-")
            console.print(table); Prompt.ask("Enter...")
        elif op == '0': break

def time_manager_menu(ent_data):
    while True:
        clear_screen()
        console.print(Panel(display_date_header(ent_data), title="GERENCIADOR DE DATA", border_style="yellow"))
        console.print("1. Avançar 1 Dia")
        console.print("2. Avançar 1 Semana (7 dias)")
        console.print("3. Avançar 1 Mês (30 dias)")
        console.print("4. Ajustar Data Manualmente")
        console.print("0. Voltar")
        
        op = Prompt.ask("Opção", choices=["1","2","3","4","0"])
        
        if op == '1': return 1
        if op == '2': return 7
        if op == '3': return 30
        if op == '4':
            # CORREÇÃO DE SEGURANÇA: GARANTE QUE A CHAVE METADATA EXISTA
            if "metadata" not in ent_data: ent_data["metadata"] = {}
            
            new_days = IntPrompt.ask("Digite o total de dias absolutos")
            ent_data["metadata"]["global_time_days"] = new_days
            save_json(ent_data, DADOS_ENTIDADES_PATH)
            console.print("[green]Data ajustada![/]")
        if op == '0': return 0

def main_menu(map_data, ent_data):
    while True:
        clear_screen()
        console.print(Panel(f"[bold]MUNDO VIVO 6.2[/]\n{display_date_header(ent_data)}", style="on blue"))
        console.print("[1] ⏳ Simulação e Tempo")
        console.print("[2] 🛠️  Gestão de Entidades (Criar/Editar)")
        console.print("[3] 🔍 Inspetor e Relatórios")
        console.print("[4] 🗺️  Visualização (Rotas/Mapas)")
        console.print("[0] Sair")
        
        op = Prompt.ask(">>", choices=["1", "2", "3", "4", "0"])
        
        if op == '1': 
            days = time_manager_menu(ent_data)
            if days > 0: process_tick(map_data, ent_data, days)
            
        elif op == '2': 
            while True:
                clear_screen()
                console.print(Panel("GESTÃO DE ENTIDADES", style="green"))
                console.print("1. Criar Nova Entidade (Detalhado)")
                console.print("2. Criar Local no Mapa")
                console.print("3. Editar/Mover Entidade Existente")
                console.print("0. Voltar")
                sub = Prompt.ask("Opção", choices=["1","2","3","0"])
                if sub == '1': create_entity_detailed(ent_data, map_data)
                elif sub == '2': 
                    try:
                        nm = Prompt.ask("Nome do Local")
                        q, r = IntPrompt.ask("X"), IntPrompt.ask("Y")
                        q = max(0, min(WIDTH-1, q))
                        r = max(0, min(HEIGHT-1, r))
                        code = str(random.randint(10000,99999))
                        map_data["metadata"]["local_atual_map"][code] = nm
                        map_data["local_atual"][r][q] = int(code)
                        with open(MAPA_CODIFICADO_PATH, 'w') as f: json.dump(map_data, f, separators=(',',':'))
                        console.print("[green]Local Salvo![/]")
                    # CORREÇÃO DE SINTAXE: Adicionado ':'
                    except Exception as e: 
                        console.print(f"[red]Erro: {e}[/]")
                elif sub == '3':
                    ent = select_entity_rich(ent_data)
                    if ent:
                        ent['q'] = IntPrompt.ask("Novo X", default=ent['q'])
                        ent['r'] = IntPrompt.ask("Novo Y", default=ent['r'])
                        save_json(ent_data, DADOS_ENTIDADES_PATH)
                elif sub == '0': break

        elif op == '3': 
            while True:
                clear_screen()
                console.print(Panel("INSPETOR & RELATÓRIOS", style="magenta"))
                console.print("1. Inspetor de Coordenada (Gera Imagem)")
                console.print("2. Relatórios Comparativos")
                console.print("0. Voltar")
                sub = Prompt.ask("Opção", choices=["1", "2", "0"])
                if sub == '1': inspector_menu(map_data, ent_data)
                elif sub == '2': reports_menu(map_data, ent_data)
                elif sub == '0': break

        elif op == '4': 
            while True:
                clear_screen()
                console.print(Panel("VISUALIZAÇÃO", style="cyan"))
                console.print("1. Gerar Mapa Completo")
                console.print("2. Visualizar Rota de Entidade")
                console.print("0. Voltar")
                sub = Prompt.ask("Opção", choices=["1", "2", "0"])
                if sub == '1': generate_world_image(map_data, ent_data)
                elif sub == '2':
                    ent = select_entity_rich(ent_data)
                    if ent and ent.get("meta_q"):
                        path = find_path_astar((ent['q'],ent['r']), (ent['meta_q'],ent['meta_r']), map_data, ent, ent_data)
                        if path: 
                            console.print(f"[green]Rota encontrada com {len(path)} passos. Gerando imagem...[/]")
                            generate_world_image(map_data, ent_data, is_route=True, path_points=path)
                            console.print(f"Salvo em: {OUTPUT_IMAGE_ROTA}")
                        else: console.print("[red]Rota impossível[/]")
                    else: console.print("[yellow]Entidade sem meta ou inválida[/]")
                    Prompt.ask("Enter...")
                elif sub == '0': break

        elif op == '0': break

def main():
    os.system("color")
    map_data = load_json(MAPA_CODIFICADO_PATH)
    ent_data = load_json(DADOS_ENTIDADES_PATH)
    
    if not map_data or not ent_data:
        console.print("[bold red]❌ Arquivos JSON faltando![/]")
        return

    # Inicialização Segura e Correção de Chaves Faltantes
    if "config" not in ent_data: ent_data["config"] = {}
    if "metadata" not in ent_data: ent_data["metadata"] = {"global_time_days": 0} # Inicia metadata se faltar
    
    idx = 0
    for k in ["npcs", "grupos", "players"]:
        if k not in ent_data: ent_data[k] = []
        for e in ent_data[k]:
            if "cor_hex" not in e: e["cor_hex"] = generate_unique_color(idx); idx+=1
            if "nome" not in e: e["nome"] = f"Entidade_{idx}"

    main_menu(map_data, ent_data)

if __name__ == "__main__":
    main()
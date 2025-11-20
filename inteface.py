import json
import os
import random
import math
import heapq
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

# ==============================================================================
# 1. CONFIGURAÇÕES GERAIS E CONSTANTES
# ==============================================================================
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
MAPA_CODIFICADO_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_codificado.json')
DADOS_ENTIDADES_PATH = os.path.join(CAMINHO_SCRIPT, 'dados_entidades.json')
OUTPUT_IMAGE_MUNDO = os.path.join(CAMINHO_SCRIPT, 'mapa_status_mundo.png')

WIDTH = 200
HEIGHT = 86

# --- ESCALA E FÍSICA ---
LARGURA_CELULA_KM = 200.0 
AREA_CELULA_KM2 = LARGURA_CELULA_KM * LARGURA_CELULA_KM # 40.000 km²
MOVIMENTO_BASE_KM_DIA = 30.0 
PONTOS_DIARIOS_MAX = 50.0 

# --- CORES CONSOLE (ANSI) ---
C = {
    "R": "\033[0m", "G": "\033[92m", "Y": "\033[93m", "B": "\033[94m", 
    "C": "\033[96m", "M": "\033[95m", "HEAD": "\033[44m\033[97m", "ERR": "\033[41m\033[97m"
}

# --- TRANSPORTES PADRÃO ---
DEFAULT_TRANSPORTS = {
    "a_pe": {"speed": 1.0, "restrict": ["oceano"], "cost_mod": 1.0},
    "cavalo": {"speed": 1.8, "restrict": ["oceano", "agua", "montanha", "rochoso"], "cost_mod": 1.0},
    "carroca": {"speed": 0.6, "restrict": ["oceano", "agua", "montanha", "floresta", "rochoso"], "cost_mod": 1.2},
    "barco_rio": {"speed": 1.2, "restrict": ["terra", "vegetacao", "gelo", "rochoso", "oceano"], "cost_mod": 0.5},
    "navio_oceano": {"speed": 1.5, "restrict": ["terra", "vegetacao", "gelo", "rochoso"], "cost_mod": 0.1},
    "voo": {"speed": 3.0, "restrict": [], "cost_mod": 0.1}
}

# --- CUSTOS DE TERRENO (Alto = Lento) ---
MOVEMENT_COSTS = {
    "agua": 3.0, "oceano": 10.0, "gelo": 2.5, "rochoso": 3.0,
    "terra": 1.0, "vegetacao": 1.5, "acampamento": 0.5, "vazio": 9999
}

# --- VISUALIZAÇÃO (CORES DO MAPA) ---
COLOR_MAP_RGB = {
    "agua": (0.27, 0.44, 0.61),      # 0: Azul Claro (Rios)
    "gelo": (0.9, 0.9, 1.0),         # 1: Branco
    "rochoso": (0.4, 0.3, 0.2),      # 2: Marrom Rochoso
    "terra": (0.55, 0.7, 0.3),       # 3: Verde Oliva (Campo)
    "vegetacao": (0.1, 0.4, 0.1),    # 4: Verde Floresta Escuro
    "vazio": (0.0, 0.0, 0.0),        # 5: Preto
    "acampamento": (0.8, 0.2, 0.2),  # 6: Vermelho
    "oceano": (0.0, 0.0, 0.4)        # 7: Azul Profundo
}
COLORS_LIST = list(COLOR_MAP_RGB.values())
LABELS_LIST = ["Rio/Lago", "Gelo", "Rochoso", "Terra/Campo", "Floresta", "Vazio", "Local/Acamp", "Oceano"]
CMAP = ListedColormap(COLORS_LIST)

# Mapeamento de String -> Índice
STR_TO_IDX = {
    "agua": 0, "gelo": 1, "rochoso": 2, "terra": 3, "gramado": 3, 
    "vegetacao": 4, "floresta": 4, "vazio": 5, "acampamento": 6, "oceano": 7
}

BASE_ENTITY_COLORS = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#33FFF6', '#FFC300', '#FFFFFF']

# ==============================================================================
# 2. GERENCIAMENTO DE DADOS E UTILITÁRIOS
# ==============================================================================

def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

def print_box(title, options=[]):
    width = 60
    print(f"\n{C['HEAD']}{title.center(width)}{C['R']}")
    print("╔" + "═"*(width-2) + "╗")
    for opt in options:
        print(f"║ {opt.ljust(width-4)} ║")
    print("╚" + "═"*(width-2) + "╝")

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
    except Exception as e: print(f"Erro Salvar: {e}")

def get_transport_config(ent_data, mode_name):
    """Retorna a config do transporte (padrão ou customizado)."""
    custom = ent_data.get("config", {}).get("custom_transports", {})
    if mode_name in custom: return custom[mode_name]
    return DEFAULT_TRANSPORTS.get(mode_name, DEFAULT_TRANSPORTS["a_pe"])

def generate_unique_color(index=None):
    if index is not None and index < len(BASE_ENTITY_COLORS): return BASE_ENTITY_COLORS[index]
    return f'#{random.randint(50, 255):02x}{random.randint(50, 255):02x}{random.randint(50, 255):02x}'

# ==============================================================================
# 3. LÓGICA DE MAPA E TERRENO
# ==============================================================================

def get_terrain_info(map_data, q, r):
    """Decodifica a célula (q,r) para strings legíveis."""
    if not (0 <= q < WIDTH and 0 <= r < HEIGHT): return "vazio", "vazio", None
    
    t_code = str(map_data["terreno"][r][q])
    a_code = str(map_data["ambiente"][r][q])
    
    t_str = map_data["metadata"]["terrenos_map"].get(t_code, "vazio")
    a_str = map_data["metadata"]["ambientes_map"].get(a_code, "vazio")
    
    # Normalização Essencial
    if t_str == "agua" and a_str == "oceano": t_str = "oceano"
    elif t_str == "gramado": t_str = "vegetacao" if a_str == "floresta" else "terra"
    
    l_val = None
    if "local_atual" in map_data:
        code = str(map_data["local_atual"][r][q])
        l_val = map_data["metadata"].get("local_atual_map", {}).get(code)
        
    return t_str, a_str, l_val

def get_visual_idx(t_str, l_val):
    """Converte string de terreno para índice de cor."""
    if l_val and l_val not in ["None", "null", "0"]: return 6 # Acampamento
    return STR_TO_IDX.get(t_str, 5) # Default Vazio

def get_location_coords(map_data, loc_name):
    """Acha coordenadas de um local pelo nome."""
    target = next((k for k, v in map_data["metadata"].get("local_atual_map", {}).items() if v == loc_name), None)
    if target:
        for r in range(HEIGHT):
            for q in range(WIDTH):
                if str(map_data["local_atual"][r][q]) == target: return q, r
    return None, None

# ==============================================================================
# 4. IA, PATHFINDING E MOVIMENTO
# ==============================================================================

def calculate_movement(entity, t_str, ent_data_root):
    """Calcula pontos de movimento para o terreno usando o transporte atual."""
    modo = entity.get("modo_transporte", "a_pe")
    config = get_transport_config(ent_data_root, modo)
    
    # Verifica restrições (Terrenos Proibidos)
    if t_str in config.get("restrict", []): return 0
    
    # Cálculo
    custo_base = MOVEMENT_COSTS.get(t_str, 9999)
    mod_custo = config.get("cost_mod", 1.0)
    speed_mult = config.get("speed", 1.0)
    
    custo_final = custo_base * mod_custo
    if custo_final >= 9000: return 0 # Bloqueio total

    vel_km_dia = (MOVIMENTO_BASE_KM_DIA * speed_mult) / custo_final
    # Conversão para "Pontos de Progresso"
    return (vel_km_dia / LARGURA_CELULA_KM) * PONTOS_DIARIOS_MAX

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_path_astar(start, goal, map_data, entity, ent_data_root, limit=1000):
    """Pathfinding A* que considera o transporte da entidade."""
    start_node, goal_node = (start[0], start[1]), (goal[0], goal[1])
    frontier = []; heapq.heappush(frontier, (0, start_node))
    came_from = {start_node: None}; cost_so_far = {start_node: 0}
    
    visited = 0
    while frontier:
        visited += 1
        if visited > limit: break # Evita travamento infinito
        
        _, current = heapq.heappop(frontier)
        if current == goal_node: break

        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nq, nr = current[0]+dx, current[1]+dy
            if not (0 <= nq < WIDTH and 0 <= nr < HEIGHT): continue
            
            t_next, _, _ = get_terrain_info(map_data, nq, nr)
            pts = calculate_movement(entity, t_next, ent_data_root)
            
            if pts <= 0.01: continue # Intransponível com transporte atual
            
            # Custo para o A* (inverso da velocidade)
            move_cost = 1.0 / (pts + 0.01)
            new_cost = cost_so_far[current] + move_cost
            
            next_node = (nq, nr)
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                prio = new_cost + heuristic(goal_node, next_node)
                heapq.heappush(frontier, (prio, next_node))
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
    """IA Central: Decide meta baseada em Casa, Tempo e Recursos."""
    
    # 1. Lógica de Casa (Home Binding)
    if ent.get("home_location") and ent.get("return_freq_days"):
        if ent.get("days_since_home", 0) >= ent["return_freq_days"]:
            hq, hr = get_location_coords(map_data, ent["home_location"])
            if hq is not None:
                if ent["q"] == hq and ent["r"] == hr:
                    ent["days_since_home"] = 0 # Já está em casa, reseta
                else:
                    return hq, hr # Vai pra casa

    # 2. Se não tem meta, ou chegou na meta
    if ent.get("meta_q") is None or (ent["q"] == ent["meta_q"] and ent["r"] == ent["meta_r"]):
        return generate_random_goal(ent, map_data, ent_data_root)
    
    return ent["meta_q"], ent["meta_r"]

def generate_random_goal(ent, map_data, ent_data_root):
    """Gera uma meta aleatória que seja possível alcançar (tentativa)."""
    for _ in range(10): 
        rq, rr = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        t, _, _ = get_terrain_info(map_data, rq, rr)
        if calculate_movement(ent, t, ent_data_root) > 0: return rq, rr
    return ent["q"], ent["r"]

def process_tick(map_data, ent_data, days=1):
    print(f"\n{C['Y']}⏳ Processando {days} dias...{C['R']}")
    
    for _ in range(days):
        for k in ["npcs", "grupos", "players"]:
            for ent in ent_data.get(k, []):
                if ent.get("status") == "parado": continue
                
                ent["days_since_home"] = ent.get("days_since_home", 0) + 1

                # IA decide meta (apenas NPCs/Grupos)
                if ent["tipo"] != "player":
                    nq, nr = decide_ia_goal(ent, map_data, ent_data)
                    ent["meta_q"], ent["meta_r"] = nq, nr
                
                if not ent.get("meta_q"): continue

                # Pathfinding
                path = find_path_astar((ent["q"], ent["r"]), (ent["meta_q"], ent["meta_r"]), map_data, ent, ent_data)
                
                if not path:
                    # Bloqueado! Se tiver casa, tenta voltar pra lá pra "pegar barco"
                    if ent.get("home_location"):
                        hq, hr = get_location_coords(map_data, ent["home_location"])
                        if hq and (hq != ent["q"] or hr != ent["r"]):
                             ent["meta_q"], ent["meta_r"] = hq, hr
                             continue
                    ent["meta_q"] = None # Desiste e fica parado
                    continue

                # Movimento
                next_q, next_r = path[0]
                t_here, _, _ = get_terrain_info(map_data, ent["q"], ent["r"])
                
                points = calculate_movement(ent, t_here, ent_data)
                ent["progresso_diario"] = ent.get("progresso_diario", 0) + points
                
                if ent["progresso_diario"] >= PONTOS_DIARIOS_MAX:
                    ent["q"], ent["r"] = next_q, next_r
                    ent["progresso_diario"] -= PONTOS_DIARIOS_MAX

    save_json(ent_data, DADOS_ENTIDADES_PATH)
    print(f"{C['G']}✅ Simulação concluída.{C['R']}")
    generate_world_image(map_data, ent_data)

# ==============================================================================
# 5. VISUALIZAÇÃO GRÁFICA (MATPLOTLIB AVANÇADO)
# ==============================================================================

def generate_world_image(map_data, ent_data):
    print("🎨 Gerando imagem do mundo...")
    
    # 1. Matriz de Cores
    mat = np.zeros((HEIGHT, WIDTH), dtype=int)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t, _, l = get_terrain_info(map_data, x, y)
            mat[y, x] = get_visual_idx(t, l)

    # 2. Configuração do Grid (Mapa + Legendas)
    fig = plt.figure(figsize=(14, 12))
    gs = gridspec.GridSpec(2, 2, height_ratios=[5, 1], width_ratios=[6, 1])
    
    # Mapa Principal
    ax_map = fig.add_subplot(gs[0, 0])
    ax_map.imshow(mat, cmap=CMAP, interpolation='nearest', vmin=0, vmax=len(COLORS_LIST)-1)
    ax_map.set_title("Mundo Vivo - Status Atual", fontsize=14, fontweight='bold', color='#333333')
    ax_map.axis('off')
    
    # Indicador de Escala (Texto no canto)
    scale_text = f"ESCALA: 1px = {AREA_CELULA_KM2:,.0f} km²".replace(",", ".")
    ax_map.text(3, HEIGHT-3, scale_text, color='white', fontsize=9, fontweight='bold', 
                bbox=dict(facecolor='black', alpha=0.7, edgecolor='none'))

    # Plota Entidades
    legend_elements = {}
    for k in ["players", "grupos", "npcs"]:
        for e in ent_data.get(k, []):
            cor = e.get("cor_hex", "#FFFFFF")
            mk = 'o' if k=="grupos" else '*' if k=="npcs" else 'D'
            sz = 100 if k=="npcs" else 60
            ax_map.scatter(e['q'], e['r'], c=cor, marker=mk, s=sz, edgecolors='black', linewidth=0.5, zorder=10)
            
            lbl = f"{e['nome']} ({e.get('modo_transporte','?')})"
            if lbl not in legend_elements:
                legend_elements[lbl] = (cor, mk)

    # Legenda de Terreno (Direita)
    ax_ter = fig.add_subplot(gs[0, 1])
    ax_ter.axis('off')
    patches = [Patch(facecolor=c, edgecolor='black', label=l) for l, c in zip(LABELS_LIST, COLORS_LIST)]
    ax_ter.legend(handles=patches, loc='center', title="Terrenos", fontsize='small', frameon=False)

    # Legenda de Entidades (Abaixo)
    ax_ent = fig.add_subplot(gs[1, :])
    ax_ent.axis('off')
    
    handles = [plt.Line2D([0], [0], marker=m, color='w', markerfacecolor=c, markersize=10, label=l) 
               for l, (c, m) in legend_elements.items()]
    
    if handles:
        ax_ent.legend(handles=handles, loc='center', ncol=4, title="Entidades no Mapa", frameon=False)
    else:
        ax_ent.text(0.5, 0.5, "Sem entidades visíveis.", ha='center')

    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE_MUNDO, dpi=150)
    plt.close(fig)
    print(f"🖼️  Imagem salva: {os.path.basename(OUTPUT_IMAGE_MUNDO)}")

# ==============================================================================
# 6. MENUS E INTERAÇÃO
# ==============================================================================

def create_transport_menu(ent_data):
    print_box("CRIADOR DE TRANSPORTE", ["Defina nome, velocidade e restrições"])
    nome = input("Nome (ex: Grifo): ").strip().lower().replace(" ", "_")
    try:
        spd = float(input("Multiplicador de Velocidade (1.0 = a pé): "))
        print(f"Terrenos: {', '.join(MOVEMENT_COSTS.keys())}")
        restr = input("Terrenos PROIBIDOS (separe por virgula): ").strip().lower().split(",")
        restr = [x.strip() for x in restr if x.strip()]
        
        if "config" not in ent_data: ent_data["config"] = {}
        if "custom_transports" not in ent_data["config"]: ent_data["config"]["custom_transports"] = {}
        
        ent_data["config"]["custom_transports"][nome] = {"speed": spd, "restrict": restr, "cost_mod": 1.0}
        save_json(ent_data, DADOS_ENTIDADES_PATH)
        print(f"{C['G']}Transporte '{nome}' criado!{C['R']}")
    except: print("Dados inválidos.")

def bind_home_menu(ent_data, map_data):
    print_box("VINCULAR CASA/BASE", ["Selecione entidade e local"])
    # Entidade
    all_ents = [e for k in ["npcs", "grupos", "players"] for e in ent_data.get(k, [])]
    for i, e in enumerate(all_ents): print(f"{i+1}. {e['nome']}")
    try:
        e_idx = int(input("ID Entidade: ")) - 1
        ent = all_ents[e_idx]
        
        # Local
        locs = [v for k, v in map_data["metadata"].get("local_atual_map", {}).items() if v not in ["None", "null"]]
        for i, l in enumerate(locs): print(f"{i+1}. {l}")
        l_idx = int(input("ID Local: ")) - 1
        
        freq = int(input("Voltar a cada quantos dias? (ex: 7): "))
        
        ent["home_location"] = locs[l_idx]
        ent["return_freq_days"] = freq
        ent["days_since_home"] = 0
        save_json(ent_data, DADOS_ENTIDADES_PATH)
        print("Vínculo criado.")
    except: print("Erro.")

def create_entity_menu(ent_data):
    print_box("CRIAR ENTIDADE", ["NPC, Grupo ou Player"])
    tipo = input("Tipo (npc/grupo/player): ").lower() + "s"
    if tipo not in ent_data: ent_data[tipo] = []
    
    nome = input("Nome: ")
    ent = {
        "nome": nome, "tipo": tipo[:-1], 
        "q": random.randint(0, WIDTH-1), "r": random.randint(0, HEIGHT-1),
        "status": "ativo", "cor_hex": generate_unique_color(len(ent_data[tipo])),
        "modo_transporte": "a_pe", "progresso_diario": 0, "meta_q": None
    }
    ent_data[tipo].append(ent)
    save_json(ent_data, DADOS_ENTIDADES_PATH)
    print("Criado.")

def create_location_menu(map_data):
    print_box("CRIAR LOCAL", ["Define um ponto fixo no mapa"])
    nome = input("Nome do Local: ")
    try:
        q = int(input("Q (X): ")); r = int(input("R (Y): "))
        code = str(random.randint(10000, 99999))
        map_data["metadata"]["local_atual_map"][code] = nome
        if "local_atual" not in map_data: map_data["local_atual"] = [[0]*WIDTH for _ in range(HEIGHT)]
        map_data["local_atual"][r][q] = int(code)
        
        # Salvar mapa codificado (compacto)
        with open(MAPA_CODIFICADO_PATH, 'w') as f: json.dump(map_data, f, separators=(',',':'))
        print("Local criado.")
    except: print("Erro.")

def stop_entity_menu(ent_data):
    print_box("PARAR / ATIVAR", ["Imede ou permite movimento"])
    all_ents = [e for k in ["npcs", "grupos", "players"] for e in ent_data.get(k, [])]
    for i, e in enumerate(all_ents): print(f"{i+1}. {e['nome']} [{e.get('status','ativo')}]")
    try:
        idx = int(input("ID: ")) - 1
        ent = all_ents[idx]
        ent["status"] = "parado" if ent.get("status") == "ativo" else "ativo"
        ent["meta_q"] = None
        save_json(ent_data, DADOS_ENTIDADES_PATH)
        print(f"Status: {ent['status']}")
    except: pass

def display_route_menu(map_data, ent_data):
    print_box("VISUALIZAR ROTA", ["Mostra o caminho A* calculado"])
    all_ents = [e for k in ["npcs", "grupos", "players"] for e in ent_data.get(k, [])]
    for i, e in enumerate(all_ents): print(f"{i+1}. {e['nome']}")
    try:
        idx = int(input("ID: ")) - 1
        ent = all_ents[idx]
        if not ent.get("meta_q"): return print("Sem meta.")
        
        path = find_path_astar((ent['q'], ent['r']), (ent['meta_q'], ent['meta_r']), map_data, ent, ent_data)
        if not path: return print("Rota impossível.")
        
        # Gera imagem temp
        mat = np.zeros((HEIGHT, WIDTH), dtype=int)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                t, _, l = get_terrain_info(map_data, x, y)
                mat[y, x] = get_visual_idx(t, l)
        
        plt.figure(figsize=(12, 6))
        plt.imshow(mat, cmap=CMAP, interpolation='nearest', vmin=0, vmax=len(COLORS_LIST)-1)
        xs, ys = zip(*path)
        plt.plot(xs, ys, 'r-', linewidth=2, label='Rota A*')
        plt.scatter(ent['q'], ent['r'], c='lime', s=100, label='Inicio', zorder=10)
        plt.scatter(ent['meta_q'], ent['meta_r'], c='magenta', marker='X', s=100, label='Fim', zorder=10)
        plt.legend()
        plt.savefig(os.path.join(CAMINHO_SCRIPT, "rota_temp.png"), dpi=100)
        plt.close()
        print("Rota salva em rota_temp.png")
    except Exception as e: print(f"Erro: {e}")

def menu_main(map_data, ent_data):
    while True:
        print_box(f"MUNDO VIVO 2.0 ({WIDTH}x{HEIGHT})", [
            "1. Criação (Entidades, Locais, Transportes)",
            "2. Gestão (Vincular Casa, Parar, Mover)",
            "3. Simulação (Passar Tempo)",
            "4. Visualização (Mapa, Rotas)",
            "0. Sair"
        ])
        op = input(">> ")
        if op == '1': menu_creation(map_data, ent_data)
        elif op == '2': menu_manage(map_data, ent_data)
        elif op == '3':
            try:
                d = int(input("Dias: "))
                process_tick(map_data, ent_data, d)
            except: pass
        elif op == '4': menu_vis(map_data, ent_data)
        elif op == '0': break

def menu_creation(map_data, ent_data):
    print_box("MENU CRIAÇÃO", ["1. Entidade", "2. Local", "3. Transporte", "0. Voltar"])
    op = input(">> ")
    if op == '1': create_entity_menu(ent_data)
    elif op == '2': create_location_menu(map_data)
    elif op == '3': create_transport_menu(ent_data)

def menu_manage(map_data, ent_data):
    print_box("MENU GESTÃO", ["1. Vincular Casa", "2. Parar/Ativar", "0. Voltar"])
    op = input(">> ")
    if op == '1': bind_home_menu(ent_data, map_data)
    elif op == '2': stop_entity_menu(ent_data)

def menu_vis(map_data, ent_data):
    print_box("VISUALIZAÇÃO", ["1. Mapa Completo", "2. Rota de Entidade", "0. Voltar"])
    op = input(">> ")
    if op == '1': generate_world_image(map_data, ent_data)
    elif op == '2': display_route_menu(map_data, ent_data)

def main():
    os.system("color")
    map_data = load_json(MAPA_CODIFICADO_PATH)
    ent_data = load_json(DADOS_ENTIDADES_PATH)
    
    if not map_data or not ent_data: return print("Arquivos faltando.")
    
    # Init
    if "config" not in ent_data: ent_data["config"] = {}
    # Garante cor para novos
    idx = 0
    for k in ["npcs", "grupos", "players"]:
        if k not in ent_data: ent_data[k] = []
        for e in ent_data[k]:
            if "cor_hex" not in e: e["cor_hex"] = generate_unique_color(idx); idx+=1

    generate_world_image(map_data, ent_data)
    menu_main(map_data, ent_data)

if __name__ == "__main__":
    main()
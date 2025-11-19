import json
import os
import random
import math
import heapq  # Necessário para o algoritmo de rota (A*)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, to_rgba
from matplotlib.patches import Patch

# ==============================================================================
# 1. CONSTANTES E CONFIGURAÇÕES DO MUNDO
# ==============================================================================
CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
MAPA_CODIFICADO_PATH = os.path.join(CAMINHO_SCRIPT, 'mapa_codificado.json')
DADOS_ENTIDADES_PATH = os.path.join(CAMINHO_SCRIPT, 'dados_entidades.json')
OUTPUT_IMAGE_MUNDO = os.path.join(CAMINHO_SCRIPT, 'mapa_status_mundo.png')

WIDTH = 200
HEIGHT = 86

# --- ESCALA E MOVIMENTO ---
LARGURA_CELULA_KM = 200.0 
MOVIMENTO_BASE_KM_DIA = 30.0 
PONTOS_DIARIOS_MAX = 50.0 

# Códigos ANSI (Cores no Terminal)
CONSOLE_COLORS = {
    "RESET": "\033[0m", 
    "GRUPO": "\033[38;5;208m", 
    "NPC": "\033[93m",         
    "PLAYER": "\033[96m",
    "HEADER": "\033[44m\033[97m",
    "SUCCESS": "\033[92m",
    "FAIL": "\033[91m"
}

# Modificadores de Velocidade (Multiplicador sobre MOVIMENTO_BASE_KM_DIA)
SPEED_MODIFIERS = {
    "a_pe": 1.0,           
    "cavalo": 1.8,         
    "carroca": 0.6,        
    "barco_rio": 1.0,      
    "navio_oceano": 1.5,   
}

# Custo de Movimento por Terreno (Custo > 1.0 significa mais lento)
MOVEMENT_COSTS = {
    "agua": 3.0,      
    "oceano": 10.0,   
    "gelo": 2.5,      
    "rochoso": 3.0,   
    "terra": 1.0,     
    "vegetacao": 1.5, 
    "acampamento": 0.5, 
    "vazio": 9999     
}

# --- MAPEAMENTO DE TERRENO PARA MELHOR MODO (IA) ---
TERRAIN_BEST_MODE = {
    "oceano": "navio_oceano",
    "agua": "barco_rio",
    "terra": "cavalo",
    "vegetacao": "a_pe", 
    "rochoso": "a_pe",
    "gelo": "a_pe",
    "acampamento": "a_pe",
    "vazio": "a_pe"
}

# --- VISUALIZAÇÃO (CORES CORRIGIDAS) ---
# Definição exata das cores para garantir que não fique tudo preto ou com cores erradas
COLOR_MAP_RGB = {
    "agua": (0.27, 0.44, 0.61),     # 0: Azul
    "gelo": (0.9, 0.9, 1.0),        # 1: Branco/Azulado
    "rochoso": (0.4, 0.4, 0.4),     # 2: Cinza Escuro (Corrigido para ser visível)
    "terra": (0.6, 0.4, 0.2),       # 3: Marrom Claro (Corrigido, antes era verde escuro)
    "vegetacao": (0.0, 0.6, 0.0),   # 4: Verde Médio (Corrigido)
    "vazio": (0.0, 0.0, 0.0),       # 5: Preto
    "acampamento": (1.0, 0.0, 0.0), # 6: Vermelho
    "oceano": (0.0, 0.0, 0.4)       # 7: Azul Profundo
}

# A ordem desta lista define o ID da cor (0 a 7)
COLORS_LIST = [
    COLOR_MAP_RGB["agua"],        # 0
    COLOR_MAP_RGB["gelo"],        # 1
    COLOR_MAP_RGB["rochoso"],     # 2
    COLOR_MAP_RGB["terra"],       # 3
    COLOR_MAP_RGB["vegetacao"],   # 4
    COLOR_MAP_RGB["vazio"],       # 5
    COLOR_MAP_RGB["acampamento"], # 6
    COLOR_MAP_RGB["oceano"]       # 7
]
LABELS_LIST = ["Rio/Lago", "Gelo", "Rochoso", "Terra", "Vegetação", "Vazio", "Acampamentos", "Oceano"]
CMAP = ListedColormap(COLORS_LIST)

# Mapeamento reverso para garantir que as strings do JSON apontem para o índice certo
# Reorganizado para clareza e robustez
STR_TO_COLOR_INDEX = {
    ("agua", "rio"): 0,            # Rio/Lago
    ("gelo", "geleira"): 1,        # Gelo
    ("rochoso", "montanha"): 2,    # Rochoso
    ("gramado", "campo"): 3,       # Terra (campo, planicie)
    ("gramado", "floresta"): 4,    # Vegetação (floresta, selva)
    ("vazio", "vazio"): 5,         # Vazio
    ("acampamento", "acampamento"): 6, # Acampamento
    ("agua", "oceano"): 7,         # Oceano (sobrepõe agua/rio se for oceano)
}

# Cores base para entidades (se esgotar, gera aleatória)
BASE_ENTITY_COLORS = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#33FFF6', '#FFC300', '#C70039', '#900C3F', '#581845']

# ==============================================================================
# 2. FUNÇÕES DE DADOS E TERRENO
# ==============================================================================

def load_json(path):
    """Carrega dados de um arquivo JSON."""
    try:
        with open(path, "r", encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return None

def save_json(data, path):
    """Salva dados em um arquivo JSON. Compacto para mapa, identado para entidades."""
    try:
        with open(path, "w", encoding='utf-8') as f:
            indent = 4 if "entidades" in path else None # Identar apenas dados de entidades
            separators = (',', ':') if "entidades" not in path else None # Compactar mapa
            json.dump(data, f, indent=indent, separators=separators, ensure_ascii=False)
    except Exception as e: print(f"{CONSOLE_COLORS['FAIL']}Erro ao salvar '{path}': {e}{CONSOLE_COLORS['RESET']}")

def get_terrain_info(map_data, q, r):
    """Retorna as strings de Terreno, Ambiente e Local Nomeado para as coordenadas (q, r)."""
    if not (0 <= q < WIDTH and 0 <= r < HEIGHT): return "vazio", "vazio", None
    
    t_code = str(map_data["terreno"][r][q])
    a_code = str(map_data["ambiente"][r][q])
    
    t_str = map_data["metadata"]["terrenos_map"].get(t_code, "vazio")
    a_str = map_data["metadata"]["ambientes_map"].get(a_code, "vazio")
    
    # Lógica de correção e padronização para o terreno (IMPORANTE PARA AS CORES)
    if t_str == "agua" and a_str == "oceano": 
        t_str = "oceano"
    elif t_str == "gramado": # 'gramado' é um termo genérico, padronizamos para 'terra' ou 'vegetacao'
        t_str = "vegetacao" if a_str == "floresta" else "terra"
    
    l_val = None
    if "local_atual" in map_data:
        l_code = str(map_data["local_atual"][r][q])
        l_val = map_data["metadata"].get("local_atual_map", {}).get(l_code)
    return t_str, a_str, l_val

def get_color_index(t_str, a_str, l_val):
    """
    Retorna o índice de cor (0-7) baseado no tipo de terreno e ambiente.
    Esta função foi aprimorada para ser mais robusta e evitar 'cores pretas'.
    """
    # 1. Locais Especiais (Acampamentos e Cidades)
    if l_val and l_val not in ["None", "null", "0"]: 
        return STR_TO_COLOR_INDEX.get(("acampamento", "acampamento"), 6) # Padrão para acampamento

    # 2. Oceano
    if t_str == "oceano":
        return STR_TO_COLOR_INDEX.get(("agua", "oceano"), 7) # ID 7 na COLORS_LIST
    
    # 3. Mapeamento Direto por Tupla (terreno, ambiente)
    # Tenta usar a combinação exata primeiro
    # Nota: 'gramado' é usado nas chaves do STR_TO_COLOR_INDEX para compatibilidade
    lookup_t = t_str
    if t_str == "terra": lookup_t = "gramado" 
    if t_str == "vegetacao": lookup_t = "gramado"
    
    if (lookup_t, a_str) in STR_TO_COLOR_INDEX: 
        return STR_TO_COLOR_INDEX[(lookup_t, a_str)]
    
    # 4. Fallbacks baseados apenas no Terreno (Para casos não mapeados explicitamente)
    if t_str == "agua": return STR_TO_COLOR_INDEX.get(("agua", "rio"), 0)
    if t_str == "gelo": return STR_TO_COLOR_INDEX.get(("gelo", "geleira"), 1)
    if t_str == "rochoso": return STR_TO_COLOR_INDEX.get(("rochoso", "montanha"), 2)
    if t_str == "terra": return STR_TO_COLOR_INDEX.get(("gramado", "campo"), 3) # Assumindo campo para 'terra' genérica
    if t_str == "vegetacao": return STR_TO_COLOR_INDEX.get(("gramado", "floresta"), 4) # Assumindo floresta para 'vegetacao' genérica

    # 5. Padrão final: Vazio (preto) se nada for encontrado
    return STR_TO_COLOR_INDEX.get(("vazio", "vazio"), 5) # ID 5 na COLORS_LIST

def get_location_coords(map_data, location_name):
    """Procura as coordenadas (Q, R) de um local nomeado no mapa."""
    if not location_name: return None, None
    target_code = next((k for k, v in map_data["metadata"].get("local_atual_map", {}).items() if v == location_name), None)
    if target_code:
        for r in range(HEIGHT):
            for q in range(WIDTH):
                if str(map_data["local_atual"][r][q]) == target_code: return q, r
    return None, None 

def generate_unique_color(index):
    """Gera uma cor hexadecimal única para novas entidades."""
    if index < len(BASE_ENTITY_COLORS): return BASE_ENTITY_COLORS[index]
    # Se acabarem as cores base, gera uma aleatória
    return f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}'

def initialize_entities(ent_data, map_data):
    """
    Garante que todas as entidades tenham atributos essenciais, 
    inicializando-os se estiverem faltando.
    """
    changed = False
    locais_validos = [v for k, v in map_data["metadata"].get("local_atual_map", {}).items() if v not in ["None", "null"]]
    entity_color_index = 0

    for tipo_key in ["npcs", "grupos", "players"]: # Itera pelas listas de tipos
        if tipo_key not in ent_data: ent_data[tipo_key] = [] # Cria a lista se não existir
        
        for ent in ent_data[tipo_key]:
            # Atributos básicos de posição e tipo
            if "q" not in ent: ent["q"], ent["r"] = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1); changed = True
            ent["tipo"] = tipo_key.replace("s", "") # Armazena tipo singular (npc, grupo, player)

            # Cor
            if "cor_hex" not in ent: ent["cor_hex"] = generate_unique_color(entity_color_index); changed = True
            entity_color_index += 1

            # Base (para NPCs e Grupos)
            if "base_local_nome" not in ent and ent["tipo"] != "player" and locais_validos:
                ent["base_local_nome"] = random.choice(locais_validos); changed = True
            
            # Movimento e Equipamento
            if "modo_transporte" not in ent: ent["modo_transporte"] = "a_pe"; changed = True
            if "modo_temporario" not in ent: ent["modo_temporario"] = None; changed = True
            if "tem_navio" not in ent: ent["tem_navio"] = random.choice([True, False]); changed = True
            if "tem_barco_rio" not in ent: ent["tem_barco_rio"] = random.choice([True, False]); changed = True
            if "tem_cavalo" not in ent: ent["tem_cavalo"] = random.choice([True, False]); changed = True
            
            # Metas e progresso
            if "meta_q" not in ent: ent["meta_q"], ent["meta_r"] = None, None; changed = True
            if "progresso_diario" not in ent: ent["progresso_diario"] = 0; changed = True
            if "status" not in ent: ent["status"] = "ativo"; changed = True # Novo: status para 'parado'

    if changed: save_json(ent_data, DADOS_ENTIDADES_PATH)
    return ent_data

# ==============================================================================
# 3. LÓGICA DE MOVIMENTO AVANÇADO (A* PATHFINDING)
# ==============================================================================

def calculate_movement_points(entity, t_str):
    """
    Calcula a capacidade de movimento diário de uma entidade em um terreno específico.
    Considera modo de transporte e equipamento.
    """
    modo = entity.get("modo_temporario") or entity.get("modo_transporte", "a_pe")
    
    # 1. Restrições e Fallbacks de Equipamento
    # Se o modo exige um equipamento que a entidade não tem, o modo é resetado para "a_pe" (a pé)
    if modo == "navio_oceano" and not entity.get("tem_navio"): modo = "a_pe"
    if modo == "barco_rio" and not entity.get("tem_barco_rio"): modo = "a_pe"
    if modo in ["cavalo", "carroca"] and not entity.get("tem_cavalo"): modo = "a_pe"
    
    # 2. Bloqueio total (ex: tentar cruzar oceano sem navio)
    if t_str == "oceano" and modo != "navio_oceano": return 0 # Movimento impossível
    
    # 3. Cálculo do Custo e Velocidade
    modifier = SPEED_MODIFIERS.get(modo, 1.0)
    custo = MOVEMENT_COSTS.get(t_str, 9999) # Custo muito alto para terrenos desconhecidos/inválidos
    
    if custo >= 9000: return 0 # Terreno intransponível
    
    # Penalidade extra para nadar/vadear em rios/lagos sem barco
    if t_str == "agua" and modo not in ["barco_rio", "navio_oceano"]:
        custo *= 5.0 # Aumenta o custo para tornar muito lento, mas não impossível

    velocidade_km_dia = (MOVIMENTO_BASE_KM_DIA * modifier) / custo
    return (velocidade_km_dia / LARGURA_CELULA_KM) * PONTOS_DIARIOS_MAX

def determine_best_mode(t_str, entity):
    """Determina o melhor modo de transporte disponível para o terreno atual, considerando equipamento."""
    best_mode = TERRAIN_BEST_MODE.get(t_str, "a_pe")
    # Verifica se a entidade possui o equipamento para o "melhor" modo
    if best_mode == "navio_oceano" and not entity.get("tem_navio"): return "a_pe"
    if best_mode == "barco_rio" and not entity.get("tem_barco_rio"): return "a_pe"
    if best_mode in ["cavalo", "carroca"] and not entity.get("tem_cavalo"): return "a_pe"
    return best_mode

def heuristic(a, b):
    """Função heurística para o algoritmo A* (distância de Manhattan)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_path_astar(start, goal, map_data, entity, limit=500):
    """
    Implementação do algoritmo A* para encontrar o caminho mais eficiente.
    Retorna uma lista de coordenadas (q, r) ou None se nenhum caminho for encontrado.
    """
    start_node = (start[0], start[1])
    goal_node = (goal[0], goal[1])
    
    frontier = [] # Fila de prioridade: (prioridade, nó)
    heapq.heappush(frontier, (0, start_node))
    came_from = {start_node: None} # Para reconstruir o caminho
    cost_so_far = {start_node: 0}  # Custo do nó inicial até o nó atual

    nodes_processed = 0
    
    while frontier:
        nodes_processed += 1
        if nodes_processed > limit: # Limite para evitar loops infinitos em mapas complexos/bloqueados
            # print(f"DEBUG: A* excedeu limite de {limit} nós. Desistindo.")
            break

        _, current = heapq.heappop(frontier)

        if current == goal_node:
            break

        # Vizinhos (Cima, Baixo, Esquerda, Direita)
        neighbors = [
            (current[0]+1, current[1]), (current[0]-1, current[1]),
            (current[0], current[1]+1), (current[0], current[1]-1)
        ]

        for next_node in neighbors:
            nq, nr = next_node
            # Verifica limites do mapa
            if not (0 <= nq < WIDTH and 0 <= nr < HEIGHT): continue
            
            # Calcula o custo de mover para o próximo nó
            t_next, _, _ = get_terrain_info(map_data, nq, nr)
            points = calculate_movement_points(entity, t_next)
            
            if points == 0: continue # Terreno intransponível
            
            # O custo para o A* é o inverso dos pontos de movimento (quanto mais pontos, mais fácil, menor o custo)
            # Adiciona um pequeno valor (0.1) para evitar divisão por zero se points for 0
            move_cost = 1.0 / (points / PONTOS_DIARIOS_MAX + 0.001) # Normaliza para uma base de 1

            new_cost = cost_so_far[current] + move_cost
            
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(goal_node, next_node)
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current

    # Reconstroi o caminho a partir do 'came_from'
    if goal_node not in came_from:
        return None # Caminho não encontrado

    path = []
    curr = goal_node
    while curr != start_node:
        path.append(curr)
        curr = came_from[curr]
    path.reverse() # Inverte para ter do início ao fim
    return path

def process_tick(map_data, ent_data, days=1, debug_mode=False):
    """Processa a simulação por um número de dias, incluindo a lógica de IA e movimento."""
    if debug_mode: print(f"\n{CONSOLE_COLORS['HEADER']} PROCESSANDO {days} DIA(S) EM MODO DEBUG {CONSOLE_COLORS['RESET']}")
    else: print(f"\n{CONSOLE_COLORS['HEADER']} PROCESSANDO {days} DIA(S)... {CONSOLE_COLORS['RESET']}")

    for day_num in range(days):
        if debug_mode: print(f"\n--- DIA {day_num + 1}/{days} ---")
        
        for tipo_key in ["npcs", "grupos", "players"]:
            for ent in ent_data.get(tipo_key, []):
                
                # Ignora entidades com status 'parado'
                if ent.get("status") == "parado": continue

                # --- LÓGICA DE IA: DECISÃO DE NOVA META ---
                if ent["tipo"] != "player": # A IA só se aplica a NPCs e Grupos
                    current_q, current_r = ent["q"], ent["r"]
                    meta_q, meta_r = ent.get("meta_q"), ent.get("meta_r")

                    # Se não tem meta ou já chegou na meta atual
                    if meta_q is None or (current_q == meta_q and current_r == meta_r):
                        # Lógica de retorno à base / reabastecimento
                        if ent.get("base_local_nome"):
                            base_q, base_r = get_location_coords(map_data, ent["base_local_nome"])
                            
                            if base_q is not None and (current_q != base_q or current_r != base_r):
                                # Se a entidade tem uma base e não está nela, mas precisa voltar para pegar equipamento
                                # (Ex: meta bloqueada por água e não tem barco/navio)
                                if ent.get("meta_orig_q") is not None and not ent.get("tem_navio") or not ent.get("tem_barco_rio"):
                                    ent["meta_q"], ent["meta_r"] = base_q, base_r
                                    if debug_mode: print(f"   {CONSOLE_COLORS['NPC']}{ent['nome']}{CONSOLE_COLORS['RESET']} volta à base para reabastecer.")
                                    continue # Recalcula o path na próxima iteração
                            elif base_q is not None and (current_q == base_q and current_r == base_r):
                                # Chegou na base. Reabastece e retoma meta original ou vaga.
                                ent["tem_navio"] = True # Assume que pode pegar um navio na base
                                ent["tem_barco_rio"] = True
                                ent["tem_cavalo"] = True
                                if ent.get("meta_orig_q") is not None:
                                    ent["meta_q"], ent["meta_r"] = ent.pop("meta_orig_q"), ent.pop("meta_orig_r")
                                    if debug_mode: print(f"   {CONSOLE_COLORS['NPC']}{ent['nome']}{CONSOLE_COLORS['RESET']} reabasteceu e retomou meta.")
                                else:
                                    nq, nr = generate_random_goal(ent, map_data)
                                    ent["meta_q"], ent["meta_r"] = nq, nr
                                    if debug_mode: print(f"   {CONSOLE_COLORS['NPC']}{ent['nome']}{CONSOLE_COLORS['RESET']} na base, agora vai vagar.")
                        else: # Se não tem base, apenas gera nova meta aleatória
                            nq, nr = generate_random_goal(ent, map_data)
                            ent["meta_q"], ent["meta_r"] = nq, nr
                            if debug_mode: print(f"   {CONSOLE_COLORS['NPC']}{ent['nome']}{CONSOLE_COLORS['RESET']} gerou nova meta.")

                if ent["meta_q"] is None: # Se mesmo após a IA não houver meta, pula a entidade
                    ent["modo_temporario"] = None
                    continue

                # --- PATHFINDING E MOVIMENTO ---
                current_pos = (ent["q"], ent["r"])
                target_pos = (ent["meta_q"], ent["meta_r"])
                
                # Encontra o caminho usando A*
                path = find_path_astar(current_pos, target_pos, map_data, ent, limit=500)
                
                if not path: # Se o A* não encontrou um caminho
                    if debug_mode: print(f"   {CONSOLE_COLORS['FAIL']}🛑 {ent['nome']} não consegue encontrar caminho para ({target_pos[0]},{target_pos[1]}).{CONSOLE_COLORS['RESET']}")
                    
                    # Lógica deFallback: Tentar voltar para a base se estiver bloqueado no meio do caminho
                    if ent.get("base_local_nome") and not ent.get("meta_orig_q"): # Se tem base e não está com meta original pausada
                         bq, br = get_location_coords(map_data, ent["base_local_nome"])
                         if bq is not None and (current_pos[0] != bq or current_pos[1] != br):
                             # Salva a meta atual como original e define a base como nova meta
                             ent["meta_orig_q"], ent["meta_orig_r"] = ent["meta_q"], ent["meta_r"]
                             ent["meta_q"], ent["meta_r"] = bq, br
                             if debug_mode: print(f"   {CONSOLE_COLORS['NPC']}{ent['nome']}{CONSOLE_COLORS['RESET']} rota bloqueada, voltando para base ({bq},{br}).")
                             continue # Pula para o próximo dia para recalcular com a nova meta
                    
                    # Se não tem base ou já está indo para a base e ainda está bloqueado, desiste da meta e fica parado
                    ent["meta_q"] = None
                    ent["modo_temporario"] = None
                    continue

                # Pega o próximo passo do caminho encontrado pelo A*
                next_q, next_r = path[0] 
                t_next_cell, _, _ = get_terrain_info(map_data, next_q, next_r)
                t_current_cell, _, _ = get_terrain_info(map_data, ent["q"], ent["r"])
                
                # Determina o melhor modo de transporte para a PRÓXIMA célula
                best_mode_for_next_cell = determine_best_mode(t_next_cell, ent)
                
                # Ajusta o modo temporário se houver uma mudança de modo vantajosa
                if best_mode_for_next_cell != ent.get("modo_transporte") and best_mode_for_next_cell != "a_pe":
                    ent["modo_temporario"] = best_mode_for_next_cell
                else:
                    ent["modo_temporario"] = None

                # Calcula os pontos de movimento para o dia, baseados no TERRENO ATUAL
                daily_move_points = calculate_movement_points(ent, t_current_cell)
                
                if daily_move_points == 0:
                    if debug_mode: print(f"   > {ent['nome']} PARADO (terreno intransponível).")
                    continue
                
                ent["progresso_diario"] += daily_move_points
                
                # Calcula quantos "passos" (células) a entidade pode dar neste dia
                num_steps = int(ent["progresso_diario"] / PONTOS_DIARIOS_MAX)
                ent["progresso_diario"] -= num_steps * PONTOS_DIARIOS_MAX # Atualiza o progresso restante

                if num_steps > 0:
                    # Move a entidade para a próxima célula (apenas 1 passo por dia no A*)
                    # O Pathfinding já garante o caminho mais eficiente, então um passo é o suficiente
                    ent["q"], ent["r"] = next_q, next_r
                    if debug_mode: 
                        print(f"   {CONSOLE_COLORS['PLAYER'] if ent['tipo']=='player' else CONSOLE_COLORS['NPC']}{ent['nome']}{CONSOLE_COLORS['RESET']} moveu para ({next_q}, {next_r}) usando '{ent.get('modo_temporario') or ent['modo_transporte']}' em '{t_next_cell}'.")

    save_json(ent_data, DADOS_ENTIDADES_PATH)
    if not debug_mode: print(f"{CONSOLE_COLORS['SUCCESS']}✅ Simulação finalizada.{CONSOLE_COLORS['RESET']}")
    generate_world_image(map_data, ent_data)

def generate_random_goal(ent, map_data):
    """Gera uma meta aleatória viável para uma entidade."""
    for _ in range(20): # Tenta 20 vezes para encontrar um local viável
        rand_q, rand_r = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        t_str, _, _ = get_terrain_info(map_data, rand_q, rand_r)
        
        # Verifica se o terreno do objetivo é acessível para a entidade
        if calculate_movement_points(ent, t_str) > 0:
            return rand_q, rand_r
    return ent["q"], ent["r"] # Retorna a posição atual se não encontrar um alvo viável

# ==============================================================================
# 4. FUNÇÕES DE VISUALIZAÇÃO
# ==============================================================================

def generate_world_image(map_data, ent_data):
    """Gera e salva uma imagem visual do mapa com entidades."""
    print("🎨 Gerando imagem do mundo...")
    color_matrix = np.full((HEIGHT, WIDTH), 5, dtype=int) # Inicializa com cor 'vazio'
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t, a, l = get_terrain_info(map_data, x, y)
            color_matrix[y, x] = get_color_index(t, a, l)

    fig, ax = plt.subplots(figsize=(16, 8))
    # 'vmin' e 'vmax' são CRUCIAIS para que as cores do colormap sejam mapeadas corretamente
    ax.imshow(
from gerenciar_banco import *




#Funcoes de adicionar

def adicionar_npc():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome: ").lower()
    descricao = input("Descrição: ")
    if nome == "" or descricao == "":
        print("Nome e descrição não podem ser vazios.")
        return
    elif nome in [p['nome'] for p in npcs]:
                print("Já existe um NPC com este nome cadastrado.")
                return
    print(f"NPC '{nome}' adicionado com a descrição: {descricao}")
    
    novo_npc = {
        "nome": nome,
        "descricao": descricao
    }
    npcs.append(novo_npc)
    salvar_dados(grupos,npcs,players,locais)

def adicionar_grupo():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome: ").lower()
    descricao = input("Descrição: ")
    quantidade_membros = int(input("Quantidade de membros: "))
    if nome == "" or descricao == "" or quantidade_membros < 0:
        print("Nome e descrição não podem ser vazios.")
        return
    elif nome in [p['nome'] for p in npcs]:
                print("Já existe um NPC com este nome cadastrado.")
                return
    print(f"NPC '{nome}' adicionado com a descrição: {descricao}")
    
    novo_grupo = {
        "nome": nome,
        "descricao": descricao,
        "quantidade_membros": quantidade_membros
    }
    grupos.append(novo_grupo)
    salvar_dados(grupos,npcs,players,locais)


def adicionar_player():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome: ").lower()
    descricao = input("Descrição: ")
    classe = input("Classe: ")
    nivel = int(input("Nível: "))
    raca = input("Raça: ")
    jogador = input("Jogador: ")
    atributos = input("Atributos (força, destreza, constituição, inteligência, sabedoria, carisma): ")
    vida = int(input("Vida: "))
    ca = int(input("Classe de Armadura (CA): "))
    anotacoes = input("Anotações: ")
    if nome == "" or descricao == "":
        print("Nome e descrição não podem ser vazios.")
        return
    elif nome in [p['nome'] for p in players]:
                print("Já existe um Player com este nome cadastrado.")
                return
    novo_player = {
        "nome": nome,
        "descricao": descricao,
        "classe": classe,
        "nivel": nivel,
        "raca": raca,
        "jogador": jogador,
        "atributos": atributos,
        "vida": vida,
        "ca": ca,
        "anotacoes": anotacoes
    }

    players.append(novo_player)
    salvar_dados(grupos,npcs,players,locais)



#funcoes de editar


def editar_player():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome do player a ser editado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    if nome not in [p['nome'] for p in players]:
        print(f"Player '{nome}' não encontrado.")
        input("Pressione Enter para continuar...")
        return
    for player in players:
        if player['nome'] == nome:
            print(f"Descrição atual: {player['descricao']}")
            print(f"Classe atual: {player['classe']}")
            print(f"Nível atual: {player['nivel']}")
            print(f"Raça atual: {player['raca']}")
            print(f"Jogador atual: {player['jogador']}")
            print(f"Atributos atuais: {player['atributos']}")
            print(f"Vida atual: {player['vida']}")
            print(f"Classe de Armadura (CA) atual: {player['ca']}")
            print(f"Anotações atuais: {player['anotacoes']}")
            print("\nDigite os novos valores:")
            player['descricao'] = input("Nova descrição: ")

            player['classe'] = input("Nova classe: ")
            if player['classe'] == "":
                print("Classe não pode ser vazia.")
                input("Pressione Enter para continuar...")
                return
            player['nivel'] = int(input("Novo nível: "))
            if player['nivel'] < 0:
                print("Nível não pode ser negativo.")
                input("Pressione Enter para continuar...")
                return
            player['raca'] = input("Nova raça: ")
            if player['raca'] == "":
                print("Raça não pode ser vazia.")
                input("Pressione Enter para continuar...")
                return
            player['jogador'] = input("Novo jogador: ")
            if player['jogador'] == "":
                print("Jogador não pode ser vazio.")
                input("Pressione Enter para continuar...")
                return
            player['atributos'] = input("Novos atributos (força, destreza, constituição, inteligência, sabedoria, carisma): ")
            if player['atributos'] == "":
                print("Atributos não podem ser vazios.")
                input("Pressione Enter para continuar...")
                return
            player['vida'] = int(input("Nova vida: "))
            if player['vida'] < 0:
                print("Vida não pode ser negativa.")
                input("Pressione Enter para continuar...")
                return
            player['ca'] = int(input("Nova Classe de Armadura (CA): "))
            if player['ca'] < 0:
                print("Classe de Armadura (CA) não pode ser negativa.")
                input("Pressione Enter para continuar...")
                return
            player['anotacoes'] = input("Novas anotações: ")

            salvar_dados(grupos,npcs,players,locais)
            limpar_tela()
            print(f"Player '{nome}' editado com sucesso.")
            input("Pressione Enter para continuar...")
            return
    print(f"Player '{nome}' não encontrado.")

def editar_npc():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome do NPC a ser editado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    elif nome not in [p['nome'] for p in npcs]:
        print(f"NPC '{nome}' não encontrado.")
        input("Pressione Enter para continuar...")
        return
    for npc in npcs:
        if npc['nome'] == nome:
            print(f"Descrição atual: {npc['descricao']}")
            npc['descricao'] = input("Nova descrição: ")
            if npc['descricao'] == "":
                print("Descrição não pode ser vazia.")
                input("Pressione Enter para continuar...")
                return
            salvar_dados(grupos,npcs,players,locais)
            limpar_tela()
            print(f"NPC '{nome}' editado com sucesso.")
            input("Pressione Enter para continuar...")
            return
    print(f"NPC '{nome}' não encontrado.")

def editar_grupo():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome do grupo a ser editado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    elif nome not in [p['nome'] for p in grupos]:
        print(f"Grupo '{nome}' não encontrado.")
        input("Pressione Enter para continuar...")
        return
    for grupo in grupos:
        if grupo['nome'] == nome:
            print(f"Descrição atual: {grupo['descricao']}")
            print(f"Quantidade de membros atual: {grupo['quantidade_membros']}")
            grupo['descricao'] = input("Nova descrição: ")
            if grupo['descricao'] == "":
                print("Descrição não pode ser vazia.")
                input("Pressione Enter para continuar...")
                return
            grupo['quantidade_membros'] = int(input("Nova quantidade de membros: "))
            if grupo['quantidade_membros'] < 0:
                print("Quantidade de membros não pode ser negativa.")
                input("Pressione Enter para continuar...")
                return
            salvar_dados(grupos,npcs,players,locais)
            limpar_tela()
            print(f"Grupo '{nome}' editado com sucesso.")
            input("Pressione Enter para continuar...")
            return
    print(f"Grupo '{nome}' não encontrado.")


#funcoes de visualizar


def visualizar_todos_players():
    grupos,npcs,players,locais = importar_dados()
    if not players:
        print("Nenhum player cadastrado.")
    else:
        limpar_tela()
        for player in players:
            print("\n -------------------------")
            print(f"\n Nome: {player['nome']} \n Descrição: {player['descricao']} \n Classe: {player['classe']} \n Nível: {player['nivel']} \n Raça: {player['raca']} \n Jogador: {player['jogador']} \n Atributos: {player['atributos']} \n Vida: {player['vida']} \n CA: {player['ca']} \n Anotações: {player['anotacoes']}")
    input("\n Pressione Enter para continuar...")


def visualizar_player():
    grupos,npcs,players,locais = importar_dados()
    limpar_tela()
    nome = input("Nome do player a ser visualizado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    for player in players:
        if player['nome'] == nome:
            limpar_tela()
            print(f"\n Nome: {player['nome']} \n Descrição: {player['descricao']} \n Classe: {player['classe']} \n Nível: {player['nivel']} \n Raça: {player['raca']} \n Jogador: {player['jogador']} \n Atributos: {player['atributos']} \n Vida: {player['vida']} \n CA: {player['ca']} \n Anotações: {player['anotacoes']}")
            input("\n Pressione Enter para continuar...")
            return
    print(f"Player '{nome}' não encontrado.")
    input("Pressione Enter para continuar...")

def visualizar_todos_grupos():
    grupos,npcs,players,locais = importar_dados()
    if not grupos:
        print("Nenhum grupo cadastrado.")
    else:
        limpar_tela()
        for grupo in grupos:
            print("\n -------------------------")
            print(f"\n Nome: {grupo['nome']} \n Descrição: {grupo['descricao']} \n Quantidade de membros: {grupo['quantidade_membros']}")
    input("\n Pressione Enter para continuar...")


def visualizar_grupo():
    grupos,npcs,players,locais = importar_dados()
    limpar_tela()
    nome = input("Nome do grupo a ser visualizado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    for grupo in grupos:
        if grupo['nome'] == nome:
            limpar_tela()
            print(f"\n Nome: {grupo['nome']} \n Descrição: {grupo['descricao']} \n Quantidade de membros: {grupo['quantidade_membros']}")
            input("\n Pressione Enter para continuar...")
            return
    print(f"Grupo '{nome}' não encontrado.")
    input("Pressione Enter para continuar...")


def  visualizar_todos_npcs():
    grupos,npcs,players,locais = importar_dados()
    if not npcs:
        print("Nenhum NPC cadastrado.")
    else:
        limpar_tela()
        for npc in npcs:
            print("\n -------------------------")
            print(f"\n Nome: {npc['nome']} \n Descrição: {npc['descricao']}")
    input("\n Pressione Enter para continuar...")


def visualizar_npc():
    grupos,npcs,players,locais = importar_dados()
    limpar_tela()
    nome = input("Nome do NPC a ser visualizado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    for npc in npcs:
        if npc['nome'] == nome:
            limpar_tela()
            print(f"\n Nome: {npc['nome']} \n Descrição: {npc['descricao']}")
            input("\n Pressione Enter para continuar...")
            return
    print(f"NPC '{nome}' não encontrado.")
    input("Pressione Enter para continuar...")


#funcoes de deletar

def deletar_player():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome do player a ser deletado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    for i, player in enumerate(players):
        if player['nome'] == nome:
            del players[i]
            salvar_dados(grupos,npcs,players,locais)
            limpar_tela()
            print(f"Player '{nome}' deletado com sucesso.")
            input("Pressione Enter para continuar...")
            return
    print(f"Player '{nome}' não encontrado.")
    input("Pressione Enter para continuar...")


def deletar_npc():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome do NPC a ser deletado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    for i, npc in enumerate(npcs):
        if npc['nome'] == nome:
            del npcs[i]
            salvar_dados(grupos,npcs,players,locais)
            limpar_tela()
            print(f"NPC '{nome}' deletado com sucesso.")
            input("Pressione Enter para continuar...")
            return
    print(f"NPC '{nome}' não encontrado.")
    input("Pressione Enter para continuar...")

def deletar_grupo():
    grupos,npcs,players,locais = importar_dados()
    nome = input("Nome do grupo a ser deletado: ").lower()
    if nome == "":
        print("Nome não pode ser vazio.")
        input("Pressione Enter para continuar...")
        return
    for i, grupo in enumerate(grupos):
        if grupo['nome'] == nome:
            del grupos[i]
            salvar_dados(grupos,npcs,players,locais)
            limpar_tela()
            print(f"Grupo '{nome}' deletado com sucesso.")
            input("Pressione Enter para continuar...")
            return
    print(f"Grupo '{nome}' não encontrado.")
    input("Pressione Enter para continuar...")


#--- funções de funcionamento do mapa ---
'''
mapa tem o tamanho total de  17.200 quadrados (200 largura x 86 altura)
mapa deve ser salvo em um arquivo externo para não perder os dados ao fechar o programa
mapa deve permitir adicionar, editar, visualizar e deletar locais
cada local deve ter um nome, descrição, coordenadas (x, y) e tamanho (largura, altura), tipo do terreno, tipo de ambiente(urbano, rural, selvagem, etc)
para ultilização do mapa deve-se ler o terreno e ambiente de cada local para determinar se o npc ou o grupo pode estar ali e se ele ira
se mover para lá
as coordenadas (x, y) representam o canto superior esquerdo do local no mapa
cada local deve ser representado por um retângulo no mapa

'''

#  gerar o mapa é uma função de uso unico para criar a estrutura inicial do mapa e os arquivos necessários para o funcionamento do mapa o mapa sera guardado em um arquivo json chamado mapa.json
#o mapa consiste em uma grade de 200x86 quadrados onde cada quadrado representa um terreno específico
#ele será uma matriz 2D onde cada elemento é um dicionário com informações sobre o terreno e o ambiente daquele quadrado
#que tera todos os quadrados armazenados mesmo que vazios para facilitar a manipulação do mapa futuramente e gerar os outros arquivos necessários para trabalhar com as layers do mapa
# gere o mapa para ter visualmente a aparencia do mapa e facilitar a manipulação futura
#cada quadrado deve armazenar as informações de terreno e ambiente, local  atual, npcs presentes, grupos presentes, players presentes, valor de movimentação (custo para se mover para aquele quadrado),  valor de estabilidade (quanto mais alto mais dificil de se manter ali)
#coloque tambem um campo de cordenadas x e y para facilitar a localização dos quadrados no mapa
#e um campo de descrição para descrever o quadrado

def gerar_mapa():
    mapa = []
    for y in range(86):
        linha = []
        for x in range(200):
            quadrado = {
                "x": x,
                "y": y,
                "terreno": "vazio",
                "ambiente": "desconhecido",
                "local_atual": None,
                "npcs_presentes": [],
                "grupos_presentes": [],
                "players_presentes": [],
                "valor_movimentacao": 1,
                "valor_estabilidade": 1,
                "descricao": ""
            }
            linha.append(quadrado)
        mapa.append(linha)
    
    with open("mapa.json", "w") as f:
        json.dump(mapa, f, indent=4)
    
    print("Mapa gerado com sucesso e salvo em 'mapa.json'.")
gerar_mapa()

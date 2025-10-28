from gerenciar_banco import *


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

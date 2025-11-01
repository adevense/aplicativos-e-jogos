import os
from funcoes import *
from gerenciar_banco import limpar_tela

# --- Funções de Sub-Menu ---

def menu_adicionar():
    while True:
        limpar_tela()
        print("\n--- MENU ADICIONAR ---")
        print("1. Adicionar grupo")
        print("2. Adicionar npc")
        print("3. Adicionar player")
        print("4. Adicionar local")
        print("5. Voltar")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            limpar_tela()
            adicionar_grupo()
        elif opcao == '2':
            limpar_tela()
            adicionar_npc()
    
        elif opcao == '3':
            limpar_tela()
            adicionar_player()

        elif opcao == '4':
            limpar_tela()

        elif opcao == '5':
            break  # Sai do loop do menu_adicionar e retorna para menu_principal
        else:
            print("Opção inválida.")
            input("Pressione Enter para continuar...")


def menu_editar():
    while True:
        limpar_tela()
        print("\n--- MENU EDITAR ---")
        print("1. Editar player")
        print("2. Editar grupo")
        print("3. Editar local")
        print("4. Editar npc")
        print("5. Voltar")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            limpar_tela()
            editar_player()
        elif opcao == '2':
            limpar_tela()
            editar_grupo()
        elif opcao == '3':
            limpar_tela()
            #editar_local()
        elif opcao == '4':
            limpar_tela()
            editar_npc()
        elif opcao == '5':
            break  # Volta ao Menu Principal
        else:
            print("Opção inválida.")
            input("Pressione Enter para continuar...")


def menu_tempo():
    while True:
        limpar_tela()
        print("\n--- MENU TEMPO ---")

        print("2. Voltar")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            limpar_tela()

            input("Pressione Enter para continuar...")
        elif opcao == '2':
            break  # Volta ao Menu Principal
        else:
            print("Opção inválida.")
            input("Pressione Enter para continuar...")



def menu_visualizar():    
    while True:
        limpar_tela()
        print("\n--- MENU VISUALIZAR ---")
        print("1. Visualizar todos os players")
        print("2. visualizar player")
        print("3. Visualizar todos os grupos")
        print("4. visualizar grupo")
        print("5. Visualizar todos os locais")
        print("6. visualizar local")
        print("7. Visualizar todos os npcs")
        print("8. visualizar npc")
        print("9. Voltar")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            limpar_tela()
            visualizar_todos_players()
        elif opcao == '2':
            limpar_tela()
            visualizar_player()
        elif opcao == '3':
            limpar_tela()
            visualizar_todos_grupos()
        elif opcao == '4':
            limpar_tela()
            visualizar_grupo()
        elif opcao == '5':
            limpar_tela()
            #visualizar_todos_locais()
        elif opcao == '6':
            limpar_tela()
           #visualizar_local()
        elif opcao == '7':
            limpar_tela()
            visualizar_todos_npcs()
        elif opcao == '8':
            limpar_tela()
            visualizar_npc()
        elif opcao == '9':
            break  # Volta ao Menu Principal


# --- Função do menu deletar ---

def menu_deletar():
    while True:
        limpar_tela()
        print("\n--- MENU DELETAR ---")
        print("1. Deletar player")
        print("2. Deletar grupo")
        print("3. Deletar local")
        print("4. Deletar npc")
        print("5. Voltar")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            limpar_tela()
            deletar_player()
        elif opcao == '2':
            limpar_tela()
            deletar_grupo()
        elif opcao == '3':
            limpar_tela()
            #deletar_local()
        elif opcao == '4':
            limpar_tela()
            deletar_npc()
        elif opcao == '5':
            break  # Volta ao Menu Principal
        else:
            print("Opção inválida.")
            input("Pressione Enter para continuar...")


# --- Função do Menu Principal ---

def menu_principal():
    while True:
        limpar_tela()
        print("\n--- MENU PRINCIPAL ---")
        print("1. Menu Adicionar")
        print("2. Menu Editar")
        print("3. Menu Tempo")
        print("4. Menu visualizar")
        print("5. Menu Deletar")
        print("6. Sair")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            # Chama o sub-menu. Quando ele retorna (por causa do 'break'), o loop continua
            menu_adicionar()
        elif opcao == '2':
            menu_editar()
        elif opcao == '3':
            menu_tempo()
        elif opcao == '4':
            menu_visualizar()
        elif opcao == '5':
            limpar_tela()
            menu_deletar()
        elif opcao == '6':
            limpar_tela()
            print("Saindo...")
            break
        else:
            print("Opção inválida.")
            input("Pressione Enter para continuar...")

# Inicia o programa
if __name__ == "__main__":
    menu_principal()
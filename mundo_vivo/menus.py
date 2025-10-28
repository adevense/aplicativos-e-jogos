import os
from funcoes import *

def limpar_tela():
    """Limpa o console."""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

# --- Funções de Sub-Menu ---

def menu_adicionar():
    while True:
        limpar_tela()
        print("--- MENU ADICIONAR ---")
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
        print("--- MENU EDITAR ---")
        print("1. Editar Item (Em desenvolvimento)")
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


def menu_tempo():
    while True:
        limpar_tela()
        print("--- MENU TEMPO ---")

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


# --- Função do Menu Principal ---

def menu_principal():
    while True:
        limpar_tela()
        print("--- MENU PRINCIPAL ---")
        print("1. Menu Adicionar")
        print("2. Menu Editar")
        print("3. Menu Tempo")
        print("4. Sair")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            # Chama o sub-menu. Quando ele retorna (por causa do 'break'), o loop continua
            menu_adicionar()
        elif opcao == '2':
            menu_editar()
        elif opcao == '3':
            menu_tempo()
        elif opcao == '4':
            limpar_tela()
            print("Saindo...")
            break
        else:
            print("Opção inválida.")
            input("Pressione Enter para continuar...")

# Inicia o programa
if __name__ == "__main__":
    menu_principal()
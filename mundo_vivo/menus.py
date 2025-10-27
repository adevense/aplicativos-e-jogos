import os

def limpar_tela():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def menu_principal():
    while True:
        limpar_tela()
        print("1. Menu adicionar")

        print("2. Menu editar")

        print("3. Menu tempo")

        print("4. Sair")
        
        opcao = input("Escolha uma opção: ").strip()
        if opcao  == '1':
            limpar_tela()
            menu_adicionar()
        elif opcao  == '2':
            limpar_tela()
            menu_editar()
        elif opcao == '3':
            limpar_tela()
            menu_tempo()
        elif opcao == '4':
            limpar_tela()
            print("Saindo...")
            break

def menu_adicionar():
    print("as")

def menu_editar():
    pass

def menu_tempo():
    pass
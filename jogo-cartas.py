import random

# --- Classes de Jogo ---

class Carta:
    """Representa uma carta com nome, ataque e defesa."""
    def __init__(self, nome, ataque, defesa):
        self.nome = nome
        self.ataque = ataque
        self.defesa = defesa

    def __str__(self):
        return f"{self.nome} (ATK: {self.ataque}, DEF: {self.defesa})"

class Baralho:
    """Gerencia as cartas do baralho: criação, embaralhamento e compra."""
    def __init__(self):
        self.cartas = []
        self.criar_baralho()
        self.embaralhar()

    def criar_baralho(self):
        # Exemplo de 16 cartas para o baralho
        nomes_cartas = ["Dragão Flamejante", "Guerreiro Sombrio", "Feiticeira do Vento", "Golem de Pedra",
                        "Elfo da Floresta", "Anjo da Luz", "Vampiro Noturno", "Troll da Montanha",
                        "Dragão de Gelo", "Guerreiro da Luz", "Sereia das Profundezas", "Elemental do Fogo",
                        "Elemental da Terra", "Minotauro Furioso", "Aranha Venenosa", "Dragão Negro"]
        for nome in nomes_cartas:
            ataque = random.randint(100, 1000)
            defesa = random.randint(100, 1000)
            self.cartas.append(Carta(nome, ataque, defesa))

    def embaralhar(self):
        random.shuffle(self.cartas)

    def comprar_carta(self):
        if self.cartas:
            return self.cartas.pop()
        return None

class Jogador:
    """Representa o jogador e a IA, com pontos de vida, mão e cartas em campo."""
    def __init__(self, nome, tipo="humano"):
        self.nome = nome
        self.pontos_vida = 2000
        self.mao = []
        self.campo = [None] * 16  # Grade de 16x16, para simplificar usamos uma lista de 16
        self.tipo = tipo

    def mostrar_mao(self):
        print(f"Mão de {self.nome}:")
        for i, carta in enumerate(self.mao):
            print(f"[{i+1}] {carta}")

    def mostrar_campo(self):
        print(f"Campo de {self.nome}:")
        campo_str = ["-"] * 16
        for i, carta in enumerate(self.campo):
            if carta:
                campo_str[i] = str(carta.ataque)
        print(" ".join(campo_str))

    def jogar_carta(self, carta, posicao):
        if self.campo[posicao] is None:
            self.campo[posicao] = carta
            self.mao.remove(carta)
            print(f"{self.nome} joga {carta.nome} na posição {posicao+1}.")
            return True
        print("Posição já ocupada!")
        return False

# --- Lógica do Jogo ---

def ia_joga(jogador_ia, jogador_oponente):
    """Lógica de IA simples: joga a primeira carta em uma posição vazia."""
    print(f"\nTurno da IA: {jogador_ia.nome}")
    
    # Lógica de ataque
    if any(jogador_ia.campo) and any(jogador_oponente.campo):
        # A IA ataca com a primeira carta no campo, se houver uma
        carta_ia = next((carta for carta in jogador_ia.campo if carta), None)
        carta_oponente = next((carta for carta in jogador_oponente.campo if carta), None)
        
        if carta_ia and carta_oponente:
            if carta_ia.ataque > carta_oponente.defesa:
                print(f"Ataque da IA: {carta_ia.nome} ataca {carta_oponente.nome}!")
                jogador_oponente.campo[jogador_oponente.campo.index(carta_oponente)] = None
                print(f"Oponente perde {carta_ia.ataque - carta_oponente.defesa} pontos de vida!")
                jogador_oponente.pontos_vida -= (carta_ia.ataque - carta_oponente.defesa)
            else:
                print(f"Ataque sem sucesso de {carta_ia.nome} contra {carta_oponente.nome}.")
    
    # Lógica de jogar carta
    if jogador_ia.mao:
        carta_para_jogar = jogador_ia.mao[0]
        posicao_vazia = next((i for i, x in enumerate(jogador_ia.campo) if x is None), None)
        if posicao_vazia is not None:
            jogador_ia.jogar_carta(carta_para_jogar, posicao_vazia)
    
def main():
    print("Iniciando Jogo de Cartas")
    
    baralho = Baralho()
    jogador_humano = Jogador("Sora")
    jogador_ia = Jogador("Máquina", "ia")

    # Inicia o jogo com 5 cartas para cada jogador
    for _ in range(5):
        jogador_humano.mao.append(baralho.comprar_carta())
        jogador_ia.mao.append(baralho.comprar_carta())

    # --- Loop Principal do Jogo ---
    while jogador_humano.pontos_vida > 0 and jogador_ia.pontos_vida > 0:
        
        # Turno do Jogador Humano
        print("\n" + "="*30)
        print(f"Pontos de Vida: Sora ({jogador_humano.pontos_vida}) vs Máquina ({jogador_ia.pontos_vida})")
        
        # Fase de Compra
        nova_carta = baralho.comprar_carta()
        if nova_carta:
            jogador_humano.mao.append(nova_carta)
            print(f"Você compra uma nova carta: {nova_carta.nome}")
        
        # Fase de Jogo
        jogador_humano.mostrar_mao()
        jogador_humano.mostrar_campo()
        print(f"Campo da Máquina:")
        jogador_ia.mostrar_campo()
        
        try:
            escolha = input("\nEscolha a carta para jogar [1-5] ou 'a' para atacar, 'p' para passar o turno: ").lower()

            if escolha.isdigit():
                escolha_idx = int(escolha) - 1
                if 0 <= escolha_idx < len(jogador_humano.mao):
                    posicao = int(input("Escolha a posição no campo [1-16]: ")) - 1
                    if 0 <= posicao < 16:
                        jogador_humano.jogar_carta(jogador_humano.mao[escolha_idx], posicao)
                    else:
                        print("Posição inválida.")
                else:
                    print("Escolha de carta inválida.")
            elif escolha == 'a':
                if any(jogador_humano.campo) and any(jogador_ia.campo):
                    carta_humano_idx = int(input("Escolha a carta no seu campo para atacar [1-16]: ")) - 1
                    carta_oponente_idx = int(input("Escolha a carta do oponente para atacar [1-16]: ")) - 1

                    if jogador_humano.campo[carta_humano_idx] and jogador_ia.campo[carta_oponente_idx]:
                        carta_humano = jogador_humano.campo[carta_humano_idx]
                        carta_oponente = jogador_ia.campo[carta_oponente_idx]
                        if carta_humano.ataque > carta_oponente.defesa:
                            print(f"{carta_humano.nome} ataca {carta_oponente.nome}!")
                            jogador_ia.campo[carta_oponente_idx] = None
                            print(f"Máquina perde {carta_humano.ataque - carta_oponente.defesa} pontos de vida!")
                            jogador_ia.pontos_vida -= (carta_humano.ataque - carta_oponente.defesa)
                        else:
                            print(f"Ataque sem sucesso de {carta_humano.nome} contra {carta_oponente.nome}.")
                    else:
                        print("Carta(s) inválida(s) para o ataque.")
            elif escolha == 'p':
                print("Passando o turno.")
            else:
                print("Comando inválido.")

        except (ValueError, IndexError):
            print("Entrada inválida. Tente novamente.")

        # Turno da IA
        ia_joga(jogador_ia, jogador_humano)

    # Fim do jogo
    print("\n" + "="*30)
    if jogador_humano.pontos_vida <= 0:
        print("Fim de Jogo! A Máquina venceu.")
    else:
        print("Fim de Jogo! Você venceu!")

if __name__ == "__main__":
    main()
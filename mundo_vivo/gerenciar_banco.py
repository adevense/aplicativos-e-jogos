import json
import os

CAMINHO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO_JSON = os.path.join(CAMINHO_SCRIPT, 'banco.json')

def importar_dados():
    with open(CAMINHO_BANCO_JSON,'r', encoding='utf-8') as banco: # estou abrindo o arquivo json em modo de leitura(r)
        dados  = json.load(banco) # estou carregando o conteudo do arquivo json para um dicionario dados
    grupos = dados["grupos"] # estou pegando o conteudo do dicionario dados e atribuindo a variavel evento
    npcs = dados["npcs"] 
    players = dados["players"]
    locais = dados["locais"]
    return grupos,npcs,players,locais



def salvar_dados(grupos,npcs,players,locais):
    with open(CAMINHO_BANCO_JSON,'w', encoding='utf-8') as banco: # estou abrindo o arquivo json em modo de escrita(w)
        dados = {
            "grupos": grupos,
            "npcs": npcs,
            "players": players,
            "locais": locais
        }
        json.dump(dados, banco, indent=4, ensure_ascii=False) # estou salvando o conteudo do dicionario dados no arquivo json
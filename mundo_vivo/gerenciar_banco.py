import json

def importar_dados():
    with open('banco.json','r', encoding='utf-8') as banco: # estou abrindo o arquivo json em modo de leitura(r)
        dados  = json.load(banco) # estou carregando o conteudo do arquivo json para um dicionario dados
    eventos = dados["eventos"] # estou pegando o conteudo do dicionario dados e atribuindo a variavel evento
    participantes = dados["participantes"] 
    return eventos,participantes


def salvar_dados(eventos,participantes):
    with open('banco.json','w', encoding='utf-8') as banco: # estou abrindo o arquivo json em modo de escrita(w)
        json.dump({"eventos": eventos, "participantes": participantes}, banco, indent=4, ensure_ascii=False)

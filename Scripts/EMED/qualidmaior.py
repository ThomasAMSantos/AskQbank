import os
import json

def encontrar_maior_id(caminho_pasta):
    """
    Percorre a pasta e suas subpastas para encontrar arquivos JSON,
    retorna o maior valor do campo 'id' e o caminho do arquivo onde ele foi encontrado.
    """
    maior_id = -1
    caminho_maior_id = None
    arquivos_analisados = 0
    ids_encontrados = 0

    print(f"Buscando arquivos JSON em: {caminho_pasta}\n")

    # Verifica se o caminho da pasta existe
    if not os.path.isdir(caminho_pasta):
        print(f"Erro: O caminho '{caminho_pasta}' não existe ou não é uma pasta.")
        return

    # Percorre a pasta e todas as suas subpastas
    for raiz, _, arquivos in os.walk(caminho_pasta):
        for nome_arquivo in arquivos:
            # Verifica se o arquivo é um JSON
            if nome_arquivo.endswith('.json'):
                caminho_arquivo = os.path.join(raiz, nome_arquivo)
                print(f"Analisando arquivo: {caminho_arquivo}")
                arquivos_analisados += 1
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        # Carrega o conteúdo do JSON
                        data = json.load(f)

                        # Verifica se o conteúdo é uma lista e encontra o maior 'id'
                        if isinstance(data, list):
                            for item in data:
                                if 'id' in item and isinstance(item['id'], (int, float)):
                                    id_atual = int(item['id'])
                                    if id_atual > maior_id:
                                        maior_id = id_atual
                                        caminho_maior_id = caminho_arquivo
                                    ids_encontrados += 1
                        else:
                            print(f"Aviso: O conteúdo do arquivo {nome_arquivo} não é uma lista. Ignorando.")

                except json.JSONDecodeError:
                    print(f"Erro: O arquivo {caminho_arquivo} não é um JSON válido. Ignorando.")
                except KeyError:
                    print(f"Aviso: O campo 'id' não foi encontrado em um item do arquivo {caminho_arquivo}. Ignorando.")
                except Exception as e:
                    print(f"Ocorreu um erro inesperado ao processar {caminho_arquivo}: {e}")

    print("\n--- Resultados ---")
    print(f"Total de arquivos JSON analisados: {arquivos_analisados}")
    print(f"Total de 'id's válidos encontrados: {ids_encontrados}")

    if maior_id > -1:
        print(f"O maior 'id' encontrado é: {maior_id}")
        print(f"Este 'id' foi encontrado no arquivo: {caminho_maior_id}")
    else:
        print("Nenhum 'id' válido foi encontrado nos arquivos JSON especificados.")


# Solicita ao usuário o caminho da pasta
pasta_para_buscar = input("Por favor, digite o caminho da pasta a ser buscada: ")

# Chama a função com o caminho fornecido pelo usuário
encontrar_maior_id(pasta_para_buscar)
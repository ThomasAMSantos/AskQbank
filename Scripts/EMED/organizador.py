import re
import json
from pathlib import Path
import os

# ==========================
# CONSOLIDAR ARQUIVOS JSON
# ==========================
def consolidar_jsons(pasta_raiz):
    print("\n--- Iniciando a consolidação dos arquivos JSON ---")

    arquivos_json_encontrados = {}
    for json_file in Path(pasta_raiz).rglob("*.json"):
        nome_sem_ext = json_file.stem
        pasta_do_arquivo = json_file.parent

        # Usamos regex para encontrar o nome base e o número
        match = re.match(r"^(.*?)(?:(\d+))?$", nome_sem_ext)
        if match:
            nome_base = match.group(1)
            # Cria uma chave única para o grupo (nome base + pasta)
            chave_grupo = f"{nome_base}_{pasta_do_arquivo}"

            if chave_grupo not in arquivos_json_encontrados:
                arquivos_json_encontrados[chave_grupo] = []
            arquivos_json_encontrados[chave_grupo].append(json_file)

    # Percorre os grupos e consolida os arquivos
    for chave, lista_arquivos in arquivos_json_encontrados.items():
        if len(lista_arquivos) > 1:
            # Encontra o arquivo principal (sem número ou com 1)
            arquivo_principal = None
            arquivos_para_deletar = []
            
            # Ordena a lista de arquivos para garantir que o principal seja encontrado primeiro
            lista_arquivos.sort(key=lambda x: (x.stem.rstrip('1').lower(), int(re.search(r'\d+', x.name).group() if re.search(r'\d+', x.name) else 0)))
            
            for arq in lista_arquivos:
                nome_arq = arq.stem
                # Procura por arquivos sem número ou com o número 1
                if re.match(r"^[a-zA-Z]+$", nome_arq) or nome_arq.endswith("1"):
                    # Se já encontrou um, os próximos são para deletar
                    if arquivo_principal:
                        arquivos_para_deletar.append(arq)
                    else:
                        arquivo_principal = arq
                else:
                    arquivos_para_deletar.append(arq)
            
            # Se não encontrou um principal, usa o primeiro da lista
            if arquivo_principal is None:
                arquivo_principal = lista_arquivos[0]
                arquivos_para_deletar = lista_arquivos[1:]

            # Renomeia se o principal terminar em '1'
            if arquivo_principal.stem.endswith("1"):
                novo_nome_principal = arquivo_principal.parent / (arquivo_principal.stem[:-1] + ".json")
                os.rename(arquivo_principal, novo_nome_principal)
                print(f"🔄 Renomeado {arquivo_principal.name} para {novo_nome_principal.name}")
                # Atualiza a referência para o novo nome do arquivo
                arquivo_principal = novo_nome_principal

            # Lê o conteúdo de todos os arquivos do grupo
            conteudo_consolidado = []
            # Usa a lista original para garantir que todos os arquivos são lidos
            for arq in lista_arquivos:
                # Se o arquivo foi renomeado e está sendo lido, use o novo nome
                if arq.stem.endswith("1"):
                    caminho_arquivo_correto = arq.parent / (arq.stem[:-1] + ".json")
                else:
                    caminho_arquivo_correto = arq
                
                try:
                    with open(caminho_arquivo_correto, "r", encoding="utf-8") as f:
                        conteudo = json.load(f)
                        conteudo_consolidado.extend(conteudo)
                except json.JSONDecodeError:
                    print(f"⚠️ Erro ao ler JSON em {caminho_arquivo_correto.name}. Ignorando...")
                except FileNotFoundError:
                    # Se já deletou, apenas ignora
                    print(f"⚠️ Arquivo {caminho_arquivo_correto.name} já foi movido/deletado. Ignorando...")
            
            # Escreve o conteúdo consolidado no arquivo principal
            with open(arquivo_principal, "w", encoding="utf-8") as f:
                json.dump(conteudo_consolidado, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Consolidado {len(arquivos_para_deletar) + 1} arquivos em {arquivo_principal.name}")

            # Deleta os arquivos extras
            for arq_del in arquivos_para_deletar:
                os.remove(arq_del)
                print(f"🗑️ Deletado arquivo duplicado: {arq_del.name}")

    print("Finalizado com sucesso!")

# ==========================
# EXECUÇÃO DO SCRIPT
# ==========================
if __name__ == "__main__":
    pasta_raiz = input("Digite o caminho da pasta raiz com os arquivos JSON: ").strip()
    if pasta_raiz:
        consolidar_jsons(pasta_raiz)
    else:
        print("Caminho da pasta inválido. Por favor, reinicie e forneça um caminho válido.")
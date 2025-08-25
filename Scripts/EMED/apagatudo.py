import os

# === Caminho da pasta raiz ===
pasta_raiz = "/home/thomas/Documentos/Scrips do mal/Questões"

# Percorre a pasta raiz e todas as subpastas
for root, dirs, files in os.walk(pasta_raiz):
    for file in files:
        if file.lower().endswith(".pdf"):
            caminho_pdf = os.path.join(root, file)
            try:
                os.remove(caminho_pdf)
                print(f"Apagado: {caminho_pdf}")
            except Exception as e:
                print(f"Erro ao apagar {caminho_pdf}: {e}")

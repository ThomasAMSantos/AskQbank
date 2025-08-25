import pdfplumber
import re
import json
from pathlib import Path

# ==========================
# PERGUNTAR ID INICIAL
# ==========================
try:
    id_inicial = int(input("Digite o ID inicial para a primeira questão: "))
except ValueError:
    print("Entrada inválida. Usando ID inicial 1 por padrão.")
    id_inicial = 1

contador_id = id_inicial

# ==========================
# FUNÇÃO AUXILIAR - Separar tags
# ==========================
def separar_tags(raw_tags: str):
    if not raw_tags:
        return []
    tags = re.findall(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+[a-záéíóúâêôãõç]+)*", raw_tags)
    return tags

# ==========================
# PROCESSAR UM PDF
# ==========================
def processar_pdf(caminho_pdf, contador_id):
    questoes = []

    with pdfplumber.open(caminho_pdf) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto += (pagina.extract_text() or "") + "\n"

        # ==========================
        # PEGAR GABARITO (últimas páginas)
        # ==========================
        gabarito_texto = ""
        for p in pdf.pages[-5:]:
            gabarito_texto += (p.extract_text() or "") + "\n"

    # Extrair pares (número da questão, letra)
    gab_pairs = re.findall(r"(\d{1,3})\s*([A-E])", gabarito_texto)
    gabarito = {int(n): alt for n, alt in gab_pairs}

    # ==========================
    # PEGAR QUESTÕES
    # ==========================
    padrao = re.compile(
        r"Quest(ão|ao)\s+(\d+)(.*?)\n(.*?)(?=(?:Quest(ão|ao)\s+\d+|$))",
        re.DOTALL | re.IGNORECASE
    )

    # Padrão regex para remover comentários
    padrao_comentario = re.compile(r"Essa questão possui comentário do professor no site \d+")

    for match in padrao.finditer(texto):
        raw_tags = match.group(3).strip()
        enunciado_e_alts = match.group(4).strip()

        tags = []  # Mantém vazio

        partes = re.split(r"\n([A-E])[\)\.\s]", enunciado_e_alts)

        if len(partes) > 1:
            enunciado = partes[0].replace('\n', ' ').strip()
            alternativas = []
            for i in range(1, len(partes), 2):
                letra = partes[i][0]
                texto_alt_raw = partes[i+1] if (i+1) < len(partes) else ""
                texto_alt_limpo = re.sub(padrao_comentario, '', texto_alt_raw)
                texto_alt = texto_alt_limpo.replace('\n', ' ').strip()
                alternativas.append({"letra": letra, "texto": texto_alt})
        else:
            enunciado = enunciado_e_alts.replace('\n', ' ').strip()
            alternativas = []

        questoes.append({
            "id": contador_id,
            "tags": tags,
            "enunciado": enunciado,
            "alternativas": alternativas,
            "resposta_correta": gabarito.get(int(match.group(2)))
        })

        contador_id += 1

    return questoes, contador_id


# ==========================
# SELECIONAR VÁRIAS PASTAS
# ==========================
pasta_raiz = input("Digite o caminho da pasta raiz: ").strip()

# Pega todas as subpastas dentro da pasta raiz
subpastas = [p for p in Path(pasta_raiz).rglob("*") if p.is_dir()]

for pasta in subpastas:
    for pdf_file in pasta.glob("*.pdf"):
        print(f"Processando: {pdf_file}")
        questoes_pdf, contador_id = processar_pdf(pdf_file, contador_id)

        if questoes_pdf:
            caminho_json = pdf_file.with_suffix(".json")  # mesmo nome do PDF
            with open(caminho_json, "w", encoding="utf-8") as f:
                json.dump(questoes_pdf, f, ensure_ascii=False, indent=2)
            print(f"✅ Salvo {len(questoes_pdf)} questões em {caminho_json}")

print("Finalizado com sucesso!")

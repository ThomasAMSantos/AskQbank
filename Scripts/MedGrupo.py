import fitz  # PyMuPDF
import json
import re
import os

def extract_questions_from_pdf(pdf_path, start_id=None):
    """
    Extrai questões e respostas de um PDF.

    Args:
        pdf_path (str): O caminho para o arquivo PDF.
        start_id (int, optional): O ID da questão para começar.

    Returns:
        list: Uma lista de dicionários, cada um representando uma questão.
    """
    questions = []
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Erro ao ler o PDF {pdf_path}: {e}")
        return []

    # O texto do PDF é uma string contínua, vamos dividi-la por ID de questão.
    # O padrão para encontrar uma questão é um ID seguido de ")". Ex: "120757)"
    # E vamos capturar o texto do enunciado e alternativas.
    
    # Adiciona um marcador para o final do arquivo para garantir que a última questão seja processada.
    text += "\n[FINAL_DO_DOCUMENTO]" 
    
    # Encontra todos os blocos de questões
    matches = re.finditer(r'(\d+)\)\nEnunciado:(.*?)(?=\n\d+\)|\n\[FINAL_DO_DOCUMENTO\])', text, re.DOTALL)

    for match in matches:
        question_id_str = match.group(1).strip()
        enunciado_block = match.group(2).strip()

        question_id = int(question_id_str)

        # Se um ID inicial foi especificado, pular as questões anteriores
        if start_id and question_id < start_id:
            continue
            
        enunciado_part = ""
        alternatives_part = ""
        
        # Tenta separar o enunciado das alternativas
        alternatives_match = re.search(r'\n([A-E]\)\s*.*?(?=\n[A-E]\)\s*|\nComentário:|\nResposta certa|\nMedicina livre))', enunciado_block, re.DOTALL)
        
        if alternatives_match:
            # Se encontrou alternativas, o enunciado é o que vem antes
            enunciado_part = enunciado_block[:alternatives_match.start()].strip()
            alternatives_part = enunciado_block[alternatives_match.start():].strip()
        else:
            # Caso contrário, todo o bloco é o enunciado
            enunciado_part = enunciado_block.strip()
        
        # Extrai alternativas
        alternativas = []
        alt_matches = re.finditer(r'([A-E])\)\s*(.*?)(?=\n[A-E]\)\s*|\nComentário:|\nResposta certa|\nMedicina livre)', alternatives_part, re.DOTALL)
        
        for alt_match in alt_matches:
            letra = alt_match.group(1).strip()
            texto = alt_match.group(2).strip()
            alternativas.append({"letra": letra, "texto": texto})

        # Extrai a resposta correta do "Comentário" ou "Gabarito"
        resposta_correta = None
        comentario_match = re.search(r'Comentário:(.*?)(?=\n\d+)\)', text, re.DOTALL)
        if comentario_match:
            comentario_text = comentario_match.group(1)
            resposta_match = re.search(r'Resposta certa (\w)\.', comentario_text)
            if resposta_match:
                resposta_correta = resposta_match.group(1).upper()
            else:
                gabarito_match = re.search(r'Gabarito (?:Alternativa )?(\w)', comentario_text)
                if gabarito_match:
                    resposta_correta = gabarito_match.group(1).upper()

        question_data = {
            "id": question_id,
            "tags": [],
            "enunciado": enunciado_part,
            "alternativas": alternativas,
            "resposta_correta": resposta_correta
        }
        questions.append(question_data)

    return questions

def process_pdfs_in_directory(directory_path):
    """
    Processa todos os arquivos PDF em um diretório e salva o JSON.
    """
    if not os.path.exists(directory_path):
        print(f"O diretório '{directory_path}' não existe.")
        return

    start_id_input = input("Com qual ID você quer começar a extração? (Deixe em branco para começar do início): ")
    try:
        start_id = int(start_id_input) if start_id_input else None
    except ValueError:
        print("ID inválido. A extração começará do início.")
        start_id = None

    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            json_filename = os.path.splitext(filename)[0] + ".json"
            json_path = os.path.join(directory_path, json_filename)
            
            print(f"Processando {filename}...")
            questions_data = extract_questions_from_pdf(pdf_path, start_id)

            if questions_data:
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(questions_data, f, ensure_ascii=False, indent=4)
                    print(f"Dados salvos em {json_path}")
                except Exception as e:
                    print(f"Erro ao salvar o arquivo JSON para {filename}: {e}")
            else:
                print(f"Nenhuma questão encontrada ou erro ao processar {filename}.")

if __name__ == "__main__":
    # Coloque aqui o caminho para a pasta onde estão seus PDFs
    pdf_directory = "MedATB/MANUAL ANTIB"  # Altere este caminho
    process_pdfs_in_directory(pdf_directory)
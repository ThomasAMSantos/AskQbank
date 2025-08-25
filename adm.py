import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os

class JsonEditorApp:
    def __init__(self, root):
        """
        Inicializa a aplicação e a interface gráfica.
        """
        self.root = root
        self.root.title("Gerenciador de Questões JSON")
        self.root.geometry("800x600")

        self.loaded_data = {}  # Armazena os dados de todos os JSONs
        self.current_file = None # Armazena o caminho do arquivo JSON da questão encontrada

        # Configura a interface do usuário
        self._create_widgets()

    def _create_widgets(self):
        """
        Cria todos os widgets da interface gráfica.
        """
        # Seletor de diretório
        frame_dir = tk.Frame(self.root, pady=10)
        frame_dir.pack(fill=tk.X, padx=10)
        self.btn_load_dir = tk.Button(frame_dir, text="Selecionar Diretório", command=self.load_directory)
        self.btn_load_dir.pack(side=tk.LEFT, padx=(0, 10))
        self.dir_path_label = tk.Label(frame_dir, text="Nenhum diretório selecionado")
        self.dir_path_label.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Barra de pesquisa
        frame_search = tk.Frame(self.root, pady=10)
        frame_search.pack(fill=tk.X, padx=10)
        tk.Label(frame_search, text="Pesquisar (ID ou Frase):").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = tk.Entry(frame_search)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.btn_search = tk.Button(frame_search, text="Buscar", command=self.search_data)
        self.btn_search.pack(side=tk.LEFT)

        # Área de exibição e edição do JSON
        frame_editor = tk.Frame(self.root, pady=10)
        frame_editor.pack(fill=tk.BOTH, expand=True, padx=10)
        self.result_text = scrolledtext.ScrolledText(frame_editor, wrap=tk.WORD, font=("Courier New", 10), state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Botões de ação
        frame_actions = tk.Frame(self.root, pady=10)
        frame_actions.pack(fill=tk.X, padx=10)
        self.btn_edit = tk.Button(frame_actions, text="Habilitar Edição", command=self.enable_editing, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_save = tk.Button(frame_actions, text="Salvar Alterações", command=self.save_changes, state=tk.DISABLED)
        self.btn_save.pack(side=tk.LEFT)

    def load_directory(self):
        """
        Abre uma caixa de diálogo para o usuário selecionar um diretório,
        e então carrega todos os arquivos JSON encontrados.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.dir_path_label.config(text=f"Diretório: {directory}")
            self.loaded_data = {}  # Limpa os dados anteriores
            self.current_file = None
            found_count = 0
            
            # Percorre o diretório e seus subdiretórios
            for root, dirs, files in os.walk(directory):
                for file_name in files:
                    if file_name.endswith(".json"):
                        file_path = os.path.join(root, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                # Adiciona o conteúdo do arquivo com o caminho como chave
                                self.loaded_data[file_path] = data
                                found_count += 1
                        except (json.JSONDecodeError, IOError) as e:
                            print(f"Erro ao ler o arquivo {file_path}: {e}")

            if found_count > 0:
                messagebox.showinfo("Sucesso", f"{found_count} arquivo(s) JSON carregado(s).")
            else:
                messagebox.showwarning("Aviso", "Nenhum arquivo JSON encontrado no diretório selecionado.")
            
            # Desabilita botões de edição até que uma pesquisa seja feita
            self.result_text.config(state=tk.DISABLED)
            self.btn_edit.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.DISABLED)

    def search_data(self):
        """
        Busca uma questão por ID ou frase nos dados carregados.
        """
        query = self.search_entry.get().strip()
        self.current_file = None
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.btn_edit.config(state=tk.DISABLED)
        self.btn_save.config(state=tk.DISABLED)

        if not self.loaded_data:
            messagebox.showwarning("Aviso", "Por favor, carregue um diretório primeiro.")
            return

        found_item = None
        found_file = None

        # Tenta buscar por ID
        try:
            query_id = int(query)
            for file_path, data_list in self.loaded_data.items():
                for item in data_list:
                    if isinstance(item, dict) and item.get("id") == query_id:
                        found_item = item
                        found_file = file_path
                        break
                if found_item:
                    break
        except ValueError:
            # Se não for um ID, busca por uma frase no enunciado
            query_lower = query.lower()
            for file_path, data_list in self.loaded_data.items():
                for item in data_list:
                    if isinstance(item, dict) and 'enunciado' in item and query_lower in item['enunciado'].lower():
                        found_item = item
                        found_file = file_path
                        break
                if found_item:
                    break

        if found_item:
            self.current_file = found_file
            self.display_data(found_item)
            self.btn_edit.config(state=tk.NORMAL)
            messagebox.showinfo("Sucesso", "Questão encontrada!")
        else:
            messagebox.showinfo("Não Encontrado", "Nenhuma questão correspondente encontrada.")

    def display_data(self, data):
        """
        Exibe os dados formatados na área de texto.
        """
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        try:
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
            self.result_text.insert(tk.END, formatted_data)
        except (TypeError, ValueError) as e:
            self.result_text.insert(tk.END, f"Erro ao formatar os dados: {e}")
        self.result_text.config(state=tk.DISABLED)

    def enable_editing(self):
        """
        Habilita a área de texto para edição.
        """
        self.result_text.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.NORMAL)
        messagebox.showinfo("Edição Ativada", "Você pode agora editar o conteúdo. Clique em 'Salvar Alterações' quando terminar.")

    def save_changes(self):
        """
        Salva as alterações feitas no conteúdo do JSON.
        
        Melhoria no tratamento de erros:
        - Exibe uma mensagem mais clara para JSON mal formatado, orientando o usuário.
        - Separa a captura de diferentes tipos de erros para mensagens mais específicas.
        """
        if not self.current_file:
            messagebox.showwarning("Aviso", "Nenhuma questão para salvar. Por favor, faça uma busca primeiro.")
            return

        try:
            # Pega o conteúdo editado
            edited_content = self.result_text.get("1.0", tk.END)
            edited_json = json.loads(edited_content)
            
            # Carrega a lista original do arquivo
            with open(self.current_file, 'r', encoding='utf-8') as f:
                original_data_list = json.load(f)

            # Encontra e substitui o item editado na lista
            found_and_updated = False
            for i, item in enumerate(original_data_list):
                if isinstance(item, dict) and item.get("id") == edited_json.get("id"):
                    original_data_list[i] = edited_json
                    found_and_updated = True
                    break

            if found_and_updated:
                # Escreve a lista atualizada de volta no arquivo
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    json.dump(original_data_list, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
                self.result_text.config(state=tk.DISABLED)
                self.btn_save.config(state=tk.DISABLED)
            else:
                messagebox.showwarning("Erro", "Não foi possível encontrar a questão original para atualizar.")

        except json.JSONDecodeError as e:
            messagebox.showerror("Erro de Formato do JSON", 
                                 f"O conteúdo que você tentou salvar não é um JSON válido. Por favor, verifique a sintaxe, especialmente as vírgulas, chaves e colchetes.\n\nDetalhes do erro: {e}")
        except IOError as e:
            messagebox.showerror("Erro de Arquivo", f"Ocorreu um erro ao salvar o arquivo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonEditorApp(root)
    root.mainloop()

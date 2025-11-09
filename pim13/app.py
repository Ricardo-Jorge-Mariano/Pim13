import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import os

# --- 1. A Ponte (ctypes) ---

# Define a estrutura em Python que "espelha" a struct do C
class Aluno(ctypes.Structure):
    _fields_ = [
        ("nome", ctypes.c_char * 100),
        ("np1", ctypes.c_float),
        ("np2", ctypes.c_float),
        ("pim", ctypes.c_float),
        ("faltas", ctypes.c_int),
        ("media_final", ctypes.c_float),
        ("status", ctypes.c_char * 20)
    ]

# Carrega a biblioteca C (use .dll ou .so dependendo do seu SO)
lib_c_path = "./database.dll"  
if not os.path.exists(lib_c_path):
    messagebox.showerror("Erro Crítico", f"Biblioteca C não encontrada em {lib_c_path}\nCompile o 'database.c' primeiro!")
    exit()

lib_c = ctypes.CDLL(lib_c_path)

# Define os tipos de argumentos e retorno (BOA PRÁTICA)
lib_c.salvarAluno.argtypes = [Aluno]
lib_c.salvarAluno.restype = None

# Para carregar, definimos que o 1º arg é um ponteiro para Aluno
lib_c.carregarAlunos.argtypes = [ctypes.POINTER(Aluno), ctypes.c_int]
lib_c.carregarAlunos.restype = ctypes.c_int

# --- 2. A Lógica de Cálculo (Python) ---

def calcular_status(np1, np2, pim, faltas):
    if faltas >= 15:
        media = 0.0  # Não importa a média, está reprovado
        status = "Reprovado (Faltas)"
        return media, status

    # Média final = (NP1*4 + NP2*4 + PIM*2) / 10
    media = ((np1 * 4) + (np2 * 4) + (pim * 2)) / 10.0
    
    if media >= 7.0:
        status = "Aprovado"
    else:
        status = "Exame"
        
    return media, status

# --- 3. A Aplicação Tkinter ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Cadastro Acadêmico")
        self.geometry("800x600")
        
        # --- Frame de Inputs ---
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill="x", side="top")

        # Labels e Entradas (Nome, NP1, NP2, PIM, Faltas)
        ttk.Label(input_frame, text="Nome:").grid(row=0, column=0, sticky="w", padx=5)
        self.entry_nome = ttk.Entry(input_frame, width=40)
        self.entry_nome.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(input_frame, text="NP1:").grid(row=1, column=0, sticky="w", padx=5)
        self.entry_np1 = ttk.Entry(input_frame, width=10)
        self.entry_np1.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(input_frame, text="NP2:").grid(row=1, column=2, sticky="w", padx=5)
        self.entry_np2 = ttk.Entry(input_frame, width=10)
        self.entry_np2.grid(row=1, column=3, sticky="w", padx=5)

        ttk.Label(input_frame, text="PIM:").grid(row=2, column=0, sticky="w", padx=5)
        self.entry_pim = ttk.Entry(input_frame, width=10)
        self.entry_pim.grid(row=2, column=1, sticky="w", padx=5)
        
        ttk.Label(input_frame, text="Faltas:").grid(row=2, column=2, sticky="w", padx=5)
        self.entry_faltas = ttk.Entry(input_frame, width=10)
        self.entry_faltas.grid(row=2, column=3, sticky="w", padx=5)

        # Botão Salvar
        self.btn_salvar = ttk.Button(input_frame, text="Salvar Aluno", command=self.salvar_aluno)
        self.btn_salvar.grid(row=3, column=0, columnspan=4, pady=10)

        # --- Frame de Exibição (Tabela) ---
        display_frame = ttk.Frame(self, padding="10")
        display_frame.pack(fill="both", expand=True)
        
        cols = ('nome', 'np1', 'np2', 'pim', 'faltas', 'media', 'status')
        self.tree = ttk.Treeview(display_frame, columns=cols, show='headings')
        
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
        
        self.tree.pack(fill="both", expand=True)
        
        # Carrega os dados iniciais
        self.atualizar_tabela()

    def salvar_aluno(self):
        try:
            # 1. Obter dados do formulário
            nome = self.entry_nome.get()
            np1 = float(self.entry_np1.get())
            np2 = float(self.entry_np2.get())
            pim = float(self.entry_pim.get())
            faltas = int(self.entry_faltas.get())
            
            if not nome:
                messagebox.showwarning("Erro", "O nome não pode estar vazio.")
                return

            # 2. Calcular Média e Status (Lógica Python)
            media, status = calcular_status(np1, np2, pim, faltas)
            
            # 3. Preparar o objeto C (ctypes)
            aluno_c = Aluno()
            aluno_c.nome = nome.encode('utf-8') # Converte string Python -> bytes
            aluno_c.np1 = np1
            aluno_c.np2 = np2
            aluno_c.pim = pim
            aluno_c.faltas = faltas
            aluno_c.media_final = media
            aluno_c.status = status.encode('utf-8')

            # 4. Chamar a função C para salvar
            lib_c.salvarAluno(aluno_c)
            
            messagebox.showinfo("Sucesso", f"Aluno {nome} salvo!")
            self.limpar_campos()
            self.atualizar_tabela()

        except ValueError:
            messagebox.showerror("Erro de Entrada", "Verifique se as notas e faltas são números válidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def atualizar_tabela(self):
        # Limpa a tabela antiga
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Prepara um buffer (array) C em memória Python
        MAX_ALUNOS = 256 # Limite de quantos alunos podemos carregar de uma vez
        AlunoArray = Aluno * MAX_ALUNOS
        buffer_c = AlunoArray()

        # Chama a função C para preencher o buffer
        # A função retorna quantos alunos foram realmente lidos
        num_alunos = lib_c.carregarAlunos(buffer_c, MAX_ALUNOS)

        # Adiciona os alunos lidos na tabela (TreeView)
        for i in range(num_alunos):
            aluno = buffer_c[i]
            self.tree.insert("", "end", values=(
                aluno.nome.decode('utf-8'), # Converte bytes -> string Python
                f"{aluno.np1:.1f}",
                f"{aluno.np2:.1f}",
                f"{aluno.pim:.1f}",
                aluno.faltas,
                f"{aluno.media_final:.2f}",
                aluno.status.decode('utf-8')
            ))

    def limpar_campos(self):
        self.entry_nome.delete(0, 'end')
        self.entry_np1.delete(0, 'end')
        self.entry_np2.delete(0, 'end')
        self.entry_pim.delete(0, 'end')
        self.entry_faltas.delete(0, 'end')


if __name__ == "__main__":
    app = App()
    app.mainloop()
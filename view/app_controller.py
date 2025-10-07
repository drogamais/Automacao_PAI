# Ficheiro: view/app_controller.py
import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime
from .main_view import MainView
from .search_view import SearchView
from controller import automation

class AppController:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Relatórios PAI")
        self.root.geometry("500x450")
        
        self.stop_requested = False
        self.automation_thread = None
        self.search_window = None

        self.is_batch_running = False

        self.main_view = MainView(root, self)
        self.main_view.pack(fill=tk.BOTH, expand=True)

    def _validate_and_get_dates(self):
        """Valida os campos de data e retorna um dicionário ou None."""
        try:
            ano_ini_str = self.main_view.ano_inicial_entry.get()
            ano_fim_str = self.main_view.ano_final_entry.get()
            mes_ini_str = self.main_view.mes_inicial_combo.get()
            mes_fim_str = self.main_view.mes_final_combo.get()

            if not (ano_ini_str.isdigit() and ano_fim_str.isdigit()):
                messagebox.showerror("Entrada Inválida", "Os anos devem ser números válidos.")
                return None

            ano_ini = int(ano_ini_str)
            ano_fim = int(ano_fim_str)
            
            # Converte nome do mês para número
            mes_ini = self.main_view.meses.index(mes_ini_str) + 1
            mes_fim = self.main_view.meses.index(mes_fim_str) + 1

            data_inicio = datetime(ano_ini, mes_ini, 1)
            data_fim = datetime(ano_fim, mes_fim, 1)

            if data_inicio > data_fim:
                messagebox.showerror("Data Inválida", "O período inicial não pode ser maior que o período final.")
                return None
            
            # Calcula a diferença em meses
            diff_meses = (data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month)

            if diff_meses >= 24:
                messagebox.showerror("Intervalo Excedido", "O intervalo entre as datas não pode ser maior que dois anos.")
                return None

            return {
                "ano_inicial": ano_ini_str,
                "mes_inicial": mes_ini_str,
                "ano_final": ano_fim_str,
                "mes_final": mes_fim_str
            }

        except (ValueError, IndexError):
            messagebox.showerror("Erro de Data", "Por favor, verifique se os meses e anos estão corretos.")
            return None

    def _start_automation_thread(self, target_func, *args):
        self.stop_requested = False
        self._set_buttons_state(tk.DISABLED)
        
        all_args = args + (self.main_view.debug_mode_var.get(),)
        
        self.automation_thread = threading.Thread(target=self._automation_wrapper, args=(target_func, all_args))
        self.automation_thread.start()
        
    def _automation_wrapper(self, target_func, args):
        try:
            target_func(*args)
            if not self.stop_requested:
                self.finalizar_automacao(sucesso=True, mensagem="Processo finalizado com sucesso!")
        except InterruptedError:
            self.finalizar_automacao(sucesso=False, mensagem="Operação interrompida pelo usuário.")
        except Exception as e:
            print(f"Erro fatal no workflow: {e}")
            if not self.stop_requested:
                self.finalizar_automacao(sucesso=False, mensagem=f"Erro fatal: {e}")

    def start_full_automation(self):
        loja = self.main_view.loja_numero_entry.get()
        if not loja.isdigit():
            messagebox.showerror("Entrada Inválida", "Número da loja deve ser preenchido corretamente.")
            return
        
        dates = self._validate_and_get_dates()
        if not dates:
            return

        self._start_automation_thread(automation.executar_workflow_completo, loja, dates["ano_inicial"], dates["mes_inicial"], dates["ano_final"], dates["mes_final"], self)

    def start_evolution_automation(self):
        loja = self.main_view.loja_numero_entry.get()
        if not loja.isdigit():
            messagebox.showerror("Entrada Inválida", "Número da loja deve ser preenchido corretamente.")
            return

        dates = self._validate_and_get_dates()
        if not dates:
            return

        self._start_automation_thread(automation.executar_workflow_evolucao, loja, dates["ano_inicial"], dates["mes_inicial"], dates["ano_final"], dates["mes_final"], self)

    def start_search(self):
        ano = self.search_window.search_ano_entry.get()
        if not ano.isdigit():
            messagebox.showerror("Entrada Inválida", "Ano deve ser preenchido corretamente.", parent=self.search_window)
            return
        self._start_automation_thread(automation.executar_workflow_busca, ano, self, self.search_window.update_results)

    def start_batch_automation(self):
        self.is_batch_running = True
        
        dates = self._validate_and_get_dates()
        if not dates:
            self.is_batch_running = False
            return
        
        lojas_selecionadas = []
        if self.search_window:
            for var, chk, info in self.search_window.check_vars:
                if var.get() and chk.cget("state") != tk.DISABLED:
                    lojas_selecionadas.append((chk, info))
        
        if not lojas_selecionadas:
            messagebox.showwarning("Nenhuma Loja", "Nenhuma loja nova foi selecionada para a automação.", parent=self.search_window)
            self.is_batch_running = False
            self._set_buttons_state(tk.NORMAL)
            return

        self._start_automation_thread(automation.executar_workflow_em_lote, lojas_selecionadas, dates["ano_inicial"], dates["mes_inicial"], dates["ano_final"], dates["mes_final"], self)

    def request_stop(self):
        if messagebox.askyesno("Confirmar Parada", "Tem certeza que deseja interromper a operação?"):
            self.atualizar_progresso(0, 100, "Parada solicitada... Finalizando...")
            self.stop_requested = True
            self._set_buttons_state(tk.DISABLED)

    def open_search_window(self):
        if self.search_window and self.search_window.winfo_exists():
            self.search_window.focus()
            return
        self.search_window = SearchView(self.root, self)

    def atualizar_progresso(self, valor, maximo, texto_status, is_search=False):
        if self.stop_requested:
            return
        self.root.after(0, self._do_update_progresso, valor, maximo, texto_status, is_search)

    def _do_update_progresso(self, valor, maximo, texto_status, is_search):
        if self.is_batch_running:
            target_label = self.main_view.status_label
            target_bar = self.main_view.progress_bar
        elif is_search and self.search_window and self.search_window.winfo_exists():
            target_label = self.search_window.search_status_label
            target_bar = self.search_window.search_progress_bar
        else:
            target_label = self.main_view.status_label
            target_bar = self.main_view.progress_bar
        
        target_label.config(text=texto_status)
        target_bar['maximum'] = maximo
        target_bar['value'] = valor

    def finalizar_automacao(self, sucesso=True, mensagem=""):
        self.is_batch_running = False
        self._set_buttons_state(tk.NORMAL)
        if sucesso:
            if mensagem: messagebox.showinfo("Sucesso", mensagem)
        else:
            if mensagem: messagebox.showerror("Erro", mensagem)

    def _set_buttons_state(self, state):
        self.main_view.start_button.config(state=state)
        self.main_view.evolution_button.config(state=state)
        
        stop_state = tk.NORMAL if state == tk.DISABLED else tk.DISABLED
        self.main_view.stop_button.config(state=stop_state)
        
        if self.search_window and self.search_window.winfo_exists():
            self.search_window.search_button.config(state=state)
            self.search_window.search_stop_button.config(state=stop_state)
            self.search_window.batch_button.config(state=state)

    def marcar_loja_como_concluida(self, chk_widget):
        if chk_widget and chk_widget.winfo_exists():
            for var, chk, info in self.search_window.check_vars:
                if chk is chk_widget:
                    var.set(False)
                    break
            chk_widget.config(text=chk_widget.cget("text") + " - Concluído!", state=tk.DISABLED)
            self.root.update_idletasks()
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datatypes import func, var, const, literal, clause, negate
from strategy import sos_resolution
from input import formalize_problem, parse_formalized_problem
from output import output_sequence, explain_solution_detailed

class LogicSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Нейро-Символический Решатель Логических Задач")
        self.root.geometry("900x700")
        
        # Переменные для управления потоком
        self.is_processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Для области ввода
        main_frame.rowconfigure(5, weight=3)  # Для области вывода (увеличили вес)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Нейро-Символический Решатель Логических Задач",
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Метка для ввода
        input_label = ttk.Label(main_frame, text="Введите логическую задачу:")
        input_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Поле ввода (немного уменьшили высоту)
        self.input_text = scrolledtext.ScrolledText(main_frame, height=5, width=80)
        self.input_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Кнопка отправки
        self.submit_button = ttk.Button(main_frame, 
                                       text="Решить задачу", 
                                       command=self.solve_problem)
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Область вывода (значительно увеличили высоту)
        output_label = ttk.Label(main_frame, text="Результат решения:")
        output_label.grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=50, width=80)  # Увеличили высоту
        self.output_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def solve_problem(self):
        """Запускает решение задачи в отдельном потоке"""
        if self.is_processing:
            return
            
        problem_text = self.input_text.get(1.0, tk.END).strip()
        if not problem_text:
            self.show_error("Пожалуйста, введите задачу")
            return
            
        # Блокируем интерфейс
        self.set_processing_state(True)
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.solve_problem_thread, args=(problem_text,))
        thread.daemon = True
        thread.start()
        
    def solve_problem_thread(self, problem_text):
        """Решение задачи в отдельном потоке"""
        try:
            self.update_status("Формализация задачи...")
            
            # Шаг 1: Формализация
            formalized = formalize_problem(problem_text)
            self.update_status("Парсинг формул...")
            
            # Шаг 2: Парсинг
            clauses = parse_formalized_problem(formalized)
            
            if len(clauses) < 2:
                self.show_result("❌ Ошибка: Недостаточно формул для доказательства")
                return
                
            self.update_status("Применение метода резолюций...")
            
            # Шаг 3: Резолюция
            premises = set(clauses[:-1])
            target = clauses[-1]
            result = sos_resolution(premises, target)
            
            if result and len(result.literals) == 0:
                self.update_status("Построение лога решения...")
                
                # Шаг 4: Логирование
                solution_log = output_sequence(result)
                
                self.update_status("Генерация объяснения...")
                
                # Шаг 5: Объяснение через LLM
                explanation = explain_solution_detailed(solution_log, problem_text)
                
                # Форматируем результат
                result_text = self.format_result(problem_text, formalized, clauses, solution_log, explanation)
                self.show_result(result_text)
                
            else:
                self.show_result("❌ Противоречие не найдено - теорема не доказана")
                
        except Exception as e:
            error_msg = f"❌ Ошибка при решении задачи: {str(e)}"
            self.show_result(error_msg)
        finally:
            self.set_processing_state(False)
            
    def format_result(self, problem_text, formalized, clauses, solution_log, explanation):
        """Форматирует результат для вывода"""
        result = "=" * 80 + "\n"
        result += "РЕЗУЛЬТАТ РЕШЕНИЯ\n"
        result += "=" * 80 + "\n\n"
        
        result += "📝 ИСХОДНАЯ ЗАДАЧА:\n"
        result += problem_text + "\n\n"
        
        result += "🔧 ФОРМАЛИЗОВАННЫЕ ФОРМУЛЫ:\n"
        result += formalized + "\n\n"
        
        result += "🧩 ПОЛУЧЕННЫЕ CLAUSES:\n"
        for i, cl in enumerate(clauses):
            result += f"{i+1}. {cl}\n"
        result += "\n"
        
        result += "🔍 ШАГИ ДОКАЗАТЕЛЬСТВА:\n"
        for step in solution_log:
            result += f"  {step}\n"
        result += "\n"
        
        result += "💡 ОБЪЯСНЕНИЕ:\n"
        result += explanation + "\n\n"
        
        result += "✅ ТЕОРЕМА ДОКАЗАНА!"
        
        return result
        
    def set_processing_state(self, processing):
        """Устанавливает состояние обработки"""
        self.is_processing = processing
        
        if processing:
            self.submit_button.config(state='disabled')
            self.status_var.set("Обработка запроса...")
            self.progress.start()
        else:
            self.submit_button.config(state='normal')
            self.status_var.set("Готов к работе")
            self.progress.stop()
            
    def update_status(self, message):
        """Обновляет статус (потокобезопасно)"""
        def update():
            self.status_var.set(message)
        self.root.after(0, update)
        
    def show_result(self, result_text):
        """Показывает результат (потокобезопасно)"""
        def show():
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, result_text)
            # Автопрокрутка в начало
            self.output_text.see(1.0)
        self.root.after(0, show)
        
    def show_error(self, error_msg):
        """Показывает ошибку"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, f"❌ {error_msg}")

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = LogicSolverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
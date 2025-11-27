import google.generativeai as genai

from datatypes import func, var, const, literal
from datatypes import clause, negate

# Улучшенная версия formalize_problem для лучшего формата вывода
def formalize_problem(problem_text):
    """Простая функция для формализации одной задачи"""

    genai.configure(api_key="")
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = """Ты преобразуешь логические задачи в формальные формулы. Следуй строгому формату:

Переменные: [список переменных через запятую]
Константы: [список констант через запятую]  
Литералы: [список предикатов через запятую]
Формулы: [список формул через точку с запятой]

ПРАВИЛА:
1. Используй только переменные: x, y, z, t
2. Формулы должны быть в КНФ: not Предикат(аргумент) v ДругойПредикат(аргумент)
3. Последняя формула - отрицание доказываемого утверждения
4. Используй только русские имена для предикатов и констант

Пример:
Задача: Сократ человек. Все люди смертны. Докажи, что Сократ смертен.
Вывод:
Переменные: x
Константы: Сократ
Литералы: Человек, Смертен
Формулы: Человек(Сократ), not Человек(x) v Смертен(x), not Смертен(Сократ)

Задача: Все кошки спят. Мурка — кошка. Докажи, что Мурка спит
Вывод:
Переменные: x
Константы: Мурка
Литералы: Кошка, Спит
Формулы: not Кошка(x) v Спит(x); Кошка(Мурка); not Спит(Мурка)

Теперь преобразуй следующую задачу:
"""
    prompt += problem_text
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Ошибка: {e}"

def parse_formalized_problem(formalized_text: str) -> list:
    """
    Парсит формализованную задачу и возвращает список clause'ов
    
    Args:
        formalized_text: Текст в формате:
            Переменные: x, y, z
            Константы: Петр, Иван, Сергей  
            Литералы: Сын, Наследует, Родитель
            Формулы: not Сын(x, y) v Наследует(x, y); not Сын(x, y) v Родитель(y); ...
    
    Returns:
        list: Список clause'ов, где последний элемент - целевое утверждение (с отрицанием)
    """
    try:
        # Разделяем текст на строки и очищаем
        lines = [line.strip() for line in formalized_text.split('\n') if line.strip()]
        
        # Инициализируем данные
        variables = []
        constants = []
        literals_list = []
        formulas_lines = []
        
        current_section = None
        
        # Парсим каждую строку
        for line in lines:
            if line.startswith('Переменные:'):
                current_section = 'variables'
                vars_str = line.replace('Переменные:', '').strip()
                variables = [v.strip() for v in vars_str.split(',') if v.strip()]
            elif line.startswith('Константы:'):
                current_section = 'constants'
                const_str = line.replace('Константы:', '').strip()
                constants = [c.strip() for c in const_str.split(',') if c.strip()]
            elif line.startswith('Литералы:'):
                current_section = 'literals'
                lit_str = line.replace('Литералы:', '').strip()
                literals_list = [l.strip() for l in lit_str.split(',') if l.strip()]
            elif line.startswith('Формулы:'):
                current_section = 'formulas'
                formulas_line = line.replace('Формулы:', '').strip()
                if formulas_line:
                    formulas_lines.append(formulas_line)
            elif current_section == 'formulas':
                formulas_lines.append(line)
        
        # Объединяем все строки формул и разделяем по разделителям
        all_formulas_text = ' '.join(formulas_lines)
        # Разделяем по ; или , или переносам строки
        formulas = []
        for separator in [';', ',', '\n']:
            if separator in all_formulas_text:
                formulas = [f.strip() for f in all_formulas_text.split(separator) if f.strip()]
                break
        else:
            # Если нет разделителей, берем всю строку как одну формулу
            formulas = [all_formulas_text] if all_formulas_text else []
        
        # Создаем объекты для переменных и констант
        var_objects = {name: var(name) for name in variables}
        const_objects = {name: const(name) for name in constants}
        
        clauses = []
        
        # Обрабатываем каждую формулу
        for formula in formulas:
            if not formula:
                continue
            
            # Разделяем формулу на литералы по ' v ' или ' ∨ '
            literal_parts = []
            if ' v ' in formula:
                literal_parts = [part.strip() for part in formula.split(' v ')]
            elif ' ∨ ' in formula:
                literal_parts = [part.strip() for part in formula.split(' ∨ ')]
            else:
                # Одиночный литерал
                literal_parts = [formula.strip()]
            
            literals_in_clause = []
            
            for part in literal_parts:
                if not part:
                    continue
                    
                # Определяем отрицание
                is_negative = False
                part_clean = part
                
                if part.startswith('not '):
                    is_negative = True
                    part_clean = part[4:].strip()
                elif part.startswith('¬'):
                    is_negative = True  
                    part_clean = part[1:].strip()
                
                # Парсим предикат и аргументы
                if '(' in part_clean and ')' in part_clean:
                    pred_start = part_clean.find('(')
                    pred_name = part_clean[:pred_start].strip()
                    args_str = part_clean[pred_start+1:part_clean.find(')')].strip()
                    
                    # Разделяем аргументы
                    args = [arg.strip() for arg in args_str.split(',')]
                    
                    # Создаем термы для аргументов
                    terms = []
                    for arg in args:
                        if arg in var_objects:
                            terms.append(var_objects[arg])
                        elif arg in const_objects:
                            terms.append(const_objects[arg])
                        else:
                            # Если аргумент не найден, создаем константу
                            const_objects[arg] = const(arg)
                            terms.append(const_objects[arg])
                    
                    # Создаем литерал
                    lit = literal(pred_name, *terms, negative=is_negative)
                    literals_in_clause.append(lit)
                else:
                    # Простой предикат без аргументов
                    pred_name = part_clean
                    lit = literal(pred_name, negative=is_negative)
                    literals_in_clause.append(lit)
            
            # Создаем clause из литералов
            if literals_in_clause:
                cl = clause(*literals_in_clause)
                clauses.append(cl)
        
        return clauses
        
    except Exception as e:
        print(f"Ошибка при парсинге формализованной задачи: {e}")
        import traceback
        traceback.print_exc()
        return []
    

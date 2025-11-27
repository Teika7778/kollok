import google.generativeai as genai
from datatypes import clause


def output_sequence(cl: clause) -> list:
    """
    Рекурсивно строит лог решения по дереву резолюции
    
    Args:
        cl: Корневой clause (обычно пустой дизъюнкт □)
    
    Returns:
        list: Список шагов решения в формате для LLM
    """
    steps = []
    
    def traverse_tree(node: clause, step_num: int) -> int:
        """
        Рекурсивный обход дерева резолюции
        
        Args:
            node: Текущий clause
            step_num: Номер текущего шага
            
        Returns:
            int: Следующий номер шага
        """
        # Если у clause есть родители, значит это результат резолюции
        if node.parent1 is not None and node.parent2 is not None:
            # Сначала обрабатываем родителей (глубокий обход)
            step_num = traverse_tree(node.parent1, step_num)
            step_num = traverse_tree(node.parent2, step_num)
            
            # Формируем описание шага
            step_info = {
                'step': step_num,
                'parent1': str(node.parent1),
                'parent2': str(node.parent2),
                'result': str(node),
                'substitution': str(node.sub) if node.sub else None
            }
            
            # Определяем тип шага
            if len(node.literals) == 0:
                step_info['type'] = 'contradiction'
                step_info['description'] = f"Резолюция {node.parent1} и {node.parent2} -> Противоречие □"
            else:
                step_info['type'] = 'resolution'
                if node.sub:
                    step_info['description'] = f"Унификация {node.sub} в {node.parent1} и {node.parent2} -> {node}"
                else:
                    step_info['description'] = f"Резолюция {node.parent1} и {node.parent2} -> {node}"
            
            steps.append(step_info)
            step_num += 1
        
        return step_num
    
    # Запускаем обход дерева
    traverse_tree(cl, 1)
    
    # Сортируем шаги по номеру (они добавляются в порядке обработки)
    steps.sort(key=lambda x: x['step'])
    
    # Форматируем вывод для LLM
    formatted_steps = []
    for step in steps:
        if step['type'] == 'contradiction':
            formatted_steps.append(f"Шаг {step['step']}: Резолюция {step['parent1']} и {step['parent2']} -> Противоречие □")
        else:
            if step['substitution']:
                formatted_steps.append(f"Шаг {step['step']}: Унификация {step['substitution']} в {step['parent1']} и {step['parent2']} -> {step['result']}")
            else:
                formatted_steps.append(f"Шаг {step['step']}: Резолюция {step['parent1']} и {step['parent2']} -> {step['result']}")
    
    return formatted_steps


def explain_solution_detailed(solution_log: list, original_formulas: list = None) -> str:
    """
    Более детальная версия с информацией об исходных формулах
    """
    try:
        genai.configure(api_key="")
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Подготовка информации об исходных формулах
        formulas_info = ""
        if original_formulas:
            formulas_info = "Исходные утверждения:\\n" + "\\n".join([f"- {formula}" for formula in original_formulas])
        
        prompt = f"""
Ты — эксперт по математической логике. Разъясни логическое доказательство:

{formulas_info}

Последовательность логических шагов:
{'\\n'.join(solution_log)}

Проанализируй доказательство и объясни его, постарайся максимально коротко и емко.

В твоем ответе должно быть только объяснение. Постарайся сделать его максимально
 понятным человеку. Не стоит объяснять  подробно
каждый шаг. Следует объяснить и показать общую картину. Например:
 [Шаг 1: Унификация x/Сократ в ¬Человек(x) ∨ Смертен(x). Шаг 2: Резолюция с Человек(Сократ) -> Смертен(Сократ). Шаг 3: 
 Резолюция Смертен(Сократ) и ¬Смертен(Сократ) -> Противоречие.]
 Объяснение:
 У нас есть общее правило: 'Если кто-то является человеком, то он смертен'. Мы применяем это правило к Сократу,
   подставляя его вместо переменной 'x'. Поскольку нам также известно, что Сократ — человек, мы приходим к выводу,
     что Сократ смертен. Но это противоречит нашему исходному предположению, что Сократ не является смертным. Это 
     противоречие доказывает, что наше предположение было ложным, а значит, Сократ действительно смертен."
"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"Ошибка при обращении к LLM: {str(e)}"

from datatypes import func, var, const, literal
from strategy import sos_resolution
from datatypes import clause, negate
from input import formalize_problem, parse_formalized_problem
from output import output_sequence, explain_solution_detailed

if __name__ == "__main__":

    #problem = "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен."
    #problem = "Все кошки спят. Мурка — кошка. Докажи, что Мурка спит"
    problem = """
    Все сыновья наследуют от отцов. 
    Все отцы являются родителями.
    Петр - сын Ивана.
    Иван - сын Сергея. 
    Сергей является родителем.
    Если X наследует от Y, и Y наследует от Z, то X наследует от Z.
    Докажи, что Петр наследует от Сергея.
    """

    result = formalize_problem(problem)

    formulas = parse_formalized_problem(result)

    if (len(formulas)== 1):
        print("Всегда верно")
        quit()

    res = sos_resolution(set(formulas[:-1]), formulas[-1])

    solution_log = (output_sequence(res))

    llm_answer = explain_solution_detailed(solution_log, formulas)

    print(llm_answer)




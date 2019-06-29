import importlib
import os

from executor import executor as e
from .action import Action

def get_actions():
    return list(Action)

def get_document_types():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    doc_type_dir = os.path.join(current_dir, "doc_types")

    checkers = os.scandir(doc_type_dir)
    return [checker.name for checker in checkers if checker.is_file()]

def get_executor_results(tasks):

    tasks_result = []
    failed_tasks_counter = 0
    
    for task in tasks:
        task_result = {
            "name": task.getName(),
            "result": "Pass" if task.getResult() == True else "Fail"
        }

        tasks_result.append(task_result)

        if task.getResult() == False:
            failed_tasks_counter += 1
    
    result = {
        "tasks_result": tasks_result,
        "failed_tasks_counter": failed_tasks_counter,
        "all_tasks_counter": len(tasks)
    }

    return result

def check(document_type, action_name, request, response):
    doc_type = importlib.import_module("." + document_type, package="parc_checker_core.doc_types")
    tasks = doc_type.run(request, response, action_name)
    exe = e.Executor(3,3, tasks)
    exe.executeTasks()
    return get_executor_results(tasks)


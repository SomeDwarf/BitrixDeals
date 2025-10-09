from copy import deepcopy


def build_department_tree(departments):
    """Создание словаря отделов с их дочерними отделами"""
    dept_dict = {}
    for d in departments:
        d_id = d.get('ID')
        dept_dict[d_id] = deepcopy(d)
        dept_dict[d_id]["children"] = []
    # Заполнение списка дочерних отделов
    for d in dept_dict.values():
        parent_id = d.get("PARENT")
        if parent_id and parent_id in dept_dict:
            dept_dict[parent_id]["children"].append(d)
    return dept_dict


def get_department_chain(dept_id, dept_map):
    """Возвращает цепочку отделов вверх по иерархии"""
    chain = []
    while dept_id:
        dept = dept_map.get(str(dept_id))
        chain.append(dept)
        dept_id = dept.get("PARENT")
    return chain


def get_heads_chain(dept_id, emp_id, dept_map, emp_map):
    """Возвращает цепочку имён и id руководителей вверх по иерархии"""
    heads_chain = []
    dept_chain = get_department_chain(dept_id, dept_map)
    for d in dept_chain:
        head_id = d.get('UF_HEAD')
        if not head_id or emp_id == head_id:
            continue
        dept_head = emp_map.get(head_id)
        full_name = f"{dept_head.get("NAME")} {dept_head.get('LAST_NAME')}".strip()
        heads_chain.append({"full_name": full_name, "id": head_id})
    return heads_chain


def collect_employees_by_department(employees, departments):
    """Собирает итоговые данные по иерархии отделов."""
    emp_map = {emp["ID"]: emp for emp in employees}
    dept_map = build_department_tree(departments)

    results = []
    for emp in employees:
        for dept_id in emp.get("UF_DEPARTMENT", []):
            dept = dept_map.get(str(dept_id))
            if not dept:
                continue
            results.append({
                "id": emp.get("ID"),
                "name": f"{emp.get('NAME')} {emp.get('LAST_NAME', '')}".strip(),
                "position": emp.get("WORK_POSITION", ""),
                "department": dept.get("NAME"),
                "department_id": dept.get("ID"),
                "heads": get_heads_chain(dept_id, emp.get("ID"), dept_map, emp_map),
                "photo": emp.get("PERSONAL_PHOTO", ""),
            })

    # Сортировка по иерархии отделов
    def sort_key(r):
        chain = get_department_chain(r["department_id"], dept_map)
        return [int(d["SORT"]) for d in reversed(chain)]
    results.sort(key=sort_key)

    return results
import json
from collections import defaultdict


# Предполагается, что каждый набор тем (урок) -- некоторый путь в искомом графе (хотя бы примерно)
# Идея: сначала найти топологическую сортировку искомого графа, и по ней построить его
#
# 1. Составляем мапу { тэг: количество уроков с ним }
# 2. В каждом уроке сортируем тэги по количество уроков с ними
# 3. Составляем мапу { тэг: соседние по уроку тэги }
# Считаем, что эти соседние уроки -- предки (т.е. из них существует путь в тэг)
# 4. Сортируем уроки по количеству тэгов в них (эвристика -- меньше тэгов => проще урок => раньше изучается)
# 5. Присваиваем урокам уровни, предположительно соответствующие их уровням в топологической сортировке искомого графа
# Теперь мы знаем уровни (длины путей от корневых) вершин.
# Осталось добавить в граф ребра в соответствии с уровнями и существующими путями (точнее, наборами тем).
# 6. Проходим по всем уровням от 0 до последнего.
# Для каждого тэга добавляем ребра из его предков, если тэг ещё недостижим из предка.


def process_lessons(lessons):
    enumeration = {}
    enumeration_rev = {0: []}
    preds = {}
    level = 0
    length = len(lessons[0])
    for lesson in lessons:
        for index, tag in enumerate(lesson):
            if tag not in enumeration:
                if len(lesson) > length:
                    level += 1
                    length = len(lesson)
                    enumeration_rev[level] = []

                enumeration[tag] = level
                enumeration_rev[level].append(tag)
                preds[tag] = lesson[:index] + lesson[index + 1:]

    return enumeration, enumeration_rev, preds


# DFS (Floyd–Warshall might be used instead to reduce complexity)
def is_reachable(graph, start, end):
    visited_nodes = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node == end:
            return True
        if node not in visited_nodes:
            visited_nodes.add(node)
            stack.extend(set(graph[node]) - visited_nodes)
    return False


def find_graph(enumeration_rev, preds):
    level = 0
    graph = defaultdict(list)

    while level in enumeration_rev:
        for tag in sorted(enumeration_rev[level], key=lambda t: len(preds[t])):
            graph[tag] = []
            for pred in preds[tag][::-1]:
                if not is_reachable(graph, pred, tag):
                    graph[pred].append(tag)
        level += 1
    return graph


def create_dot_from_graph(graph):
    result = 'digraph G {\n'
    for node in graph:
        result += '    "{}";\n'.format(node)

    for node in graph:
        for child in graph[node]:
            result += '    "{}" -> "{}";\n'.format(node, child)

    result += '}'
    return result


def run_test(lesson):
    enumeration, enumeration_rev, preds = process_lessons(lesson)
    print(enumeration_rev)
    # assert len(enumeration) == len(enumeration_rev)
    print(len(enumeration))
    print(len(enumeration_rev))
    graph = find_graph(enumeration_rev, preds)
    dot_descr = create_dot_from_graph(graph)
    print("Enumeration: {}".format(enumeration))
    print("Prerequisites: {}".format(preds))
    print("Graph: {}".format(graph))
    print("Dot:\n{}".format(dot_descr))
    import os

    with open('builded_graph.dot', 'w') as f:
        f.write(dot_descr)
    os.system("dot -Tpng builded_graph.dot -o theme_graph.png")


REPLACE_MAP = {
    "for loop": "loop",
    "while loop": "loop",
    "abstract data type": "data type",
}


def preprocess_real(lessons, occurrences):
    result = []
    for lesson in lessons[::-1]:
        new_lesson = set()
        for tag in lesson:
            new_tag = tag.lower()
            if new_tag in REPLACE_MAP:
                new_tag = REPLACE_MAP[new_tag]
            new_lesson.add(new_tag)
        new_lessons = sorted(list(new_lesson), key=lambda tags: occurrences[tags], reverse=True)
        result.append(new_lessons)
    return result


def calc_occurrences(lessons):
    result = {}
    all_tags = get_all_tags(lessons)
    for tag in all_tags:
        count = 0
        for lesson in lessons:
            if tag in lesson:
                count += 1
        result[tag.lower()] = count
    return result


def get_all_tags(lessons):
    result = set()
    for lesson in lessons:
        for tag in lesson:
            result.add(tag)
    return result


if __name__ == '__main__':
    with open('lessons_to_tags_pre.json') as f:
        topics_dic = json.load(f)
        lessons = list(topics_dic.values())
        occurrences = calc_occurrences(lessons)
        lessons = preprocess_real(lessons, occurrences)
        run_test(lessons)
        # write results to file
    with open('lessons_to_paths.json', 'w') as f:
        lesson_ids = list(topics_dic.keys())[::-1]
        paths_dic = dict(zip(lesson_ids, lessons))
        j = json.dumps(paths_dic, indent=4)
        f.write(j)
        f.close()

import json
import os
import requests
from collections import defaultdict

properties_parents: set = {'instance of', 'subclass of', 'part of'}


def get_property_of(wikidataId, props):
    url = 'https://query.wikidata.org/sparql'
    res = []
    query = """
    SELECT ?wdLabel ?ps_Label ?wdpqLabel ?pq_Label ?ps_ {
      VALUES (?company) {(wd:%s)}

      ?company ?p ?statement .
      ?statement ?ps ?ps_ .

      ?wd wikibase:claim ?p.
      ?wd wikibase:statementProperty ?ps.

      OPTIONAL {
      ?statement ?pq ?pq_ .
      ?wdpq wikibase:qualifier ?pq .
      }

      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
    } ORDER BY ?wd ?statement ?ps_
    """ % wikidataId
    r = requests.get(url, params={'format': 'json', 'query': query})
    data = r.json()
    rows = data['results']['bindings']
    for row in rows:
        if row['wdLabel']['value'] in props:
            link = row['ps_']['value']
            id = link[link.rfind("/") + 1:]
            res.append((row['ps_Label']['value'], id))
    return res


def getGraph(topicsdic: dict, reduced: bool = False):
    possible_children: dict = defaultdict(set)
    child_to_parent: dict = defaultdict(set)

    added_values = set()

    for topic_id, topic_name in topicsdic.items():
        # get all parents
        parents = get_property_of(topic_id, properties_parents)

        for parent, parent_id in parents:
            if parent in topicsdic.values():
                child_to_parent[topic_name].add(parent)
            else:
                possible_children[parent].add(topic_name)

    for parent, children in possible_children.items():
        if len(children) < 2:
            continue
        for child in children:
            child_to_parent[child].add(parent)
            added_values.add(parent)

    for topic_id, topic_name in topicsdic.items():
        parents = get_property_of(topic_id, properties_parents)

        for parent, parent_id in parents:
            if parent in topicsdic.values():
                continue
            else:
                grandparents = get_property_of(parent_id, properties_parents)
                for grandpa, grandpa_id in grandparents:
                    if grandpa in topicsdic.values() or grandpa in added_values:
                        if reduced:
                            child_to_parent[topic_name].add(grandpa)
                        else:
                            child_to_parent[topic_name].add(parent)
                            child_to_parent[parent].add(grandpa)
                    else:
                        grandgrandparents = get_property_of(grandpa_id, properties_parents)
                        for grandgrandpa, grandgrandpa_id in grandgrandparents:
                            if grandgrandpa in topicsdic.values() or grandgrandpa in added_values:
                                if reduced:
                                    child_to_parent[topic_name].add(grandgrandpa)
                                else:
                                    child_to_parent[topic_name].add(parent)
                                    child_to_parent[parent].add(grandpa)
                                    child_to_parent[grandpa].add(grandgrandpa)

    return child_to_parent


def save_graph(graph):
    dot_description = "digraph {\n"

    for topic in topics_dic.values():
        dot_description += '  "' + topic + '" [style=filled, fillcolor=powderblue]\n'

    for node in graph:
        for parent in graph[node]:
            dot_description += '  "' + node + '" -> "' + parent + '"\n'

    dot_description += "}\n"
    with open('graph.dot', 'w') as f:
        f.write(dot_description)

    os.system("dot -Tpng graph.dot -o graph.png")


if __name__ == '__main__':
    with open('topics_by_wiki_id.json') as f:
        topics_dic = json.load(f)

    graph = getGraph(topics_dic, True)
    #print(graph)
    save_graph(graph)


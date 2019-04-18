import pandas as pd
from openpyxl import load_workbook

labeled_topics = load_workbook('topics.xlsx')

topics = labeled_topics['Topics']
requirements = labeled_topics['Requirements']

import random

load_sample = False
SAMPLE_SIZE = 1000
idxs = random.sample(range(1, len(list(topics.values))), SAMPLE_SIZE)

topics_df = pd.DataFrame(topics.values) if not load_sample \
    else pd.DataFrame(topics.values).ix[idxs]
requirements_df = pd.DataFrame(requirements.values) if not load_sample \
    else pd.DataFrame(requirements.values).ix[idxs]

submissions = pd.read_csv("submissions.csv").ix[idxs] if (load_sample) \
    else pd.read_csv("submissions.csv")

all_topics_col = list(topics_df[3][1:].append(requirements_df[3][1:]))  # column containing topics
all_topics_wiki_id = list(topics_df[4][1:].append(requirements_df[4][1:]))  # wiki_ids
all_topics_lesson_id = list(topics_df[0][1:].append(requirements_df[0][1:]))  # lesson_ids
topics_dic = dict()
for i, id in enumerate(all_topics_lesson_id):
    if id in topics_dic.keys():
        if not (all_topics_col[i] == 'Python'):
            topics_dic[id].append(all_topics_col[i])
    else:
        if not (all_topics_col[i] == 'Python'):
            topics_dic[id] = list([all_topics_col[i]])
all_topics = set(all_topics_col)
all_topics.remove('Python')
all_topics_lesson_id_set = set(all_topics_lesson_id)
topics_by_wiki_id = dict(zip(all_topics_wiki_id, all_topics_col))
category_links = list(topics_by_wiki_id.keys())
with open('topics_wiki_ids.txt', 'w') as f:
    for i in category_links:
        f.write('https://www.wikidata.org/wiki/' + str(i) + '\n')

lesson_links = set(all_topics_lesson_id)
with open('lesson_links.txt', 'w') as f:
    for i in lesson_links:
        f.write('https://stepik.org/lesson/' + str(int(i)) + '\n')

category_names = [str(key) for key in topics_by_wiki_id.values()]
for i in category_names:
    i = str(i)
    print(i)

all_topics = [str(topic) for topic in all_topics_col]
popularity = [all_topics.count(cat) for cat in category_names]

import json

with open('topics_by_wiki_id.json', 'w') as outfile:
    json.dump(topics_by_wiki_id, outfile)

codes_wrong = submissions[submissions['status'] == 'wrong'][['lesson_id', 'reply']].to_dict()
codes_correct = submissions[submissions['status'] == 'correct'][['lesson_id', 'reply']].to_dict()

from collections import defaultdict

ids = codes_correct['lesson_id']
replies = codes_correct['reply']

id_to_codes = defaultdict(list)

for k, v in ids.items():
    id_to_codes[v].append(replies[k])

import ast
from ast_processing import process_code

index_to_code = {}
index_to_ast = {}
index_to_topics = defaultdict(list)
index_to_id = defaultdict(list)

index = 0
for id, codes in id_to_codes.items():
    for code in codes:
        if ('code' in ast.literal_eval(code).keys()):
            code_text = ast.literal_eval(code)['code']
            try:
                code_ast, code_text_s = process_code(code_text)
            except TypeError:
                continue
            index_to_code[index] = code_text_s
            index_to_ast[index] = code_ast
            index_to_topics[index] += topics_dic[id]
            index_to_id[index] = id
            index += 1


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


with open("index_to_id.json", "w") as f:
    j = json.dumps(index_to_id, indent=4, cls=SetEncoder)
    f.write(j)
    f.close()

with open("all_topics.json", "w") as f:
    j = json.dumps(all_topics, indent=4, cls=SetEncoder)
    f.write(j)
    f.close()

with open("index_to_code.json", "w") as f:
    j = json.dumps(index_to_code, indent=4)
    f.write(j)
    f.close()

with open("index_to_topics.json", "w") as f:
    j = json.dumps(index_to_topics, indent=4)
    f.write(j)
    f.close()

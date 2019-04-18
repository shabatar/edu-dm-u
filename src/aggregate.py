import csv
import json
from collections import OrderedDict
from collections import defaultdict

with open('topics.json') as f:
    topics = json.load(f)
    topicss = list(topics)

with open('predicted.txt') as f:
    wr = csv.reader(f)
    predicted_topics = list(wr)

with open('lesson_id.txt') as f:
    wr = csv.reader(f)
    lesson_ids = list(wr)
    for i, item in enumerate(lesson_ids):
        lesson_ids[i] = item[1]


def count_topic_by_lesson_id(topic, lesson_id):
    cnt = 0
    for i, t_list in enumerate(predicted_topics):
        id = lesson_ids[i]
        if id == lesson_id and topic in t_list:
            cnt += 1
    return cnt


lesson_ids_to_topics = defaultdict(list)
leng = 0
for i, id in enumerate(lesson_ids):
    # print("id:" + str(id))
    topics = predicted_topics[i]
    lesson_ids_to_topics[id] = sorted(list(set().union(lesson_ids_to_topics[id], topics)))
    leng = max(len(lesson_ids_to_topics[id]), leng)

print(leng)
with open("lessons_to_tags_init.json", "w") as f:
    lesson_ids_to_topics_out = OrderedDict(sorted(lesson_ids_to_topics.items(),
                                                  key=lambda x: len(x[1]), reverse=True))
    j = json.dumps(lesson_ids_to_topics_out, indent=4)
    f.write(j)
    f.close()
print(len(lesson_ids_to_topics_out))


def exclude_by_count_occurences(ids_to_topics, min_th):
    topic_to_count = defaultdict(list)
    for lesson_id, topics_list in ids_to_topics.items():
        for top in topics_list:
            if (top not in topic_to_count.keys()):
                topic_to_count[top] = 1
            else:
                topic_to_count[top] += 1
    leng = 0
    # exclude those topics which occurs not often at all
    for lesson_id, topics_list in ids_to_topics.items():
        newList = []
        for topic in topics_list:
            if (topic_to_count[topic] >= min_th):
                newList.append(topic)
        ids_to_topics[lesson_id] = sorted(newList)
        leng = max(len(ids_to_topics[lesson_id]), leng)
    print("Max leng now: " + str(leng))


def exclude_by_lesson_id_occurences(ids_to_topics, min_th):
    # exclude those topics which occurs not often by any lesson_id
    # get all submissions with selected  lesson_id and count num of topic occurencies
    leng = 0
    for id, topics in ids_to_topics.items():
        new_topics = []
        cnts = []
        for topic in topics:
            cnt = count_topic_by_lesson_id(topic, id)
            cnts.append(cnt)
            if (cnt >= min_th):
                new_topics.append(topic)
        new_topics = sorted(new_topics)
        ids_to_topics[id] = new_topics
        leng = max(len(ids_to_topics[id]), leng)
    print("Max leng now: " + str(leng))


exclude_by_count_occurences(lesson_ids_to_topics, 10)

with open("lessons_to_tags_pre.json", "w") as f:
    lesson_ids_to_topics_out = OrderedDict(sorted(lesson_ids_to_topics.items(),
                                                  key=lambda x: len(x[1]), reverse=True))
    j = json.dumps(lesson_ids_to_topics_out, indent=4)
    f.write(j)
    f.close()

exclude_by_lesson_id_occurences(lesson_ids_to_topics, 3)

with open("lessons_to_tags.json", "w") as f:
    lesson_ids_to_topics_out = OrderedDict(sorted(lesson_ids_to_topics.items(),
                                                  key=lambda x: len(x[1]), reverse=True))
    j = json.dumps(lesson_ids_to_topics_out, indent=4)
    f.write(j)
    f.close()
# print(leng)
print(len(lesson_ids_to_topics_out))

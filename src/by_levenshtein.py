import csv
import json

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

with open('index_to_code.json') as f:
    index_to_code = json.load(f)
with open('index_to_topics.json') as f:
    index_to_topics = json.load(f)
with open('all_topics.json') as f:
    topics = json.load(f)

index_to_code = {int(k): v for k, v in index_to_code.items()}
index_to_topics = {int(k): v for k, v in index_to_topics.items()}
code_train, code_test, topic_train, topic_test = train_test_split(index_to_code, index_to_topics, random_state=42,
                                                                  test_size=0.33, shuffle=True)

train_df = pd.DataFrame({'code': pd.Series(code_train), 'topic': pd.Series(topic_train)})
test_df = pd.DataFrame({'code': pd.Series(code_test), 'topic': pd.Series(topic_test)})

tr = train_df.drop_duplicates()

OneVsTheRest = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', OneVsRestClassifier(MultinomialNB(
        fit_prior=False, class_prior=None))),
])

topicss = dict.fromkeys(topics, 0)
k = 0
for topic in topicss.keys():
    topicss[topic] = k
    k += 1

topics_train = list(train_df['topic'])
topics_test = list(test_df['topic'])
codes = np.array(train_df['code'])

MLB = MultiLabelBinarizer()
topics_train = MLB.fit_transform(topics_train)
OneVsTheRest.fit(codes, topics_train)
prediction = OneVsTheRest.predict(np.array(test_df['code']))
print('Test accuracy: {}'.format(accuracy_score(MultiLabelBinarizer().fit_transform(topics_test), prediction)))
target_names = [t for t in topicss.values()]
print(classification_report(MultiLabelBinarizer().fit_transform(topics_test), prediction), labels=target_names)

# print(MLB.inverse_transform(prediction))
# print('-------')
# print(test_df['topic'])
prediction = MLB.inverse_transform(prediction)
# prediction = [list(elem) for elem in prediction]
# print(classification_report(topics_test, prediction))

with open("predicted.txt", "w") as f:
    wr = csv.writer(f)
    wr.writerows(prediction)

with open("actual.txt", "w") as f:
    wr = csv.writer(f)
    wr.writerows(topics_test)


def intersect(a, b):
    sb = set(b)
    bs = [val for val in a if val in sb]
    return bs


# if (predicted intersection with test) >= 80% of test value then True
def moreThan80Percents(list1, list2):
    list1 = sorted(list1)
    list2 = sorted(list2)
    list3 = intersect(list1, list2)
    leninter = len(list3)
    if leninter >= 0.8 * len(list2):
        return True
    return False


matches = 0
for pred, val in zip(prediction, topics_test):
    if (moreThan80Percents(pred, val)):
        matches += 1
print("Test accuracy (80%) : " + str(matches / len(prediction)))

import requests

from enums import OrderDirection
from orm.queries import list_questions
from constants import ES_ENDPOINT, ES_AUTH_TOKEN


def populate_questions():
    """
    Retrieve paginated questions from the database.
    And add them into Elasticsearch.
    Elasticsearch will index these questions which we can later search.
    """
    PER_PAGE = 20
    offset = 0
    while True:
        questions = list_questions(order_direction=OrderDirection.ASC, limit=PER_PAGE, offset=offset, all_subdomains=True)
        print(questions)
        for question in questions:
            data = {'text': question.text}
            _id = question.id
            url = f'{ES_ENDPOINT}/questions/_doc/{_id}'
            resp = requests.put(url, json=data, headers={'Authorization': f'Bearer {ES_AUTH_TOKEN}'})
        if len(questions) == 0:
            break
        offset += PER_PAGE

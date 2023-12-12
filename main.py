import random
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic_types import QuestionType, ChoicesType

from orm.models import Question
from enums import OrderDirection

from services import create_question_choices, read_question, list_questions, create_instance


app = FastAPI()


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "hello world"}


@app.post("/questions")
def post_question(question: QuestionType):
    question_id = create_instance(Question, {'text': question.text, 'subdomain': question.subdomain, 'level': question.level, 'explanation': question.explanation})
    question = read_question(question_id)
    return question


@app.post("/questions/{question_id}/choices")
def post_choices(question_id: int, choices: ChoicesType):
    try:
        created, message = create_question_choices(question_id, choices.choices)
        if not created:
            return JSONResponse(content={"message": message}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception:
        # Log an error with message as exc
        return Response(content="Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    question = read_question(question_id)
    return question


@app.get("/questions")
def get_questions(order_by=Question.created_at.name, order_direction=OrderDirection.DESC, limit=20, offset=0, category=None):
    questions = list_questions(order_by=order_by, order_direction=order_direction, limit=limit, offset=offset, category=category)
    random.shuffle(questions)
    return questions

from typing import Annotated
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pydantic_types import QuestionType, ChoicesType, RegisterUser, UserAnswerType, UserAnswerTypeBulk, ChoiceReadType, QuestionReadType

from orm.models import Question, User
from enums import OrderDirection

from services import create_question_choices, read_question, list_questions, create_instance, create_user_answer, create_user_answers
from auth import register_user, get_current_user, authenticate
from constants import ADMIN_EMAIL


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
def post_question(question: QuestionType, user: Annotated[User, Depends(get_current_user)]):
    if user.email != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    question_id = create_instance(Question, {'text': question.text, 'subdomain': question.subdomain, 'level': question.level, 'explanation': question.explanation, 'snippet': question.snippet})
    question = read_question(question_id)
    return question


@app.post("/questions/{question_id}/choices")
def post_choices(question_id: int, choices: ChoicesType, user: Annotated[User, Depends(get_current_user)]):
    if user.email != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        created, message = create_question_choices(question_id, choices.choices)
        if not created:
            return JSONResponse(content={"message": message}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception:
        # Log an error with message as exc
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    question = read_question(question_id)
    return question


@app.get("/questions")
def get_questions(order_by=Question.created_at.name, order_direction=OrderDirection.DESC, limit=20, offset=0, subdomain=None, category=None, difficulty_level=None):
    questions = list_questions(order_by=order_by, order_direction=order_direction, limit=limit, offset=offset, subdomain=subdomain, category=category, difficulty_level=difficulty_level)
    to_return = []
    for question in questions:
        choice_types = []
        for choice in question.choices:
            choice_type = ChoiceReadType(id=choice.id, text=choice.text)
            choice_types.append(choice_type)
        question_type = QuestionReadType(id=question.id, text=question.text, snippet=question.snippet, explanation=question.explanation, choices=choice_types)
        to_return.append(question_type)
    return to_return


@app.post("/answers")
def post_answers(answer: UserAnswerType, user: Annotated[User, Depends(get_current_user)]):
    try:
        created, message = create_user_answer(user, answer)
        if not created:
            return JSONResponse(content={"message": message}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception:
        # Log an error with message as exc
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    question = read_question(answer.question_id)
    correct_choice = list(filter(lambda choice: choice.is_answer, question.choices))[0]
    data = {
        'correct': correct_choice.id == answer.choice_id,
        'answer_id': correct_choice.id
    }
    return data


@app.post("/answers/bulk")
def post_answers_bulk(answers: UserAnswerTypeBulk, user: Annotated[User, Depends(get_current_user)]):
    created, message = create_user_answers(user, answers.answers)
    data = {
        "message": "Success"
    }
    return data


@app.post("/register")
def register(user: RegisterUser):
    if len(user.email) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email too short")
    if len(user.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short")
    token, message = register_user(user.email, user.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {'access_token': token, "token_type": "bearer", 'message': message}


@app.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token, message = authenticate(form_data)
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"access_token": token, "token_type": "bearer"}

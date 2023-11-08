from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from graphmaker.api import graph_api, Response

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/graph", response_model=Response)
def graph():
    """Получение графа.

    Args:
        group (GroupBy, optional): Задает значение группировки связей.
            Defaults to GroupBy.id.

    Returns:
        GraphData: граф
    """
    data = graph_api()
    return data

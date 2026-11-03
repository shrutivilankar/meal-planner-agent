from fastapi import FastAPI
from schema  import Diner, Recipe
from workflow import generate_meal_plan
from meal_planner_agent.vector_langchain_workflow import chat_with_retriever

app = FastAPI(title="Meal Planner Agent")


@app.post("/generate", response_model=list[Recipe])
async def generate() -> list[Recipe]:
    state = await generate_meal_plan()
    return state["recipes"]


@app.post("/chat_with_user", response_model=str)
async def chat_with_user(query: str) -> str:
    return await chat_with_retriever(query)
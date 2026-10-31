from fastapi import FastAPI
from schema  import Diner, Recipe
from workflow import generate_meal_plan


app = FastAPI(title="Meal Planner Agent")


@app.post("/generate", response_model=list[Recipe])
async def generate() -> list[Recipe]:
    state = await generate_meal_plan()
    return state["recipes"]

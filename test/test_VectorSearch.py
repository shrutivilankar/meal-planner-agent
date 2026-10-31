import os, io
from pathlib import Path
from meal_planner_agent.vector_langchain_workflow import maintainRecipes


if __name__ == "__main__":
    path = Path("Lemon-Herb_Chicken_with_Quinoa-Chickpea_Salad_and_Roasted_Veg_(Mediterranean).txt").resolve()
    maintainRecipes(path)
import os, io
from pathlib import Path
from meal_planner_agent.vector_langchain_workflow import maintain_recipes


if __name__ == "__main__":
    path = Path("Lemon-Herb_Chicken_with_Quinoa-Chickpea_Salad_and_Roasted_Veg_(Mediterranean).txt").resolve()
    maintain_recipes(path, "what is portion size for Joy?")
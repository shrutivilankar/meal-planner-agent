from typing import TypedDict, Literal
from pathlib import Path

class MealPlanAgentState(TypedDict):
    requested_action: Literal["generate_meal_plan", "generate_grocery_list", "generate_preparation_steps", "generate_cooking_instructions"]
    diners: list[dict]  # List of diners with their dietary restrictions, allergies, and other relevant information
    recipes: list[dict]  # List of recipes generated for the meal plan
    aggregated_info: dict  # Aggregated information about the preparation steps, shopping list, etc.
    recipeFile: Path

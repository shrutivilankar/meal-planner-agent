from pydantic import BaseModel, Field
from typing import List


class Nutrition(BaseModel):
    model_config = {"extra": "forbid"}
    calories: int = Field(..., description="Caloric content of the meal in kilocalories")
    protein: float = Field(..., description="Protein content of the meal in gm")
    fat: float = Field(..., description="Fat content of the meal in gm")
    carbohydrates: float = Field(..., description="Carbohydrate content of the meal in gm")
    fiber: float = Field(..., description="Fiber content of the meal in gm")

class Minerals(BaseModel):
    model_config = {"extra": "forbid"}
    # Define common expected minerals explicitly with default values or Optional types
    calcium: float = Field(0.0, description="Calcium content in mg")
    iron: float = Field(0.0, description="Iron content in mg")
    potassium: float = Field(0.0, description="Potassium content in mg")
    magnesium: float = Field(0.0, description="Magnesium content in mg")
    zinc: float = Field(0.0, description="Zinc content in mg")

# 3. Vitamins Sub-Model
class Vitamins(BaseModel):
    model_config = {"extra": "forbid"}
    # Define common expected vitamins explicitly
    vitamin_a: float = Field(0.0, description="Vitamin A content in microgm (mcg) or IU")
    vitamin_c: float = Field(0.0, description="Vitamin C content in mg")
    vitamin_d: float = Field(0.0, description="Vitamin D content in microgm (mcg) or IU")
    vitamin_e: float = Field(0.0, description="Vitamin E content in mg")
    vitamin_b6: float = Field(0.0, description="Vitamin B6 content in mg")
    vitamin_b12: float = Field(0.0, description="Vitamin B12 content in microgm (mcg)")

class NutritionRequirements(BaseModel):
    model_config = {"extra": "forbid"}
    calories: int = Field(..., description="Calories per meal")
    protein: float = Field(...)
    fat: float = Field(...)
    carbohydrates: float = Field(...)
    fiber: float = Field(...)
    sodium_max: float = Field(...)
    # minerals: Minerals = Field(default_factory=Minerals)
    # vitamins: Vitamins = Field(default_factory=Vitamins)

class Diner(BaseModel):
    model_config = {"extra": "forbid"}
    name: str = Field(..., description="Name of the diner")
    dietary_restrictions: List[str] = Field(..., description="List of dietary restrictions for the diner (e.g., vegetarian, gluten-free)")
    allergies: List[str] = Field(..., description="List of allergies for the diner (e.g., peanuts, shellfish)")
    complications: List[str] = Field(..., description="List of complications for the diner (e.g., diabetes, high blood pressure)")
    age: int = Field(..., description="Age of the diner")
    weight: float = Field(..., description="Weight of the diner in kg")
    height: float = Field(..., description="Height of the diner in centimeters")
    ideal_weight: float = Field(..., description="Ideal weight of the diner in kg")
    gender: str = Field(..., description="Gender of the diner (e.g., male, female, non-binary)")
    nutrition_requirement_per_meal: NutritionRequirements = Field(..., description="Nutritional requirements per meal for the diner ")
    weightloss_goal: str = Field(..., description="Weight loss goal for the diner (e.g., slow and sustainable progress per week)")
    #daily_totals: Nutrition = Field(..., description="Daily nutritional totals for the diner ")
    calories_per_day: int = Field(..., description="Total caloric intake per day for the diner in kilocalories")
     

class Ingredient(BaseModel):
    model_config = {"extra": "forbid"}
    name: str = Field(..., description="Name of the ingredient")
    measurement: str = Field(..., description="Measurement of the ingredient in gm or cups or count")
    unit: str = Field(..., description="Unit of measurement for the ingredient (e.g., gm, cups or count)")
    

class PrePrepStep(BaseModel):
    model_config = {"extra": "forbid"}
    step_number: int = Field(..., description="Step number in the weekly pre-preparation process")
    description: str = Field(..., description="Description of the weekly pre-preparation step")
    measurement: str = Field(..., description="Measurement of the ingredient in gm or cups or count if any")

class CookingAssemblyInstructions(BaseModel):
    model_config = {"extra": "forbid"}
    step_number: int = Field(..., description="Step number in the cooking and assembly process")
    description: str = Field(..., description="Description of the cooking assembly step")
    

class MealComponent(BaseModel): 
    model_config = {"extra": "forbid"}  
    name: str = Field(..., description="Name of the meal component (e.g., daal, rice, salad)")
    type: str = Field(..., description="Type of the meal component (e.g., main dish, side dish, dessert)")
    serving_size_per_diner: List[ServingSize] = Field(..., description="List of serving sizes per diner for this meal component") 
    
    
class ServingSize(BaseModel):
    model_config = {"extra": "forbid"}
    diner: str = Field(..., description="Diner for whom the serving size is defined")    
    size: str = Field(..., description="Size of the serving (e.g., cups, pieces, gm)")
    

class NutritionPerDinerPerRecipe(BaseModel):
    model_config = {"extra": "forbid"} 
    diner: str = Field(..., description="Diner for whom the nutritional content is defined")       
    nutrition: NutritionRequirements = Field(..., description="Nutritional content of the meal for the diner")     
    

class Recipe(BaseModel):
    model_config = {"extra": "forbid"}
    title: str = Field(..., description="Title of the recipe")
    ingredients: List[Ingredient] = Field(..., description="List of ingredients for the recipe")
    pre_prep_steps: List[PrePrepStep] = Field(..., description="List of pre-preparation steps to be done week in advance of the meal")
    meal_components: List[MealComponent] = Field(..., description="List of meal components for the recipe")
    cooking_assembly_instructions: List[CookingAssemblyInstructions] = Field(..., description="List of cooking and assembly instructions on the day of meal")
    nutrition_per_diner: List[NutritionPerDinerPerRecipe] = Field(..., description="List of nutritional content per diner")
    
       
    

class WeeklyShoppingList(BaseModel):
    model_config = {"extra": "forbid"} 
    ingredients: List[Ingredient] = Field(..., description="consolidated and aggregated list of ingredients for the shopping list")

class WeeklyPreparationAggregator(BaseModel):
    model_config = {"extra": "forbid"}
    weeks_prep_steps: List[PrePrepStep] = Field(..., description="consolidated and aggregated list of pre-preparation steps for the week")




def format_recipe(r: dict) -> str:
    lines = [r["title"], "", "🛒 Ingredients"]
    for i in r["ingredients"]:
        amt = f"x{i['measurement']}" if i["unit"] == "count" else f"{i['measurement']} {i['unit']}"
        lines.append(f"• {i['name']} — {amt}")
    lines.append("🧊 Prep Ahead")
    for p in r["pre_prep_steps"]:
        lines.append(f"{p['step_number']}. {p['description']} ({p['measurement']})")
    lines.append("👨‍🍳 Steps")
    for s in r["cooking_assembly_instructions"]:
        lines.append(f"{s['step_number']}. {s['description']}")
    lines.append("🍽 Servings")
    for c in r["meal_components"]:
        for s in c["serving_size_per_diner"]:
            lines.append(f"{s['diner']}: {c['name']} — {s['size']}")
    lines.append("📊 Nutrition")
    for n in r["nutrition_per_diner"]:
        nu = n["nutrition"]
        lines.append(f"{n['diner']}: {nu['calories']} kcal, {nu['protein']} g protein")
    return "\n".join(lines)
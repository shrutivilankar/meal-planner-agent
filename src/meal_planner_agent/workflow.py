import httpx
import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from meal_planner_agent.schema import Recipe, Diner, NutritionRequirements, Nutrition, Minerals, Vitamins, Ingredient, PrePrepStep, CookingAssemblyInstructions, MealComponent, ServingSize, NutritionPerDinerPerRecipe, format_recipe
import json
from langgraph.graph import StateGraph, MessagesState, START, END
from meal_planner_agent.memory import MealPlanAgentState
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal


load_dotenv()

# async def fetch_meal_plan():
#     client = AsyncOpenAI(
#         api_key=os.getenv("OPENROUTER_API_KEY"),
#         base_url="https://openrouter.ai/api/v1"
# )
#     diner1 = Diner(
#         name="Joy",
#         dietary_restrictions=["no red meat", "no sugar"],
#         allergies=["none"],
#         complications=["diabetes", "hypertention"],
#         age=40,
#         weight=110.0,
#         height=170.0,
#         ideal_weight=72.0,
#         gender="male",
#         weightloss_goal="slow and sustainableprogress per week, should not feel hungry or deprived, should be able to maintain the weight loss after reaching the goal",
#         nutrition_requirement_per_meal=NutritionRequirements(
#             calories=600, protein=32, fat=20, carbohydrates=50, fiber=12, sodium_max=650,
#             minerals=Minerals(calcium=333, iron=2.7),
#             vitamins=Vitamins(vitamin_a=300, vitamin_c=30),   # snake_case
#         ),
#         daily_totals=NutritionRequirements(calories=2000, protein=120, fat=65, carbohydrates=200, fiber=35),
#         calories_per_day=2000)  
    

#     diner2 = Diner(
#         name="Alice",
#         dietary_restrictions=["no red meat", "no sugar"],
#         allergies=["none"],
#         complications=["overweight"],
#         age=40,
#         weight=70.0,
#         height=154.0,
#         ideal_weight=57.0,
#         gender="female",
#         weightloss_goal="sustainable progress per week",
#         calories_per_day=1500,
#         nutrition_requirement_per_meal=NutritionRequirements(
#             calories=450,
#             protein=25,
#             fat=15,
#             carbohydrates=45,
#             fiber=8,
#             sodium_max=600,
#             minerals=Minerals(calcium=333, iron=6.0),
#             vitamins=Vitamins(vitamin_a=233, vitamin_c=25)
#         ),
#         daily_totals=NutritionRequirements(
#             calories=1500,
#             protein=90,
#             fat=50,
#             carbohydrates=172,
#             fiber=28
#         )
#     )

#     response = await client.chat.completions.parse(
#         model="google/gemini-2.5-flash", 
#         messages=[{"role": "system", "content": "You are a chef and a dietician"}, {"role": "user", "content": f"Generate a dinner meal plan for a family of two diners {diner1.model_dump_json()} and {diner2.model_dump_json()}."}],
#         response_format=Recipe,
#         max_tokens=5000)
#     print(response.choices[0].message.parsed)
   




def initializeDiner(state: MealPlanAgentState):
    print("Initializing diners...")
    diner1 = Diner(
        name="Joy",
        dietary_restrictions=["no red meat", "no sugar"],
        allergies=["none"],
        complications=["diabetes", "hypertention"],
        age=40,
        weight=110.0,
        height=170.0,
        ideal_weight=72.0,
        gender="male",
        weightloss_goal="sustainable progress per week",
        calories_per_day=2000,
        nutrition_requirement_per_meal=NutritionRequirements(
            calories=600, protein=32, fat=20, carbohydrates=50, fiber=12, sodium_max=650
        )
            # minerals=Minerals(calcium=333, iron=2.7),
            # vitamins=Vitamins(vitamin_a=300, vitamin_c=30),   # snake_case
        # ),
        # daily_totals=Nutrition(calories=2000, protein=120, fat=65, carbohydrates=200, fiber=35),
        )  
    

    diner2 = Diner(
        name="Alice",
        dietary_restrictions=["no red meat", "no sugar"],
        allergies=["none"],
        complications=["overweight"],
        age=40,
        weight=70.0,
        height=154.0,
        ideal_weight=57.0,
        gender="female",
        weightloss_goal="sustainable progress per week",
        calories_per_day=1500,
        nutrition_requirement_per_meal=NutritionRequirements(
            calories=450,
            protein=25,
            fat=15,
            carbohydrates=45,
            fiber=8,
            sodium_max=600,
        )
            # minerals=Minerals(calcium=333, iron=6.0),
            # vitamins=Vitamins(vitamin_a=233, vitamin_c=25)
        # ),
        # daily_totals=Nutrition(
        #     calories=1500,
        #     protein=90,
        #     fat=50,
        #     carbohydrates=172,
        #     fiber=28
        # )
    )
    state["diners"] = [diner1.model_dump(), diner2.model_dump()]
    return state

async def chef_agent_node(state: MealPlanAgentState) -> Command[Literal["review_week_plan"]]:
    print("Generating meal plan for diners...")

    # client = AsyncOpenAI(
    #     api_key=os.getenv("OPENROUTER_API_KEY"),
    #     base_url="https://openrouter.ai/api/v1"
    # )

    client = AsyncOpenAI(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        base_url="https://api.anthropic.com/v1"
    )

    # response = await client.chat.completions.parse(
    #     model=os.getenv("MODEL", "google/gemini-2.5-flash"),
    #     messages=[{"role": "system", "content": "You are a chef and a dietician"}, {"role": "user", "content": f"Generate easy dinner meal plan for a family of two diners {state['diners'][0]} and {state['diners'][1]}. Keep info concise. Choose from Mediterranean, indian, asian cusine"}],
    #     response_format=Recipe,
    #     max_tokens=9000)
    # recipe = response.choices[0].message.parsed
    
    recipe = Recipe(title='Lemon-Garlic Baked Chicken with Lentil-Quinoa Pilaf, Roasted Broccoli and Cucumber-Tomato Salad', ingredients=[Ingredient(name='Chicken breast, skinless raw', measurement='180', unit='gm'), Ingredient(name='Dry green lentils', measurement='60', unit='gm'), Ingredient(name='Dry quinoa', measurement='40', unit='gm'), Ingredient(name='Broccoli florets', measurement='300', unit='gm'), Ingredient(name='Cucumber', measurement='150', unit='gm'), Ingredient(name='Tomato', measurement='150', unit='gm'), Ingredient(name='Extra virgin olive oil', measurement='25', unit='gm'), Ingredient(name='Lemon', measurement='1', unit='count'), Ingredient(name='Garlic cloves', measurement='3', unit='count'), Ingredient(name='Dried oregano', measurement='2', unit='gm'), Ingredient(name='Black pepper', measurement='1', unit='gm'), Ingredient(name='Salt', measurement='1', unit='gm'), Ingredient(name='Slivered almonds', measurement='20', unit='gm')], pre_prep_steps=[PrePrepStep(step_number=1, description='Mix lemon juice, minced garlic, oregano, pepper and 5 gm olive oil. Marinate chicken in the fridge (or freeze up to a week).', measurement='180 gm chicken'), PrePrepStep(step_number=2, description='Simmer lentils and quinoa together in water for about 20 minutes until tender. Drain and refrigerate.', measurement='60 gm lentils, 40 gm quinoa'), PrePrepStep(step_number=3, description='Wash and cut broccoli, cucumber and tomato. Store separately in airtight containers.', measurement='600 gm vegetables')], meal_components=[MealComponent(name='Lemon-garlic baked chicken breast', type='main dish', serving_size_per_diner=[ServingSize(diner='Joy', size='100 gm raw (about 75 gm cooked)'), ServingSize(diner='Alice', size='80 gm raw (about 60 gm cooked)')]), MealComponent(name='Lentil-quinoa pilaf', type='side dish', serving_size_per_diner=[ServingSize(diner='Joy', size='170 gm cooked (about 1 cup)'), ServingSize(diner='Alice', size='130 gm cooked (about 3/4 cup)')]), MealComponent(name='Roasted broccoli', type='side dish', serving_size_per_diner=[ServingSize(diner='Joy', size='170 gm'), ServingSize(diner='Alice', size='130 gm')]), MealComponent(name='Cucumber-tomato salad with almonds', type='side dish', serving_size_per_diner=[ServingSize(diner='Joy', size='170 gm with 12 gm almonds'), ServingSize(diner='Alice', size='130 gm with 8 gm almonds')])], cooking_assembly_instructions=[CookingAssemblyInstructions(step_number=1, description='Preheat oven to 220C (425F). Bake marinated chicken on a lined tray for 18-22 minutes until it reaches 74C (165F). Rest for 5 minutes.'), CookingAssemblyInstructions(step_number=2, description='Toss broccoli with 10 gm olive oil, a pinch of pepper and half the salt. Roast on a second tray for 15-18 minutes.'), CookingAssemblyInstructions(step_number=3, description='Reheat the lentil-quinoa pilaf in a pan with a splash of water and the remaining salt. Add a squeeze of lemon.'), CookingAssemblyInstructions(step_number=4, description='Toss cucumber and tomato with 10 gm olive oil, lemon juice and pepper. Top with almonds.'), CookingAssemblyInstructions(step_number=5, description='Plate by portion: Joy gets the larger portions and Alice the smaller ones. Slice the chicken and serve with the pilaf, broccoli and salad.')], nutrition_per_diner=[NutritionPerDinerPerRecipe(diner='Joy', nutrition=NutritionRequirements(calories=590, protein=36.0, fat=21.0, carbohydrates=54.0, fiber=14.0, sodium_max=330.0)), NutritionPerDinerPerRecipe(diner='Alice', nutrition=NutritionRequirements(calories=450, protein=28.0, fat=15.0, carbohydrates=42.0, fiber=11.0, sodium_max=300.0))])

    # recipe = Recipe(title='Lemon-Dill Baked Salmon with Quinoa, Roasted Broccoli & Peppers and Fresh Garden Salad', 
    #     ingredients=[Ingredient(name='Salmon fillet, skinless (wild or farmed)', measurement='210', unit='grams'), Ingredient(name='Quinoa, dry', measurement='90', unit='grams'), Ingredient(name='Broccoli florets', measurement='300', unit='grams'), Ingredient(name='Red bell pepper', measurement='150', unit='grams'), Ingredient(name='Baby spinach', measurement='100', unit='grams'), Ingredient(name='Cucumber', measurement='150', unit='grams'), Ingredient(name='Cherry tomatoes', measurement='150', unit='grams'), Ingredient(name='Extra virgin olive oil', measurement='14', unit='grams'), Ingredient(name='Lemon', measurement='1', unit='count'), Ingredient(name='Garlic cloves', measurement='3', unit='count'), Ingredient(name='Dried dill', measurement='2', unit='grams'), Ingredient(name='Black pepper', measurement='1', unit='grams'), Ingredient(name='Salt', measurement='1', unit='grams'), Ingredient(name='Water for cooking quinoa', measurement='2', unit='cups')],
    #     pre_prep_steps=[PrePrepStep(step_number=1, description='Portion the salmon into one 120 g fillet (Joy) and one 90 g fillet (Alice), wrap tightly and freeze. Move to the refrigerator the night before cooking to thaw.', measurement='210 grams salmon'), PrePrepStep(step_number=2, description='Rinse the quinoa well, cook in water until fluffy (about 15 minutes), cool completely, then freeze in an airtight container. Reheat on the day of the meal.', measurement='90 grams dry quinoa with 2 cups water'), PrePrepStep(step_number=3, description='Mince the garlic and mix with the olive oil and dill. Store in a small jar in the refrigerator.', measurement='3 garlic cloves, 14 grams olive oil, 2 grams dill'), PrePrepStep(step_number=4, description='Cut the broccoli into florets and slice the red bell pepper into strips. Store in separate containers in the refrigerator (use within 5 days of the meal).', measurement='300 grams broccoli, 150 grams bell pepper')],
    #     meal_components=[MealComponent(name='Lemon-dill baked salmon', type='main dish'), MealComponent(name='Quinoa', type='side dish'), MealComponent(name='Roasted broccoli and red bell pepper', type='side dish'), MealComponent(name='Spinach, cucumber and tomato salad with lemon', type='side dish')],
    #     cooking_assembly_instructions=[CookingAssemblyInstructions(step_number=1, description='Preheat the oven to 220°C (425°F). Line a baking sheet with parchment. Thaw the salmon and pat dry.  Zest the lemon and juice it, setting both aside.  Reheat the quinoa in a covered pan with a splash of water over low heat until hot, then fluff with a fork.'), CookingAssemblyInstructions(step_number=2, description='Toss the broccoli and bell pepper with about one third of the garlic-dill oil, half the black pepper and a pinch of the salt. Spread on half of the baking sheet.'), CookingAssemblyInstructions(step_number=3, description='Place the salmon on the other half of the sheet. Brush with the remaining garlic-dill oil, except for 1 teaspoon, and sprinkle with lemon zest, remaining pepper and a pinch of salt. Roast for 12 to 15 minutes until the salmon flakes easily and the vegetables are tender with lightly browned edges.'), CookingAssemblyInstructions(step_number=4, description='While it roasts, slice the cucumber and halve the cherry tomatoes. Toss with the spinach, the reserved 1 teaspoon of garlic-dill oil, the juice of half the lemon and the remaining pinch of salt.'), CookingAssemblyInstructions(step_number=5, description='Squeeze the remaining lemon juice over the salmon and quinoa. Plate: Joy gets 120 g salmon, about 1 cup cooked quinoa, a large serving of roasted vegetables and a big portion of salad. Alice gets 90 g salmon, 3/4 cup quinoa, a medium serving of roasted vegetables and a medium salad. Eat slowly and enjoy.')],
    #     nutrition_per_diner=[NutritionPerDinerPerRecipe(diner='Joy', nutrition=NutritionRequirements(calories=600, protein=36.0, fat=24.0, carbohydrates=52.0, fiber=11.0, sodium_max=380.0, minerals=Minerals(calcium=180.0, iron=4.5, potassium=1300.0, magnesium=200.0, zinc=2.5), vitamins=Vitamins(vitamin_a=600.0, vitamin_c=150.0, vitamin_d=10.0, vitamin_e=4.0, vitamin_b6=1.5, vitamin_b12=4.0))), NutritionPerDinerPerRecipe(diner='Alice', nutrition=NutritionRequirements(calories=460, protein=29.0, fat=19.0, carbohydrates=42.0, fiber=9.0, sodium_max=320.0, minerals=Minerals(calcium=150.0, iron=3.5, potassium=1000.0, magnesium=160.0, zinc=2.0), vitamins=Vitamins(vitamin_a=480.0, vitamin_c=120.0, vitamin_d=8.0, vitamin_e=3.0, vitamin_b6=1.2, vitamin_b12=3.0)))],
    #     serving_size_per_diner=[ServingSize(diner='Joy', meal_component=MealComponent(name='Lemon-dill baked salmon', type='main dish'), size='120 grams raw weight (about 1 fillet)'), ServingSize(diner='Joy', meal_component=MealComponent(name='Quinoa', type='side dish'), size='1 cup cooked (50 grams dry)'), ServingSize(diner='Joy', meal_component=MealComponent(name='Roasted broccoli and red bell pepper', type='side dish'), size='1.5 cups (about 200 grams raw weight)'), ServingSize(diner='Joy', meal_component=MealComponent(name='Spinach, cucumber and tomato salad with lemon', type='side dish'), size='2 cups (about 230 grams)'), ServingSize(diner='Alice', meal_component=MealComponent(name='Lemon-dill baked salmon', type='main dish'), size='90 grams raw weight (about 1 small fillet)'), ServingSize(diner='Alice', meal_component=MealComponent(name='Quinoa', type='side dish'), size='3/4 cup cooked (40 grams dry)'), ServingSize(diner='Alice', meal_component=MealComponent(name='Roasted broccoli and red bell pepper', type='side dish'), size='1 cup (about 150 grams raw weight)'), ServingSize(diner='Alice', meal_component=MealComponent(name='Spinach, cucumber and tomato salad with lemon', type='side dish'), size='1.5 cups (about 170 grams)')])

    print(state["recipes"])

    return Command(
        update={"recipes": state["recipes"] + [recipe]},
        goto = "review_week_plan"
    )

def review_week_plan(state: MealPlanAgentState) -> Command[Literal["generate_grocery_list", "chef_agent_node"]]:
    print("Reviewing meal plan for the week...")
    print(state["recipes"])

    if len(state["recipes"]) < 7:
        return Command(
            update={},
            goto = "chef_agent_node"
        )
    else:
        return Command(
            update={},
            goto = "generate_grocery_list"
        ) 


def generate_grocery_list(state: MealPlanAgentState) -> Command[Literal["transform_for_user"]]:
    print("Generating grocery list from meal plan...")

    # Aggregate ingredients from all recipes
    aggregated_ingredients = {}
    for recipe in state["recipes"]:
        for ingredient in recipe.ingredients:
            if ingredient.name not in aggregated_ingredients:
                aggregated_ingredients[ingredient.name] = {
                    "measurement": ingredient.measurement,
                    "unit": ingredient.unit,
                    "quantity": 1
                }
            else:
                aggregated_ingredients[ingredient.name]["quantity"] += 1

    print("Aggregated Grocery List:", aggregated_ingredients)
    return Command(
        update={"aggregated_info": {"grocery_list": aggregated_ingredients}},
        goto = "transform_for_user"
    )

def transform_for_user(state: MealPlanAgentState) -> Command[Literal[END]]:
     #transform for user output
    formatted_recipe = None

    for recipe in state["recipes"]:         
        new = format_recipe(recipe.model_dump())
        formatted_recipe = new if formatted_recipe is None else formatted_recipe + "\n\n" + new
    
    print(f"Generated Meal Plan: {formatted_recipe}")  # Log the result for debugging        

    file = io.BytesIO(formatted_recipe.encode("utf-8")) 
    file.name = f"{state['recipes'][0].title.replace(' ', '_')}.txt"

    with open(file.name, "w", encoding="utf-8") as f:
        f.write(formatted_recipe)

    return Command(
        update={"recipeFile": Path(f.name).resolve()},
        goto = END
    )



async def generate_meal_plan() -> MealPlanAgentState:
  
        workflow = StateGraph(MealPlanAgentState)
        workflow.add_node("initializeDiner",initializeDiner)
        workflow.add_node("chef_agent_node", chef_agent_node)
        workflow.add_node("review_week_plan", review_week_plan)
        workflow.add_node("generate_grocery_list", generate_grocery_list)

        workflow.add_edge(START, "initializeDiner")
        workflow.add_edge("initializeDiner", "chef_agent_node")
        workflow.add_edge("generate_grocery_list", END)

        memory = MemorySaver()
        graph = workflow.compile(checkpointer=memory)

        state: MealPlanAgentState = {"requested_action": "generate_meal_plan", "recipes": [], "diners": [], "aggregated_info": {}}
        
        config = {"configurable": {"thread_id": "meal_123"}}

        result = await graph.ainvoke(state, config, version="v3")       

        return result

class RecipeSchema(LanceModel):
    # Specify the vector column and its exact dimensions (e.g., 384 for all-MiniLM-L6-v2)
    vector: Vector(384)
    text: str


from langsmith import Client
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from meal_planner_agent.vector_langchain_workflow import chat_with_retriever
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

llm = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",        
    )
evaluator = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model=os.getenv("MODEL"),
    judge= llm,
    feedback_key="correctness"
)

def dataset_creation():
    client =Client()
    dataset = client.create_dataset(dataset_name="meal_planner_agent", description="Dataset for meal planner agent evaluation")


    examples = [
        {
            "inputs": {"query": "What are names of the diners?"},
            "outputs": {"answer": "The names of the diners are Joy, and Alice."}
        },
        {
            "inputs": {"query": "What is portion size of chickenfor Joy in first recipe?"},
            "outputs": {"answer": "The portion size of chicken for Joy in the first recipe is 120 gm raw (about 90 gm cooked)."}
        },
        {
            "inputs": {"query": "What is the title of first recipe?"},
            "outputs": {"answer": "Lemon-Herb Chicken with Quinoa-Chickpea Salad and Roasted Veg (Mediterranean)."}
        }
    ]

    client.create_examples(dataset_id=dataset.id, examples=examples)
    print(f"Dataset name: {dataset.name}")
    return dataset


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs:dict):
    
    return evaluator(inputs=inputs, outputs=outputs, reference_outputs=reference_outputs)

def main():
    client = Client()
    if client.has_dataset(dataset_name="meal_planner_agent"):
        dataset = client.delete_dataset(dataset_name="meal_planner_agent")
    
    dataset = dataset_creation()
    print("Dataset created successfully.")
    
    experiment_results = client.evaluate(
        chat_with_retriever,
        data = dataset.name,
        evaluators=[correctness_evaluator],
        experiment_prefix="First eval test",
        max_concurrency=1
    )
    print(f"Experiment results: {experiment_results}")

if __name__ == "__main__":
    main()
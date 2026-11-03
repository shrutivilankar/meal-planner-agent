from ragas import EvaluationDataset, evaluate
from meal_plan_agent.vector_langchain_workflow import maintain_recipes
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from ragas.metrics import LLMContextRecall, FaithFulness, FactualCorrectness
from ragas.llm_wrappers import LangchainLLMWrapper

load_dotenv()
sample_queries = [
    "What are names of the diners?",
    "What is portion size of chickenfor Joy in first recipe?",
    "What is the title of first recipe?"
]

expected_responses = [
    "The names of the diners are Joy, and Alice.",
    "The portion size of chicken for Joy in the first recipe is 120 gm raw (about 90 gm cooked).",
    "Lemon-Herb Chicken with Quinoa-Chickpea Salad and Roasted Veg (Mediterranean)."
]


dataset = []
for query, expected_response in zip(sample_queries, expected_responses):

    response, vector_retriever = maintain_recipes("Lemon-Herb_Chicken_with_Quinoa-Chickpea_Salad_and_Roasted_Veg_(Mediterranean).txt", query)
    context = vector_retriever.retrieve(query)
    dataset.append({
        "user_input": query,
        "retrieved_context": [line for line in context],
        "response": response,
        "reference": expected_response        
    })
evaluation_dataset = EvaluationDataset.from_list(dataset)    

llm = ChatOpenAI(
        model=os.getenv("MODEL"), 
        open_api_key=os.getenv("OPENROUTER_API_KEY"), 
        open_api_base="https://openrouter.ai/api/v1", 
        max_tokens=512
        )
evaluator_llm = LangchainLLMWrapper(llm)
result = evaluate(
    dataset=evaluation_dataset, 
    metrics=[LLMContextRecall(), FaithFulness(), FactualCorrectness()], 
    llm=evaluator_llm)

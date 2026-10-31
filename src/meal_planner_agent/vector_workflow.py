from sentence_transformers import SentenceTransformer
from lancedb.pydantic import LanceModel, Vector
import lancedb
import pandas
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def maintainRecipes(file_path: Path):
    print("inside maintainRecipes")

    with open(file_path, "r", encoding="utf-8") as f:
        content= f.read()
    chunks = content.splitlines()
    print(f"chunks: {chunks}")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks).astype("float32")
    # vector_dimension = embeddings.shape[1]
    # index = faiss.IndexFlatL2(vector_dimension)
    # index.add(embeddings)
    # print(f"Total entries successfully indexed: {index.ntotal}")

    dataFrame = pandas.DataFrame({
        "text": chunks,
        "vector": embeddings.tolist()
    })

    db = lancedb.connect("./myRecipesLanceDb")
    table = db.create_table("recipes_table", data=dataFrame, mode="overwrite")

    print(f"Total entries successfully inserted: {len(table)}")

    query_text = "What is the first recipe name?"

    result = find_answer_to_user_query(query_text)

    call_llm_reply_to_user(result, query_text)

    

def find_answer_to_user_query(query_text: String):

    
    db = lancedb.connect("./myRecipesLanceDb")
    table1 = db.open_table("recipes_table")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    query_vector = model.encode(query_text).astype("float32").tolist()

    results_df = table1.search(query_vector).limit(3).to_pandas()

    print(results_df[["text","_distance"]])
    return results_df

def call_llm_reply_to_user(dataframe: DataFrame, query_text: String):
    retrieved_texts = dataframe["text"].tolist()
    context = "\n --- \n".join(retrieved_texts)

    system_prompt = (
        "You are a helpful kitchen assistant. Answer the user's question using ONLY the provided recipe context.If the context doesn't contain the answer, "
        "say 'I cannot find that in the recipe book.'"
    )
    user_prompt = f"""Context from recipe book: {context}
    Question: {query_text}
    Answer: """

    client = OpenAI(
        api_key= os.getenv("OPENROUTER_API_KEY"),
        base_url= "https://openrouter.ai/api/v1"
    )

    result = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages = [{ "role":"system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        max_completion_tokens = 2000,
        temperature = 0.2,
        reasoning_effort = "low",
    )

    print(result.choices[0].message)
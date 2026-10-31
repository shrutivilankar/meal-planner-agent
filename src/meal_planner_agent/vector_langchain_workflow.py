
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_core.documents import Document
from langchain_classic.retrievers.document_compressors import FlashrankRerank
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import LanceDB
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# from sentence_transformers import SentenceTransformer
# from lancedb.pydantic import LanceModel, Vector
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

    documentlist = [Document(page_content=text, metadata={"source": "diet recipes"}) for text in chunks]

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    db = lancedb.connect("./chain_recipes_db")
    vector_store = LanceDB.from_documents(
        documents = documentlist,
        embedding = embeddings,
        connection = db,
        table_name = "recipes"

    )
    print(f"Successfully created table recipes and ingested vectors.")

    query = "what is portion size for Joy?"

    #search_results = vector_store.similarity_search(query, k=2)
    

    prompt = ChatPromptTemplate([
        ("system", "You are a helpful kitchen assistant. Answer the user's question using ONLY the provided context.If the context doesn't contain the answer, say 'I cannot find that in the recipe book.'"),
        ("human", "Question: {question}")
    ]
    )
    vector_retriever = vector_store.as_retriever(search_kwargs={"k":1})


    rag_chain = (
        {
            "context": vector_retriever,
            "question":RunnablePassthrough()
        }
        | prompt
        | RunnableLambda(call_llm_reply_to_user)
        | StrOutputParser()
    )

    print(f"question: {query}")
    answer = rag_chain.invoke(query)

    print(f"Result:\n{answer}")

    # compressor_flashrank = FlashrankRerank(model="ms-marco-MiniLM-L-12-v2")

    # vector_retriever = vector_store.as_retriever(search_kwargs={"k":15})

    # compression_retriever = ContextualCompressionRetriever(
    #     base_compressor=compressor_flashrank,
    #     base_retriever = vector_retriever
    # )

    # search_results = compression_retriever.invoke(query)


    # print(f"\n--- Search Results for Query: '{query}' ---")
    # for idx, doc in enumerate(search_results):
    #     print(f"\nMatch #{idx + 1}:")
    #     print(f"Content: {doc.page_content}")
    #     print(f"Metadata: {doc.metadata}")
    













def call_llm_reply_to_user(formatted_prompt):
  

    client = OpenAI(
        api_key= os.getenv("OPENROUTER_API_KEY"),
        base_url= "https://openrouter.ai/api/v1"
    )

    result = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages = [{ "role":"user", "content": formatted_prompt.to_string()}],
        max_completion_tokens = 2000,
        temperature = 0.2,
        reasoning_effort = "low",
    )
    print(result.choices[0].message)

    return result.choices[0].message.content

    
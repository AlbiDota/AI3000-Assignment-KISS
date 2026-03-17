"""
================================
MAIN PROGRAM
================================
REFERENCE FILES:
    06_embeddings_and_similarity.py
    07_simple_rag.py

IDEAS AND GOALS:
We want to use embeddings to convert texts from json into a list of vectors.
Semantically similar texts -> similar vectors. 
This way, we want to create a kind of AI-wrapper to act 
like a chatbot with knowledge limited strictly to our written information.
With limited pre-defined knowledge, we can hopefully avoid hallucinations.

SEMANTIC VECTORS & COSINE DISTANCE:
We will pre-load one or more difference "libraries" of rules
This pre-loaded information will be our "knowledge base."
With this knowledge base, we find its semantic vectors
using "all-MiniLM-L6-v2" embeddings.
    1.0 = identical meaning
    0.0 = completely unrelated

BASIC FLOW:
First we choose the relevant "knowledge library",
and load its vectors.
Then the user inputs a question, which we also need to transform to vector-format.
We calculate cosine similarity between user input
and knowledge base of chosen library and filter out
the "weaker" matches, or append their "score" in some way.
Afterwards, we feed the relevant options from the knowledge base
into a bigger prompt, along with the users input question.
This prompt will be formatted and fed to a free version
of "claude-sonnet-4-2025-05-14"
Then we return claudes answer to the user.

REQUIREMENTS:
    pip install sentence-transformers openai python-dotenv

"""
# dependencies n stuff
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# api key from env file :D
load_dotenv()

# our knowledge libraries of doom
import faq
import internal_doc

def chatbot(type, question):
    
    # input validation
    if type != "faq" and type != "internal":
        return {"status":400, "message":"Bad request: type must be 'internal' or 'faq'"}

    # fetching correct knowledge base, based on specified type
    knowledge_base = []
    if type=="faq":
        knowledge_base = faq.faq_data
    elif type=="internal":
        knowledge_base = internal_doc.internal_kb
    

    # declaring embedding tool
    # embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # pre-loading embeddings for chosen documents
    # optimally, we would do this once and store them permanently in separate documents or db :D
    doc_texts = [doc["content"] for doc in knowledge_base]
    doc_embeddings = embedder.encode(doc_texts)

    # helper function for finding top_k most relevant documents for the given query
    def retrieve(q, top_k=2):
        # get vectors for question
        question_embeddings = embedder.encode(q).reshape(1, -1)

        # compare with document vectors
        scores = cosine_similarity(question_embeddings, doc_embeddings)[0]

        # get indexes of top hits
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for i in top_indices:
            results.append({
                "document": knowledge_base[i],
                "score": scores[i]
            })
        return results
    # end of helper function

    # calling helper function to retrieve relevant documents with cosine similarity
    retrieved = retrieve(q=question, top_k=5)
    # print(retrieved)
    # retrieve relevant documents and build prompt
    context_parts = []
    for i, result in enumerate(retrieved, 1):
        doc = result["document"]
        context_parts.append(
            f"[Source: {doc["id"]} - {doc["title"]}]\n{doc["content"]}"
        )
    context = "\n\n".join(context_parts)

    prompt = f"""
    Answer the question based ONLY on the following documents.
    If the answer is NOT in the documents, say "I don't have information about that."
    Always mention which source document(s) you used.

    DOCUMENTS:
    {context}

    QUESTION: {question}

    ANSWER:
    """

    # final step
    # send to llm
    try:
        from openai import OpenAI

        client = OpenAI()

        system_prompt = "You are a chatbot for our game store. Answer truthfully and concise."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        # if response:
            # print(f"{response.choices[0]}")
        # return
        return {"status": 200, "response": response.choices[0].message.content}
    
    except Exception as e:
        return {"status":500, "message":f"{str(e)}"}


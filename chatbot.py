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
We have a budget of $9 at openAI to play around with their different models.
We send the prompt to our chosen model,
Then we return its answer to the user.

REQUIREMENTS:
    pip install sentence-transformers openai python-dotenv

"""
# dependencies n stuff
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import json

# api key from env file :D
load_dotenv()

# our knowledge libraries of doom
# import documents.faq as faq
# import documents.internal_doc as internal_doc
# swapped with json files for a better and more realistic approach

def chatbot(type, question, history=None):
    
    # input validation
    if type != "faq" and type != "internal":
        return {"status":400, "message":"Bad request: type must be 'internal' or 'faq'"}

    if not question:
        return {"status":400, "message":"Bad request: missing question"}

    # fetching correct knowledge base, based on specified type
    knowledge_base = []
    if type=="faq":
       with open('documents/faq.json', 'r') as f:
            knowledge_base = json.load(f)
    elif type=="internal":
        with open('documents/internal_kb.json', 'r') as f:
            knowledge_base = json.load(f)
    

    # declaring embedding tool
    # embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # fetching semantic vectors from document
    doc_embeddings = np.array([doc["semantic_vectors"] for doc in knowledge_base])

    # helper function for finding top_k most relevant documents for the given query
    def retrieve(q, top_k=2):
        # get vectors for question
        question_embeddings = embedder.encode(q).reshape(1, -1)

        # compare with document vectors
        scores = cosine_similarity(question_embeddings, doc_embeddings)[0]
        print(scores)
        # get indexes of top hits
        top_indexes = np.argsort(scores)[::-1][:top_k]

        results = []
        for i in top_indexes:
            results.append({
                "document": knowledge_base[i],
                "score": scores[i]
            })
        return results
    # end of helper function

    # calling helper function to retrieve relevant documents with cosine similarity
    retrieved = retrieve(q=question, top_k=8)
    # print(retrieved)
    # retrieve relevant documents and build prompt
    context_parts = []
    for i, result in enumerate(retrieved, 1):
        doc = result["document"]
        context_parts.append(
            f"[Source: {doc["id"]} - {doc["title"]}]\n{doc["content"]}"
        )
    context = "\n\n".join(context_parts)
    # print(context)

    prompt = f"""

    Du skal svare KUN basert på følgende "documents" og context/history (hvis du har blitt gitt noe).
    HVIS du IKKE klarer å produsere et godt svar utifra "documents" eller contexten du er gitt, MÅ du innrømme at du 
    mangler informasjon, og svar gjerne med "Det har jeg ikke tilstrekkelig med informasjon om" eller liknende.
    ALLTID nevn hvilke kilder du har brukt fra "documents" Kildehenvisninger skal KUN foregå på slutten av svaret ditt.
    Kilder skal ALLTID være på slutten av svaret, og formattert for eksempel som "kilder brukt: faq-034, faq-025, faq-026, faq-031"
    Du skal svare kort og ryddig.

    HISTORY/CONTEXT:
    {history}

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

        # system_prompt = "You are a chatbot and knowledge-base for our game store. Answer truthfully and concise."
        system_prompt = "Du er en chatbot og knowledge-base for vår spillbutikk. Du skal svare ærlig og kort. (Du er navngitt 'bot' i chat context)"

        # messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if history:
            messages.extend(history);
        
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="gpt-5-nano",
            # messages=[
            #     {"role": "system", "content": system_prompt},
            #     {"role": "user", "content": prompt}
            # ]
            messages=messages
        )
        if response:
            usage = response.usage
            print("Prompt tokens:", usage.prompt_tokens)
            print("Completion tokens:", usage.completion_tokens)
            print("Total tokens:", usage.total_tokens)
            
        # return
        return {"status": 200, "response": response.choices[0].message.content}
    
    except Exception as e:
        return {"status":500, "message":f"{str(e)}"}


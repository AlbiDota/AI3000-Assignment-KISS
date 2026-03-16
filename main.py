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
    pip install sentence-transformers

"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


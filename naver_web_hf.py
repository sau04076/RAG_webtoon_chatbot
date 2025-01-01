import os
import streamlit as st
from elasticsearch import Elasticsearch
from transformers import pipeline

# Required Environment Variables
# cloud_id - Elastic Cloud Deployment ID
# cloud_user - Elasticsearch Cluster User
# cloud_pass - Elasticsearch User Password

# Connect to Elastic Cloud cluster
def es_connect(cid, user, passwd):
    es = Elasticsearch(cloud_id=cid, http_auth=(user, passwd))
    return es

# Search Elasticsearch index and return body and URL of the result
def search(query_text):
    cid = 'My_deployment:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQyYThmNjY1NjFkOGQ0YzNkYjFkYmQ2MWU4MTFmNmViOCQwMGJlYTFjMmM3NjM0NTJlYWYyZmZiNGQwMTBlMGNjNw=='
    cp = 'rOExSFwoQrHT8iXYLpggryBX'
    cu = 'elastic'
    es = es_connect(cid, cu, cp)

    # Elasticsearch query (BM25) and kNN configuration for hybrid search
    query = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["*"],
                "operator": "or"
            }
        }
    }

    index = 'naver_webtoon'
    resp = es.search(index=index, body=query, size=1)

    if resp['hits']['hits']:
        if len(resp['hits']['hits']) > 0:
            body = resp['hits']['hits'][0]['_source']
        else:
            body = "No documents found in the hits."
    else:
        body = "No results found."

    return body

# Generate a response from ChatGPT based on the given prompt
def chat_gpt(prompt, model):
    generator = pipeline('text-generation', model=model, device=0)
    response = generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
    return response

st.title("네이버 웹툰 검색\nBy 박희망(DiLab)")

# Main chat form
with st.form("chat_form"):
    query = st.text_input("You: ")
    submit_button = st.form_submit_button("Send")

# Generate and display response on form submission
negResponse = "I'm unable to answer the question based on the information I have from Elastic Docs."
if submit_button:
    resp = search(query)
    prompt = f"Answer this question in Korean: {query}\nUsing only the information from this Elastic Doc: {resp}\nIf the answer is not contained in the supplied doc reply '{negResponse}' and nothing else"
    answer = chat_gpt(prompt, model="davidkim205/komt-Llama-2-7b-chat-hf-lora")

    if negResponse in answer:
        st.write(f"ChatGPT: {answer.strip()}")
    else:
        st.write(f"ChatGPT: {answer.strip()}\n")
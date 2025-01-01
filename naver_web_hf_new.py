import os
import streamlit as st
import openai
from elasticsearch import Elasticsearch

# This code is part of an Elastic Blog showing how to combine
# Elasticsearch's search relevancy power with
# OpenAI's GPT's Question Answering power
# https://www.elastic.co/blog/chatgpt-elasticsearch-openai-meets-private-data

# Code is presented for demo purposes but should not be used in production
# You may encounter exceptions which are not handled in the code


# Required Environment Variables
# openai_api - OpenAI API Key
# cloud_id - Elastic Cloud Deployment ID
# cloud_user - Elasticsearch Cluster User
# cloud_pass - Elasticsearch User Password

openai.api_key = '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'
model = "gpt-3.5-turbo-0301"

# Connect to Elastic Cloud cluster
def es_connect(cid, user, passwd):
    es = Elasticsearch(cloud_id=cid, http_auth=(user, passwd))
    return es

# Search ElasticSearch index and return body and URL of the result
def search(query_text):
    cid = '9e66664f7f9f483bb0fb06bfd955aeea:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRlOGQyOTQ2YjdlYWY0MDYxYTNlMDZkYjllNjY3ZDgzOSRjZGFmODQ1MTQwNzY0Yzg4ODY1NThhODU0ODE4ZmM1Ng=='
    cp = 'FDbEf5MFsfsJGfz32ddZWExY'
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

    #fields = ["text_embedding.predicted_value"]
    index = 'naver_webtoon_all'
    resp = es.search(index=index,
                     body=query,
                     #knn=knn,
                     #fields=fields,
                     size=1,
                     #source=False
                     )

    if resp['hits']['hits']:
        if len(resp['hits']['hits']) > 0:
            body = resp['hits']['hits'][0]['_source']
        else:
            body = "No documents found in the hits."
    else: body = "No results found."

    return body

def truncate_text(text, max_tokens):
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text

    return ' '.join(tokens[:max_tokens])

# Generate a response from ChatGPT based on the given prompt
def chat_gpt(prompt, model="gpt-3.5-turbo", max_tokens=4096, max_context_tokens=4096, safety_margin=5):
    # Truncate the prompt content to fit within the model's context length
    truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)

    response = openai.ChatCompletion.create(model=model,
                                            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": truncated_prompt}])

    return response["choices"][0]["message"]["content"]


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
    answer = chat_gpt(prompt)
    
    if negResponse in answer:
        st.write(f"ChatGPT: {answer.strip()}")
    else:
        st.write(f"ChatGPT: {answer.strip()}\n")
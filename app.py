import os
from langchain_community.embeddings.llamacpp import LlamaCppEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

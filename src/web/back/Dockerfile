FROM condaforge/miniforge3:latest

WORKDIR /app

#  Copy the Conda environment spec from the repo root into /app
#  We'll build with “docker build -f src/web/back/Dockerfile .”
#  so the build context is the repo root, where environment.yml lives.
COPY environment-backend.yml /app/

RUN conda env create --quiet --file environment-backend.yml

SHELL ["conda", "run", "-n", "stock-backend", "/bin/bash", "-lc"]

# Copy the entire repository into /app (so that .dvc/config and data/processed/*.dvc are available)
# We copy “.” because the build context is the repo root.
COPY . /app

EXPOSE 8000

COPY src/web/back/docker-entrypoint-back.sh /app/docker-entrypoint-back.sh
RUN chmod +x /app/docker-entrypoint-back.sh

# Default environment variables (to be overridden in Azure)
ENV AZURE_STORAGE_CONNECTION_STRING=""
ENV LANGSMITH_API_KEY=""
ENV GOOGLE_API_KEY=""
ENV GOOGLE_API_KEY_1=""
ENV GENERATIVE_MODEL="gemini-2.5-flash-preview-05-20"
ENV SIMPLE_TASK_MODEL="gemini-2.0-flash-lite"
ENV EMBEDDING_MODEL="models/text-embedding-004"
ENV USER_AGENT="DefaultLangchainUserAgent"
ENV PINECONE_API_KEY=""
ENV INDEX_NAME=""
ENV KERAS_BACKEND="torch"
ENV BACKEND_CACHE_EXPIRATION_TIME=""
ENV DISABLE_BACKEND_CACHE="false"
ENV FRONTEND_URL=""


SHELL ["/bin/bash", "-lc"]

ENTRYPOINT [ "/app/docker-entrypoint-back.sh" ]

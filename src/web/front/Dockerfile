FROM condaforge/miniforge3:latest

WORKDIR /app

COPY environment-frontend.yml /app/

RUN mamba env create --quiet --file environment-frontend.yml \
 && conda clean -afy \
 && mamba clean --all --yes

 SHELL ["conda", "run", "-n", "stock-frontend", "/bin/bash", "-lc"]

# Copy the repo into /app so that your app files are available
COPY . /app

EXPOSE 8501

# Default environment variables (to be overridden in Azure)
ENV BACKEND_URL=""
ENV FRONTEND_CACHE_EXPIRATION_TIME="300"
ENV WINDOW_SIZE=""

SHELL ["/bin/bash", "-lc"]

ENTRYPOINT ["bash", "-lc", "source /opt/conda/etc/profile.d/conda.sh && conda activate stock-frontend && streamlit run src/web/front/home.py --server.port 8501 --server.address 0.0.0.0"]

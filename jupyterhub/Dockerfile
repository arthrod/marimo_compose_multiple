FROM quay.io/jupyterhub/jupyterhub:latest

# Install dependencies
RUN cd /srv/jupyterhub && jupyterhub --generate-config && \
    pip install uv && \
    uv pip install --no-cache-dir \
        dockerspawner \
        psycopg2-binary \
        click \
        nbformat \
        anthropic \
        notebook \
        'marimo>=0.6.21' \
        jupyter-collaboration \
        oauthenticator \
        https://github.com/jyio/jupyter-marimo-proxy/archive/main.zip \
        --system --break-system-packages

# Create directory for JupyterHub state
RUN mkdir -p /srv/jupyterhub

# Create shared directory
RUN mkdir -p /shared && chmod 777 /shared

# Copy JupyterHub config file
COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

# Set working directory
WORKDIR /srv/jupyterhub

# Expose the port JupyterHub will run on
EXPOSE 8000/tcp

# Start JupyterHub
CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]

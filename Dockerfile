FROM quay.io/jupyterhub/jupyterhub:latest

# Accept password arguments
ARG ARTHRODPASS
ARG GUESTPASS
ARG PCPASS
ARG FORTUNAPASS

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
        https://github.com/jyio/jupyter-marimo-proxy/archive/main.zip \
        --system --break-system-packages

# Create users with passwords from environment variables
RUN useradd -m -s /bin/bash arthrod && \
    echo "arthrod:${ARTHRODPASS}" | chpasswd && \
    useradd -m -s /bin/bash guest && \
    echo "guest:${GUESTPASS}" | chpasswd && \
    useradd -m -s /bin/bash pc && \
    echo "pc:${PCPASS}" | chpasswd && \
    useradd -m -s /bin/bash fortuna && \
    echo "fortuna:${FORTUNAPASS}" | chpasswd && \
    mkdir -p /shared && \
    chmod 777 /shared

EXPOSE 8000/tcp

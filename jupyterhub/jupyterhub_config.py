import os
import random
import string
from pathlib import Path

from jupyterhub.config import get_config

# JupyterHub config object
c = get_config()

# -----------------------------------------------------------------------------
# Generic JupyterHub Options
# -----------------------------------------------------------------------------
# JupyterHub will listen on port 8000 by default. In Docker Compose,
# we expose that port externally. SSL is assumed to be handled by Coolify.
c.JupyterHub.bind_url = "http://:8000"

# Use a simple SQLite database stored in /srv/jupyterhub/jupyterhub.sqlite
c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/jupyterhub.sqlite"

# Persist cookie secret & database in /srv/jupyterhub (mounted volume)
c.JupyterHub.cookie_secret_file = "/srv/jupyterhub/jupyterhub_cookie_secret"

# Allows each user to spawn multiple named servers (e.g., personal + communal).
c.JupyterHub.allow_named_servers = True

# (Optional) If you want to limit the max named servers per user:
# c.JupyterHub.named_server_limit_per_user = 3

# -----------------------------------------------------------------------------
# Authenticator: GitHub OAuth
# -----------------------------------------------------------------------------
from oauthenticator.github import GitHubOAuthenticator

c.JupyterHub.authenticator_class = GitHubOAuthenticator

# Read these from environment variables (set via Coolify or .env)
client_id = os.environ.get("GITHUB_CLIENT_ID", "")
client_secret = os.environ.get("GITHUB_CLIENT_SECRET", "")
callback_url = os.environ.get("OAUTH_CALLBACK_URL", "")
c.GitHubOAuthenticator.client_id = client_id
c.GitHubOAuthenticator.client_secret = client_secret
c.GitHubOAuthenticator.oauth_callback_url = callback_url

# (Optional) Restrict to specific GitHub org(s):
# allowed_orgs = os.environ.get("ALLOWED_GITHUB_ORGS", "")
# if allowed_orgs:
#     c.GitHubOAuthenticator.allowed_organizations = {org.strip() for org in allowed_orgs.split(",")}

# Admin users (comma-separated GH usernames in ADMIN_GITHUB_USERS)
admin_users_env = os.environ.get("ADMIN_GITHUB_USERS", "")
if admin_users_env:
    c.Authenticator.admin_users = {u.strip() for u in admin_users_env.split(",")}

# By default, no user is blocked, so any GitHub login can access the server
# (unless you specify allowed_organizations or a userlist approach).

# -----------------------------------------------------------------------------
# Spawner: DockerSpawner
# -----------------------------------------------------------------------------
from dockerspawner import DockerSpawner

c.JupyterHub.spawner_class = DockerSpawner

# The Docker image(s) used for single-user notebook containers.
# We'll define a dictionary to let users pick from multiple images.
# (In the UI, they can choose on spawn if we set an options form.)
base_image = os.environ.get("DOCKER_NOTEBOOK_IMAGE_BASE", "jupyter/base-notebook:latest")
datascience_image = os.environ.get("DOCKER_NOTEBOOK_IMAGE_DATASCIENCE", "jupyter/datascience-notebook:latest")

# We'll provide an 'options form' below to let each user select which image to spawn.
c.DockerSpawner.allowed_images = {
    "Base Notebook": base_image,
    "DataScience Notebook": datascience_image
}

# Where notebooks will be stored inside the container
c.DockerSpawner.notebook_dir = "/home/jovyan/work"

# Create a dedicated Docker volume for each user's server:
# We'll name volumes like jhub-user-<username>-<servername>
c.DockerSpawner.volumes = {
    # Each server is unique by user + server name
    "jhub-user-{username}-{servername}": "/home/jovyan/work"
}

# Have the Docker containers join the same network as the Hub
c.DockerSpawner.network_name = "hubnet"

# JupyterLab as default interface
c.Spawner.default_url = "/lab"

# Clean up containers when user stops server
c.DockerSpawner.remove = True

# If using named servers, you might want to limit CPU/memory usage or set container names differently.

# -----------------------------------------------------------------------------
# Container Name Templates
# -----------------------------------------------------------------------------
# The default container name is something like jupyter-{username}, but with named servers,
# we can do jupyter-{username}-{servername}.
c.DockerSpawner.container_name_template = "jupyter-{username}-{servername}"

# -----------------------------------------------------------------------------
# Using the JupyterHub form to let users pick an image
# -----------------------------------------------------------------------------
def _options_form(spawner):
    """Generate HTML form for user to pick which Docker image to spawn."""
    # Build radio buttons from allowed_images
    option_lines = []
    for name, image in c.DockerSpawner.allowed_images.items():
        option_lines.append(
            f'<option value="{image}">{name}</option>'
        )
    options_html = "".join(option_lines)
    return f"""
    <label for="image">Select your notebook image:</label>
    <select name="image" id="image">
        {options_html}
    </select>
    <br>
    <p>You can spawn multiple servers (e.g., 'personal', 'communal') by selecting a server name in the JupyterHub UI. Everyone with the link to a communal server can collaborate if you share credentials or if real-time collaboration is enabled.</p>
    """

c.Spawner.options_form = _options_form

def options_from_form(spawner, formdata):
    """Parse the form submission to set spawner.image."""
    image = formdata.get('image', [''])[0].strip()
    if image in c.DockerSpawner.allowed_images.values():
        spawner.image = image
    else:
        # default fallback
        spawner.image = base_image

c.Spawner.options_from_form = options_from_form

# -----------------------------------------------------------------------------
# Real-Time Collaboration (Optional)
# -----------------------------------------------------------------------------
# JupyterLab 3.2+ supports Google Docs-style collaboration. If you want that:
# c.Spawner.args = ['--collaborative']

# -----------------------------------------------------------------------------
# Hub IP / Container Bridge
# -----------------------------------------------------------------------------
# If JupyterHub fails to connect to user containers, explicitly set hub_ip to the Docker gateway.
# For a single-node Compose, often the default works. If needed:
# c.JupyterHub.hub_ip = 'jupyterhub'  # The container name or IP inside the Docker network

# -----------------------------------------------------------------------------
# Random Secret Generation (Optional)
# -----------------------------------------------------------------------------
# If you want to supply a cookie secret or let Hub generate. Usually the volume persists it.
if not Path("/srv/jupyterhub/jupyterhub_cookie_secret").exists():
    secret = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    with Path("/srv/jupyterhub/jupyterhub_cookie_secret").open("w") as f:
        f.write(secret)
    print("Generated a new cookie secret at /srv/jupyterhub/jupyterhub_cookie_secret")

# Done!

# Implementation Checklist

- [x] 1. Basic Setup
  - [x] Directory structure setup
  - [x] Docker Compose configuration
  - [x] JupyterHub Dockerfile
  - [x] Environment variables configuration

- [x] 2. Authentication Setup
  - [x] GitHub OAuth configuration
  - [x] JupyterHub authenticator setup
  - [x] Admin users configuration

- [x] 3. Container Management
  - [x] DockerSpawner configuration
  - [x] Multiple image support
  - [x] Named servers support
  - [x] Volume persistence setup

- [x] 4. Networking & Security
  - [x] Docker network configuration
  - [x] SSL/HTTPS setup
  - [x] Cookie secret management

- [x] 5. User Experience
  - [x] JupyterLab as default interface
  - [x] Server options form
  - [ ] Resource limits configuration
  - [ ] Idle server culling

- [ ] 6. Testing & Deployment
  - [ ] Local testing
  - [ ] GitHub OAuth app creation
  - [ ] Coolify deployment
  - [ ] End-to-end testing

JupyterHub with Individual JupyterLab Instances (DockerSpawner)
Overview: This approach deploys JupyterHub as a central service that spawns a dedicated JupyterLab server for each user. Each user’s server runs in an isolated Docker container (using DockerSpawner) with its own workspace. JupyterHub manages authentication through GitHub OAuth, so users log in with their GitHub credentials. User data is stored on persistent volumes, ensuring notebooks aren’t lost when containers stop. All configuration can be supplied via environment variables (suitable for Coolify), and SSL is offloaded to Coolify’s proxy (JupyterHub itself can run on HTTP internally).Key Features:
Isolated per-user environments: Using DockerSpawner, JupyterHub launches a separate single-user JupyterLab instance in a Docker container (using DockerSpawner) with its own workspace.
GITHUB.COM
. This provides strong isolation (each user has their own Linux environment, Python packages, etc.).
GitHub OAuth Authentication: JupyterHub integrates with GitHub OAuth via the OAuthenticator plugin. Users are redirected to GitHub to log in, and upon success JupyterHub spawns their container. You’ll need to register a GitHub OAuth app and set the credentials in JupyterHub’s config (more below).
Persistent storage: Each user’s container can mount a Docker volume for the home directory or workspace. This means user notebooks and data persist between sessions. For example, you can map a host path or named volume to /home/jovyan (if using Jupyter Docker stacks) so that when a container is removed, the data remains
GITHUB.COM
.
Coolify compatibility: All necessary configuration (GitHub OAuth credentials, DockerSpawner settings, etc.) can be provided via environment variables or an .env file, which Coolify supports. No in-container SSL setup is needed – JupyterHub can listen on an internal port without HTTPS, because Coolify will terminate SSL at the proxy level.
Deployment Steps:
Prepare a JupyterHub Docker image: Use the official JupyterHub Docker image or build a custom one that includes the DockerSpawner and OAuthenticator. For example, you might start from the jupyterhub/jupyterhub image and pip install dockerspawner oauthenticator. JupyterHub is designed to manage multiple single-user servers
GITHUB.COM
, and DockerSpawner enables it to launch those servers in Docker containers
GITHUB.COM
. Ensure JupyterLab is available in the single-user image (e.g. by using Jupyter Docker stack images like jupyter/base-notebook or similar as the spawn target).
Configure GitHub OAuth credentials: In GitHub, create an OAuth App for your JupyterHub deployment. Set the Authorization Callback URL to https://<your-domain>/hub/oauth_callback (if Coolify provides a domain, use that)
GITHUB.COM
. In Coolify’s interface (or your environment), set the following environment variables for JupyterHub before launch
JUPYTERHUB.READTHEDOCS.IO
:
GITHUB_CLIENT_ID – the Client ID of your GitHub OAuth app
GITHUB_CLIENT_SECRET – the Client Secret of the OAuth app (store this securely)
OAUTH_CALLBACK_URL – the callback URL, e.g. https://<your-domain>/hub/oauth_callback
JupyterHub’s GitHub OAuthenticator will use these values to perform OAuth. (These correspond to JupyterHub config keys c.GitHubOAuthenticator.client_id, client_secret, and oauth_callback_url, which the OAuthenticator reads from the environment by default
JUPYTERHUB.READTHEDOCS.IO
.) Note: Keep the client secret safe (use Coolify’s secret storage if available)
GITHUB.COM
.
Enable GitHub OAuth in JupyterHub: Set JupyterHub to use the GitHub OAuthenticator. This is done by configuring:
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
You can supply this in a jupyterhub_config.py or via the environment (some images allow $AUTHENTICATOR_CLASS env). If using a config file, mount it into the container via Coolify. You may also specify allowed users or organizations – for example, limit login to members of a GitHub org by setting c.GitHubOAuthenticator.allowed_organizations = {'YourOrg'} (via env var OAUTHenticator_ALLOWED_ORGANIZATIONS). If you want to allow any GitHub user (open signup), you can set c.Authenticator.allowed_users = set() and perhaps c.Authenticator.allow_all = True
GITHUB.COM
.
Configure DockerSpawner for user containers: In JupyterHub’s config, set the spawner class and Docker options. Key settings include:
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner' – enables DockerSpawner
GITHUB.COM
.
Single-user image: c.DockerSpawner.image = 'jupyter/base-notebook:latest' (or any Docker image that launches JupyterLab). This is the image each user container will run
GITHUB.COM
.
Default to JupyterLab: Ensure the spawned notebooks open JupyterLab by default. Set c.Spawner.default_url = '/lab'
GITHUB.COM
 so that users get the JupyterLab interface instead of the classic notebook.
Networking: If needed, set c.DockerSpawner.network_name to the Docker network that JupyterHub and user containers will share (in Docker-compose or Coolify, ensure they join the same network). Also, JupyterHub needs to know its IP for containers to reach it – in DockerSpawner this is often the Docker bridge IP. You can set c.JupyterHub.hub_ip = '0.0.0.0' or the internal hostname so containers can callback to Hub
GITHUB.COM
. (In many cases, leaving it default works if using DockerSpawner in a single Docker host setup.)
Persistent volumes: Use DockerSpawner’s volume mapping to persist data. For example: c.DockerSpawner.notebook_dir = '/home/jovyan/work' and c.DockerSpawner.volumes = { 'jhub-user-{username}': '/home/jovyan/work' }
GITHUB.COM
. This maps a Docker volume (named with the user’s name) into the container’s working directory. Replace with paths appropriate for your image (in Jupyter Docker stack images, home is usually /home/jovyan). This ensures that stopping/restarting a user’s container retains their files.
Environment and runtime settings (Coolify specifics): In Coolify, set the environment variables from steps 2 and any others required (such as JupyterHub’s internal cookie secret or proxy token if needed – though if not set, JupyterHub will auto-generate a cookie secret). For simplicity, you might also set JUPYTERHUB_COOKIE_SECRET to a random hex and CONFIGPROXY_AUTH_TOKEN (the proxy auth token) as env vars
JUPYTERHUB.READTHEDOCS.IO
, or let JupyterHub generate them. Disable JupyterHub’s internal SSL: do not set c.JupyterHub.ssl_key/cert (leave them unset). Instead, configure JupyterHub to listen on HTTP. By default, JupyterHub listens on port 8000 – you can keep that. Coolify will provide the external HTTPS endpoint. Make sure JupyterHub knows it’s behind a proxy (set c.JupyterHub.bind_url = 'http://:8000' and perhaps c.JupyterHub.allow_remote_access = True if needed). This way, all OAuth callback URLs use the external https address but JupyterHub itself doesn’t do SSL (avoids conflicts with Coolify’s SSL).
Launch JupyterHub: Deploy the JupyterHub service through Coolify with the above configuration. Once running, users can access the Hub via the provided URL. On first visit, JupyterHub will redirect them to GitHub to authenticate. After GitHub OAuth login and consent, GitHub redirects back to JupyterHub (/hub/oauth_callback). JupyterHub then creates a new container for the user (using DockerSpawner) and directs the user to their running JupyterLab instance
GITHUB.COM
. From the user’s perspective, they log in with GitHub and “magically” get their own JupyterLab workspace in the browser. Each user’s server is isolated, and they cannot interfere with each other’s environment or files (unless shared volumes are intentionally configured). Admins can use JupyterHub’s admin panel to stop/start user servers as needed.
This JupyterHub-based solution is a robust, production-grade setup for multi-user Jupyter environments. It requires a bit more initial setup (OAuth app registration and config), but after deployment it’s largely self-managing. Each user’s environment persists and is secure. The use of DockerSpawner means you can also customize the single-user image (e.g., pre-install certain libraries for all users) easily by updating the image.

Below is a **complete Docker Compose-based** solution (“Implementation #1”) featuring:

- **JupyterHub** as a single service (so from Coolify’s perspective, it’s one container to deploy).
- **GitHub OAuth** for user authentication (no manual tokens needed).
- **DockerSpawner** to launch **separate JupyterLab containers** for each user (isolation).
- **Multiple single-user notebook images** offered (so each user can select a “base” or “datascience” environment, for example).
- **Named servers** enabled, allowing each user to spawn multiple servers (e.g., one personal server and one “communal” server that multiple people can work in if they share the link).
- **Persistent storage**:
  1. A volume for JupyterHub’s own state (cookie secret, database).
  2. Per-user volumes so that each user’s notebooks/data persist across container restarts.

This setup is designed for **Coolify** deployment:
- You provide environment variables (like `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`) in Coolify’s dashboard.
- Coolify will handle **HTTPS certificates and domain** routing, so no SSL is configured inside JupyterHub (it listens on HTTP).
- From JupyterHub’s perspective, the OAuth callback URL is HTTPS-based (the domain provided by Coolify).

## File/Directory Layout

A recommended structure is:

```
your_project/
├─ docker-compose.yml
└─ jupyterhub/
    ├─ Dockerfile
    └─ jupyterhub_config.py
```

1. **`docker-compose.yml`** – Defines the JupyterHub service (the only container from Compose’s perspective).
2. **`jupyterhub/Dockerfile`** – Builds a custom image, installing `oauthenticator` (for GitHub OAuth) and `dockerspawner`.
3. **`jupyterhub/jupyterhub_config.py`** – The JupyterHub configuration (DockerSpawner, GitHub OAuth, named servers, etc.).

Below are the full contents of each file.

---

## 1. `docker-compose.yml`

```yaml
version: '3.8'
services:
  jupyterhub:
    build:
      context: ./jupyterhub
      dockerfile: Dockerfile
    container_name: jupyterhub
    # Expose the default JupyterHub port (8000). Coolify can map its own domain/port to this.
    ports:
      - "8000:8000"
    # JupyterHub needs to spawn user containers; we mount the Docker socket read-write to do so.
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      # Persist hub database & secrets:
      - jhub-data:/srv/jupyterhub
    environment:
      # GitHub OAuth credentials (you'll set these in Coolify's UI)
      GITHUB_CLIENT_ID: "${GITHUB_CLIENT_ID}"
      GITHUB_CLIENT_SECRET: "${GITHUB_CLIENT_SECRET}"
      OAUTH_CALLBACK_URL: "${OAUTH_CALLBACK_URL}"

      # (Optional) You can override the default single-user images at runtime:
      # DOCKER_NOTEBOOK_IMAGE_BASE: "jupyter/base-notebook:latest"
      # DOCKER_NOTEBOOK_IMAGE_DATASCIENCE: "jupyter/datascience-notebook:latest"

      # If you want to restrict to a specific GitHub org:
      # ALLOWED_GITHUB_ORGS: "MyOrg"

      # If you want to restrict to a specific set of GH usernames or just certain admins:
      # ADMIN_GITHUB_USERS: "your_github_username,another_admin"

    # Run JupyterHub with our config file
    command: >
      jupyterhub
        --config /srv/jupyterhub/jupyterhub_config.py
    networks:
      - hubnet

networks:
  hubnet:
    name: hubnet
    driver: bridge

volumes:
  jhub-data:
```

### Explanation

- **`build: ./jupyterhub`** instructs Docker Compose to build the Docker image from the `Dockerfile` in `jupyterhub/`.
- We **mount** `/var/run/docker.sock` so that DockerSpawner can start/stop containers on the same host.
- `jhub-data` is a named volume storing the Hub’s SQLite database, cookie secret, etc.
- Environment variables like `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `OAUTH_CALLBACK_URL` are placeholders that you will set in **Coolify’s environment variables** section. JupyterHub reads them in `jupyterhub_config.py`.

---

## 2. `jupyterhub/Dockerfile`

A minimal Dockerfile extending **`jupyterhub/jupyterhub:latest`**, adding the needed spawners/auth packages:

```dockerfile
FROM jupyterhub/jupyterhub:4.0.2

# Install dependencies
RUN pip install --no-cache-dir \
    dockerspawner==13.0.0 \
    oauthenticator==16.2.1 \
    jupyterlab==4.0.11 \
    marimo

# Create directory for JupyterHub state
RUN mkdir -p /srv/jupyterhub

# Copy JupyterHub config file
COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

# Set working directory
WORKDIR /srv/jupyterhub

# Expose the port JupyterHub will run on
EXPOSE 8000

# Start JupyterHub
CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
```

### Marimo Integration

To include Marimo in the single-user notebook containers, add the following line to the `jupyterhub/Dockerfile`:

```dockerfile
RUN pip install marimo
```

This will install Marimo in the Docker image, making it available to users in their JupyterLab environment.


### Explanation

- **`jupyterhub/jupyterhub:latest`** already includes JupyterHub. We add:
  - `oauthenticator` to handle GitHub OAuth.
  - `dockerspawner` so JupyterHub can spawn containers.
  - `jupyterlab` ensures the Hub image itself has JupyterLab installed (though single-user containers also have their own copy).
- The line `COPY jupyterhub_config.py ...` copies our config file into the image so it’s available at runtime.
- This image runs `jupyterhub` by default (via the `command` in docker-compose).

---

## 3. `jupyterhub/jupyterhub_config.py`

Below is a fully annotated config implementing:

- **GitHub OAuth** using environment variables.
- **DockerSpawner** for user containers.
- **Multiple images** to choose from (base vs. data-science, etc.).
- **Named servers** so a user can spawn more than one environment (e.g., “personal” vs. “communal”).

```python
import os
import random
import string

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
if not os.path.exists("/srv/jupyterhub/jupyterhub_cookie_secret"):
    secret = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    with open("/srv/jupyterhub/jupyterhub_cookie_secret", "w") as f:
        f.write(secret)
    print("Generated a new cookie secret at /srv/jupyterhub/jupyterhub_cookie_secret")

# Done!
```

### Explanation Highlights

- **OAuth**:
  - `c.JupyterHub.authenticator_class = GitHubOAuthenticator`
  - Reads `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `OAUTH_CALLBACK_URL` from environment (all set in the Docker Compose or Coolify’s environment UI).
  - Optionally restricts logins to a GH org or a list of admin GitHub users.

- **DockerSpawner**:
  - `allowed_images` dictionary lists multiple Docker images. The user picks which image they want (via an options form).
  - Volumes: `"jhub-user-{username}-{servername}"` ensures each user server has a unique volume.
  - `c.JupyterHub.allow_named_servers = True` so that each user can spawn multiple servers (they can name them “personal” or “communal”).

- **No token-based logins**: All user authentication is through GitHub OAuth. The single-user servers do not require tokens from the user. Instead, JupyterHub handles the user identity, and the spawn is done on behalf of that user.

- **Persistent Hub data** is stored in `/srv/jupyterhub`, which is mapped to the `jhub-data` volume. Each user’s containers will also have a persistent volume that gets created automatically.

---

## Environment Variables

The following environment variables can be configured in Coolify to customize the JupyterHub deployment:

| Variable | Required | Description |
|---|---|---|
| `GITHUB_CLIENT_ID` | Yes | The Client ID of your GitHub OAuth app. |
| `GITHUB_CLIENT_SECRET` | Yes | The Client Secret of your GitHub OAuth app. |
| `OAUTH_CALLBACK_URL` | Yes | The callback URL for GitHub OAuth, e.g., `https://<your-coolify-domain>/hub/oauth_callback`. |
| `DOCKER_NOTEBOOK_IMAGE_BASE` | No | The default Docker image for single-user notebook containers (base). Defaults to `jupyter/base-notebook:latest`. |
| `DOCKER_NOTEBOOK_IMAGE_DATASCIENCE` | No | The Docker image for single-user notebook containers (data science). Defaults to `jupyter/datascience-notebook:latest`. |
| `ALLOWED_GITHUB_ORGS` | No | A comma-separated list of GitHub organizations that are allowed to log in. |
| `ADMIN_GITHUB_USERS` | No | A comma-separated list of GitHub usernames that will be granted admin access. |
| `JUPYTERHUB_COOKIE_SECRET` | No | A random hex string used to secure cookies. If not set, JupyterHub will auto-generate one. |
| `CONFIGPROXY_AUTH_TOKEN` | No | The proxy auth token. If not set, JupyterHub will generate one. |

---

## How to Deploy on Coolify

1. **Create a GitHub OAuth App**:
   - Go to [GitHub’s Developer Settings](https://github.com/settings/developers).
   - Create an “OAuth App” with the following settings:
     - **Application name:** A descriptive name for your JupyterHub deployment.
     - **Homepage URL:** The URL of your JupyterHub deployment (e.g., `https://<your-coolify-domain>`).
     - **Authorization callback URL:** The callback URL for GitHub OAuth (e.g., `https://<your-coolify-domain>/hub/oauth_callback`).
   - Copy the **Client ID** and **Client Secret**.

2. **Add a Docker Compose application in Coolify**:
   - In Coolify, create a new application and select the “Docker Compose” deployment type.
   - Provide Repository Details: Provide the URL of your repository containing the `docker-compose.yml` file and the `jupyterhub` directory.
   - Configure the Source Path: If your `docker-compose.yml` file is not in the root of the repository, specify the path to the directory containing the `docker-compose.yml` file in the "Source Path" setting.

3. **Configure Environment Variables** in Coolify**:
   - Set `GITHUB_CLIENT_ID` to the OAuth app’s Client ID.
   - Set `GITHUB_CLIENT_SECRET` to the OAuth app’s Client Secret.
   - Set `OAUTH_CALLBACK_URL` to `https://<your-coolify-domain>/hub/oauth_callback`.
   - (Optional) Set `ADMIN_GITHUB_USERS`, `ALLOWED_GITHUB_ORGS`, or different `DOCKER_NOTEBOOK_IMAGE_BASE`/`DOCKER_NOTEBOOK_IMAGE_DATASCIENCE`.

4. **Select a Domain and SSL**:
   - In Coolify, assign a domain or subdomain to the JupyterHub service and enable SSL.
   - Coolify will automatically set up HTTPS via Let’s Encrypt.
   - Make sure the domain matches the callback URL you set in GitHub’s OAuth config.

5. **Deploy**:
   - Coolify will build the Docker image (from `jupyterhub/Dockerfile`) and run the service.
   - The container starts JupyterHub listening on port 8000. Coolify proxies port 443 → port 8000 with SSL offloading.

6. **Test**:
   - Go to `https://<your-coolify-domain>` (whatever domain you set).
   - You should see the JupyterHub login page. It will redirect you to GitHub to authorize if you’re not logged in.
   - Once you authorize, you’ll be taken back to JupyterHub.
   - On the “Start My Server” page, you can **choose a server name** (if you want named servers) and **select from the available images** (the base or data-science environment). Click “Start.”
   - JupyterHub spawns a container running that image, mounting a volume for your user+server.
   - You end up in JupyterLab. You can create notebooks, install libraries (within the container), and your data persists in the Docker volume.

7. **Named Server for a Communal Workspace**:
   - Each user can create additional named servers.
   - If you want a truly shared environment, a user can create a server named “communal,” then share the resulting URL with others. **Caution**: By default, each user can only access **their** own named servers. If you want multiple users to share the same container, you can enable JupyterLab’s real-time collaboration so they can simultaneously edit the same notebook. But typically, each named server belongs to the user who spawned it.
   - Alternatively, you can create a special “shared” user with “admin” privileges that logs in and spawns a named server, and then share that user’s credentials. That’s a bit hacky, but it’s one way to have a truly single container for everyone. A more robust approach is using “collaborative editing” in JupyterLab.

---

## Testing & Deployment

### Local Testing

Before deploying to Coolify, you can test the JupyterHub setup locally using Docker Compose:

1. **Clone the repository:** Clone the repository containing the `docker-compose.yml` file and the `jupyterhub` directory.
2. **Set environment variables:** Create a `.env` file in the root directory and set the required environment variables (e.g., `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `OAUTH_CALLBACK_URL`).
3. **Start the services:** Run `docker-compose up --build` in the root directory to build the Docker image and start the JupyterHub service.
4. **Access JupyterHub:** Open your browser and go to `http://localhost:8000` to access the JupyterHub login page.

### GitHub OAuth App Creation

To enable GitHub OAuth authentication, you need to create a GitHub OAuth App:

1. **Go to GitHub Developer Settings:** Go to [GitHub’s Developer Settings](https://github.com/settings/developers).
2. **Create a New OAuth App:** Click on “New OAuth App” and fill in the required information:
   - **Application name:** A descriptive name for your JupyterHub deployment.
   - **Homepage URL:** The URL of your JupyterHub deployment (e.g., `https://<your-coolify-domain>`).
   - **Authorization callback URL:** The callback URL for GitHub OAuth (e.g., `https://<your-coolify-domain>/hub/oauth_callback`).
3. **Copy Client ID and Secret:** Copy the **Client ID** and **Client Secret** from the OAuth App settings. You will need these values to configure the environment variables in Coolify.

### Coolify Deployment

To deploy the JupyterHub setup to Coolify:

1. **Create a New Application:** In Coolify, create a new application and select the “Docker Compose” deployment type.
2. **Provide Repository Details:** Provide the URL of your repository containing the `docker-compose.yml` file and the `jupyterhub` directory.
3. **Configure Environment Variables:** Add the required environment variables (e.g., `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `OAUTH_CALLBACK_URL`) in the Coolify application settings.
4. **Select a Domain and SSL:** Assign a domain or subdomain to the JupyterHub service and enable SSL.
5. **Deploy the Application:** Deploy the application and wait for the deployment process to complete.

### End-to-End Testing

After deploying the JupyterHub setup to Coolify, perform the following end-to-end tests:

1. **Access JupyterHub:** Open your browser and go to the domain you assigned to the JupyterHub service.
2. **Login with GitHub:** You should be redirected to GitHub to authorize the OAuth App.
3. **Authorize the App:** Authorize the OAuth App to grant access to your GitHub account.
4. **Start a Server:** After successful authorization, you should be redirected back to JupyterHub and be able to start a new server.
5. **Access JupyterLab:** After the server starts, you should be redirected to the JupyterLab interface.
6. **Create a Notebook:** Create a new notebook and verify that you can execute code and save the notebook.
7. **Test Marimo:** Create a new Marimo app and verify that it runs correctly.

---

## Further Customization

- **User Resource Limits**: You can set memory or CPU limits per user container with DockerSpawner. For example:
  ```python
  c.Spawner.mem_limit = '2G'
  c.Spawner.cpu_limit = 1
  ```
- **Idle Culling**: JupyterHub can automatically stop idle servers. This helps save resources if you have many users.
  ```python
  c.JupyterHub.services = [
    {
      "name": "cull-idle",
      "admin": True,
      "command": [
          "cull_idle_servers",
          "--timeout=3600"
      ]
    }
  ]
  ```
- **Multiple Spawner Classes**: You might create different spawner classes for different user groups (but that’s more advanced).
- **Restricting Access**: If you only want certain GitHub usernames or organizations, set `c.GitHubOAuthenticator.allowed_organizations = {...}` or maintain a userlist.

Enjoy your JupyterHub-based solution with GitHub OAuth and DockerSpawner!

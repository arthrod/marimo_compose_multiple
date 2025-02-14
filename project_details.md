upyterHub with Individual JupyterLab Instances (DockerSpawner)
Overview: This approach deploys JupyterHub as a central service that spawns a dedicated JupyterLab server for each user. Each user’s server runs in an isolated Docker container (using DockerSpawner) with its own workspace. JupyterHub manages authentication through GitHub OAuth, so users log in with their GitHub credentials. User data is stored on persistent volumes, ensuring notebooks aren’t lost when containers stop. All configuration can be supplied via environment variables (suitable for Coolify), and SSL is offloaded to Coolify’s proxy (JupyterHub itself can run on HTTP internally).Key Features:
Isolated per-user environments: Using DockerSpawner, JupyterHub launches a separate single-user JupyterLab instance in a Docker container for each authenticated user​
GITHUB.COM
. This provides strong isolation (each user has their own Linux environment, Python packages, etc.).
GitHub OAuth Authentication: JupyterHub integrates with GitHub OAuth via the OAuthenticator plugin. Users are redirected to GitHub to log in, and upon success JupyterHub spawns their container. You’ll need to register a GitHub OAuth app and set the credentials in JupyterHub’s config (more below).
Persistent storage: Each user’s container can mount a Docker volume for the home directory or workspace. This means user notebooks and data persist between sessions. For example, you can map a host path or named volume to /home/jovyan (if using Jupyter Docker stacks) so that when a container is removed, the data remains​
GITHUB.COM
.
Coolify compatibility: All necessary configuration (GitHub OAuth credentials, DockerSpawner settings, etc.) can be provided via environment variables or an .env file, which Coolify supports. No in-container SSL setup is needed – JupyterHub can listen on an internal port without HTTPS, because Coolify will terminate SSL at the proxy level.
Deployment Steps:
Prepare a JupyterHub Docker image: Use the official JupyterHub Docker image or build a custom one that includes the DockerSpawner and OAuthenticator. For example, you might start from the jupyterhub/jupyterhub image and pip install dockerspawner oauthenticator. JupyterHub is designed to manage multiple single-user servers​
GITHUB.COM
, and DockerSpawner enables it to launch those servers in Docker containers​
GITHUB.COM
. Ensure JupyterLab is available in the single-user image (e.g. by using Jupyter Docker stack images like jupyter/base-notebook or similar as the spawn target).
Configure GitHub OAuth credentials: In GitHub, create an OAuth App for your JupyterHub deployment. Set the Authorization Callback URL to https://<your-domain>/hub/oauth_callback (if Coolify provides a domain, use that)​
GITHUB.COM
. In Coolify’s interface (or your environment), set the following environment variables for JupyterHub before launch​
JUPYTERHUB.READTHEDOCS.IO
:
GITHUB_CLIENT_ID – the Client ID of your GitHub OAuth app
GITHUB_CLIENT_SECRET – the Client Secret of the OAuth app (store this securely)
OAUTH_CALLBACK_URL – the callback URL, e.g. https://<your-domain>/hub/oauth_callback
JupyterHub’s GitHub OAuthenticator will use these values to perform OAuth. (These correspond to JupyterHub config keys c.GitHubOAuthenticator.client_id, client_secret, and oauth_callback_url, which the OAuthenticator reads from the environment by default​
JUPYTERHUB.READTHEDOCS.IO
.) Note: Keep the client secret safe (use Coolify’s secret storage if available)​
GITHUB.COM
.
Enable GitHub OAuth in JupyterHub: Set JupyterHub to use the GitHub OAuthenticator. This is done by configuring:
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
You can supply this in a jupyterhub_config.py or via the environment (some images allow $AUTHENTICATOR_CLASS env). If using a config file, mount it into the container via Coolify. You may also specify allowed users or organizations – for example, limit login to members of a GitHub org by setting c.GitHubOAuthenticator.allowed_organizations = {'YourOrg'} (via env var OAUTHenticator_ALLOWED_ORGANIZATIONS). If you want to allow any GitHub user (open signup), you can set c.Authenticator.allowed_users = set() and perhaps c.Authenticator.allow_all = True​
GITHUB.COM
.
Configure DockerSpawner for user containers: In JupyterHub’s config, set the spawner class and Docker options. Key settings include:
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner' – enables DockerSpawner​
GITHUB.COM
.
Single-user image: c.DockerSpawner.image = 'jupyter/base-notebook:latest' (or any Docker image that launches JupyterLab). This is the image each user container will run​
GITHUB.COM
.
Default to JupyterLab: Ensure the spawned notebooks open JupyterLab by default. Set c.Spawner.default_url = '/lab'​
GITHUB.COM
 so that users get the JupyterLab interface instead of the classic notebook.
Networking: If needed, set c.DockerSpawner.network_name to the Docker network that JupyterHub and user containers will share (in Docker-compose or Coolify, ensure they join the same network). Also, JupyterHub needs to know its IP for containers to reach it – in DockerSpawner this is often the Docker bridge IP. You can set c.JupyterHub.hub_ip = '0.0.0.0' or the internal hostname so containers can callback to Hub​
GITHUB.COM
. (In many cases, leaving it default works if using DockerSpawner in a single Docker host setup.)
Persistent volumes: Use DockerSpawner’s volume mapping to persist data. For example: c.DockerSpawner.notebook_dir = '/home/jovyan/work' and c.DockerSpawner.volumes = { 'jhub-user-{username}': '/home/jovyan/work' }​
GITHUB.COM
. This maps a Docker volume (named with the user’s name) into the container’s working directory. Replace with paths appropriate for your image (in Jupyter Docker stack images, home is usually /home/jovyan). This ensures that stopping/restarting a user’s container retains their files.
Environment and runtime settings (Coolify specifics): In Coolify, set the environment variables from steps 2 and any others required (such as JupyterHub’s internal cookie secret or proxy token if needed – though if not set, JupyterHub will auto-generate a cookie secret). For simplicity, you might also set JUPYTERHUB_COOKIE_SECRET to a random hex and CONFIGPROXY_AUTH_TOKEN (the proxy auth token) as env vars​
JUPYTERHUB.READTHEDOCS.IO
, or let JupyterHub generate them. Disable JupyterHub’s internal SSL: do not set c.JupyterHub.ssl_key/cert (leave them unset). Instead, configure JupyterHub to listen on HTTP. By default, JupyterHub listens on port 8000 – you can keep that. Coolify will provide the external HTTPS endpoint. Make sure JupyterHub knows it’s behind a proxy (set c.JupyterHub.bind_url = 'http://:8000' and perhaps c.JupyterHub.allow_remote_access = True if needed). This way, all OAuth callback URLs use the external https address but JupyterHub itself doesn’t do SSL (avoids conflicts with Coolify’s SSL).
Launch JupyterHub: Deploy the JupyterHub service through Coolify with the above configuration. Once running, users can access the Hub via the provided URL. On first visit, JupyterHub will redirect them to GitHub to authenticate. After GitHub OAuth login and consent, GitHub redirects back to JupyterHub (/hub/oauth_callback). JupyterHub then creates a new container for the user (using DockerSpawner) and directs the user to their running JupyterLab instance​
GITHUB.COM
. From the user’s perspective, they log in with GitHub and “magically” get their own JupyterLab workspace in the browser. Each user’s server is isolated, and they cannot interfere with each other’s environment or files (unless shared volumes are intentionally configured). Admins can use JupyterHub’s admin panel to stop/start user servers as needed.
This JupyterHub-based solution is a robust, production-grade setup for multi-user Jupyter environments. It requires a bit more initial setup (OAuth app registration and config), but after deployment it’s largely self-managing. Each user’s environment persists and is secure. The use of DockerSpawner means you can also customize the single-user image (e.g., pre-install certain libraries for all users) easily by updating the image.
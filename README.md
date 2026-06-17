# Product Service

## Run with Docker Desktop (Runtime Environment Variables)

This project uses runtime environment variable injection for Docker Desktop.
Do not bake secrets into the image.

1. Create a local runtime env file from the template:

```powershell
Copy-Item .env.docker.example .env.docker
```

2. Edit `.env.docker` and set real values.

3. Build the production image:

```powershell
docker build -f Dockerfile.production -t product-service:prod .
```

4. Run the container with runtime env vars:

```powershell
docker run --rm -p 5000:5000 --env-file .env.docker product-service:prod
```

Notes:
- `.env.docker` is ignored by Git and Docker build context.
- Keep secrets only in runtime env files or secret managers.

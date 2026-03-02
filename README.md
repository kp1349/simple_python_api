# simple_python_api
This is a simple Python Dockerized application that will expose some easy REST endpoints

# running
```sh
# env
conda activate myenv
# one time
pip install -r requirements.txt

# run
uvicorn main:app --reload

# test
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/hello \
  -H "Content-Type: application/json" \
  -d '{"name":"John"}'
  
# docs
http://127.0.0.1:8000/docs
```

# docker
```sh
# build locally
docker build -t simple-python-api:local .
# run locally
docker run --rm -p 8000:8000 --name simple-python-api simple-python-api:local
# docker compose
docker compose -f docker-compose.local.yml up

# build with gitlab
docker pull registry.gitlab.com/k_paul/simple_python_api:<latest_sha>
# run - find the sha here: https://gitlab.com/k_paul/simple_python_api/container_registry/10937258
docker run --rm -p 8000:8000 registry.gitlab.com/k_paul/simple_python_api:<latest_sha>
# use docker compose with latest tag
docker compose -f docker-compose.gitlab.yml up
```

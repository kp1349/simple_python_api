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

## pushing to dockerhub
```sh
# login
docker login
# build
docker build -t simple-python-api:latest .
# verify
docker images
# tag
docker tag <local_image_or_existing_tag> kp1349/simple_python_api:latest
docker tag simple-python-api:latest kp1349/simple_python_api:latest
# push
docker push kp1349/simple_python_api:latest
# find the latest tag here: https://hub.docker.com/repository/docker/kp1349/simple_python_api/general
```


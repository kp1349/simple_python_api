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

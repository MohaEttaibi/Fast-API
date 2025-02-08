## To run the app

```
pipenv install fastapi
pipenv install "uvicorn[standard]"
uvicorn main:app --reload --port 8000
```

## documentation
```http://localhost:8000/docs```

## Installing Packages
``` pipenv install -r requirements-dev.txt ```

### https://github.com/tecladocode/fastapi-stream-app

### Logtail = Log managment

### https://medium.com/@mohit_kmr/production-ready-fastapi-application-from-0-to-1-part-2-1ed97cf5c242

## Testing
```
pytest 
pytest -k class_name
```
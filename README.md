# KR_5

## Local setup

```
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests

```
pytest
```

## Docker

```
docker compose up --build
```

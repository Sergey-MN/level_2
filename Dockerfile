FROM python:3.11-slim

RUN python -m pip install --upgrade pip

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv pip install --system .

COPY ./app_project/ /app/app_project/

CMD ["uvicorn", "app_project.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

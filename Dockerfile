FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# torch's helper libraries from the normal index, then CPU-only torch itself
RUN pip install --no-cache-dir typing-extensions fsspec filelock jinja2 networkx sympy
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src ./src

ENV HF_HOME=/models
EXPOSE 8000
CMD ["uvicorn", "api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
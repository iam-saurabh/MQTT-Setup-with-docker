FROM python:3.8-alpine
WORKDIR /code
COPY FastApiEndpoint/main.py .
COPY FastApiEndpoint/models.py .
COPY FastApiEndpoint/requirement.txt .
COPY FastApiEndpoint/index.html .
RUN pip install -r requirement.txt
CMD ["python","main.py"]
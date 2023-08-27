FROM python:3.8-alpine
WORKDIR /code
COPY FastApiEndpoint/requirement.txt .
RUN pip install -r requirement.txt
CMD ["python","main.py"]

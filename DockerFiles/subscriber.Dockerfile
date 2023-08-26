FROM python:3.8-alpine
WORKDIR /code
COPY MQTTSubscriber/subscriber.py .
COPY MQTTSubscriber/requirement.txt .
RUN pip install -r requirement.txt
CMD ["python","subscriber.py"]
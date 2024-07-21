FROM python:3.10-slim

WORKDIR /bot 
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . /bot 

CMD [ "python3", "main.py" ]
FROM python:3.9

ARG PRENOM="Toto"
ENV PRENOM=$PRENOM

COPY . /api
WORKDIR ./api 
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
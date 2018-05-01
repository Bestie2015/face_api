FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV AZURE_FACE_API_KEY ${AZURE_FACE_API_KEY}

COPY . .

CMD [ "python", "app.py"]

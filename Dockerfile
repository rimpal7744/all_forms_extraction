FROM python:3.8

WORKDIR /app


RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && apt-get install -y default-jre
RUN apt-get install poppler-utils -y

COPY requirement.txt requirement.txt
RUN pip install -r requirement.txt
RUN apt install tesseract-ocr -y
RUN apt install libtesseract-dev -y
RUN apt install poppler-utils
COPY . .
#CMD ["python /app/main.py"]
#CMD [ "python", "main.py"]
CMD uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
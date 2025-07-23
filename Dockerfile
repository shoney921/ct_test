FROM python:3.10

WORKDIR /app
ENV HOSTNAME "0.0.0.0"

RUN apt-get update && apt-get install -y ca-certificates
RUN apt-get install -y curl
RUN apt-get install -y gnupg
RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py

RUN pip install --upgrade pip

COPY requirements.txt ./requirements.txt
RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["python", "main.py"]

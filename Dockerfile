FROM bitnami/kubectl:1.20.9 as kubectl
FROM --platform=linux/amd64 ubuntu:latest

RUN apt update
RUN apt install python3.11 python3-pip -y

WORKDIR /KGS-UPLOAD

COPY requirement.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirement.txt
COPY main.py ./
COPY cert.pem ./

COPY --from=kubectl /opt/bitnami/kubectl/bin/kubectl /usr/local/bin/

CMD ["python3", "./main.py"]
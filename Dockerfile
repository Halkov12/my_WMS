FROM python:3.13

RUN apt update && mkdir /wms

WORKDIR /wms

COPY ./src ./src
COPY ./requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["bash"]
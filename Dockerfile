FROM python:3.12

RUN apt update && mkdir /wms

WORKDIR /wms

COPY ./src ./src
COPY ./requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["bash"]
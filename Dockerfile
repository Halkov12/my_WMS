FROM python:3.12

RUN apt update && mkdir -p /wms

WORKDIR /wms

COPY ./src ./
COPY ./requirements.txt /wms/requirements.txt

RUN python -m pip install --upgrade pip && pip install -r /wms/requirements.txt

CMD ["bash"]
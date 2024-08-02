ARG PYTHON_MAJOR=3
ARG PYTHON_MINOR=12
ARG OS_VARIANT=slim-bookworm
FROM --platform=linux/amd64 public.ecr.aws/docker/library/python:${PYTHON_MAJOR}.${PYTHON_MINOR}-${OS_VARIANT}

RUN python -m pip install roboto
COPY src/tag_dataset/ ./tag_dataset

ENTRYPOINT [ "python", "-m", "tag_dataset" ]

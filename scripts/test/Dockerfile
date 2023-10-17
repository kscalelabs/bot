# Dockerfile for the FastAPI application.

FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install 'fastapi[all]' 'mangum'

COPY ./scripts/test/main.py ./

RUN python -c "from main import handler"

CMD ["main.handler"]

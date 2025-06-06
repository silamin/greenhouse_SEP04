# Use AWS Lambda Python 3.10 base image (includes Lambda Runtime Interface)
FROM public.ecr.aws/lambda/python:3.10

# Copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app
COPY models/ ${LAMBDA_TASK_ROOT}/models
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# Install Python dependencies into the Lambda task root
RUN pip install \
    --upgrade pip \
    && pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt \
    --target "${LAMBDA_TASK_ROOT}" \
    --no-cache-dir

# Set working directory to the Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Specify the Lambda handler (app/main.py → handler)
CMD ["app/main.handler"]

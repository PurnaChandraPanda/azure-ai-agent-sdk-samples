FROM ubuntu:22.04

ARG MINICONDA_VERSION=py311_24.3.0-0          # adjust if needed
ENV DEBIAN_FRONTEND=noninteractive

# OS prerequisites
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends wget bzip2 ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Miniconda install
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/miniconda && \
    rm /tmp/miniconda.sh

ENV PATH=/opt/miniconda/bin:$PATH

# Conda env from conda.yml
COPY conda.yml /tmp/conda.yml
RUN conda env create -n app -f /tmp/conda.yml && \
    conda clean -afy
ENV PATH=/opt/miniconda/envs/app/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Application code
WORKDIR /app
COPY src/ /app/src

# Expose port for the application
EXPOSE 4001

# Set the entrypoint to run the application, default command
CMD ["python", "-m", "src.engine.api", "0.0.0.0", "4001"]
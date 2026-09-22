FROM kicad/kicad:10.0.5
USER root
ARG FREEROUTING_VERSION=2.2.4
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-venv curl ca-certificates tar \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/freerouting /opt/java25 \
    && curl -fsSL "https://api.adoptium.net/v3/binary/latest/25/ga/linux/x64/jre/hotspot/normal/eclipse?project=jdk" -o /tmp/jre25.tar.gz \
    && tar -xzf /tmp/jre25.tar.gz -C /opt/java25 --strip-components=1 \
    && rm -f /tmp/jre25.tar.gz \
    && curl -fsSL "https://github.com/freerouting/freerouting/releases/download/v${FREEROUTING_VERSION}/freerouting-${FREEROUTING_VERSION}.jar" \
       -o /opt/freerouting/freerouting.jar \
    && test -s /opt/freerouting/freerouting.jar
WORKDIR /workspace
COPY requirements.txt .
RUN python3 -m venv /opt/pcb-lab-venv \
    && /opt/pcb-lab-venv/bin/python -m pip install --upgrade pip \
    && /opt/pcb-lab-venv/bin/python -m pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PCB_LAB_ROOT=/workspace
ENV JAVA_HOME=/opt/java25
ENV PATH=/opt/java25/bin:/opt/pcb-lab-venv/bin:$PATH
ENV FREEROUTING_JAR=/opt/freerouting/freerouting.jar
RUN kicad-cli version && java -version && /opt/pcb-lab-venv/bin/python -c "import fastapi,uvicorn,pydantic"
RUN /opt/pcb-lab-venv/bin/python -m compileall -q api worker scripts tests
CMD ["uvicorn","api.main:app","--host","0.0.0.0","--port","8000"]

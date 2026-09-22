FROM kicad/kicad:10.0.5
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip default-jre-headless curl && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY requirements.txt .
RUN python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /opt/freerouting \
 && curl -fL --retry 4 --retry-delay 2 https://github.com/freerouting/freerouting/releases/download/v2.2.4/freerouting-2.2.4.jar -o /opt/freerouting/freerouting.jar \
 && test -s /opt/freerouting/freerouting.jar
ENV PCB_LAB_ROOT=/workspace
ENV FREEROUTING_JAR=/opt/freerouting/freerouting.jar
CMD ["uvicorn","api.main:app","--host","0.0.0.0","--port","8000"]

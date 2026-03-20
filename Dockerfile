FROM maven:3.9-eclipse-temurin-21 AS java-build
WORKDIR /build
COPY java/ java/
COPY scripts/build-java.sh scripts/
RUN cd java && mvn -B clean package -P release -DskipTests

FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends default-jre-headless && rm -rf /var/lib/apt/lists/*

COPY python/opendataloader-pdf/ python/opendataloader-pdf/
COPY LICENSE NOTICE README.md ./
COPY THIRD_PARTY/ THIRD_PARTY/
COPY --from=java-build /build/java/opendataloader-pdf-cli/target/opendataloader-pdf-cli-*.jar \
    python/opendataloader-pdf/src/opendataloader_pdf/jar/opendataloader-pdf-cli.jar

RUN cp LICENSE python/opendataloader-pdf/src/opendataloader_pdf/LICENSE && \
    cp NOTICE python/opendataloader-pdf/src/opendataloader_pdf/NOTICE && \
    cp README.md python/opendataloader-pdf/README.md && \
    cp -r THIRD_PARTY python/opendataloader-pdf/src/opendataloader_pdf/THIRD_PARTY

RUN pip install --no-cache-dir \
    python/opendataloader-pdf/ \
    fastapi>=0.100.0 \
    uvicorn>=0.20.0 \
    python-multipart>=0.0.22

COPY examples/python/api/main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Multi-stage build para otimizar a imagem
FROM python:3.11-slim as builder

WORKDIR /app

# Instala dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Imagem final
FROM python:3.11-slim

WORKDIR /app

# Copia dependências instaladas do builder
COPY --from=builder /root/.local /root/.local

# Adiciona o diretório local ao PATH
ENV PATH=/root/.local/bin:$PATH

# Copia o código da aplicação
COPY src/ ./src/

# Cria diretório para downloads (se necessário)
RUN mkdir -p downloads

# Expõe a porta do FastAPI
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Comando para iniciar a aplicação
CMD ["python", "-m", "src.main"]

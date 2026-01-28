# Hackaton SOAT11 - Video Processor

Aplicação Python para processar vídeos do S3, extraindo frames e gerando arquivos ZIP, com processamento paralelo via Kafka.

## 📋 Descrição

Esta aplicação roda um servidor FastAPI que:
- Escuta eventos do Kafka com informações de vídeos
- Baixa vídeos do AWS S3
- Extrai frames distribuídos ao longo do vídeo (início, meio e fim)
- Gera arquivo ZIP com as imagens
- Faz upload do ZIP no S3
- Envia mensagem de conclusão para outro tópico Kafka
- **Processa múltiplos vídeos simultaneamente**

## 🚀 Funcionalidades

- ✅ **Processamento Paralelo** - Processa múltiplos vídeos ao mesmo tempo
- ✅ Servidor FastAPI com healthcheck para EKS/Docker
- ✅ Consumer Kafka rodando em background
- ✅ Extração inteligente de frames (início, meio e fim do vídeo)
- ✅ Geração automática de ZIP com frames
- ✅ Upload automático no S3 (pasta `zip/`)
- ✅ Producer Kafka para notificação de conclusão
- ✅ Arquitetura Hexagonal (Ports & Adapters)
- ✅ Logging detalhado por vídeo
- ✅ Validação de configurações
- ✅ Documentação automática (Swagger)

## 📦 Pré-requisitos

- Python 3.8+
- Kafka rodando (local ou remoto)
- Conta AWS com acesso ao S3
- OpenCV (incluído no requirements.txt)
- Ambiente virtual Python (recomendado)

## 🔧 Instalação

1. Clone o repositório e ative o ambiente virtual:

```powershell
cd hackaton-soat11-videoprc
.venv\Scripts\activate
```

2. Instale as dependências:

```powershell
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:

```powershell
# Copie o arquivo de exemplo
Copy-Item .env.example .env

# Edite o arquivo .env com suas configurações
```

## ⚙️ Configuração

Edite o arquivo `.env` com suas credenciais e configurações:

```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=              # Tópico de entrada
KAFKA_OUTPUT_TOPIC=video-processed    # Tópico de saída
KAFKA_GROUP_ID=video-processor-group
KAFKA_AUTO_OFFSET_RESET=earliest

# AWS S3
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=seu-bucket

# Aplicação
LOG_LEVEL=INFO
APP_NAME=video-processor
MAX_WORKERS=3  # Número de vídeos processando simultaneamente
```s Mensagens Kafka

### Mensagem de Entrada (Tópico: video-events)

```json
{
  "video_id": "1",
  "path": "video/nome-do-video.mp4"
}
```

### Mensagem de Saída (Tópico: video-processed)

```json
{
  "video_id": "1",
  "path": "zip/nome-do-video.zip",
  "message": "Pronto para download"
}
```

## 🔄 Fluxo de Processamento

```
📥 Kafka (video-events)
    ↓
📦 Download vídeo do S3
    ↓3000
```

O servidor estará disponível em: http://localhost:3000

**Endpoints disponíveis:**
- `GET /video-processor/health` - Healthcheck para EKS/Docker
- `GET /video-processor/api

### 🎯 Extração de Frames

Os frames são extraídos de forma distribuída:
- **Frame 1**: Início do vídeo (frame 0)
- **Frame 2**: Meio do vídeo (~33%)
- **Frame 3**: Meio-fim do vídeo (~66%)
- **Frame 4**: Final do vídeo (último frame)

Exemplo: Vídeo com 300 frames → Extrai frames: 0, 100, 200, 299
```

## 🎯 Estrutura da Mensagem Kafka

A mensagem no Kafka deve conter a chave do arquivo S3. Exemplo:

```json
{
  "s3_key": "videos/meu-video.mp4",
  "metadata": {
    "timestamp": "2026-01-09T20:00:00Z",
    "userocessamento Paralelo

A aplicação utiliza **ThreadPoolExecutor** para processar múltiplos vídeos simultaneamente:

- Configure `MAX_WORKERS` no `.env` (padrão: 3)
- Cada vídeo é processado em uma thread separada
- O Consumer Kafka não bloqueia durante o processamento
- Logs identificam qual thread está processando cada vídeo

**Exemplo de log com processamento paralelo:**
```
INFO - 🎬 [Video ID: 1] Tarefa submetida para processamento
INFO - 🎬 [Video ID: 2] Tarefa submetida para processamento
INFO - 📊 Tarefas em processamento: ~2
INFO - [Thread-1] Processando vídeo - Video ID: 1
INFO - [Thread-2] Processando vídeo - Video ID: 2
INFO - ✅ [Video ID: 1] Vídeo processado com sucesso!
INFO - ✅ [Video ID: 2] Vídeo processado com sucesso!
```

## 🏗️ Adomain/                 # Entidades do domínio
│   │   └── entities/
│   │       └── video_entity.py
│   │
│   ├── application/            # Lógica de negócio
│   │   ├── ports/             # Interfaces (contratos)
│   │   │   ├── storage_port.py
│   │   │   └── message_producer_port.py
│   │   ├── services/          # Serviços de domínio
│   │   │   └── video_processing_service.py
│   │   └── use_cases/         # Casos de uso
│   │       └── process_video_use_case.py
│   │
│   ├── adapters/              # Implementações dos ports
│   │   ├── input/            # Entrada (driving)
│   │   │   ├── consumers/
│   │   │   │   └── kafka_consumer.py
│   │   │   └── routers/
│   │   │       └── health_controller.py
│   │   └── output/           # Saída (driven)
│   │       ├── persistence/
│   │       │   └── s3/
│   │       │       └── s3_client.py
│   │       └── producers/
│   │           └── kafka_producer.py
│   │
│   ├── config/
│   │   └── settings.py        # Configurações
│   └── main.py                # Ponto de entrada
│
├── tests/
├── .env.example               # Exemplo de configuração
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── IMPLEMENTATION_GUIDE.md    # Guia detalhado
**Endpoints disponíveis:**
- `GET /` - Informações básicas da aplicação
- `GET /health` - Healthcheck para EKS/Docker
- `GET /docs` - Documentação interativa (Swagger)

Para parar, pressione `Ctrl+C`

## 🛠️ Personalização

Você pode personalizar o processamento editando a função `custom_message_handler` em [src/main.py](src/main.py):

```python
def custom_message_handler(message_data: dict, file_content: bytes):
    # Seu código de processamento aqui
    # Exemplos:
    # - Processar vídeo
    # - Extrair metadados
    # - Salvar em banco de dados
    # - Enviar para outro serviço
    pass
```

## 📁 Estrutura do Projeto

```
hackaton-soat11-videoprc/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configurações da aplicação
│   ├── s3_client.py        # Cliente S3
│   ├── kafka_consumer.py   # Consumer Kafka
│   └── main.py             # FastAPI Server com lifespan
├── tests/
├── .env.example            # Exemplo de configuração
├── .gitignore
├── Dockerfile              # Imagem Docker
├── docker-compose.yml      # Orquestração Docker
├── k8s-deployment.yaml     # Deploy Kubernetes/EKS
├── requirements.txt
└── README.md
```

## 🐳 Deploy com Docker

### Build da imagem:

```powershell
docker build -t video-processor:latest .
```

### Executar com Docker:

```powershell
docker run -d \
  --name video-processor \
  -p 8000:8000 \
  --env-file .env \
  video-processor:latest
```

### Executar com Docker Compose:

```powershell
docker-compose up -d
```

### Verificar logs:

```powershell
docker logs -f video-processor
```

## ☸️ Deploy no Kubernetes/EKS

### 1. Edite o arquivo k8s-deployment.yaml com suas configurações

### 2. Aplique os recursos:

```powershell
kubectl apply -f k8s-deployment.yaml
```

### 3. Verifique o status:3000/video-processor/health

# Ou no navegador:
# http://localhost:3000/video-processor/health
# http://localhost:3000/video-processor/apidocs
```

### 4. Envie mensagens de teste:

```powershell
# Use o kafka-console-producer
kafka-console-producer --broker-list localhost:9092 --topic video-events
```

Digite as mensagens JSON (uma por linha):
```json
{"video_id": "1", "path": "video/teste-1.mp4"}
{"video_id": "2", "path": "video/teste-2.mp4"}
{"video_id": "3", "path": "video/teste-3.mp4"}
```detalhados para cada vídeo processado:

```
INFO - 🚀 Iniciando aplicação...
INFO - ✅ ThreadPoolExecutor inicializado com 3 workers
INFO - ✅ S3 Client inicializado
INFO - ✅ Kafka Producer inicializado
INFO - ✅ Video Processing Service inicializado
INFO - ✅ Process Video Use Case inicializado
INFO - ✅ Kafka Consumer inicializado
INFO - 🎉 Aplicação iniciada com sucesso!

INFO - 🎬 [Video ID: 1] Tarefa submetida para processamento
INFO - 📊 Tarefas em processamento: ~1
INFO - === [Thread-ThreadPoolExecutor-0_0] Processando vídeo ===
INFO - Video ID: 1
INFO - Path: video/teste.mp4
INFO - Obtendo conteúdo do arquivo video/teste.mp4 do S3...
INFO - Vídeo carregado: 300 frames, 30.0 FPS
INFO - Extraindo frames nas posições: [0, 100, 200, 299]
INFO - Frame 1/4 extraído
INFO - Frame 2/4 extraído
INFO - Frame 3/4 extraído
INFO - Frame 4/4 extraído
- Verifique se os tópicos foram criados

### Erro de acesso ao S3
- Valide suas credenciais AWS
- Verifique as permissões IAM do bucket
- Confirme que o bucket existe na região especificada

### Arquivo não encontrado no S3
- Verifique se o path na mensagem está correto
- Confirme que o arquivo existe no bucket configurado
- Certifique-se que o path não começa com `/`

### Erro ao processar vídeo
- Verifique se o arquivo é um vídeo válido (mp4, avi, etc.)
- Confirme que o OpenCV está instalado: `pip install opencv-python`
- Verifique os logs para detalhes específicos do erro

### Processamento lento
- Aumente `MAX_WORKERS` no `.env` (cuidado com recursos do sistema)
- Verifique a conexão com S3 (latência de rede)
- Considere usar instâncias com mais CPU/memória

## 📚 Documentação Adicional

- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Guia completo de implementação e arquitetura
# Com Docker
docker-compose up -d kafka
```

### 2. Inicie a aplicação:

```powershell
python -m src.main
```

### 3. Verifique o healthcheck:

```powershell
# PowerShell
Invoke-WebRequest http://localhost:8000/health

# Ou no navegador:
# http://localhost:8000/health
# http://localhost:8000/docs
```

### 4. Envie uma mensagem de teste:

```powershell
# Use o kafka-console-producer ou sua ferramenta preferida
kafka-console-producer --broker-list localhost:9092 --topic video-events

# Digite a mensagem JSON:
{"s3_key": "test/video.mp4"}
```

## 📝 Logs

A aplicação gera logs no formato:

```
2026-01-09 20:00:00 - src.kafka_consumer - INFO - Mensagem recebida: {'s3_key': 'videos/test.mp4'}
2026-01-09 20:00:01 - src.s3_client - INFO - Obtendo conteúdo do arquivo videos/test.mp4 do S3...
2026-01-09 20:00:02 - src.s3_client - INFO - Arquivo videos/test.mp4 lido com sucesso (1024000 bytes)
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.

## 🆘 Troubleshooting

### Erro de conexão com Kafka
- Verifique se o Kafka está rodando
- Confirme o endereço em `KAFKA_BOOTSTRAP_SERVERS`

### Erro de acesso ao S3
- Valide suas credenciais AWS
- Verifique as permissões IAM do bucket
- Confirme que o bucket existe na região especificada

### Arquivo não encontrado no S3
- Verifique se o campo `s3_key` na mensagem está correto
- Confirme que o arquivo existe no bucket configurado
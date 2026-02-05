# Hackaton SOAT11 - Video Processor

Aplicação Python para processar vídeos do S3, extraindo frames e gerando arquivos ZIP, com processamento paralelo via **AWS SQS** e integração com PostgreSQL.

## 📋 Descrição

Esta aplicação roda um servidor FastAPI que:
- Escuta mensagens do **AWS SQS** com informações de vídeos
- Gerencia processamento de vídeos com banco de dados PostgreSQL (RDS)
- Controla status de processamento (aguardando, processando, finalizado, erro)
- Baixa vídeos do AWS S3
- Extrai frames distribuídos ao longo do vídeo (início, meio e fim)
- Gera arquivo ZIP com as imagens
- Faz upload do ZIP no S3
- Envia mensagem de conclusão com dados do usuário para fila SQS de saída
- **Processa múltiplos vídeos simultaneamente**

## 🚀 Funcionalidades

- ✅ **Processamento Paralelo** - Processa múltiplos vídeos ao mesmo tempo
- ✅ **Integração com AWS SQS** - Mensageria escalável e gerenciada
- ✅ **Integração com PostgreSQL (RDS)** - Controle de status e dados de vídeos/usuários
- ✅ Servidor FastAPI com healthcheck para EKS/Docker
- ✅ Consumer SQS rodando em background com long polling
- ✅ Extração inteligente de frames (início, meio e fim do vídeo)
- ✅ Geração automática de ZIP com frames
- ✅ Upload automático no S3 (pasta `zip/`)
- ✅ Producer SQS para notificação de conclusão com dados do usuário
- ✅ Tratamento de erros com atualização de status
- ✅ Arquitetura Hexagonal (Ports & Adapters)
- ✅ Logging detalhado por vídeo
- ✅ Validação de configurações
- ✅ Documentação automática (Swagger)
- ✅ Infraestrutura como Código (Terraform)

## 📦 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+ (RDS ou local para desenvolvimento)
- Conta AWS com acesso ao SQS e S3
- OpenCV (incluído no requirements.txt)
- Ambiente virtual Python (recomendado)

### Para Desenvolvimento Local
- Docker e Docker Compose (para LocalStack e PostgreSQL)
- AWS CLI configurado

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

### Para Produção (AWS Real)
```env
# AWS SQS
SQS_INPUT_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/video-input-queue
SQS_OUTPUT_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/video-output-queue

# AWS S3
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=seu-bucket

# PostgreSQL Database (RDS)
DB_HOST=seu-rds-endpoint.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=videoprocessor
DB_USER=postgres
DB_PASSWORD=sua-senha-segura

# Aplicação
LOG_LEVEL=INFO
APP_NAME=video-processor-api
MAX_WORKERS=3  # Número de vídeos processando simultaneamente
```

### Para Desenvolvimento Local (com LocalStack)
```env
# AWS SQS
SQS_INPUT_QUEUE_URL=http://localhost:4566/000000000000/video-input-queue
SQS_OUTPUT_QUEUE_URL=http://localhost:4566/000000000000/video-output-queue

# AWS (LocalStack)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
S3_BUCKET_NAME=video-bucket-local

# PostgreSQL Database (local)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=videoprocessor
DB_USER=postgres
DB_PASSWORD=postgres

# Aplicação
LOG_LEVEL=INFO
APP_NAME=video-processor-api
MAX_WORKERS=3
```

## 🗄️ Banco de Dados

### Estrutura das Tabelas

#### Tabela: cliptozip.videos

```sql
CREATE TABLE cliptozip.videos (
    video_id uuid NOT NULL,
    user_id uuid NOT NULL,
    data_video_up timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status int4 NOT NULL,
    video_name varchar(200) NULL,
    zip_name varchar(200) NULL,
    descricao varchar(500) NULL,
    titulo varchar(150) NULL,
    metadados jsonb NULL,
    CONSTRAINT videos_pkey PRIMARY KEY (video_id),
    CONSTRAINT videos_user_fk FOREIGN KEY (user_id) REFERENCES cliptozip."user"(user_id)
);
```

#### Tabela: cliptozip.user

```sql
CREATE TABLE cliptozip."user" (
    user_id uuid DEFAULT gen_random_uuid() NOT NULL,
    "name" varchar(255) NULL,
    email varchar(255) NOT NULL,
    password_hash varchar(255) NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (user_id)
);
CREATE INDEX idx_app_user_email ON cliptozip."user" USING btree (email);
```

### Status dos Vídeos

| Status | Descrição |
|--------|-----------|
| 1 | Aguardando processamento |
| 2 | Processando |
| 3 | Finalizado com sucesso |
| 4 | Erro no processamento |

## 📨 Mensagens SQS

### Mensagem de Entrada (Fila: video-input-queue)

```json
{
  "video_id": "uuid-do-video",
  "path": "video/nome-do-video.mp4"
}
```

### Mensagem de Saída - Sucesso (Fila: video-output-queue)

```json
{
  "titulo": "Nome do vídeo",
  "status": "Finalizado",
  "mensagem": "Seu zip está pronto para download",
  "emailUsuario": "usuario@email.com",
  "nomeUsuario": "Nome do Usuário"
}
```

### Mensagem de Saída - Erro (Fila: video-output-queue)

```json
{
  "titulo": "Nome do vídeo",
  "status": "Erro",
  "mensagem": "Houve um erro no processamento do seu vídeo",
  "emailUsuario": "usuario@email.com",
  "nomeUsuario": "Nome do Usuário"
}
```

## 🔄 Fluxo de Processamento

```
📥 SQS (video-input-queue) - Recebe video_id e path
    ↓
🔍 Busca vídeo e usuário no PostgreSQL pelo video_id
    ↓
✅ Valida status = 1 (aguardando processamento)
    ↓
🔄 Atualiza status = 2 (processando)
    ↓
📦 Download vídeo do S3
    ↓
🎬 Extração de 4 frames (início, meio, fim)
    ↓
📦 Criação de arquivo ZIP com frames
    ↓
☁️ Upload do ZIP para S3 (pasta zip/)
    ↓
✅ Sucesso: Status = 3 + salva zip_name + envia mensagem com dados do usuário
❌ Erro: Status = 4 + envia mensagem de erro com dados do usuário
    ↓
📤 SQS (video-output-queue) - Notificação ao usuário
    ↓
🗑️ Mensagem deletada da fila de entrada
```

### 🎯 Extração de Frames

Os frames são extraídos de forma distribuída:
- **Frame 1**: Início do vídeo (frame 0)
- **Frame 2**: Meio do vídeo (~33%)
- **Frame 3**: Meio-fim do vídeo (~66%)
- **Frame 4**: Final do vídeo (último frame)

Exemplo: Vídeo com 300 frames → Extrai frames: 0, 100, 200, 299

## ⚡ Processamento Paralelo

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

## 🏗️ Arquitetura

```
src/
├── domain/                    # Entidades do domínio
│   └── entities/
│       ├── video_entity.py    # Entidade de vídeo (com campos do banco)
│       └── user_entity.py     # Entidade de usuário
│
├── application/               # Lógica de negócio
│   ├── ports/                # Interfaces (contratos)
│   │   ├── storage_port.py
│   │   ├── message_producer_port.py
│   │   └── repository_port.py  # Port para acesso ao banco
│   ├── services/             # Serviços de domínio
│   │   └── video_processing_service.py
│   └── use_cases/            # Casos de uso
│       └── process_video_use_case.py
│
├── adapters/                 # Implementações dos ports
│   ├── input/               # Entrada (driving)
│   │   ├── consumers/
│   │   │   └── kafka_consumer.py
│   │   └── routers/
│   │       └── health_controller.py
│   └── output/              # Saída (driven)
│       ├── persistence/
│       │   ├── database_connection.py    # Conexão PostgreSQL
│       │   ├── repositories/
│       │   │   └── video_repository.py   # Repositório de vídeos
│       │   └── s3/
│       │       └── s3_client.py
│       └── producers/
│           └── sqs_producer.py          # Producer SQS
│
├── config/
│   └── settings.py           # Configurações
└── main.py                   # Ponto de entrada
```

## 🚀 Executando a Aplicação

### Opção 1: Desenvolvimento Local (com LocalStack)

#### 1. Inicie os serviços Docker:

```powershell
docker-compose up -d
```

Isso iniciará:
- PostgreSQL (porta 5432)
- LocalStack (porta 4566) - simula SQS e S3

#### 2. Inicialize recursos AWS no LocalStack:

```powershell
# PowerShell
.\scripts\init-localstack.ps1

# Bash (Linux/Mac)
chmod +x ./scripts/init-localstack.sh
./scripts/init-localstack.sh
```

#### 3. Configure o `.env` conforme mostrado na seção de configuração

#### 4. Inicie a aplicação:

```powershell
python -m src.main
```

O servidor estará disponível em: http://localhost:3000

**Endpoints disponíveis:**
- `GET /video-processor-api/health` - Healthcheck para EKS/Docker
- `GET /video-processor-api/apidocs` - Documentação interativa (Swagger)

#### 5. Verifique o healthcheck:

```powershell
# PowerShell
Invoke-WebRequest http://localhost:3000/video-processor-api/health

# Ou no navegador:
# http://localhost:3000/video-processor-api/health
# http://localhost:3000/video-processor-api/apidocs
```

#### 6. Envie mensagens de teste para SQS:

```powershell
# PowerShell - LocalStack
aws --endpoint-url=http://localhost:4566 sqs send-message `
  --queue-url http://localhost:4566/000000000000/video-input-queue `
  --message-body '{"video_id": "uuid-do-video", "path": "video/teste.mp4"}'
```

### Opção 2: Produção (AWS Real)

#### 1. Provisione a infraestrutura AWS com Terraform:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Veja detalhes em [terraform/README.md](terraform/README.md)

#### 2. Configure o `.env` com os valores reais da AWS

Use os outputs do Terraform para preencher as variáveis de ambiente.

#### 3. Inicie a aplicação:

```bash
python -m src.main
```

#### 4. Envie mensagens para SQS (AWS Real):

```bash
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/video-input-queue \
  --message-body '{"video_id": "uuid-do-video", "path": "video/teste.mp4"}'
```

Para parar, pressione `Ctrl+C`

## 📝 Logs

A aplicação gera logs detalhados para cada vídeo processado:

```
INFO - 🚀 Iniciando aplicação...
INFO - ✅ Conexão com PostgreSQL estabelecida
INFO - ✅ ThreadPoolExecutor inicializado com 3 workers
INFO - ✅ S3 Client inicializado
INFO - ✅ SQS Producer inicializado
INFO - ✅ Video Processing Service inicializado
INFO - ✅ Process Video Use Case inicializado
INFO - ✅ SQS Consumer inicializado
INFO - 🎉 Aplicação iniciada com sucesso!

INFO - 🎬 [Video ID: uuid-123] Tarefa submetida para processamento
INFO - 📊 Tarefas em processamento: ~1
INFO - === [Thread-ThreadPoolExecutor-0_0] Processando vídeo ===
INFO - Video ID: uuid-123
INFO - Vídeo encontrado: Meu Vídeo Teste
INFO - Usuário: João Silva (joao@email.com)
INFO - Status atualizado para: 2 (Processando)
INFO - Vídeo carregado: 300 frames, 30.0 FPS
INFO - Extraindo frames nas posições: [0, 100, 200, 299]
INFO - 4 frames extraídos com sucesso
INFO - ZIP criado com sucesso
INFO - ZIP enviado com sucesso para S3: zip/teste.zip
INFO - Status atualizado para: 3 (Finalizado)
INFO - ✅ [Video ID: uuid-123] Vídeo processado com sucesso!
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
  -p 3000:3000 \
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

## 📁 Estrutura do Projeto

```
hackaton-soat11-videoprc/
├── src/
│   ├── __init__.py
│   ├── main.py                # Ponto de entrada
│   ├── domain/
│   │   └── entities/
│   │       ├── video_entity.py
│   │       └── user_entity.py
│   ├── application/
│   │   ├── ports/
│   │   ├── services/
│   │   └── use_cases/
│   ├── adapters/
│   │   ├── input/
│   │   └── output/
│   └── config/
│       └── settings.py
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🆘 Troubleshooting

### Erro de conexão com PostgreSQL
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais em `DB_USER` e `DB_PASSWORD`
- Verifique se o banco de dados `cliptozip` existe
- Confirme que as tabelas foram criadas corretamente

### Vídeo não processado
- Verifique se o vídeo existe no banco com status = 1
- Confirme que o `video_id` na mensagem Kafka está correto
- Verifique se há relação com usuário válido (FK)

### Erro de conexão com Kafka
- Verifique se o Kafka está rodando
- Confirme o endereço em `KAFKA_BOOTSTRAP_SERVERS`
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

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.
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
##  Documenta��o Adicional

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Guia completo de migra��o do Kafka para SQS
- [terraform/README.md](terraform/README.md) - Como provisionar infraestrutura AWS com Terraform

##  Migra��o do Kafka para SQS

Esta aplica��o foi migrada do Kafka para AWS SQS. Para detalhes completos sobre:
- Mudan�as realizadas
- Compara��o Kafka vs SQS
- Instru��es de configura��o
- Permiss�es IAM necess�rias

Consulte: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

##  Changelog

### v2.0.0 - Migra��o para AWS SQS (2026-02-04)
-  Migra��o completa de Kafka para AWS SQS
-  Adicionado suporte para LocalStack (desenvolvimento local)
-  Criados scripts de inicializa��o de recursos AWS
-  Adicionada infraestrutura como c�digo (Terraform)
-  Removidas todas as depend�ncias do Kafka
-  Atualizada documenta��o completa

### v1.0.0 - Vers�o inicial com Kafka
-  Processamento de v�deos com Kafka
-  Integra��o com PostgreSQL
-  Extra��o de frames e gera��o de ZIP
-  Upload para S3

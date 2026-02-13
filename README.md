![Static Badge](https://img.shields.io/badge/Python-3.11-blue)
![Static Badge](https://img.shields.io/badge/FastAPI-latest-green)
[![Apache 2.0 License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

# 📱 Hackaton FIAP - ClipToZip - Microsserviço de Processamento de Vídeo - Grupo 13

![Logo ClipToZip](/docs/cliptozip.png)

## 📝 Sobre o Projeto

Este repositório contém o código-fonte do microsserviço de **Processamento de Vídeo** do ecossistema **ClipToZip**, desenvolvido pelo Grupo 13 como parte do projeto Hackaton da FIAP.

O objetivo principal deste serviço é processar vídeos recebidos via eventos SQS, extrair frames utilizando OpenCV e disponibilizar os frames processados em formato ZIP no S3.

### Funcionalidades Principais

*   **Consumer SQS**: Escuta fila de eventos, aguardando por novos vídeos no sistema.
*   **Processamento de Vídeo**: Faz o processamento dos vídeos e divide em frames utilizando OpenCV.
*   **Upload de arquivo ZIP**: Gera arquivo ZIP com os frames extraídos e salva em S3.
*   **Producer SQS**: Envia mensagem para fila SQS de notificação após conclusão do processamento.
*   **Processamento Paralelo**: Utiliza ThreadPoolExecutor para processar múltiplos vídeos simultaneamente.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes tecnologias e bibliotecas:

*   **Linguagem**: [Python 3.11](https://www.python.org/)
*   **Framework Web**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Servidor ASGI**: [Uvicorn](https://www.uvicorn.org/)
*   **Banco de Dados**: [PostgreSQL](https://www.postgresql.org/)
*   **Processamento de Vídeo**: [OpenCV](https://opencv.org/)
*   **Serviços AWS**: [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) (SQS, S3)
*   **Validação**: [Pydantic](https://docs.pydantic.dev/)
*   **Testes**: [pytest](https://pytest.org/), pytest-cov, pytest-mock, pytest-asyncio
*   **Containerização**: [Docker](https://www.docker.com/) & Docker Compose
*   **Ambiente Local AWS**: [LocalStack](https://localstack.cloud/)

---

## 🧩 Arquitetura da Solução

A aplicação segue os princípios da **Arquitetura Hexagonal (Ports and Adapters)**, promovendo o desacoplamento entre a lógica de negócio e os detalhes de infraestrutura.

### Camadas da Aplicação

1.  **Domain (Núcleo)**: Contém as entidades (`User`, `Video`) e regras de negócio fundamentais. É isolado de frameworks externos.
2.  **Application (Casos de Uso)**: Orquestra o fluxo de dados.
    *   `ProcessVideoUseCase`: Responsável por coordenar o processamento de vídeos.
    *   `VideoProcessingService`: Serviço que realiza a extração de frames do vídeo.
    *   **Ports**: Interfaces que definem os contratos de entrada (In) e saída (Out).
3.  **Adapters (Infraestrutura)**: Implementações concretas das portas.
    *   **In (Entrada)**:
        *   `SQSConsumer`: Consumer de mensagens da fila SQS.
        *   `HealthController`: Exposição de endpoint de healthcheck REST.
    *   **Out (Saída)**:
        *   `VideoRepository`: Persistência no PostgreSQL.
        *   `S3Client`: Gerenciamento de upload/download de arquivos no S3.
        *   `SQSProducer`: Producer de mensagens para fila SQS de notificação.

---

## 🚀 Como Executar

### Python 3.11 instalado
*   Docker e Docker Compose instalados

### Passo a Passo

1.  **Subir a Infraestrutura Local**:
    Utilize o Docker Compose para iniciar o PostgreSQL e o LocalStack (SQS, S3).
    ```bash
    docker-compose up -d
    ```

2.  **Instalar as Dependências**:
    Instale as dependências do projeto.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Variáveis de Ambiente**:
    Crie um arquivo `.env` na raiz do projeto com as variáveis necessárias (veja `.env.example` se disponível).

4.  **Executar a Aplicação**:
    Inicie a aplicação.
    ```bash
    python -m src.main
    ```

5.  **Acessar a API**:
    *   URL Base: `http://localhost:8000`
    *   Healthcheck: `http://localhost:8000/health
    *   Swaggerpytest e pytest-mock para validar a lógica de negócio isolada, garantindo que cada componente (especialmente nas camadas de domain e application) funcione conforme o esperado.
*   **Cobertura**: O projeto mantém uma cobertura de código superior a 80%, verificada automaticamente no pipeline de CI/CD.
*   **Foco**: Validação de regras de negócio, processamento de vídeos e integração com serviços AWS.

### ⚙️ Como executar os testes
Para rodar a suíte completa de testes unitários e gerar o relatório de cobertura, execute:

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

Após a execução, o relatório estará disponível em:
- Relatório de Cobertura (HTML): `htmlcov
Para rodar a suíte completa de testes unitários e gerar o relatório de cobertura, execute o comando Maven:

```Bash
mvn clean verify
```

Após a execução, o relatório estará disponível em:
- RGET` | `/health` | Healthcheck da aplicação (status do serviço). |

### Processamento Assíncrono

O processamento de vídeos é realizado de forma assíncrona através de:
*   **Consumer SQS**: Escuta a fila `CLIPTOZIP_EVENTS_URL` para receber eventos de novos vídeos.
*   **Producer SQS**: Envia notificações para a fila `CLIPTOZIP_NOTIFICATIONS_URL` após conclusão do processamento.
| `GET` | `/swagger-ui/index.html` | Documentação interativa da API (Swagger/OpenAPI). |

---

## 📂 Recursos Adicionais

*   **Postman Collection**: Para facilitar os testes e a integração, disponibilizamos uma collection do Postman com as requisições configuradas.
    *   [Baixar Collection Postman](docs/ClickToZip-Auth.postman_collection.json)
---

## 👥 Autores - Grupo 13

| Nome | RM |
|---|---|
| **Fabiana Casagrande Costa** | RM362339 |
| **Felipe Costacurta Paruce** | RM364868 |
| **Rafael Fonseca Hermes Azevedo** | RM361445 |
| **Samuel Videira** | RM363405 |

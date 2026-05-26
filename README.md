# docsmart
Intelligent information extraction from various document source.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Examples](#examples)
- [Usage](#usage)
- [License](#license)

## 📖 Project Overview
This repository contains a growing collection of **out-of-the-box tools** and **hands-on examples** demonstrating how to extract information effectively from documents based-on the following techniques:

* 🔍 Intelligent web crawling
* 🧠 LLM-powered extraction
* 🤖 OCR Integration
* 📊 Table Extraction
* 📄 Structured data parsing
* 🧹 Content cleaning & markdown generation
* ⚡ Async workflows
* 🌐 Browser automation

## 💻 Tech Stack
* **Project Manager**: [astral-sh/uv](https://github.com/astral-sh/uv "uv GitHub")
* **Language**: [Python 3.12+](https://python.org "Python Official Site")
* **Web Scraping**: [Crawl4AI](https://github.com/unclecode/crawl4ai "Crawl4AI GitHub")
* **Document Processing**: [Docling](https://github.com/docling-project/docling "Docling GitHub")
* **LLM Server**: [Ollama](https://ollama.com/ "Ollama Official Site")
* **LLM Frameworks**: [LangChain](https://github.com/langchain-ai/langchain "LangChain GitHub")

## 🚀 Getting Started

### Prerequisites

#### 1. Ensure you have uv(Python package and project manager) installed, then install the core library:

1.1 Install uv
```bash
# uv Installation 
# 1. on macOS or Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. on Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

1.2 Install python via uv
```bash
# Python 3.12+ Installation
uv python install 3.12

# Verification
uv python list
```

#### 2. (Optional) Setup and run the ollama server (Docker is recommended), then install your preferred models.

2.1 Create the isolated folder and docker-compose.yml
```bash
mkdir llm
cd llm
vim docker-compose.yml
```

2.2 Edit the docker-compose.yml for ollama and open-webui
```yaml
services:
  ollama:
    volumes:
      - ./ollama:/root/.ollama
    container_name: ollama
    ports:
      - 11434:11434
    pull_policy: always
    tty: true
    restart: unless-stopped
    image: ollama/ollama

  open-webui:
    build:
      context: .
      args:
        OLLAMA_BASE_URL: '/ollama'
      dockerfile: Dockerfile
    image: ghcr.io/open-webui/open-webui #:main
    container_name: open-webui
    volumes:
      - ./open-webui:/app/backend/data
    depends_on:
      - ollama
    ports:
      - 3000:8080
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped

volumes:
  ollama:
  open-webui:
```

2.3 Create the shell script for making ollama and open-webui folders
```bash
vim reset.sh
```

2.4 Edit the shell script
```bash
#!/bin/bash
#This program reset the ollama and open-webui folders
echo "---------------------------------"
echo "  Hello, Reset Ollama Script!"
echo "---------------------------------"
rm -rf ./ollama
rm -rf ./open-webui
ls
echo "-------- ollama and open-webui folders removed --------"
mkdir ./ollama
mkdir ./open-webui
ls
echo "-------- ollama and open-webui folders created --------"
```

2.5 Change mode to be executable
```bash
chmod u+x ./reset.sh
```

2.6 Excecute docker compose
```bash
docker compose pull
docker compose up -d
```

2.7 Install your preferred models via API
```bash
curl http://localhost:11434/api/pull -d '{
  "name": "granite4.1:8b"
}'

curl http://localhost:11434/api/pull -d '{
  "name": "nomic-embed-text-v2-moe:latest"
}'
```

2.8 Stop docker compose
```bash
docker compose down -v
```

### Installation
```bash
# Step 1: Clone this repository
git clone https://github.com/hsinpeng/docsmart.git

# Step 2: Enter the project folder
cd docsmart
   
# Step 3: Install project-specific dependencies
uv sync
   
# Step 4: Initialize and configure the environment for the Crawl4AI framework
crawl4ai-setup
   
# Step 5: Make a empty folder for outputs
mkdir outputs
```

## 🛠️ Usage
Run the basic conversion script:
```python
Under Construction...
```

## 📄 License
This project is licensed under the **MIT License**.


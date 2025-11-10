# 🚀 Subtitle Translator

Este projeto fornece uma solução completa para extrair, limpar, traduzir e reembutir legendas em arquivos de vídeo MKV e MP4, utilizando a API Google Gemini AI para tradução.

## ✨ Funcionalidades

- **Extração de Legendas**: Extrai legendas SRT de arquivos MKV e MP4.
- **Limpeza de Legendas**: Remove tags HTML e duplicações de legendas SRT.
- **Tradução AI**: Traduz legendas SRT para o idioma desejado (padrão: Português do Brasil) usando a API Google Gemini.
- **Reembutimento de Legendas**: Reembuti a legenda traduzida de volta no arquivo de vídeo original (MKV ou MP4), criando um novo arquivo de vídeo com legendas.
- **Interface Gráfica (GUI)**: Uma aplicação PyQt6 para gerenciar e executar o pipeline de tradução de forma interativa, com suporte a arrastar e soltar.
- **Suporte Multi-formato**: Funciona tanto com arquivos MKV quanto MP4, preservando o formato original do vídeo.

## 📦 Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd subtitle-translator
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # .\venv\Scripts\activate  # No Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Instale ferramentas externas:**
    *   **FFmpeg**: Necessário para extração de legendas e reembutimento em arquivos MP4. [Download FFmpeg](https://ffmpeg.org/download.html)
    *   **mkvtoolnix**: Necessário para reembutir legendas em arquivos MKV. [Download mkvtoolnix](https://mkvtoolnix.download/)

## 🔑 Configuração da API Key do Gemini

1.  Obtenha sua chave API no [Google AI Studio](https://aistudio.google.com/apikey).
2.  Defina a chave API como uma variável de ambiente (recomendado):
    ```bash
    export GEMINI_API_KEY="SUA_CHAVE_API_AQUI" # Linux/macOS
    # set GEMINI_API_KEY=SUA_CHAVE_API_AQUI   # Windows (CMD)
    # $env:GEMINI_API_KEY="SUA_CHAVE_API_AQUI" # Windows (PowerShell)
    ```
    Alternativamente, você pode inseri-la diretamente na GUI.

## 🚀 Como Usar

### Via Interface Gráfica (GUI)

1.  Inicie a aplicação GUI:
    ```bash
    python gui_translator.py
    ```
2.  Adicione arquivos de vídeo (MKV ou MP4) arrastando e soltando-os na lista ou usando "Arquivo -> Abrir Vídeo(s)...".
3.  (Opcional) Ajuste o idioma de destino ou insira sua chave API do Gemini.
4.  Clique em "Traduzir Vídeos" para iniciar o processo.

Todos os arquivos gerados (legendas intermediárias e o vídeo final com legenda traduzida) serão salvos na pasta `output/` dentro do diretório do projeto. O formato original do vídeo (MKV ou MP4) será preservado.

### Via Linha de Comando (CLI) - Pipeline Completo

Para usar o pipeline completo via CLI, execute o script `full_translation_pipeline.py`:

```bash
python scripts/full_translation_pipeline.py <CAMINHO_PARA_VIDEO> [--lang "Idioma de Destino"] [--api-key "SUA_CHAVE_API"]
```

**Exemplo com MKV:**
```bash
python scripts/full_translation_pipeline.py "/caminho/para/seu/video.mkv" --lang "Brazilian Portuguese"
```

**Exemplo com MP4:**
```bash
python scripts/full_translation_pipeline.py "/caminho/para/seu/video.mp4" --lang "Brazilian Portuguese"
```

## ⚙️ Estrutura do Projeto

```
subtitle-translator/
├── gui_translator.py
├── scripts/
│   ├── extract_sub.sh
│   ├── clean_dedup_srt.py
│   ├── reembed_srt.py
│   └── full_translation_pipeline.py
├── output/ (criado automaticamente para artefatos)
├── README.md
└── requirements.txt
```

## 📝 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

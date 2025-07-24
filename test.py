import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def baixar_recursivo(url: str, caminho_local: str):
    """
    Baixa arquivos de uma URL recursivamente.
    Se a URL for um diretório, cria uma pasta local e baixa seu conteúdo.
    Se for um arquivo, faz o download diretamente.
    """
    print(f"-> Processando: {url}")
    try:
        # Faz a requisição para a URL
        resposta = requests.get(url, timeout=10)
        # Lança um erro para status ruins (404, 500, etc.)
        resposta.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"   [ERRO] Não foi possível acessar a URL {url}: {e}")
        return

    # Se a resposta for uma página HTML, provavelmente é um diretório
    if 'text/html' in resposta.headers.get('Content-Type', ''):
        # Cria a pasta local se ela não existir
        if not os.path.exists(caminho_local):
            print(f"   [*] Criando pasta: {caminho_local}")
            os.makedirs(caminho_local)
        
        # Analisa o HTML para encontrar todos os links (tags <a>)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            
            # Ignora links irrelevantes (para pasta pai, âncoras, etc.)
            if href is None or href.startswith('?') or href.startswith('#') or href == '../' or href == '/':
                continue
            
            # Monta a URL completa para o próximo item
            url_completa_filho = urljoin(url, href)
            # Monta o caminho local completo para o próximo item
            caminho_local_filho = os.path.join(caminho_local, href)
            
            # Chama a função recursivamente para o próximo link
            baixar_recursivo(url_completa_filho, caminho_local_filho)
            
    # Se não for HTML, trata como um arquivo para download
    else:
        # Extrai o nome do diretório do caminho local
        pasta_pai = os.path.dirname(caminho_local)
        
        # Cria a pasta pai se ela não existir
        if not os.path.exists(pasta_pai):
            print(f"   [*] Criando pasta pai: {pasta_pai}")
            os.makedirs(pasta_pai)
            
        print(f"   [*] Baixando arquivo: {os.path.basename(caminho_local)}")
        try:
            # Salva o conteúdo do arquivo
            with open(caminho_local, 'wb') as f:
                f.write(resposta.content)
        except IOError as e:
            print(f"   [ERRO] Não foi possível salvar o arquivo {caminho_local}: {e}")


# --- PONTO DE PARTIDA ---
if __name__ == "__main__":
    # URL inicial de onde começar o download.
    # Exemplo: um diretório público de arquivos de um projeto.
    URL_INICIAL = "https://teste1234-eight.vercel.app/"
    
    # Pasta local onde tudo será salvo.
    PASTA_DOWNLOAD = "downloads"

    print(f"Iniciando download recursivo de: {URL_INICIAL}")
    print(f"Salvando em: ./{PASTA_DOWNLOAD}/\n")

    # Garante que a pasta principal de download exista
    if not os.path.exists(PASTA_DOWNLOAD):
        os.makedirs(PASTA_DOWNLOAD)

    # Inicia o processo
    baixar_recursivo(URL_INICIAL, PASTA_DOWNLOAD)

    print("\nDownload Concluído!")

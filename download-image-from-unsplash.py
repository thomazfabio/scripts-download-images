import os
import requests
from .keys.keys import unsplashKey

# Configurações de API
UNSPLASH_ACCESS_KEY = unsplashKey # Insira sua chave de acesso aqui

def create_folder(folder_name):
    root_folder = "downloads-unsplash"
    full_path = os.path.join(root_folder, folder_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path

def download_images(image_links, folder_name, file_extension):
    count = 1
    for link in image_links:
        try:
            response = requests.get(link, stream=True)
            if response.status_code == 200:
                image_path = os.path.join(folder_name, f'{os.path.basename(folder_name)}_{count}{file_extension}')
                with open(image_path, 'wb') as out_file:
                    for chunk in response:
                        out_file.write(chunk)
                print(f'Downloaded {image_path}')
                count += 1
            del response
        except Exception as e:
            print(f"Erro ao baixar a imagem: {e}")
            continue

def get_image_links(query, num_images, page_start=1, downloaded_links=None):
    image_links = []
    page = page_start
    per_page = min(num_images, 50)  # Limita a quantidade de imagens por consulta a 50
    downloaded_links = downloaded_links or set()  # Conjunto para evitar duplicatas

    while len(image_links) < num_images:
        search_url = f"https://api.unsplash.com/search/photos?query={query}&page={page}&per_page={per_page}&client_id={UNSPLASH_ACCESS_KEY}"
        response = requests.get(search_url)
        
        if response.status_code == 200:
            results = response.json()
            items = results.get('results', [])
            if not items:
                break  # Se não houver mais resultados, interrompe o loop
            for item in items:
                link = item['urls']['regular']
                if link not in downloaded_links:
                    image_links.append(link)
                    downloaded_links.add(link)
        else:
            print(f"Erro na solicitação: {response.status_code}")
            break
        
        page += 1  # Avança para a próxima página de resultados
    
    return image_links[:num_images], page, downloaded_links  # Retorna as novas imagens, próxima página e links já baixados

def main():
    # Interação com o usuário
    query = input("Digite a descrição da imagem que você deseja baixar: ")
    file_extension = ".jpg"  # Unsplash retorna URLs de imagens em formato .jpg
    num_images = int(input("Digite a quantidade de imagens que deseja baixar: "))
    folder_name = input("Digite o nome da pasta onde deseja salvar as imagens: ")
    page_start = int(input("Digite o número da página de onde começar a busca (por exemplo, se já baixou as primeiras 50, coloque 2): "))
    
    # Cria a pasta para salvar as imagens dentro de 'downloads-unsplash'
    full_folder_path = create_folder(folder_name)
    
    # Busca links de imagens
    print(f"Buscando imagens para: {query}, a partir da página {page_start}")
    downloaded_links = set()  # Conjunto para rastrear os links já baixados

    # Busca novas imagens a partir da página especificada
    image_links, last_page, downloaded_links = get_image_links(query, num_images, page_start, downloaded_links)
    
    if not image_links:
        print("Nenhuma imagem encontrada.")
        return
    
    # Faz o download das imagens
    download_images(image_links, full_folder_path, file_extension)
    
    print(f"Download concluído! As imagens foram salvas na pasta {full_folder_path}.")
    print(f"Próxima página a buscar: {last_page}")  # Informa ao usuário qual página buscar da próxima vez

if __name__ == "__main__":
    main()

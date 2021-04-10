import requests
import json
import datetime


def write_json(data, name_json):
    with open(name_json, 'w') as file:
        json.dump(data, file, ensure_ascii=False)

token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'


URL = 'https://api.vk.com/method/users.get'
params = dict(user_ids='begemot_korovin', access_token=token_vk, v='5.130')
res = requests.get(URL, params=params)
begemot_id = res.json()['response'][0]['id']
count = 5

def main():
    response = requests.get('https://api.vk.com/method/photos.get',
                            params={
                                'owner_id': begemot_id,
                                'album_id': 'profile',
                                'access_token': token_vk,
                                'v': '5.130',
                                'count': count,
                                'extended': 1
                            })
    write_json(response.json()['response'], 'photos.json')

if __name__=='__main__':
    main()

def get_largest(size_dict):
    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    else:
        return size_dict['height']




photos = json.load(open('photos.json'))

for i in range(count):
    likes = sum((photos['items'][i]['likes']).values())
    date = photos['items'][i]['date']

like_list = []
url_list = []
info = {}
for photo in photos['items']:
    date = datetime.date.fromtimestamp(photo['date'])
    likes = str(sum((photo['likes']).values())) + '.jpg'
    if likes in like_list:
        likes = str(likes) + ', ' + str(date)
    like_list.append(likes)
    sizes = photo['sizes']
    max_size_url = (max(sizes, key = get_largest)['url'])
    url_list.append((max_size_url))
info['name'] = like_list
info['url'] = url_list



with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()

class YaUploader:
    def __init__(self, token: str):
        self.token = token


    def create_folder(self, name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': name}
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        response = requests.put(url, headers=headers, params=params)
        return response.json()


    def upload_file_to_disk(self, folder_name):
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.create_folder(folder_name)
        for i in range(len(url_list)):
            name = str(info['name'][i])
            params = {'url': info['url'][i], 'path': folder_name + '/' + name, 'overwrite': 'true'}
            response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print("Файлы выгружены успешно")




if __name__ == '__main__':
    yandex_disk = YaUploader(token=token)
    yandex_disk.upload_file_to_disk('фото')


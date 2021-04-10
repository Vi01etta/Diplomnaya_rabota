import token

import requests
import json
import datetime
from pprint import pprint



class VK_unload:
    def __init__(self):
        token_vk = input('Введите Ваш токен Вконтакте: ')
        self.token = token_vk
        input_id = input('Введите идентификатор пользователя: ')
        self.input_id = input_id

    def get_id(self):

        """Позволяет получить id человека"""

        URL = 'https://api.vk.com/method/users.get'
        params = dict(user_ids=self.input_id, access_token=self.token, v='5.130')
        res = requests.get(URL, params=params)
        id_vk = res.json()['response'][0]['id']
        return id_vk

    def write_json(self, data, name_json):
        with open(name_json, 'w') as file:
            json.dump(data, file, ensure_ascii=False)


    def get_album_id(self):

        """Определение id альбома для выгрузки фото"""

        URL = 'https://api.vk.com/method/photos.getAlbums'
        input_id = self.get_id()
        params = dict(owner_id=input_id, access_token=self.token, need_system='1', v='5.130')
        res = requests.get(URL, params=params)
        res.raise_for_status()
        print(res.json())
        for result in res.json().values():
            for name_album in result['items']:
                pprint('Для альбома "{}" id альбома: "{}"'.format(name_album["title"], name_album["id"]))
        album_id = int(input('Введите id запрашиваемого альбома: '))
        return album_id



    def photo_json(self):

        """Создание json-файла, чтобы с ним работать и в других классах"""

        count = int(input('Введите количество фотографий для выгрузки: '))
        input_id = self.get_id()
        response = requests.get('https://api.vk.com/method/photos.get',
                                params={
                                    'owner_id': input_id,
                                    'album_id': self.get_album_id(),
                                    'access_token': self.token,
                                    'v': '5.130',
                                    'count': count,
                                    'extended': 1
                                })
        self.write_json(response.json()['response'], 'photo_info.json')
        print('Создан файл "photo_info.json" с информацией по загружаемым фотографиям ')



class YaUploader:
    def __init__(self):
        token_ya = input("Введите Ваш токен Яндекс Диск: ")
        self.token = token_ya


    def get_largest(self, size_dict):

        """Определение максимальный размер фотографий"""

        if size_dict['width'] >= size_dict['height']:
            return size_dict['width']
        else:
            return size_dict['height']


    def change_name(self):

        """Присваивание имён фотографиям"""

        photos = json.load(open('photo_info.json'))
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
            max_size_url = (max(sizes, key=self.get_largest)['url'])
            url_list.append((max_size_url))
        info['name'] = like_list
        info['url'] = url_list
        return info



    def create_folder(self, name):

        """Создание папки, в которую будут сохранятся фотографии"""

        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': name}
        headers = {'Content-Type': 'application/json', 'Authorization': self.token}
        response = requests.put(url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, folder_name):

        """Выгрузка файлов на Яндекс диск"""

        headers = {'Content-Type': 'application/json', 'Authorization': self.token}
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.create_folder(folder_name)
        info_dict = self.change_name()
        for i in range(len(info_dict['url'])):
            name = str(info_dict['name'][i])
            progressive = round(100/len(info_dict['url'])*(i+1), 2)
            params = {'url': info_dict['url'][i], 'path': folder_name + '/' + name, 'overwrite': 'true'}
            response = requests.post(url, headers=headers, params=params)
            print('Загружаю фото № {} из {}. Прогресс: {} %'.format(i+1, len(info_dict['url']), progressive))
        response.raise_for_status()
        if response.status_code == 202:
            print("Файлы выгружены успешно")
        else:
            print('Произошла ошибка')


if __name__ == '__main__':
    vk_photos = VK_unload()
    vk_photos.photo_json()
    yandex_disk = YaUploader()
    yandex_disk.upload_file_to_disk('фото')

import requests
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pprint import pprint
import os
import json
import random
import string
import uuid
import shutil


class RedditScraper:
    def __init__(self, subreddit):
        self.subreddit = subreddit
        self.base_url = f"https://old.reddit.com/r/{subreddit}/top/?sort=top&t=day"
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    @property
    def recent_posts(self):
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to load page {self.base_url}")

        soup = BeautifulSoup(response.content, 'html.parser')
        site_table = soup.find('div', id='siteTable')
        posts = site_table.find_all(
            'div', {'data-context': 'listing'}, limit=10)

        top_posts = []
        for post in posts:
            # Get Author
            author_elm = post.find('a', class_='author')
            author = author_elm.text if author_elm else None
            # Get details
            title_elm = post.find('a', {'data-event-action': 'title'})
            if title_elm:
                href = title_elm['href']
                text = title_elm.text
                if href.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    post_type = 'image'
                elif 'v.redd.it' in href:
                    post_type = 'video'
                else:
                    continue
                top_posts.append(
                    {'title': text, 'url': href, 'type': post_type, 'author': author})
        return top_posts

    def save_media(self):
        project_root = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(project_root, 'build/tmp')
        if os.path.exists(build_dir):
            print('Clearing TMP Folder')
            shutil.rmtree(build_dir)
        os.makedirs(build_dir, exist_ok=True)

        manifest_content = []
        for post in self.recent_posts:
            if post['type'] == 'image':
                url = post['url']

                url_as_path = urlparse(url).path
                file_extension = os.path.splitext(url_as_path)[1]
                name = f'{uuid.uuid4()}{file_extension}'
                path = os.path.join(build_dir, name)

                urllib.request.urlretrieve(url, path)
                manifest_content.append({
                    'author': post['author'],
                    'url': url,
                    'path': path,
                    'name': name,
                    'title': post['title'],
                    'type': 'image'
                })
                print(f'Saved image {name}')
            elif post['type'] == 'video':
                video_page_url = post['url']
                response = requests.get(video_page_url, headers=self.headers)
                if response.status_code != 200:
                    raise Exception(
                        f"Failed to load video page {video_page_url}")
                soup = BeautifulSoup(response.content, 'html.parser')
                video_element = soup.find('shreddit-player-2')
                packaged_media_json = video_element['packaged-media-json']
                media_data = json.loads(packaged_media_json)

                permutations = media_data['playbackMp4s']['permutations']
                highest_res_video = max(
                    permutations, key=lambda x: x['source']['dimensions']['height'])
                duration = media_data['playbackMp4s']['duration']
                dimensions = highest_res_video['source']['dimensions']
                url = highest_res_video['source']['url']

                url_as_path = urlparse(url).path
                file_extension = os.path.splitext(url_as_path)[1]
                name = f'{uuid.uuid4()}{file_extension}'
                path = os.path.join(build_dir, name)

                urllib.request.urlretrieve(url, path)

                manifest_content.append({
                    'author': post['author'],
                    'url': url,
                    'path': path,
                    'name': name,
                    'title': post['title'],
                    'duration': duration,
                    'dimensions': dimensions,
                    'type': 'video'
                })
                print(
                    f"Saved video {name}. Data: {duration}s {dimensions['width']}x{dimensions['height']}")

        manifest_path = os.path.join(build_dir, 'manifest.json')
        with open(manifest_path, 'w') as manifest_file:
            json.dump(manifest_content, manifest_file, indent=4)
        print(f'Manifest saved to {manifest_path}')

    @property
    def manifest(self):
        project_root = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(project_root, 'build/tmp')
        manifest_path = os.path.join(build_dir, 'manifest.json')
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as manifest_file:
                return json.load(manifest_file)
        return None
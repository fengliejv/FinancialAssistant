import json

import requests
from bs4 import BeautifulSoup
from certifi import contents
from tenacity import sleep


def load_json(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            hot = json.load(file)
            return hot
    except FileNotFoundError:
        print("未找到指定的 JSON 文件。")


def get_hot_topics():
    url = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true'

    headers = load_json('hot.json')['headers']
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.text
        # result = load_json('hot.json')['sample']
        result = json.loads(result)
        topics = result['data']
        descs = []
        for topic in topics:
            target = topic['target']
            link = target['link']
            title = target['title_area']
            excerpt = target['excerpt_area']

            headers = load_json('target.json')['headers']
            result = requests.get(link['url'], headers=headers)
            result.raise_for_status()
            text = result.text
            # text =load_json('target.json')['sample']
            soup = BeautifulSoup(text, 'lxml')
            question_page = soup.find(class_='QuestionHeader')
            if question_page:
                target_elements =  question_page.find('span', class_='RichText ztext CopyrightRichText-richText css-ob6uua')
                if target_elements is None:
                    print("can not find target.")
                    continue
                contents = target_elements.find_all('p')
                desc = ''
                for content in contents:
                    desc = f'{desc}\n{content.get_text()}'
                print(desc)
                descs.append(desc)
            sleep(5)
        return descs
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return []

# 模拟发表评论（仅为示例，实际需要登录等操作）
def post_comment(topic_url, comment):
    # 这里只是示例，实际需要携带登录后的cookie等信息
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    data = {
        'comment': comment
    }
    try:
        response = requests.post(topic_url, headers=headers, data=data)
        response.raise_for_status()
        print("评论发表成功")
    except requests.RequestException as e:
        print(f"评论发表失败: {e}")

if __name__ == "__main__":
    hot_topics = get_hot_topics()
    print("知乎热门话题:")
    for i, topic in enumerate(hot_topics, 1):
        print(f"{i}. {topic}")

    # 示例：模拟对第一个话题发表评论
    # if hot_topics:
    #     # 这里需要根据实际情况获取正确的话题URL
    #     topic_url = "https://www.zhihu.com/some_topic_url"
    #     comment = "这是一条测试评论"
    #     post_comment(topic_url, comment)
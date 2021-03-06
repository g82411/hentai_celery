from __future__ import absolute_import
import requests
import os
from bs4 import BeautifulSoup
from celery import Celery
from crawler.celery import app
from celery.utils.log import get_logger

from kombu import Exchange, Queue
from celery import group
from time import sleep

logger = get_logger(__name__)
HEADERS = {
    "Host": "exhentai.org",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
    "Connection": "keep-alive"
}

COOKIES = {
    "sk":"nfirszmhxpxzezi6t522ahv6n76t",
    "s":"7a35705f2",
    "lv":"1523895124-1525492055",
    "ipb_pass_hash":"a8f176f10adc6fd2273d1f6a40804aba",
    "ipb_member_id":"2950929",
    "igneous":"942c9e50d"
}
@app.task(bind=True)
def getIndex(self, url):
    res = requests.get(url, headers=HEADERS , cookies=COOKIES)
    page = BeautifulSoup(res.content)
    pageUrls = set(map(lambda x:x["href"], page.select(".gtb a")))
    logger.info("This comic has {0} pages".format(len(pageUrls)))
    tasks = [ getImageUrl.apply_async([url, ], queue="parsing", routing_key="parsing") for url in pageUrls ]

@app.task(bind=True)
def getImageUrl(self, url):
    res = requests.get(url, headers=HEADERS, cookies=COOKIES)
    page = BeautifulSoup(res.content)
    imageUrls = set(map(lambda x:x["href"], page.select(".gdtl a")))
    downloadTasks = group([downloadImage.s(url) for url in imageUrls ])
    downloadPaths = downloadTasks.apply_async(queue="download", routing_key="download")
    while not downloadPaths.ready():
        logger.info("Wait for download tasks")
        sleep(5)


@app.task(bind=True)
def downloadImage(self, url):
    res = requests.get(url, headers=HEADERS, cookies=COOKIES)
    page = BeautifulSoup(res.content)
    imageUrl = page.select("a #img")[0]["src"]
    root_path = url.strip().split("/")[-1].strip().split("-")[0]
    image_name = imageUrl.strip().split("/")[-1]
    downloadPath = "{0}/{1}".format(root_path, image_name)
    if not os.path.isdir(root_path):
        os.mkdir(root_path)
    with open(downloadPath, "wb") as image_fd:
        imageRes = requests.get(imageUrl, headers=HEADERS, cookies=COOKIES)
        image_fd.write(imageRes.content)
    return downloadPath


if __name__ == '__main__':
    getIndex.apply_async(args=["https://exhentai.org/g/1220208/ff58343db8/", ],
                        queue="default", 
                        routing_key="default")


from __future__ import absolute_import
from crawler.tasks import getIndex

if __name__ == "__main__":
    getIndex.apply_async(args=["https://exhentai.org/g/1220208/ff58343db8/", ],
                    queue="default", 
                    routing_key="default")
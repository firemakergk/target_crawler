# -*- coding: utf-8 -*-

# Scrapy settings for web_single_crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'web_single_crawler'
LOG_LEVEL = 'CRITICAL'
SPIDER_MODULES = ['web_single_crawler.spiders']
NEWSPIDER_MODULE = 'web_single_crawler.spiders'

ITEM_PIPELINES = {
	'web_single_crawler.pipelines.WebSinglePipeline':300
}

DOWNLOADER_MIDDLEWARES = {
    'web_single_crawler.middleware.WebkitDownloader': 1
}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'sinanews (+http://www.yourdomain.com)'

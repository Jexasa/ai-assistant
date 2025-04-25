import scrapy

class NewsSpider(scrapy.Spider):
    name = "news"
    start_urls = ["https://example.com/news"]  # Replace with real site

    def parse(self, response):
        for article in response.css("article"):
            yield {
                "content": article.css("p::text").get(),
                "url": response.url
            }
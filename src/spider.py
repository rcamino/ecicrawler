import os
import codecs

from urlparse import urlparse

from scrapy import Spider, Request


class ECISpider(Spider):

    name = "ECI"
    start_urls = ["http://www.dc.uba.ar/events/eci"]
    allowed_domains = [
        "www-2.dc.uba.ar",
        "dc.uba.ar",
    ]
    directory = "data/web"
    prefixes = [
        "http://www-2.dc.uba.ar/eci/",
        "http://www.dc.uba.ar/events/eci/",
    ]
    filtered_sufixes = [
        ".pdf",
        ".doc"
    ]

    def parse(self, response):
        requests = []
        for a in response.css("#content-core a"):
            text_extraction = a.css("::text").extract()
            if len(text_extraction) == 1 and text_extraction[0].startswith("ECI"):
                child_url = a.css("::attr(href)").extract()[0]
                requests.append(Request(child_url, callback=self.parse_child))
        return requests

    def parse_child(self, response):
        if not "text/html" in response.headers.get("Content-Type"):
            return

        url = None
        for prefix in self.prefixes:
            if response.url.startswith(prefix):
                url = response.url[len(prefix):]
                break
        if url is None:
            return

        tokens = url.rstrip("/").split("/")
        file_name = tokens[-1]
        if "." not in file_name:
            file_name += ".html"
        if len(tokens) > 1:
            directory = os.path.join(self.directory, os.path.join(*tokens[:-1]))
            if not os.path.exists(directory):
                os.makedirs(directory)
        else:
            directory = self.directory
        file_path = os.path.join(directory, file_name)
        body = response.body.decode(response.encoding)
        with codecs.open(file_path, "w", "utf8") as body_file:
            body_file.write(body)

        children_urls = response.css("a::attr(href)").extract()
        children_urls = map(lambda child_url: self.map_child(response.url, child_url), children_urls)
        children_urls = filter(self.filter_child, children_urls)
        return map(lambda child_url: Request(child_url, callback=self.parse_child), children_urls)

    def filter_child(self, child_url):
        for prefix in self.prefixes:
            if child_url.startswith(prefix):
                for sufix in self.filtered_sufixes:
                    if child_url.endswith(sufix):
                        return False
                return True
        return False

    def map_child(self, response_url, child_url):
        if child_url.startswith("/"):
            parsed_url = urlparse(response_url)
            return parsed_url.scheme + "://" + parsed_url.hostname + child_url

        tokens = child_url.split("/")
        if len(tokens) == 1:
            child_url = response_url
            if not child_url.endswith("/"):
                child_url += "/"
            return child_url + tokens[0]

        return child_url

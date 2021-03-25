# Custom web crawler

## WARNING
DO NOT USE OUTSIDE OF TEST ENVIRONMENTS

**No frameworks like Scrapy are used.**

### Features
Feature | Status
--------|--------
Web Crawl | ![iJrod/web-crawler](https://img.shields.io/badge/Web_Crawler-Working-green)

### Installation
Install the requirements and run with Python3.

```sh
$ cd web-crawler
$ pip3 install -r requirements.txt
```
### Run
To run, please use the following example: 
```sh
$ python3 main.py --url/-u <url> --maxpages/-m <integer>
```

To display the help: 
```sh
$ python3 main.py -h
```

For this version, please make sure to use https:// or http:// where appropriate. For example, 'monzo.com' and 'http://example.com' do not work in this current version as Example uses HTTPS, so 'https://example.com' is required.

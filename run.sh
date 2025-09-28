#!/bin/bash
source venv/bin/activate
get-product-urls > url_test.txt
head -n 10 url_test.txt | scrape-product-pages

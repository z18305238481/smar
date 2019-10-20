# -*- coding: utf-8 -*-
from scrapy import cmdline
import sys

begin = "scrapy crawl samr -a qt=%s -a beginTime=%s -a batchNumber=%s"%(sys.argv[1],sys.argv[2],sys.argv[3])
print(begin)
cmdline.execute(begin.split())

#!/usr/bin/env python
import jieba;
from xml.etree.ElementTree import ElementTree;

def xml_str
def main():
    xmldoc=ElementTree();
    xmldoc.parse("raw-data/news.smp");
    itemlist=xmldoc.findall("doc");
    print len(itemlist);
    dir(itemlist[0]);
    print itemlist[0];

if __name__=="__main__":
    main();

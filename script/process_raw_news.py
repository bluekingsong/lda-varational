#!/usr/bin/env python
#import jieba;
import xml.etree.ElementTree as ET;

def xml_str_generator(filename,num):
    cnt=0;
    f=open(filename);
    xml_str="";
    for line in f:
        xml_str+=line;
        if line=="</doc>\n":
            yield xml_str.decode("gb18030").encode("utf-8");
            xml_str="";
            cnt+=1;
            if cnt>=num:
                break;
    f.close();
def main():
    #xmldoc=ElementTree();
    for xml_str in xml_str_generator("raw-data/news.smp",3):
        xmldoc=ET.fromstring(xml_str);
        content=xmldoc.find("content");
        print content.text;
        print "*"*20

if __name__=="__main__":
    main();

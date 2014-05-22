#!/usr/bin/env python
from datetime import datetime;
import re;
import sys;
import jieba;
import xml.etree.ElementTree as ET;

def xml_str_generator(filename,num):
    cnt=1;
    line_cnt=1;
    p=re.compile(u"^[\u4e00-\u9fa5]");
    f=open(filename);
    xml_str="";
    for line in f:
        xml_str+=line;
        if line=="</doc>\n":
            xml_str=xml_str.decode("gb18030");
            #xml_str=p.sub("",xml_str);
            #print xml_str.encode("utf-8");
#            xml_str=re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",xml_str);
            xml_str=xml_str.encode("utf-8");
            yield xml_str,cnt,line_cnt;
            xml_str="";
            cnt+=1;
            if num>0 and cnt>=num:
                break;
        line_cnt+=1;
    f.close();
class Vocab:
    def __init__(self):
        self.index=[]; ## for global use
        self.wordMap={}; ## for global use
        self.freqCnt={}; ## term freq for global use, doc freq for local use(build vocab by some docs)
    def add(self,term,freq=1):
        if term not in self.wordMap:
            self.wordMap[term]=len(self.index);
            self.index.append(term);
        Id=self.wordMap[term];
        self.freqCnt[Id]=self.freqCnt.get(Id,0)+freq;
        return Id;
    def add_doc(self,rawStr):
        for para in rawStr.split("\t")[1:]:
            tid=int(para.split(" ")[0]);
            self.freqCnt[tid]=self.freqCnt.get(tid,0)+1;
    def simplify_by_df(self,freqEps):
        to_del=[tid for tid in self.freqCnt if self.freqCnt[tid]<freqEps];
        for tid in to_del:
            del self.freqCnt[tid];
    def save(self,filename):
        fout=open(filename,"w");
        for term in self.wordMap:
            Id=self.wordMap[term];
            content=term+"\t"+str(Id)+"\t"+str(self.freqCnt[Id])+"\n";
            fout.write(content);
        fout.close();
    def load(self,filename,termFreqEps):
        for line in open(filename):
            paras=line.split("\t");
            t=paras[0];
            tid=int(paras[1]);
            freq=int(paras[2]);
            if freq<termFreqEps:
                continue;
            self.wordMap[t]=tid;
            self.freqCnt[tid]=freq;
    def get_term_id_list(self):
        return self.freqCnt.keys();
    def has_term_id(self,tid):
        return tid in self.freqCnt;
    def list_info(self):
        print "number of terms:",len(self.index);
def main():
    fout=open("data/docs","w");
    vocab=Vocab();
    filename="raw-data/news_tensite_xml.dat";
    cnt=0;
    error_cnt=0;
    print "start cut words:",datetime.now();
    for xml_str,docId,lineId in xml_str_generator(filename,-1):
        if cnt%10000==0:
            print >> sys.stderr,"process :",cnt,"errors:",error_cnt,"time:",datetime.now();
        cnt+=1;
        try:
            xmldoc=ET.fromstring(xml_str);
        except:
            error_cnt+=1;
            continue;
        content=xmldoc.find("content");
        if content is None or content.text is None:
            error_cnt+=1;
            #print "content is None?",(content is None);
            #print xml_str;
            #print "*"*60;
            continue;
        doc_nums={};
        for term in jieba.cut(content.text):
            Id=vocab.add(term.encode("utf-8"));
            doc_nums[Id]=doc_nums.get(Id,0)+1;
        content=str(docId)+" "+str(lineId);
        for Id in doc_nums:
            t=str(Id)+" "+str(doc_nums[Id]);
            content+="\t"+t;
        fout.write(content+"\n");
    vocab.list_info();
    fout.close();
    vocab.save("data/vocab");
if __name__=="__main__":
    main();

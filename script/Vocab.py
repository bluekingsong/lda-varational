#!/usr/bin/env python
from datetime import datetime;

class Vocab:
    def __init__(self):
        self.index=[];
        self.termIdMap={};
        self.docFreq={};
    def add_doc(self,rawStr):
        for para in rawStr.split("\t")[1:]:
            tid=int(para.split(" ")[0]);
            if tid not in self.termIdMap:
                self.termIdMap[tid]=len(self.index);
                self.index.append(tid);
            self.docFreq[tid]=self.docFreq.get(tid,0)+1;
    def simplify_by_df(self,freqEps):
        to_del=[tid for tid in self.docFreq if self.docFreq[tid]<freqEps];
        for tid in to_del:
            del self.docFreq[tid];
            del self.termIdMap[tid];
        self.index=self.termIdMap.keys();
        for i in xrange(len(self.index)):
            self.termIdMap[self.index[i]]=i;
    def save(self,filename):
        fout=open(filename,"w");
        for term in self.wordMap:
            Id=self.wordMap[term];
            content=term+"\t"+str(Id)+"\t"+str(self.freqCnt[Id])+"\n";
            fout.write(content);
        fout.close();
    def __len__(self):
        return len(self.index);
    def has_term_id(self,tid):
        return tid in self.termIdMap;
    def list_info(self):
        print "number of terms:",len(self.index);


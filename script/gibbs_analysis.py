#!/usr/bin/env python
from datetime import datetime;
from sys import argv;

def analysis(theta_file,phi_file,vocab_file,doc_file):
    vocab_index=[];
    for line in open(vocab_file):
        vocab_index.append(line.split("\t")[2]);
    print "size of vocab=",len(vocab_index);
    i=0;
    fout=open(phi_file.replace("phi","topic_word"),"w");
    for line in open(phi_file):
        words=[];
        j=0;
        for item in line[:-1].split(" "):
            words.append((vocab_index[j],float(item)));
            j+=1;
        words.sort(key=lambda x:x[1],reverse=True);
        content=str(i);
        for k in words[:10]:
            content+="\t"+str(k[0])+" "+str(k[1]);
        i+=1;
        fout.write(content+"\n");
    fout.close();

if __name__=="__main__":
    if len(argv)!=5:
        print "usage:",argv[0]," theta phi vocab doc";
    else:
        analysis(argv[1],argv[2],argv[3],argv[4]);

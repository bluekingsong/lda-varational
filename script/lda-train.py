#!/usr/bin/env python
import resource;
from datetime import datetime;
from Model import Model;
from Doc import Doc;
from process_raw_news import Vocab;

def load_docs(docs_filename,numOfDoc,vocab,model):
    cnt=0;
    docs=[None]*numOfDoc;
    len_sum=0;
    for line in open(docs_filename):
        doc=Doc(line,vocab);
        doc.init_varational_parameters(vocab,model);
        len_sum+=len(doc);
        docs[cnt]=doc;
        if cnt%1000==0:
            print "progress:",cnt,"memoery useage:",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000,"time:",datetime.now();
        cnt+=1;
        if cnt>=numOfDoc:
            break;
    print "ave length of doc:",float(len_sum)/cnt;
    return docs;
def load_local_vocab(docs_filename,numOfDoc,dfEps):
    vocab=Vocab();
    cnt=0;
    for line in open(docs_filename):
        vocab.add_doc(line);
        cnt+=1;
        if cnt>=numOfDoc:
            break;
    vocab.simplify_by_df(dfEps);
    return vocab;
def train(docs_filename,numOfDoc,vocab_filename,dfEps,topicNum=50,epsilon=1e-5,maxIter=1e6):
    #globalVocab=Vocab();
    #globalVocab.load(vocab_filename,0);
    print "globalVocab memoery useage:",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000,"time:",datetime.now();
    vocab=load_local_vocab(docs_filename,numOfDoc,dfEps);
    print "local vocab memoery useage:",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000,"time:",datetime.now();
    print "vocab loaded, size=",len(vocab.get_term_id_list());
    model=Model(topicNum,vocab);
    model.init_parameters();
    print "model memoery useage:",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000,"time:",datetime.now();
    print "start load docs,time:",datetime.now();
    docs=load_docs(docs_filename,numOfDoc,vocab,model);
    print "end of load docs",datetime.now();
    avg_likelihood=1e10; ##model.lowerbound_likelihood(docs);
    iteration=0;
    while iteration<maxIter:
        print "iteration#",iteration,"ave_likelihood#",avg_likelihood,"time:",datetime.now();
        doc_cnt=0;
        for doc in docs:
            if doc_cnt%40==0:
                print "doc varational inference progress:",doc_cnt,"time:",datetime.now();
            doc_cnt+=1;
            doc.varational_inference(model,vocab);
        print "end of docs varataional inference,time:",datetime.now();
        model.max_likelihood_estimate(docs);
        print "end of MLE,time:",datetime.now();
        new_likelihood=model.lowerbound_likelihood(docs);
        if abs(avg_likelihood-new_likelihood)<epsilon:
            break;
        avg_likelihood=new_likelihood;
        iteration+=1;
    pass; # save model

if __name__=="__main__":
    train("data/docs",200,"data/vocab",10,topicNum=20,epsilon=1e-4,maxIter=20);

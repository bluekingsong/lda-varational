#!/usr/bin/env python
from datetime import datetime;
from Model import Model;
from Doc import Doc;
from process_raw_news import Vocab;

def load_docs(docs_filename,numOfDoc,vocab,model):
    cnt=0;
    docs=[None]*numOfDoc;
    for line in open(docs_filename):
        doc=Doc(line,vocab);
        doc.init_varational_parameters(vocab,model);
        docs[cnt]=doc;
        cnt+=1;
        if cnt>=numOfDoc:
            break;
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
    globalVocab=Vocab();
    globalVocab.load(vocab_filename,0);
    vocab=load_local_vocab(docs_filename,numOfDoc,dfEps);
    print "vocab loaded, size=",len(vocab.get_term_id_list());
    model=Model(topicNum,vocab);
    model.init_parameters();
    print "start load docs,time:",datetime.now();
    docs=load_docs(docs_filename,numOfDoc,vocab,model);
    print "end of load docs",datetime.now();
    avg_likelihood=model.lowerbound_likelihood(docs);
    iteration=0;
    while iteration<maxIter:
        for doc in docs:
            doc.varational_inference(model,vocab);
        model.max_likelihood_estimate(docs);
        new_likelihood=model.lowerbound_likelihood(docs);
        if abs(avg_likelihood-new_likelihood)<epsilon:
            break;
        avg_likelihood=new_likelihood;
        iteration+=1;
        print "iteration#",iteration,"time:",datetime.now();
    pass; # save model

if __name__=="__main__":
    train("data/docs",10000,"data/vocab",10);

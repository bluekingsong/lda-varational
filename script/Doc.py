#!/usr/bin/env python
from datetime import datetime;
from math import log,exp;
from scipy.special import polygamma,gammaln;

class Doc:
    def __init__(self,rawStr,vocab):
        self.terms={};
        self.totalTerms=0;
        mark=True;
        for term in rawStr.split("\t"):
            items=term.split(" ");
            t1=int(items[0]);
            t2=int(items[1]);
            if mark:
                self.docId=t1;
                self.lineId=t2;
                mark=False;
            elif vocab.has_term_id(t1):
                self.terms[t1]=t2;
                self.totalTerms+=t2;
        self.gamma=[]; # the varational parameter for topics' pirior parameter
        self.phi={}; # the varation parameter for topics' parameter
        self.topicNum=0;
    def varational_inference(self,model,vocab,epsilon=1e-6,maxIter=1e6):
        self.topicNum=model.topicNum;
        self.init_varational_parameters(vocab,model);
        ## varational inference;
        low_bound=1e10; #model.doc_lowerbound_likelihood(self);
        iteration=0;
        while iteration<maxIter:
            for termId in self.terms:
                s=0.0;
                for i in xrange(self.topicNum):
                    t=model.beta[(i,termId)]*exp(polygamma(0,self.gamma[i]));
                    s+=t*self.terms[termId];
                    self.phi[(i,termId)]=t;
                for i in xrange(self.topicNum):
                    self.phi[(i,termId)]/=s;
            for i in xrange(self.topicNum):
                self.gamma[i]=model.alpha[i];
                for j in self.terms:
                    self.gamma[i]+=self.phi[(i,j)]*self.terms[j];
            iteration+=1;
            bound=model.doc_lowerbound_likelihood(self);
            if abs(bound-low_bound)<epsilon:
                break;
            low_bound=bound;
        print "hint: in Doc varational_inference, iterations=",iteration,"lowerbound_likelihood=",bound,"time:",datetime.now();
    def init_varational_parameters(self,vocab,model):
        self.topicNum=model.topicNum;
        #print "varational parameters, topicNum=",self.topicNum,"vocab size=",len(vocab.get_term_id_list());
        self.gamma=[];
        for i in xrange(self.topicNum):
            self.gamma.append(1.0/self.topicNum);
        for i in xrange(self.topicNum):
            for j in self.terms:
                self.phi[(i,j)]=model.alpha[i]+float(self.totalTerms)/self.topicNum;
    def get_term_id_list(self):
        return self.terms.keys();
    def __len__(self):
        return len(self.terms);

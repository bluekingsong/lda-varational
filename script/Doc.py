#!/usr/bin/env python

class Doc:
    def __init__(self,rawStr):
        self.terms={};
        self.totalTerms=0;
        for term in rawStr.split("\t"):
            items=term.split(" ");
            self.terms[int(items[0])]=int(terms[1]);
            self.totalTerms+=int(terms[1]);
        self.gamma=[]; # the varational parameter for topics' pirior parameter
        self.phi={}; # the varation parameter for topics' parameter
        self.topicNum=0;
    def varational_inference(self,model,vocab):
        self.topicNum=model.topicNum;
        self.init_varational_parameters(vocab);
        ## varational inference;
        for termId in self.terms:
            s=0.0;
            for i in xrange(self.topicNum):
                t=model.beta[(i,termId)]*exp(polygamma(0,gamma[i]));
                s+=t*self.terms[termId];
                self.phi[(i,termId)]=t;
            for i in xrange(self.topicNum):
                self.phi[(i,termId)]/=s;
        for i in xrange(self.topicNum):
            self.gamma[i]=model.alpha[i];
            for j in self.terms:
                self.gamma[i]+=self.phi[(i,j)]*self.terms[j];
        ##
    def init_varational_parameters(self,vocab): # by random
        self.gamma=[];
        for i in xrange(self.topicNum):
            self.gamma.append(1.0/self.topicNum);
        for i in xrange(self.topicNum):
            for j in vocab.get_term_id_list():
                self.phi[(i,j)]=model.alpha[i]+float(self.totalTerms)/self.topicNum;


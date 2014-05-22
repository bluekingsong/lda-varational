#!/usr/bin/env python
from math import log;
from random import uniform;
import numpy;
from scipy.special import polygamma,gammaln;

class Model:
    def __init__(self,topicNum,vocab):
        self.topicNum=topicNum;
        self.vocab=vocab;
        self.alpha=[];
        self.beta={};
    def max_likelihood_estimate(self,docs,epsilon=1e-6,maxIter=1e6):
        # estimate beta parameters
        for i in xrange(self.topicNum):
            beta_sum=0.0;
            for j in self.vocab.get_term_id_list():
                self.beta[(i,j)]=0.0;
                for doc in docs:
                    freq=doc.get_term_freq(j);
                    if freq<=0:
                        continue;
                    t=doc.phi[(i,j)]*freq;
                    self.beta[(i,j)]+=t;
                    beta_sum+=t;
            for j in self.vocab.get_term_id_list():
                self.beta[(i,j)]/=beta_sum;
        # estimate alpha parameter
        iteration=0;
        obj=self.log_likelihood_rel_alpha(docs);
        while iteration<maxIter:
            g=self.calc_gradient_rel_alpha(docs);
            h,z=self.calc_hessian_rel_alpha(docs);
            c1=0.0;
            c2=0.0;
            for i in xrange(self.topicNum):
                c1+=g[i]/h[i];
                c2+=1.0/h[i];
            c=c1/(1.0/z+c2);
            for i in xrange(self.topicNum):
                self.alpha[i]-=(g[i]-c)/h[i];
            new_obj=self.log_likelihood_rel_alpha(docs);
            if new_obj-obj<epsilon:
                break;
            obj=new_obj;
            iteration+=1;
    def calc_gradient_rel_alpha(self,docs):
        g=numpy.array([0.0]*self.topicNum);
        for doc in docs:
            g+=polygamma(doc.gamma);
            g-=polygamma(sum(doc.gamma));
        g+=len(docs)*polygamma(0,sum(self.alpha));
        g-=len(docs)*polygamma(0,self.alpha);
        return g;
    def calc_hessian_rel_alpha(self,docs):
        h=len(docs)*polygamma(1,self.alpha);
        z=-polygamma(1,sum(self.alpha));
        return h,z;
    def lowerbound_likelihood_rel_alpha(self,docs):
        m=len(docs);
        obj=m*gammaln(sum(self.alpha));
        obj-=m*gammaln(self.alpha).sum();
        for doc in docs:
            c=polygamma(0,sum(doc.gamma));
            for i in xrange(self.topicNum):
                obj+=(self.alpha[i]-1)*(polygamma(0,doc.gamma[i])-c);
        return obj;
    def lowerbound_likelihood(self,docs):
        m=len(docs);
        obj=m*gammaln(sum(self.alpha))-m*gammaln(self.alpha).sum();
        for doc in docs:
            obj+=self.doc_lowerbound_likelihood(doc);
        return obj/len(docs);
    def doc_lowerbound_likelihood(self,doc):
        obj=0.0;
        sum_digamma=polygamma(0,sum(doc.gamma));
        digamma=polygamma(0,doc.gamma);
        for i in xrange(self.topicNum):
            obj+=(self.alpha[i]-1)*(digamma[i]-sum_digamma);
            for j in doc.get_term_id_list():
                obj+=doc.phi[(i,j)]*(digamma[i]-sum_digamma+log(self.beta[(i,j)]));
                obj-=doc.phi[(i,j)]*log(doc.phi[(i,j)]);
            obj-=(doc.gamma[i]-1)*(digamma[i]-sum_digamma);
            obj+=gammaln(doc.gamma).sum()-gammaln(sum(doc.gamma));
        return obj;
    def init_parameters(self):
        self.alpha=[];
        self.beta={};
        for i in xrange(self.topicNum):
            self.alpha.append(uniform(2,10));
            beta_sum=0;
            for j in self.vocab.get_term_id_list():
                t=uniform(1,2);
                self.beta[(i,j)]=t;
                beta_sum+=t;
            for j in self.vocab.get_term_id_list():
                self.beta[(i,j)]/=beta_sum;

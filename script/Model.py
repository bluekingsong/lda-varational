#!/usr/bin/env python

class Model:
    def __init__(self,topicNum,vocabSize):
        self.topicNum=topicNum;
        self.vocabSize=vocabSize;
        self.alpha=[];
        self.beta={};


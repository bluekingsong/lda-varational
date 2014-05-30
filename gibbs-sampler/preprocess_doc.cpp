#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <map>
#include <vector>
#include "cpp_common.h"
using namespace std;
using namespace CppCommonFunction;

void write_local_vocab(const map<int,string>& globalVocab,const vector<int>& vidIndex,const map<int,int>& freqDict,const string& filename){
    ofstream fout(filename.c_str());
    for(int i=0;i<vidIndex.size();++i){
        int tid=vidIndex[i];
        fout<<i<<"\t"<<tid<<"\t"<<globalVocab.find(tid)->second<<"\t"<<freqDict.find(tid)->second<<endl;
    }
    fout.close();
}
int load_global_vocab(const char *filename,map<int,string>& vocab){
    vocab.clear();
    ifstream fin(filename);
    if(!fin.is_open()){
        cerr<<"Error,open file "<<filename<<" failed in load_global_vocab()"<<endl;
        return -1;
    }
    vector<string> lineVec;
    string line;
    while(getline(fin,line)){
        StringFunction::split(line,'\t',lineVec);
        int tid=atoi(lineVec[1].c_str());
        vocab.insert(map<int,string>::value_type(tid,lineVec[0]));
    }
    fin.close();
    return vocab.size();
}
int preprocess(const char *docFile,const char *vocabFile,int docNum,int dfEps){
    ifstream docFin(docFile);
    map<int,int> freqDict;
    int cnt=0;
    string line;
    vector<string> lineVec;
    vector<string> itemVec;
    while(cnt++<docNum && getline(docFin,line)){
        int n=StringFunction::split(line,'\t',lineVec);
        for(int i=1;i<n;++i){
            StringFunction::split(lineVec[i],' ',itemVec);
            int tid=atoi(itemVec[0].c_str());
            if(freqDict.find(tid)==freqDict.end()){
                freqDict.insert(map<int,int>::value_type(tid,1));
            }else{
                freqDict[tid]+=1;
            }
        }
    }
    vector<int> vidIndex;
    for(map<int,int>::const_iterator iter=freqDict.begin();iter!=freqDict.end();++iter){
        if(iter->second>=dfEps) vidIndex.push_back(iter->first);
    }
    map<int,string> vocab;
    stringstream nameBuffer;
    nameBuffer<<vocabFile<<"."<<docNum<<"."<<dfEps;
    load_global_vocab(vocabFile,vocab);
    write_local_vocab(vocab,vidIndex,freqDict,nameBuffer.str());
    int wordCnt=0;
    cnt=0;
    docFin.seekg(0);
    nameBuffer.str("");
    nameBuffer<<docFile<<"."<<docNum;
    ofstream fout(nameBuffer.str().c_str());
    while(cnt++<docNum && getline(docFin,line)){
        int n=StringFunction::split(line,'\t',lineVec);
        fout<<lineVec[0];
        for(int i=1;i<n;++i){
            StringFunction::split(lineVec[i],' ',itemVec);
            int tid=atoi(itemVec[0].c_str());
            int tf=atoi(itemVec[1].c_str());
            if(freqDict[tid]<dfEps)  continue;
            fout<<"\t"<<lineVec[i];
            wordCnt+=tf;
        }
        fout<<endl;
    }
    docFin.close();
    fout.close();
    return wordCnt;
}

int main(int argc,char **argv){
    if(argc!=3){
        cout<<"usage:"<<argv[0]<<" selected_number_of_doc doc_freq_epslion"<<endl;
        return -1;
    }
    int docNum=atoi(argv[1]);
    int dfEps=atoi(argv[2]);
    int words=preprocess("./data/docs","./data/vocab",docNum,dfEps);
    cout<<"we have "<<words<<" words in the text corpus."<<endl;
}

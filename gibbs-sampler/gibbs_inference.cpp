#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstring>
#include <map>
#include <vector>
#include "cpp_common.h"
using namespace std;
using namespace CppCommonFunction;

bool check_convergence(int iteration,int maxBurnInIter){
    return iteration>=maxBurnInIter;
}
int read_docs(const char *filename,unsigned int *docs,unsigned int *words,int M){
    ifstream fin(filename);
    if(!fin.is_open()){
        cerr<<"Error: open "<<filename<<" failed in read_docs()"<<endl;
        return -1;
    }
    string line;
    vector<string> lineVec;
    vector<string> itemVec;
    unsigned int cnt=0;
    int m=0;
    while(m<M && getline(fin,line)){
        int n=StringFunction::split(line,'\t',lineVec);
        for(int i=0;i<n;++i){
            StringFunction::split(lineVec[i],' ',itemVec);
            unsigned int t1=atoi(itemVec[0].c_str());
            unsigned int t2=atoi(itemVec[1].c_str());
            if(i==0){
                docs[3*m]=cnt;
                docs[3*m+2]=t2; // line number in origin corpus
            }else{
                while(t2--)  words[cnt++]=t1;
            }
        }
        docs[3*m+1]=cnt-1;
        ++m;
    }
    cout<<"hint(In read_docs): read words="<<cnt<<endl;
    return m;
}
void initialize(unsigned int *docs,unsigned int *words,unsigned int *topics,unsigned int *topicTerm,unsigned int *topicDoc,unsigned int *topicBucket,int M,int W,int V,int K){
    for(int m=0;m<M;++m){
        unsigned int beg=docs[3*m];
        unsigned int end=docs[3*m+1];
        for(unsigned int i=beg;i<=end;++i){
            unsigned int k=rand()%K;
            topics[i]=k;
            unsigned int t=words[i];
            ++topicTerm[k*V+t];
            ++topicDoc[k*M+m];
            ++topicBucket[k];
        }
    }
}
unsigned int multi_sample(double *sampleWeights,unsigned int K){
    double r=rand()/(double)RAND_MAX;
    double s=0.0;
    for(unsigned int i=0;i<K;++i)  s+=sampleWeights[i];
    double t=0.0;
    for(unsigned int i=0;i<K;++i){
        t+=sampleWeights[i];
        if(r<=t/s)  return i;
    }
    return K-1;
}
void transit(unsigned int *docs,unsigned int *words,unsigned int *topics,unsigned int *topicTerm,unsigned int *topicDoc,unsigned int *topicBucket,double *sampleWeights,int M,int W,int V,int K,double alpha,double beta){
    for(unsigned int m=0;m<M;++m){
        unsigned int beg=docs[3*m];
        unsigned int end=docs[3*m+1];
        for(unsigned int i=beg;i<=end;++i){
            unsigned int t=words[i];
            unsigned int k=topics[i];
            --topicTerm[k*V+t];
            --topicDoc[k*M+m];
            --topicBucket[k];
            for(unsigned int l=0;l<K;++l){
                double a1=topicTerm[l*V+t]+beta,b1=topicBucket[l]+beta;
                double a2=topicDoc[l*M+m]+alpha,b2=end-beg+alpha;
                sampleWeights[l]=a1*a2/(b1*b2);
            }
            k=multi_sample(sampleWeights,K);
            ++topicTerm[k*V+t];
            ++topicDoc[k*M+m];
            ++topicBucket[k];
        }
    }
}
void write_parameter(const string& filename,float *parameter,int I,int J,float eps=1e-6){
    ofstream fout(filename.c_str());
    for(int i=0;i<I;++i){
        float t=parameter[i*J];
        if(t<eps) fout<<0;
        else fout<<t;
        for(int j=1;j<J;++j){
            t=parameter[i*J+j];
            if(t<eps) fout<<" 0";
            else fout<<" "<<t;
        }
        fout<<endl;
    }
    fout.close();
}
// Memeory need: O(3*M+2*W+K*V+K*M)
// M: number of docs in corpus
// W: number of words in corpus
// K: number of topics
// V: number of terms in vocab
// Time need: O(K*T*W)
// T: total number of sampling iteration,including burin-in peroid.
void inference(const char *filename,int numDocs,int numWords,int vocabSize,int numTopics,int maxBurnInIter,int maxIter,int sampleLag,double alpha,double beta){
    int M=numDocs,W=numWords,V=vocabSize,K=numTopics;
    unsigned int memLen=3*M+2*W+K*V+K*M+K+2*K+K*V+K*M;
    unsigned int *mem=new unsigned int[memLen];
    memset(mem,0,sizeof(unsigned int)*memLen);
    unsigned int *docs=mem;
    unsigned int *words=docs+3*M;
    unsigned int *topics=words+W;
    unsigned int *topicTerm=topics+W;
    unsigned int *topicDoc=topicTerm+K*V;
    unsigned int *topicBucket=topicDoc+K*M;
    double *sampleWeights=(double*)(topicBucket+K);
    float *phi=(float*)(topicBucket+3*K);
    float *theta=phi+K*V;
    cout<<"begin to read docs."<<endl;
    if(read_docs(filename,docs,words,M)<0)  return;
    cout<<"begin to initailize. time:"<<TimeFunction::now()<<endl;
    initialize(docs,words,topics,topicTerm,topicDoc,topicBucket,M,W,V,K);
    cout<<"start gibbs iteration. time:"<<TimeFunction::now()<<endl;
    int iteration=0;
    int T=0;
    bool burn_in_peroid=true;
    int burn_in_iter=0;
    while(iteration++ < maxIter){
        transit(docs,words,topics,topicTerm,topicDoc,topicBucket,sampleWeights,M,W,V,K,alpha,beta);
        if(iteration==1)  cout<<"first iteration. time:"<<TimeFunction::now()<<endl;
        if(burn_in_peroid){
            if(check_convergence(iteration,maxBurnInIter)){
                burn_in_peroid=false;
                burn_in_iter=iteration;
            }
        }
        if(!burn_in_peroid){
            if((iteration-burn_in_iter)%sampleLag==0){
                // read out parameters
                for(unsigned int k=0;k<K;++k){
                    for(unsigned int t=0;t<V;++t){
                        phi[k*V+t]+=(topicTerm[k*V+t]+beta)/(topicBucket[k]+beta);
                    }
                    for(unsigned int m=0;m<M;++m){
                        theta[m*K+k]+=(topicDoc[k*M+m]+alpha)/(docs[3*m+1]-docs[3*m]+1+alpha);
                    }
                }
                ++T;
            }
        }
        if(iteration%1000==0){
            cout<<"hint(in inference): iteration="<<iteration<<" time:"<<TimeFunction::now()<<endl;
        }
    }
    // save inference results;
    // average
    for(unsigned int i=0;i<K*V;++i) phi[i]/=T;
    for(unsigned int i=0;i<K*M;++i) theta[i]/=T;
    ostringstream buffer;
    buffer<<"data/phi."<<K<<"."<<V;
    string phiFilename=buffer.str();
    buffer.str("");
    buffer<<"data/theta."<<M<<"."<<K;
    write_parameter(phiFilename,phi,K,V);
    write_parameter(buffer.str(),theta,M,K);
    cout<<"END. time:"<<TimeFunction::now()<<endl;
}

int main(int argc,char **argv){
    //const char *filename="data/docs.10000.2119690";
    const char *filename="data/docs.100000.22553156";
    //int numDocs=10000,numWords=2119690,vocabSize=3513,numTopics=50,maxBurnInIter=5000,maxIter=10000,sampleLag=100;
    int numDocs=100000,numWords=22553156,vocabSize=12843,numTopics=50,maxBurnInIter=10000,maxIter=20000,sampleLag=1000;
    double alpha=50.0/numTopics,beta=0.01;
    inference(filename,numDocs,numWords,vocabSize,numTopics,maxBurnInIter,maxIter,sampleLag,alpha,beta);
}

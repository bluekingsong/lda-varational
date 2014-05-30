#include <sstream>
#include <ctime>
#include "cpp_common.h"
using namespace CppCommonFunction;

int StringFunction::split(const string& str, char spliter,vector<string>& result){
    result.clear();
    istringstream ss( str );
    string feild;
    while (!ss.eof()){
        string x;              // here's a nice, empty string
        getline( ss, feild, spliter );  // try to read the next field into it
        result.push_back(feild);
        //   cout << x << endl;    // print it out, even if we already hit EOF
    }
    return result.size();
}

string StringFunction::join(const vector<string>& strs,char sep){
    if(strs.size()==0){
        return string("");
    }
    if(strs.size()==1){
        return strs[0];
    }
    string sep_str(1,sep);
    string result;
    for(int i=0;i<strs.size()-1;i++){
        result+=strs[i]+sep_str;
    }
    return result+=strs.back();
}

string TimeFunction::now(){
    time_t t=time(0);
    return string(asctime(localtime(&t)));
}

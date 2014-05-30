#ifndef __COMMON_H__
#define __COMMON_H__

#include <vector>
#include <string>
using namespace std;

namespace CppCommonFunction{

class StringFunction{
  public:
    static int split(const string& str, char spliter,vector<string>& result);
    static string join(const vector<string>& strs,char sep);
};
class TimeFunction{
  public:
    static string now();
};

};
#endif

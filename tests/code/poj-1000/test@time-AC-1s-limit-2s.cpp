#include <iostream>
#ifdef _WINDOWS
#include <windows.h>
#else
#include <unistd.h>
#define Sleep(x) usleep((x)*1000)
#endif
// Time Limit: 2s
using namespace std;
int main() {
  int n, m;
  cin >> n >> m;
  cout << n + m << endl;
  Sleep(1000);
  return 0;
}
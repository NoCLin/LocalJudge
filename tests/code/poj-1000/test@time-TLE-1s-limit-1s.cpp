#include <iostream>
#ifdef _WINDOWS
#include <windows.h>
#else
#include <unistd.h>
#define Sleep(x) usleep((x)*1000)
#endif
using namespace std;
// Time Limit: 1s
// POJ: 660K 0MS
int main() {
  int n, m;
  cin >> n >> m;
  cout << n + m << endl;
  Sleep(1000);
  return 0;
}
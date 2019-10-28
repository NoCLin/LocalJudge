#include <iostream>
#include <unistd.h>
using namespace std;
/**
 * Memory Limit: 5M
 * POJ:
 * macOS  : 1018.07ms |     1.8 M
 * Windows: 1104.18ms |     3.6 M
 * Linux  : 1102.88ms |     3.8 M
**/

int main() {
  int n, m;
  char *p = new char[1024*1024];
  fill(p, p + 1024 * 1024, 1);
  cin >> n >> m;
  cout << n + m << endl;
  sleep(1);
  return 0;
}
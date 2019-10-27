#include <iostream>
#include <unistd.h>
using namespace std;
/**
 * Memory Limit: 2M
 * POJ  Memory: 1716K		Time: 0MS
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
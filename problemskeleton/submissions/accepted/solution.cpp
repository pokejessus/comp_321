#include <algorithm>
#include <cstdio>
#include <vector>
using namespace std;

int main() {
    int n;
    scanf("%d", &n);
    vector<int> a(n), indeg(n, 0);
    for (int i = 0; i < n; i++) {
        scanf("%d", &a[i]);
        a[i]--;
        indeg[a[i]]++;
    }

    vector<int> dp0(n, 0), dp1(n, 1);

    // Peel the trees (leaves first)
    vector<int> st;
    for (int i = 0; i < n; i++)
        if (indeg[i] == 0) st.push_back(i);
    while (!st.empty()) {
        int v = st.back();
        st.pop_back();
        int u = a[v];
        dp0[u] += max(dp0[v], dp1[v]);
        dp1[u] += dp0[v];
        if (--indeg[u] == 0) st.push_back(u);
    }

    const int NEG = -1000000000;
    vector<char> visited(n, 0);
    long long ans = 0;

    for (int s = 0; s < n; s++) {
        if (indeg[s] > 0 && !visited[s]) {
            // collect the cycle
            vector<int> cyc;
            int v = s;
            while (!visited[v]) {
                visited[v] = 1;
                cyc.push_back(v);
                v = a[v];
            }

            int best = 0;
            for (int firstTaken = 0; firstTaken < 2; firstTaken++) {
                int c0 = cyc[0];
                int p0, p1;
                if (firstTaken) { p0 = NEG; p1 = dp1[c0]; }
                else            { p0 = dp0[c0]; p1 = NEG; }
                for (size_t i = 1; i < cyc.size(); i++) {
                    int c = cyc[i];
                    int n0 = max(p0, p1) + dp0[c];
                    int n1 = p0 + dp1[c];
                    p0 = n0;
                    p1 = n1;
                }
                // last vertex is adjacent to the first one
                int res = firstTaken ? p0 : max(p0, p1);
                best = max(best, res);
            }
            ans += best;
        }
    }

    printf("%lld\n", ans);
    return 0;
}
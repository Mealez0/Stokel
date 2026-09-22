#include <bits/stdc++.h>
using namespace std;
vector<int> costs(int N,int MAXC=15){
  int F=1<<(1<<N),ALL=F-1; vector<int> cost(F,-1);
  vector<vector<uint32_t>> bucket(MAXC+1);
  auto add=[&](int f,int c){if(cost[f]<0){cost[f]=c;bucket[c].push_back(f);}};
  add(0,0);add(ALL,0);
  for(int v=0;v<N;v++){int m=0;for(int a=0;a<(1<<N);a++)if((a>>v)&1)m|=1<<a;add(m,0);add((~m)&ALL,0);}
  int total=bucket[0].size();
  for(int c=1;c<=MAXC&&total<F;c++){
    vector<unsigned char> mark(F);
    for(int ca=0;ca<c;ca++){int cb=c-1-ca;if(ca>cb)continue;
      for(size_t i=0;i<bucket[ca].size();i++){size_t j0=(ca==cb?i:0);
        for(size_t j=j0;j<bucket[cb].size();j++){int a=bucket[ca][i],b=bucket[cb][j];
          int u=a&b,o=a|b;if(cost[u]<0)mark[u]=1;if(cost[o]<0)mark[o]=1;}}}
    for(int f=0;f<F;f++)if(mark[f]&&cost[f]<0){cost[f]=c;bucket[c].push_back(f);}
    total+=bucket[c].size();
  }
  return cost;
}
string hexCosts(const vector<int>& c){ static const char*h="0123456789abcdef"; string s; s.reserve(c.size()); for(int x:c)s+=h[x]; return s; }
int main(){
  auto C3=costs(3),C4=costs(4);
  cout<<"import Lean\n\n";
  cout<<"def c3hex : String := \""<<hexCosts(C3)<<"\"\n";
  cout<<"def c4hex : String := \""<<hexCosts(C4)<<"\"\n\n";
  cout<<R"LEAN(
def hexCost (s : String) (i : Nat) : Nat :=
  let n := (s.toUTF8[i]!).toNat
  if n <= 57 then n - 48 else n - 87

def cost3 (i : Nat) : Nat := hexCost c3hex i
def cost4 (i : Nat) : Nat := hexCost c4hex i

def restrict4to3 (f v val : Nat) : Nat := Id.run do
  let mut g := 0
  for a3 in [0:8] do
    let mut a4 := 0
    let mut j := 0
    for q in [0:4] do
      let bit := if q = v then val = 1 else Nat.testBit a3 j
      if q != v then j := j + 1
      if bit then a4 := a4 + (1 <<< q)
    if Nat.testBit f a4 then g := g + (1 <<< a3)
  return g

def restrictionSum (f : Nat) : Nat := Id.run do
  let mut s := 0
  for v in [0:4] do
    for b in [0:2] do
      s := s + cost3 (restrict4to3 f v b)
  return s

def oddParity4 : Nat := Id.run do
  let mut p := 0
  for a in [0:16] do
    let ones :=
      (if Nat.testBit a 0 then 1 else 0) +
      (if Nat.testBit a 1 then 1 else 0) +
      (if Nat.testBit a 2 then 1 else 0) +
      (if Nat.testBit a 3 then 1 else 0)
    if ones % 2 = 1 then p := p + (1 <<< a)
  return p

def certificateCheck : Bool := Id.run do
  if c3hex.toUTF8.size != 256 || c4hex.toUTF8.size != 65536 then return false
  let mut max3 := 0
  for i in [0:256] do max3 := Nat.max max3 (cost3 i)
  let mut max4 := 0
  let mut eq : Array Nat := #[]
  for f in [0:65536] do
    let L := cost4 f
    max4 := Nat.max max4 L
    if L > 0 then
      let S := restrictionSum f
      if 5*S > 24*L then return false
      if 5*S = 24*L then eq := eq.push f
  if max3 != 9 || max4 != 15 then return false
  if eq != #[27030,38505] then return false
  if oddParity4 != 27030 || cost4 oddParity4 != 15 then return false
  for v in [0:4] do for b in [0:2] do
    if cost3 (restrict4to3 oddParity4 v b) != 9 then return false
  return true

theorem AGION_certificate_checked : certificateCheck = true := by
  native_decide

#print axioms AGION_certificate_checked
)LEAN";
}

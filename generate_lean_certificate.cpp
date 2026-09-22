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
int main(){
  auto c3=costs(3),c4=costs(4);
  cout<<"import Lean\n\n";
  auto emit=[&](const char*name,const vector<int>&c){cout<<"def "<<name<<" : Array Nat := #[";for(size_t i=0;i<c.size();++i){if(i)cout<<",";cout<<c[i];}cout<<"]\n\n";};
  emit("c3",c3);emit("c4",c4);
  cout<<R"LEAN(
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
      s := s + c3[restrict4to3 f v b]!
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
  if c3.size != 256 || c4.size != 65536 then return false
  let mut eq : Array Nat := #[]
  for f in [0:65536] do
    let L := c4[f]!
    if L > 0 then
      let S := restrictionSum f
      if 5*S > 24*L then return false
      if 5*S = 24*L then eq := eq.push f
  if eq != #[27030,38505] then return false
  if c3.foldl Nat.max 0 != 9 || c4.foldl Nat.max 0 != 15 then return false
  if oddParity4 != 27030 || c4[oddParity4]! != 15 then return false
  for v in [0:4] do for b in [0:2] do
    if c3[restrict4to3 oddParity4 v b]! != 9 then return false
  return true

theorem AGION_certificate_checked : certificateCheck = true := by
  native_decide

#print axioms AGION_certificate_checked
)LEAN";
}

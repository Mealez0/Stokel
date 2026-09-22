import Std.Tactic.NativeDecide

/-
AGION finite restriction lemma verification.
Model:
* Boolean functions on n variables are truth-table masks.
* Leaves x_i, ¬x_i, 0, 1 have cost 0.
* Binary AND/OR gates cost 1.
* Formula is a tree (no DAG sharing).
* L_n(f) is minimum AND/OR gate count.
-/

def variableMask (n v : Nat) : Nat := Id.run do
  let assignments := 1 <<< n
  let mut m := 0
  for a in [0:assignments] do
    if Nat.testBit a v then
      m := m + (1 <<< a)
  return m

def computeCosts (n : Nat) (maxC : Nat := 40) : Array Nat := Id.run do
  let F := 1 <<< (1 <<< n)
  let ALL := F - 1
  let sentinel := maxC + 1
  let mut cost : Array Nat := Array.replicate F sentinel
  let mut buckets : Array (Array Nat) := Array.replicate (maxC + 1) #[]

  let mut initial : Array Nat := #[0, ALL]
  for v in [0:n] do
    let m := variableMask n v
    initial := initial.push m
    initial := initial.push (ALL - m)

  for f in initial do
    if cost[f]! = sentinel then
      cost := cost.set! f 0
      buckets := buckets.set! 0 ((buckets[0]!).push f)

  for c in [1:maxC+1] do
    let mut mark : Array Bool := Array.replicate F false
    for ca in [0:c] do
      let cb := c - 1 - ca
      if ca ≤ cb then
        let A := buckets[ca]!
        let B := buckets[cb]!
        for i in [0:A.size] do
          let j0 := if ca = cb then i else 0
          for j in [j0:B.size] do
            let a := A[i]!
            let b := B[j]!
            let u := a &&& b
            let o := a ||| b
            if cost[u]! = sentinel then mark := mark.set! u true
            if cost[o]! = sentinel then mark := mark.set! o true
    for f in [0:F] do
      if mark[f]! && cost[f]! = sentinel then
        cost := cost.set! f c
        buckets := buckets.set! c ((buckets[c]!).push f)
  return cost

def restrict4to3 (f v val : Nat) : Nat := Id.run do
  let mut g := 0
  for a3 in [0:8] do
    let mut a4 := 0
    let mut j := 0
    for q in [0:4] do
      let bit := if q = v then val = 1 else Nat.testBit a3 j
      if q ≠ v then j := j + 1
      if bit then a4 := a4 + (1 <<< q)
    if Nat.testBit f a4 then
      g := g + (1 <<< a3)
  return g

def restrictionSum (c3 : Array Nat) (f : Nat) : Nat := Id.run do
  let mut s := 0
  for v in [0:4] do
    for b in [0:2] do
      s := s + c3[restrict4to3 f v b]!
  return s

def allCostsResolved (c : Array Nat) (sentinel : Nat) : Bool :=
  c.all (fun x => x < sentinel)

def boundCheck : Bool := Id.run do
  let c3 := computeCosts 3
  let c4 := computeCosts 4
  if !(allCostsResolved c3 41 && allCostsResolved c4 41) then return false
  for f in [0:65536] do
    let L := c4[f]!
    if L > 0 then
      let S := restrictionSum c3 f
      if 5*S > 24*L then return false
  return true

def equalityMasks : Array Nat := Id.run do
  let c3 := computeCosts 3
  let c4 := computeCosts 4
  let mut out : Array Nat := #[]
  for f in [0:65536] do
    let L := c4[f]!
    if L > 0 then
      let S := restrictionSum c3 f
      if 5*S = 24*L then out := out.push f
  return out

def maxCost (c : Array Nat) : Nat := c.foldl Nat.max 0

def oddParity4 : Nat := Id.run do
  let mut p := 0
  for a in [0:16] do
    if a.countOnes % 2 = 1 then p := p + (1 <<< a)
  return p

def parityRestrictionCosts : Array Nat := Id.run do
  let c3 := computeCosts 3
  let mut out : Array Nat := #[]
  for v in [0:4] do
    for b in [0:2] do
      out := out.push c3[restrict4to3 oddParity4 v b]!
  return out

theorem all_4var_restrictions_shrink_three_fifths : boundCheck = true := by
  native_decide

theorem equality_cases_exactly_parity_and_complement :
    equalityMasks = #[27030, 38505] := by
  native_decide

theorem exact_maximum_costs :
    maxCost (computeCosts 3) = 9 ∧ maxCost (computeCosts 4) = 15 := by
  native_decide

theorem parity_certificate :
    oddParity4 = 27030 ∧
    (computeCosts 4)[oddParity4]! = 15 ∧
    parityRestrictionCosts = #[9,9,9,9,9,9,9,9] := by
  native_decide

#eval ("boundCheck=" ++ toString boundCheck)
#eval ("equalityMasks=" ++ toString equalityMasks)
#eval ("max3=" ++ toString (maxCost (computeCosts 3)) ++
       " max4=" ++ toString (maxCost (computeCosts 4)))
#eval ("oddParity4=" ++ toString oddParity4 ++
       " restrictions=" ++ toString parityRestrictionCosts)

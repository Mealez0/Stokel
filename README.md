# Stokel — Particle-Based Symbolic Regression System

A self-modifying physics simulation that discovers mathematical formulas from data.  
Built from scratch. No ML frameworks. No pretraining.

-----

## What it does

Three processes run in parallel, communicating via shared memory (mmap):

- **Sandbox** — N-body particle physics engine with LIF neurons and Hebbian learning
- **NEAT agent** — Evolutionary algorithm that optimizes sandbox parameters in real time
- **SymReg agent** — Symbolic regression that searches for formulas explaining system behavior

The system observes itself, evolves, and tries to explain what it finds.

-----

## Results

### Strassen’s Matrix Multiplication — Rediscovered

Strassen (1969) showed that 2×2 matrix multiplication requires only 7 multiplications instead of 8.  
The system was given **no hints**, no seed formulas, no reference to Strassen.  
It found 6 of 7 intermediate values with **zero error** in 10,000 generations:

|Formula|Target     |Found                |Error  |
|-------|-----------|---------------------|-------|
|m0     |(a+d)(e+h) |((h+e)·neg(neg(a)−d))|0.00000|
|m1     |(c+d)·e    |((d+c)·e)            |0.00000|
|m2     |a·(f−h)    |neg((h−f)·a)         |0.00000|
|m3     |d·(g−e)    |neg((e−g)·d)         |0.00000|
|m4     |(a+b)·h    |(h·neg(d−(a+(b+d)))) |0.00000|
|m5     |(c−a)·(e+f)|((c−a)·(f+e))        |0.00000|
|m6     |(b−d)·(g+h)|*seed provided*      |—      |

The formulas look different syntactically but are mathematically identical to Strassen’s.  
The system also discovered standard 8-multiplication matrix multiplication **without any guidance**.

-----

### Criticality Detection

The SymReg agent, running on the physics sandbox, spontaneously produced:

```
wc_excitatory(max(sync, 1.226), 1.226)
hh_sodium(noise, noise, -0.051)
```

- `wc_excitatory` — Wilson-Cowan excitatory dynamics, threshold set by the system itself (1.226)
- `hh_sodium` — Used noise as both membrane voltage and gate variable; **-0.051 is close to biological resting potential** (normalized from ~−70mV)

These were not prompted. The system found that its own particle dynamics resemble biological neural criticality.

-----

## Architecture

```
sandbox.py        ←──→  neat_agent.py
     ↕                        ↕
shared_state.mmap  ←──→  symreg_agent.py
     ↕                        ↕
  config.py             toolkit.py
```

**toolkit.py** — 56 scientific functions across physics, neuroscience, statistics, biology, and fusion plasma physics. SymReg can compose these freely.

**shared_state.py** — Binary mmap protocol. Three separate processes exchange state with near-zero latency, no sockets, no HTTP.

**loop.py** — Hypothesis loop: generate hypothesis → run experiment → evaluate → generate next hypothesis.

-----

## How to run

```bash
# Terminal 1 — physics engine
python sandbox.py

# Terminal 2 — evolutionary optimizer
python neat_agent.py

# Terminal 3 — symbolic discovery
python symreg_agent.py

# Optional: automated research loop
python loop.py --rounds 10
```

Dependencies: `numpy`, `torch` (for particle-language system only)

-----

## Core idea

> Physics = Computation.  
> Particles attract and repel. The system minimizes energy.  
> While doing so, it watches itself and adjusts its parameters.  
> Nothing else.

The same principle drives everything: the physics engine, the optimizer, and the formula search.  
Meaning is position. Learning is movement.

-----

## What’s next

- Fusion plasma: searching for unknown turbulence-confinement relationships (τ_E = f(n, T, turbulence, B))
- Scaling to larger symbolic search spaces
- Testing whether the system can find formulas that differ from known solutions (not just rediscover them)

-----

*Built independently. All results produced on a standard laptop.*

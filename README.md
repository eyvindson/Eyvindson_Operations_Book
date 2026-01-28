# Eyvindson Operations Book — Replication Code

This repository contains replication code and illustrative examples accompanying the **Operations** chapter authored by *Eyvindson & Kangas*.  
The purpose of the repository is to provide transparent, runnable implementations of the optimization models discussed in the chapter, using both **CPLEX/OPL** and **Python (Pyomo)**.

The models focus on **forest operations planning**, including assignment, cost, and risk considerations.

---

## Repository contents

```
Eyvindson_Operations_Book/
├── Operation.mod        # CPLEX / OPL implementation of the operations model
├── Operation.py         # Python / Pyomo implementation of the operations model
├── Tactical.mod         # CPLEX / OPL implementation of the tactical model
├── Tactical.py          # Python / Pyomo implementation of the tactical model
└── README.md            # This file
```

---

## Models included

### Operations model
The operations model formulates a mixed-integer optimization problem that includes:
- assignment of forest operators to machines,
- assignment of operator–machine pairs to sites,
- time and cost calculations,
- expected risk calculations,
- optional cost–risk trade-off analysis.

The same formulation is provided in:
- **CPLEX/OPL** (`Operation.mod`)
- **Python / Pyomo** (`Operation.py`)

### Tactical model
The tactical model illustrates a higher-level planning problem aligned with the chapter discussion and is likewise provided in both OPL and Pyomo formats.

---

## Requirements (Python)

To run the Python versions of the models you need:

- Python ≥ 3.8
- Pyomo
- A MILP solver, e.g.:
  - **CBC** (open-source)
  - **Gurobi** or **CPLEX** (commercial, optional)

Install Python dependencies with:

```bash
pip install pyomo pandas matplotlib numpy
```

Make sure your solver executable (e.g. `cbc`) is available on your system `PATH`.

---

## Running the models

### Python (Pyomo)

From the repository root:

```bash
python Operation.py
```

or

```bash
python Tactical.py
```

The scripts:
- build the optimization model,
- solve it using the selected solver,
- print solution details (assignments, cost, risk),
- optionally generate plots (e.g. cost–risk frontiers).

### CPLEX / OPL

The '.mod' files can be opened and solved directly in **IBM ILOG CPLEX Optimization Studio**.

---

## Outputs

Depending on the script, outputs may include:
- operator–machine assignments,
- site-level management decisions,
- total operational cost,
- expected risk,
- Pareto frontiers illustrating cost–risk trade-offs,
- figures saved as '.png' files.

All data used in the examples is defined directly in the scripts for clarity and ease of modification.

---

## Customization

The models are intentionally written to be easy to adapt. You can modify:
- number of sites, machines, or operators,
- cost and productivity parameters,
- risk definitions,
- solver choice,
- ε-constraint or weighted-sum settings for trade-off analysis.

---

## Intended use

This repository is intended for:
- readers of the Operations chapter,
- teaching and demonstration purposes,
- method development and experimentation,
- transparent replication of example models.

It is **not** intended as a production-ready planning system.

---

## Citation

If you use or adapt this code in academic work, please cite the corresponding book chapter by Eyvindson & Kangas.

---

## Contact

Kyle Eyvindson  
University of Helsinki  
kyle.eyvindson@helsinki.fi

---

## License

This repository is provided under the **MIT License**.

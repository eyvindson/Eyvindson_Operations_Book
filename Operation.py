import numpy as np
import pyomo.environ as pyo
import pandas as pd


def Simulated_damage():
    # ------------------------
    # PARAMETERS
    # ------------------------
    R_SEGMENTS = 4
    DAMAGE_SCEN = 4
    SCEN = 100000

    Deactivation = np.array([4100, 4600, 4400, 3300])

    E_Damage = np.array([
        [0, 0.1, 6.2, 62],
        [0, 0.2, 14, 182],
        [0, 0.6, 33, 792],
        [0, 0.7, 42, 1218]
    ])
    E_Damage=E_Damage.T

    st_dev_Damage = np.array([
        [0, 0.02, 1.24, 12.4],
        [0, 0.04, 2.8, 36.4],
        [0, 0.12, 6.6, 158.4],
        [0, 0.14, 8.4, 243.6]
    ])
    st_dev_Damage = st_dev_Damage.T
    Prob_damage = np.array([0.40, 0.35, 0.20, 0.05])
    cum_prob = np.cumsum(Prob_damage)

    rng = np.random.default_rng()

    # ------------------------
    # SCENARIO SELECTION
    # ------------------------
    rand_vals = rng.random(SCEN)
    chosen_scen = np.searchsorted(cum_prob, rand_vals)

    # ------------------------
    # DAMAGE SIMULATION
    # ------------------------
    SimulatedDamage = np.zeros((SCEN, R_SEGMENTS))

    for s in range(SCEN):
        scen = chosen_scen[s]
        for g in range(R_SEGMENTS):
            normals = rng.random(12).sum()
            SimulatedDamage[s, g] = (
                E_Damage[scen, g]
                + st_dev_Damage[scen, g] * (normals - 6) / 2
            )
    return SimulatedDamage

def solve_for_budget(Budget):

    model = pyo.ConcreteModel()

    # ------------------------
    # SETS
    # ------------------------
    model.G = range(R_SEGMENTS)
    model.S = range(SCEN)

    # ------------------------
    # VARIABLES
    # ------------------------
    model.X = pyo.Var(model.G, within=pyo.Binary)
    model.C_ECOL = pyo.Var(model.G, model.S, within=pyo.NonNegativeReals)
    model.C_ECON = pyo.Var(model.G, within=pyo.NonNegativeReals)

    # ------------------------
    # CONSTRAINTS
    # ------------------------
    def econ_rule(m, g):
        return m.C_ECON[g] == m.X[g] * Deactivation[g]
    model.Econ = pyo.Constraint(model.G, rule=econ_rule)

    def ecol_rule(m, g, s):
        return m.C_ECOL[g, s] == (
            (1 - m.X[g]) * SimulatedDamage[s, g]
            + m.X[g] * SimulatedDamage[s, g] * 0.15
        )
    model.Ecol = pyo.Constraint(model.G, model.S, rule=ecol_rule)

    model.BudgetConstraint = pyo.Constraint(
        expr=sum(model.X[g] * Deactivation[g] for g in model.G) <= Budget
    )
    

    # ------------------------
    # OBJECTIVE
    # ------------------------
    model.Obj = pyo.Objective(
        expr=sum(model.C_ECOL[g, s] for g in model.G for s in model.S) / SCEN,
        sense=pyo.minimize
    )

    # ------------------------
    # SOLVE
    # ------------------------
    solver = pyo.SolverFactory("cbc")  # or "gurobi"
    solver.solve(model, tee=False)
    
    econ_val = sum(pyo.value(model.C_ECON[g]) for g in model.G)
    ecol_val = sum(pyo.value(model.C_ECOL[g, s]) for g in model.G for s in model.S) / SCEN
    
    data = []

    for g in model.G:
        for s in model.S:
            data.append({
                "g": g,
                "s": s,
                "C_ECOL": model.C_ECOL[g, s].value
            })

    df_C_ECOL = pd.DataFrame(data)
    
    return econ_val, ecol_val, df_C_ECOL

R_SEGMENTS = 4
DAMAGE_SCEN = 4
SCEN = 100000
Deactivation = np.array([4100, 4600, 4400, 3300])

for k in range(2):
    SimulatedDamage = Simulated_damage()
    path = "/users/keyvinds/BOOK/"
    with open(path+"2024_11_15_OPERATIONS_book.txt", "w") as f:
        f.write("Budget,Econ,Ecol\n")

        for B in range(0, 20001, 1000):
            econ, ecol,data = solve_for_budget(B)
            f.write(f"{B},{econ},{ecol}\n")
            print(f"{B},{econ},{ecol}")
            t = []
            for i in range(100):
                t = t+[(data[data['s']==i]['C_ECOL'].sum())]

    print()
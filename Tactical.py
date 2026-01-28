import pyomo.environ as pyo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyomo.opt import TerminationCondition

# ============================================================
# Data (translated from OPL)
# ============================================================

# Forest operator: [Perf new, Perf old, Ability risky, Hour cost]
FO = {
    0: [0.95, 0.95, 0.95, 70],
    1: [0.95, 0.85, 0.75, 60],
}

# Forest machine: [stems per hour, technology]
FM = {
    0: [50, 1.0],
    1: [45, 0.7],
}

# Sites: [stems, difficulty]
sites = {
    0: [1340, 0.05],
    1: [1090, 0.15],
    2: [1400, 0.05],
    3: [1390, 0.05],
    4: [900,  0.30],
    5: [1030, 0.30],
    6: [1350, 0.15],
    7: [1090, 0.15],
    8: [1360, 0.30],
    9: [1380, 0.25],
}

# ============================================================
# Build model
# ============================================================

model = pyo.ConcreteModel()

# Sets
model.O = pyo.Set(initialize=FO.keys())       # operators
model.M = pyo.Set(initialize=FM.keys())       # machines
model.T = pyo.Set(initialize=sites.keys())    # sites

# Variables
model.RISK = pyo.Var(model.O, within=pyo.NonNegativeReals)
model.time_FO = pyo.Var(model.O, within=pyo.NonNegativeReals)
model.COST = pyo.Var(within=pyo.NonNegativeReals)

model.FMAssign = pyo.Var(model.O, model.M, within=pyo.Binary)
model.FMManage = pyo.Var(model.T, model.O, model.M, within=pyo.Binary)

# ============================================================
# Objective: minimize cost
# ============================================================

def obj_rule(m):
    return sum(m.time_FO[o] * FO[o][3] for o in m.O)

model.Obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

# ============================================================
# Constraints
# ============================================================

# Each operator → exactly one machine
def assign_operator_rule(m, o):
    return sum(m.FMAssign[o, mm] for mm in m.M) == 1
model.AssignOperator = pyo.Constraint(model.O, rule=assign_operator_rule)

# Each machine → exactly one operator
def assign_machine_rule(m, mm):
    return sum(m.FMAssign[o, mm] for o in m.O) == 1
model.AssignMachine = pyo.Constraint(model.M, rule=assign_machine_rule)

# Linking constraint
def manage_link_rule(m, t, o, mm):
    return m.FMManage[t, o, mm] <= m.FMAssign[o, mm]
model.ManageLink = pyo.Constraint(model.T, model.O, model.M, rule=manage_link_rule)

# Max 6 sites per operator
def max_sites_rule(m, o):
    return sum(m.FMManage[t, o, mm] for t in m.T for mm in m.M) <= 6
model.MaxSites = pyo.Constraint(model.O, rule=max_sites_rule)

# Every site must be managed
def all_sites_rule(m, t):
    return sum(m.FMManage[t, o, mm] for o in m.O for mm in m.M) == 1
model.AllSites = pyo.Constraint(model.T, rule=all_sites_rule)

# Time calculation
def time_rule(m, o):
    return m.time_FO[o] == sum(
        m.FMManage[t, o, mm] * (sites[t][0] / FM[mm][0])
        for t in m.T for mm in m.M
    )
model.TimeCalc = pyo.Constraint(model.O, rule=time_rule)

# Risk calculation
# (matches OPL logic: using FO[o][1] in (1 - FO[o][1]))
def risk_rule(m, o):
    return m.RISK[o] == sum(
        m.FMManage[t, o, mm] * ((1 - FO[o][1]) * sites[t][1])
        for t in m.T for mm in m.M
    )
model.RiskCalc = pyo.Constraint(model.O, rule=risk_rule)

# Total cost definition
def cost_rule(m):
    return m.COST == sum(m.time_FO[o] * FO[o][3] for o in m.O)
model.CostCalc = pyo.Constraint(rule=cost_rule)

# ============================================================
# Total risk expression + epsilon constraint
# ============================================================

def total_risk_rule(m):
    return sum(m.RISK[o] for o in m.O)

model.TotalRisk = pyo.Expression(rule=total_risk_rule)

# Placeholder epsilon constraint (will be updated)
model.RiskLimit = pyo.Constraint(expr=model.TotalRisk <= 1e6)

# ============================================================
# Solve repeatedly to build Pareto frontier
# ============================================================

solver = pyo.SolverFactory("cbc")

risk_limits = np.linspace(0.118, 0.2, 50)  # adjust upper bound if needed
frontier = []

for eps in risk_limits:
    model.RiskLimit.set_value(model.TotalRisk <= eps)
    result = solver.solve(model, tee=False)

    if result.solver.termination_condition == TerminationCondition.optimal:
        frontier.append({
            "Cost": pyo.value(model.COST),
            "Risk": pyo.value(model.TotalRisk),
            "RiskLimit": eps
        })

df_frontier = pd.DataFrame(frontier)

# ============================================================
# Plot Pareto frontier
# ============================================================

plt.figure(figsize=(7, 5))
plt.scatter(df_frontier["Cost"], df_frontier["Risk"])
plt.xlabel("Operations Cost (€)")
plt.ylabel("Expected Risk")

plt.grid(True)
#plt.xlim(left=0)
#plt.ylim(bottom=0)
plt.tight_layout()
plt.show()

# ============================================================
# Optional: inspect frontier table
# ============================================================
plt.savefig("Tactical_tradeoff.png", dpi=300)
print(df_frontier)

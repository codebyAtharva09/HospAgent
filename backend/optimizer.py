from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpInteger

def optimize_resources(predicted_patients, avg_patients=200):
    """
    Optimize staffing and supplies based on predicted patient surge.
    Uses PuLP for linear programming to minimize costs while meeting demands.
    """
    if predicted_patients <= avg_patients:
        return {"extra_staff": 0, "extra_supplies": 0}

    # Calculate base extra needs
    extra_patients = predicted_patients - avg_patients
    extra_staff = max(0, extra_patients // 20)  # Doctors/nurses
    extra_supplies = max(0, extra_patients * 2)  # Masks, medicines, etc.

    # Simple optimization: minimize cost subject to constraints
    prob = LpProblem("Resource_Optimization", LpMinimize)

    # Variables
    staff = LpVariable("staff", lowBound=0, cat=LpInteger)
    supplies = LpVariable("supplies", lowBound=0, cat=LpInteger)

    # Objective: minimize cost (assume staff cost 1000/unit, supplies 50/unit)
    prob += 1000 * staff + 50 * supplies

    # Constraints
    prob += staff >= extra_staff
    prob += supplies >= extra_supplies
    prob += staff <= extra_patients // 10  # Upper bound
    prob += supplies <= extra_patients * 3

    # Solve
    prob.solve()

    return {
        "extra_staff": int(staff.varValue) if staff.varValue else 0,
        "extra_supplies": int(supplies.varValue) if supplies.varValue else 0
    }

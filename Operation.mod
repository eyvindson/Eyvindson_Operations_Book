/*********************************************
 * OPL 22.1.0.0 Model
 * Author: kyey
 * Creation Date: 13. nov. 2024 at 07:05:26
 *********************************************/

int R_Segments = 4;
int DAMAGE_SCEN = 4;
int SCEN = 100000;
float Budget = ...;

float cumulativeProb[1..DAMAGE_SCEN]  = [0,0,0,0];

float Deactivation[1..R_Segments] = [4100,4600,4400,3300];
 
float E_Damage[1..DAMAGE_SCEN][1..R_Segments]= [[0,0.1,6.2,62],
 									   [0,0.2,14,182],
 									   [0,0.6,33,792],
 									   [0,0.7,42,1218]];
float st_dev_Damage[1..DAMAGE_SCEN][1..R_Segments]= [[0,0.02,1.24,12.4],
	[0,0.04,2.8,36.4],
	[0,0.12,6.6,158.4],
	[0,0.14,8.4,243.6]];

float Prob_damage[1..DAMAGE_SCEN] = [0.40,0.35,0.20,0.05];

//function to generate new seed
/*execute{
  var now = new Date();
    Opl.srand(now.getTime()%Math.pow(2,31));
}*/

float RandomValues[i in 1..SCEN] = rand(100000)/100000;

// Function to select a scenario based on probability
// Array to store simulated damage for each scenario and segment
float SimulatedDamage[1..SCEN][1..R_Segments];

//Function to create random distribution of events, writen to SimulatedDamage
execute {
    //float cumulativeProb[1..DAMAGE_SCEN];
    var chosen_scenario = 0;
    var randValue = 0;
    var sumRandoms = 0;
    
    cumulativeProb[1] = Prob_damage[1];
    for (var i = 2; i <= DAMAGE_SCEN; i = i + 1) {
        cumulativeProb[i] = cumulativeProb[i - 1] + Prob_damage[i];
    }
	
    // Generate damage values for each scenario
    for (var s = 1; s <= SCEN; s = s + 1) {
        randValue = RandomValues[s];
        //chosen_scenario = DAMAGE_SCEN;

        for (var i = 1; i <= DAMAGE_SCEN; i = i + 1) {
            if (randValue < cumulativeProb[i]) {
                chosen_scenario = i;
                break;
            }
        }
		for (var g =1; g <= R_Segments;g=g+1){
        // Approximate normal distribution by summing multiple uniform random values
        for (var r = 1; r <= R_Segments; r = r + 1) {
            sumRandoms = 0;
            for (var j = 1; j <= 12; j = j + 1) {
                sumRandoms += RandomValues[(s + j) % 100 + 1];
            }
            // Adjust to mean and standard deviation
            SimulatedDamage[s][g] = E_Damage[g][chosen_scenario] + 
                                    st_dev_Damage[g][chosen_scenario] * (sumRandoms - 6) / 2;
      }
    }        
  }
}

dvar boolean X[1..4];
dvar float+ C_ECOL[1..4][1..SCEN];
dvar float+ C_ECON[1..4];
dvar float+ C_ECON_print;
dvar float+ C_ECOL_print;



minimize sum(g in 1..4, n in 1..SCEN) (C_ECOL[g][n]/SCEN);//#*1000 +C_ECON[g]);

subject to {
 forall(g in 1..4)
 C_ECON[g] == X[g]*Deactivation[g];
 
 C_ECON_print == sum(g in 1..4)(C_ECON[g]);
 
 C_ECOL_print == sum(g in 1..4,n in 1..1)(C_ECOL[g][n]);
  
 forall(g in 1..4,n in 1..SCEN)
 C_ECOL[g][n] == (1-X[g])*SimulatedDamage[n][g] + (X[g]*SimulatedDamage[n][g]*.15);
 
 sum (g in 1..4) X[g]*Deactivation[g] <= Budget;

}  



  main {
  var status = 0;
  thisOplModel.generate();
  var model = thisOplModel;
  var data = model.dataElements;
  var def = model.modelDefinition;

  model = new IloOplModel(def, cplex);
  
  // cplex.param.TimeLimit = 30;
  data.Budget=0
   
  model.addDataSource(data);
  model.generate();

  model = new IloOplModel(def, cplex);

  
  model.addDataSource(data);
  model.generate();

  var ofile = new IloOplOutputFile("2024_11_15_OPERATIONS_book.txt"); // this line saves the output to a file.
  ofile.writeln("Budget,Econ,Ecol");
  
  var prevObjValue = -Infinity;  // Initialize previous objective value to a very low number
  //between the ideal values of income and carbon & volume indicators -- find all solutions that maximize BD 
  
  for (var T1 = 0; T1 <= 20000; T1 += 1000) {
      model = new IloOplModel(def, cplex);
      data.Budget = T1;

      model.addDataSource(data);
      model.generate();

      var before = new Date();
      if (cplex.solve()) {
        var after = new Date();
        var solvingTime = after.getTime() - before.getTime();
        writeln("Solving time ~= ", solvingTime, " ms");    
		// Check if the current optimization result is the same as the previous
        var curr = cplex.getObjValue();
		ofile.writeln(model.Budget, ",", model.C_ECON_print, ",", model.C_ECOL_print);

    }  	
    }
  ofile.close();
}

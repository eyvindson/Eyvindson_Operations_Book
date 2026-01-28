/*********************************************
 * OPL 22.1.0.0 Model
 * Author: kyey
 * Creation Date: 16. nov. 2024 at 11:50:07
 *********************************************/

//Forest operator: Performace  with new machines,Performace  with old machines,Ability to manage risky situations,Performance,Per hour cost
 float FO[1..2][1..4] = [[0.95,0.95,0.95,70],[0.95,0.85,0.75,60]];

//Performance of forest machine, new and old -- Stems per hour, technology in maching (percentage)
 float FM[1..2][1..2] = [[50,1],[45,0.7]];

//site characteristics, stems and difficulty
 float sites[1..10][1..2] =[[1340,0.05],[1090,0.15],[1400,0.05],[1390,0.05],[900,0.3],[1030,0.3],[1350,0.15],[1090,0.15],[1360,0.3],[1380,0.25]];
 
 //Uncertainty of forest operator as stdev; Performace  with new machines,Performace  with old machines,Ability to manage risky situations,Performance,Per hour cost 
 float FOU[1..2][1..4] = [[0.025,0.025,0.025,0], [0.025,0.10,0.2,0]];
 
 // uncertainty of forest machine stdev: 
 float FMU[1..2][1..2] = [[5,0], [7.5,.1]];
 
 //Uncertainty of site, stdev of difficulty.
 float sitesU[1..10] =[0.025,0.05,0.025,0.025,0.15,0.15,0.025,0.025,0.15,0.15];
 
 dvar float+ RISK[1..2];
 
 dvar float+ time_FO[1..2];
 dvar float+ COST;
 
dvar boolean FMAssign[1..2][1..2]; // Operator to machine assignment
dvar boolean FMManage[1..10][1..2][1..2]; // Site to operator-machine management


minimize sum(i in 1..2) time_FO[i]*FO[i][4];

//min risk = 17324
//min cost = 
subject to {
  // Machine assignment constraint
  forall(o in 1..2)
    sum(m in 1..2) FMAssign[o][m] == 1;
    
  forall(m in 1..2)
    sum(o in 1..2) FMAssign[o][m] == 1;

  // Link machine assignment to site management
  forall(t in 1..10, o in 1..2, m in 1..2)
    FMManage[t][o][m] <= FMAssign[o][m];

  // One operator can do at max 6 sites
 forall(o in 1..2)
 	sum(t in 1..10, m in 1..2) FMManage[t][o][m] <=6;

  // Require all sites managed
  forall(t in 1..10)
    sum(o in 1..2, m in 1..2) FMManage[t][o][m] == 1;

  // Operator time calculation
  forall(o in 1..2)
    time_FO[o] == sum(t in 1..10, m in 1..2) FMManage[t][o][m] * (sites[t][1] / FM[m][1]);
  
  // Operator price calculation  
  forall(o in 1..2)
    time_FO[o] == sum(t in 1..10, m in 1..2) (FMManage[t][o][m] * (sites[t][1] / FM[m][1]));
    

  // Risk calculation
  forall(o in 1..2)
    RISK[o] == sum(t in 1..10, m in 1..2) FMManage[t][o][m] * ((1 - FO[o][2]) * sites[t][2]);
    
  COST ==sum(i in 1..2) time_FO[i]*FO[i][4];   
  
}
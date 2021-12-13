// Gmsh project created on Tue Nov 09 20:20:00 2021
//+
SetFactory("OpenCASCADE");
Box(1) = {0, 0, 0, 1, 1, 2};//+
Cylinder(2) = {1/3, 1/3, 1.25, 0, 0, 0.25, 0.05, 2*Pi};
//+
Cylinder(3) = {2/3, 1/3, 1.25, 0, 0, 0.25, 0.05, 2*Pi};
//+
Cylinder(4) = {2/3, 2/3, 1.25, 0, 0, 0.25, 0.05, 2*Pi};
//+
Cylinder(6) = {1/3, 2/3, 1.25, 0, 0, 0.25, 0.05, 2*Pi};
//+
BooleanDifference{ Volume{1}; Delete; }{ Volume{6}; Volume{2}; Volume{4}; Volume{3}; Delete; }
//+
Physical Volume(37) = {1};
//+
Physical Surface(1) = {19, 22, 20, 24, 21, 23};
//+
Physical Surface(2) = {17, 18, 16, 15, 13, 14, 8, 7, 9, 12, 10, 11};

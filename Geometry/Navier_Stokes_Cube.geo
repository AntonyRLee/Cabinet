//+
SetFactory("OpenCASCADE");
//+
Box(1) = {0, 0, 0, 1, 1, 1};
//+
Cylinder(2) = {0.6, 0.3, 0.2, 0, 0, 0.5, 0.1, 2*Pi};
//+
Physical Surface("InletSurface", 16) = {3};
//+
Physical Surface("Boundary", 17) = {1, 6, 5, 2, 4};
//+
Physical Volume("CubeVolume", 18) = {1};
//+
Physical Volume("CylinderVolume", 19) = {2};
//+
Physical Surface("CylinderSurface", 20) = {7, 8, 9};

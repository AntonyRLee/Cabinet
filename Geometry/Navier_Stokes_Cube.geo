//+
SetFactory("OpenCASCADE");
Box(1) = {0, 0, 0, 1, 1, 1};
//+
Cylinder(2) = {0.6, 0.3, 0.2, 0, 0, 0.5, 0.1, 2*Pi};
//+
Surface Loop(3) = {8, 7, 9};
//+
Physical Volume("CylinderVolume", 16) = {2};
//+
Curve Loop(10) = {13};
//+
Physical Surface("CylinderSurface", 17) = {8, 7, 9};
//+
Physical Surface("CubeSurface", 18) = {6, 1, 3, 2, 4, 5};
//+
Physical Volume("CubeSpace", 1) = {1};

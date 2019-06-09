import PyNormaliz

init_data = {"vertices": [(-3,-2,-1,1), (-1,1,-1,2), (1,1,-1,1), (1,1,1,1)]}

C = PyNormaliz.NmzCone(**init_data)

# PyNormaliz.NmzResult( C, "EmbeddingDim" ); 
# PyNormaliz.NmzResult( C, "ExcludedFaces" ); 
# PyNormaliz.NmzResult( C, "WitnessNotIntegrallyClosed" ); 
# PyNormaliz.NmzResult( C, "RecessionRank" ); 
# PyNormaliz.NmzResult( C, "ReesPrimaryMultiplicity" ); 
# PyNormaliz.NmzResult( C, "Rank" ); 
# PyNormaliz.NmzResult( C, "Volume" ); 
# PyNormaliz.NmzResult( C, "IsIntegrallyClosed" ); 
# PyNormaliz.NmzResult( C, "ModuleRank" ); 
# PyNormaliz.NmzResult( C, "Congruences" ); 


# PyNormaliz.NmzResult( C, "IsPointed" ); 
# PyNormaliz.NmzResult( C, "ExternalIndex" ); 
# PyNormaliz.NmzResult( C, "AffineDim" );


# PyNormaliz.NmzResult( C, "InclusionExclusionData" ); 
PyNormaliz.NmzResult( C, "EhrhartQuasiPolynomial" ); 
# PyNormaliz.NmzResult( C, "UnitGroupIndex" ); 
# PyNormaliz.NmzResult( C, "IsInhomogeneous" );
PyNormaliz.NmzResult( C, "ExtremeRays" ); 
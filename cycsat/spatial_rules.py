"""
Possible spatial rules

within -- placed feature must be within a target feature (return target feature)
near -- placed feature must be near (within a specified distance) to a target feature (donut buffer)
distant -- placed feature must be distant (a specified distance) to a target feature (cut buffer around target)

"""
from cycsat.prototypes.reactor import SampleReactor

ct1 = SampleCoolingTower1()
ct2 = SampleCoolingTower2()







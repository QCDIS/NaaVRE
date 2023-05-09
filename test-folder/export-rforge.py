import rpy2.robjects as robjects
import json

# Set CRAN mirror to the Netherlands
robjects.r('chooseCRANmirror(ind=46)')
robjects.r('options(repos = c(RForge = "http://r-forge.r-project.org"))')
packages = list(robjects.r('available.packages()[, c("Package")]'))

# # Save the JSON string to a file
with open('rforgePackages.json', 'w') as f:
    json.dump(packages, f)
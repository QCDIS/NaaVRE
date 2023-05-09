import rpy2.robjects as robjects
import json

# Set CRAN mirror to the Netherlands
robjects.r('chooseCRANmirror(ind=46)')
packages = list(robjects.r('tools::CRAN_package_db()[, c("Package")]'))

# Save the JSON string to a file
with open('cranPackages.json', 'w') as f:
    json.dump(packages, f)

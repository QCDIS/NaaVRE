import rpy2.robjects as robjects
import json

# Set CRAN mirror to the Netherlands
robjects.r('chooseCRANmirror(ind=46)')

# Check if ggplot2 package is available on CRAN
packages = list(robjects.r('library(BiocManager); BiocManager::available()'))

# Save the JSON string to a file
with open('bioconductorPackages.json', 'w') as f:
    json.dump(packages, f)

print(packages)
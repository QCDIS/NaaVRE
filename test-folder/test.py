import rpy2.robjects as robjects

# Define an R script
r_script = """
my_function <- function(x) {
  return(x^2)
}
"""

# Execute the R script
robjects.r(r_script)

# Call an R function from Python
my_function = robjects.globalenv['my_function']
result = my_function(5)
print(result) # Output: [1] 25

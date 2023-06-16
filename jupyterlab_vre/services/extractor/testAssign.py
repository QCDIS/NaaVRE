import rpy2.rinterface as rinterface
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
from rpy2.robjects.packages import importr
import pandas as pd
import json

# Load the base R package for parsing and evaluation
base = importr('base')

text = '''
dataset=read.csv('~/Unisalento/Lifewatch/Phyto_VRE/Script_R/Data_Filtering/dfdataset.csv',stringsAsFactors=F,sep = ";", dec = ".")
ClusterWhole=param_cluster_whole
cluster=clusterin
taxlev=param_taxlev
TraitDensity=param_density

if(ClusterWhole==0) {
  if(length(cluster)>1) ID<-apply(dataset[,cluster],1,paste,collapse='.')
  if(length(cluster)==1) ID<-dataset[,cluster]
} else if(ClusterWhole==1) {
  ID<-rep('all',dim(dataset)[1]) }

if (TraitDensity==1) {
  
  IDZ<-unique(ID)  
  IDLIST<-list()
  length(IDLIST)<-length(IDZ)
  names(IDLIST)<-IDZ
  
  # ranked distribution of the taxa
  for(j in 1:length(IDZ)){
    ddd<-dataset[ID==IDZ[j],]
    totz<-sum(ddd[,'density'],na.rm=T)
    matz<-tapply(ddd[,'density'],ddd[,taxlev],function(x)sum(x,na.rm=T)/totz)
    matz<-sort(matz,decreasing=T) 
    
    # cumulative contribution to the overall density
    k<-2
    trs<-max(matz)
    while (trs<threshold) {
      matz[k]<-matz[k-1]+matz[k]
      trs<-matz[k]
      k<-k+1 }
    
    matzx<-matz[1:k-1]
    
    IDLIST[[j]] <- ddd[ddd[,taxlev]%in%names(matzx),]
  }
  
  # filtered dataset for density
  dataset.d <- do.call('rbind',IDLIST)
  
} else dataset.d <- dataset[FALSE,]

write.table(dataset.d,paste('~/Unisalento/Lifewatch/Phyto_VRE/Script_R/Data_Filtering/datasetD.csv',sep=''),row.names=F,sep = ";",dec = ".",quote=F)
'''

parsed_expr = base.parse(text=text, keep_source=True)
parsed_expr_py = robjects.conversion.rpy2py(parsed_expr)

def recursive_variables(my_expr, result):
    if isinstance(my_expr, rinterface.LangSexpVector):

        # check if there are enough data values. for an assignment there must be three namely VARIABLE SYMBOL VALUE. e.g. a = 3
        if len(my_expr) >= 3:

            # check for matches
            c = str(my_expr[0])
            variable = my_expr[1]

            # check if assignment. (TODO) is there a better way to check if it is an assignment?
            if (c == "<-" or c == "="):
                if isinstance(my_expr[1], rinterface.SexpSymbol):
                    result.append(str(variable))    
    try:
        for expr in my_expr:
            recursive_variables(expr, result)
    except Exception as e:
        a=1
    return result

def old_res():
    result = []
    for expr in parsed_expr_py:

        # Check for a specific type. otherwise continue
        if not isinstance(expr, rinterface.LangSexpVector):
            continue

        # check if there are enough data values. for an assignment there must be three namely VARIABLE SYMBOL VALUE. e.g. a = 3
        if len(expr) <= 2:
            continue

        # check for matches
        c = str(expr[0])
        variable = str(expr[1])

        # check if assignment. (TODO) is there a better way to check if it is an assignment?
        if not ((c == "<-" or c == "=")):
            continue

        result.append(variable)
    return result

print("Old variables: ", old_res())
variables = pd.Series(recursive_variables(parsed_expr_py, [])).unique()
print("New variables: ", variables)
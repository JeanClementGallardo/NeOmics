BiocRequire <- function(pkg) {
    if (pkg %in% rownames(installed.packages()) == FALSE) {
        BiocManager::install(pkg)
    }
}

BiocRequire("RankProd")
library(RankProd)
setwd("./NeOmics/media/Scripts/Params")
data = read.csv("./NeOmics/media/Scripts/Params/GSE7631_loc.csv", header = T, row.names = 1)


lateral_root_cap = data[, 1 : 6]
epidermic_cortex = data[, 7 : 12]
pericycle_root = data[, 13 : 18]
protoplast_root = data[, 19 : 24]


grp.cl = c(0, 0, 0, 1, 1, 1)


RP_lateral = RankProducts(lateral_root_cap, grp.cl, logged = T, na.rm = FALSE, plot = FALSE, rand = 123)
res_lateral = topGene(RP_lateral, cutoff = 0.1, method = "pfp", logged = TRUE, logbase = 2, gene.names = rownames(data))

RP_epidermic = RankProducts(epidermic_cortex, grp.cl, logged = T, na.rm = FALSE, plot = FALSE, rand = 123)
res_epidermic = topGene(RP_epidermic, cutoff = 0.1, method = "pfp", logged = TRUE, logbase = 2, gene.names = rownames(data))

RP_pericycle = RankProducts(pericycle_root, grp.cl, logged = T, na.rm = FALSE, plot = FALSE, rand = 123)
res_pericycle = topGene(RP_pericycle, cutoff = 0.1, method = "pfp", logged = TRUE, logbase = 2, gene.names = rownames(data))

RP_protoplast = RankProducts(protoplast_root, grp.cl, logged = T, na.rm = FALSE, plot = FALSE, rand = 123)
res_protoplast = topGene(RP_protoplast, cutoff = 0.1, method = "pfp", logged = TRUE, logbase = 2, gene.names = rownames(data))

# write_res_csv = function(rankprod_res, directory){
#     df <- data.frame(V1 = rep(NA, max(sapply(list(rownames(rankprod_res$Table1), rownames(rankprod_res$Table2)), length))))
#     df[1 : length(rownames(rankprod_res$Table1)), 1] = rownames(rankprod_res$Table1)
#     if (length(rownames(rankprod_res$Table2))) {
#         df[1 : length(rownames(rankprod_res$Table2)), 2] = rownames(rankprod_res$Table2)
#     } else {
#         df[1 : length(rownames(rankprod_res$Table1)), 2] = rep(NA, length(rownames(rankprod_res$Table1)))
#     }
#     write.table(df, file = paste(directory, 'RP.csv', sep = ""), col.names = FALSE, row.names = FALSE, na = 'NA')
# }
# 
# 
# write_res_csv(res_lateral, "./Arabidopsis/Lateral_root_cap/KNO3_KCL/")
# write_res_csv(res_epidermic, "./Arabidopsis/Epidermic_cortex/KNO3_KCL/")
# write_res_csv(res_pericycle, "./Arabidopsis/Pericycle_root/KNO3_KCL/")
# write_res_csv(res_protoplast, "./Arabidopsis/Protoplasted_root/KNO3_KCL/")
# 
# ############### Test ################ 
# df <- data.frame(V1 = rep(NA, max(sapply(list(rownames(res_lateral$Table1), rownames(res_lateral$Table2)), length))))
# df[1 : length(rownames(res_lateral$Table1)), 1] = rownames(res_lateral$Table1)
# if (length(rownames(res_lateral$Table2))) {
#     df[1 : length(rownames(res_lateral$Table2)), 2] = rownames(res_lateral$Table2)
# } else {
#     df[1 : length(rownames(res_lateral$Table1)), 2] = rep(NA, length(rownames(res_lateral$Table1)))
# }
############### Eliot ############### 
library(dplyr)

bindNodes <- function(...) {
  dataFramesList <- list(...) # Get dataframes to fuse
  outDF = data.frame()
  for (df in dataFramesList) { # For each df given as argument
    outDF = tryCatch({
      full_join(outDF, df) # Try to join df to the output by Common columns
    }, error = function(error_condition) { # If no Common columns (first df)
      outDF = rbind(outDF, df) # simply add df to current outDF
    })
  }
  # Create node_id
  outDF$node_id = seq.int(nrow(outDF))
  # Place node_id first
  outDF = outDF %>% select("node_id", everything())
  return(outDF)
}

# Genes 
nbGene = nrow(data)
geneDF = data.frame(matrix(vector(), nrow=nbGene ))
geneDF$node_labels = rep(":Gene", nbGene)
geneDF$name = rownames(data)

# Conditions
conditions = c("Lateral Root Cap", "Epidermic Cortex", "Pericycle Root", "Protoplasted Root")
results = list(res_lateral, res_epidermic, res_pericycle, res_protoplast)

nbCondition = length(conditions)
conditionDF = data.frame(matrix(vector(), nrow=nbCondition )) 
conditionDF$node_labels = rep(":Condition", nbCondition)
conditionDF$tissue = conditions
conditionDF$name = conditionDF$tissue
conditionDF$experiment = rep("KNO3 KCL", nbCondition)
conditionDF$analysis = rep("RP", nbCondition)
conditionDF$organism = rep("A.thaliana", nbCondition)

# Group
nbGroup = nbCondition * 2
groupDF = data.frame(matrix(vector(), nrow=nbGroup ))
groupDF$node_labels = rep(":Group", nbGroup)
groupDF$name = rep(c("Up", "Down"), nbCondition)
groupDF$condition = rep(conditionDF$name, each=2)

nodesDF = bindNodes(geneDF, conditionDF, groupDF)

relDF = data.frame(rel_start = integer(), rel_end = integer(), rel_type = character(0), stringsAsFactors = F)
for (n in 1:length(conditions)) {
  result = results[[n]]
  condition_id = inner_join(nodesDF, data.frame(name = conditions[n]), by="name")$node_id
  
  up_node_id = inner_join(nodesDF, data.frame(condition = conditions[n], name = "Up"), by=c("condition","name"))$node_id
  down_node_id = inner_join(nodesDF, data.frame(condition = conditions[n], name = "Down"), by=c("condition","name"))$node_id
  
  relDF[nrow(relDF) + 1,] = c(condition_id, up_node_id, "EXPRESS")
  relDF[nrow(relDF) + 1,] = c(condition_id, down_node_id, "EXPRESS")
  
  if (!isEmpty(result$Table1)){
    up_regulated = inner_join(nodesDF, data.frame(name = rownames(result$Table1)), by="name")$node_id
    for (id in up_regulated) {
      relDF[nrow(relDF) + 1,] = c(up_node_id, id, "IS_UP_EXPRESSED")
    }
  }
  
  if (!isEmpty(result$Table2)){
    down_regulated = inner_join(nodesDF, data.frame(name = rownames(result$Table2)), by="name")$node_id
    for (id in down_regulated) {
      relDF[nrow(relDF) + 1,] = c(down_node_id, id, "IS_DOWN_EXPRESSED")
    }
  }
}

oriNodesDF = nodesDF
nodesDF[colnames(relDF)] <- NA
relDF[colnames(oriNodesDF)] <- NA
result = rbind(nodesDF, relDF)
  
write.table(result, file = 'graph.csv', col.names = T, row.names = F, na = "")

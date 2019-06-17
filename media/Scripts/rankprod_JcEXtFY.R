###
# Author: L. Léauté
# Editors: E. Ragueneau and J.C. Gallardo
# Date: June 2019
###



## Collect arguments
args <- commandArgs(TRUE)

## Parse arguments (we expect the form --arg=value)
parseArgs <- function(x) strsplit(sub("^--", "", x), "=")
argsL <- as.list(as.character(as.data.frame(do.call("rbind", parseArgs(args)))$V2))
names(argsL) <- as.data.frame(do.call("rbind", parseArgs(args)))$V1
args <- argsL
rm(argsL)

usePackage <- function(p) {
    if (! is.element(p, installed.packages()[, 1]))
    install.packages(p, dep = TRUE)
    require(p, character.only = TRUE)
}

usePackage("BiocManager")

BiocRequire <- function(pkg) {
    if (pkg %in% rownames(installed.packages()) == FALSE) {
        BiocManager::install(pkg)
    }
    require(pkg, character.only = TRUE)
}

BiocRequire("RankProd")
usePackage("rowr") # cbind.fill
usePackage("icesTAF") # mkdir function
setwd(args$out_dir)

usePackage("Rlabkey")

labkey.setDefaults(apiKey = "apikey|e436926d8507eb2239e9771f3a994d47")
labkey.setDefaults(baseUrl = "https://labkey.bph.u-bordeaux.fr:8443/")

#TODO Automatize data accession through parameters
data <- labkey.selectRows(
folderPath = "/Neomics/ARABIDOPSIS",
schemaName = "lists",
queryName = "GSE7631",
viewName = "",
colFilter = NULL,
containerFilter = NULL
)

row.names(data) <- data[, 1]
data <- data[- 1]

#TODO Specify those thing by parameters
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

write_res_csv = function(rankprod_res, directory){
    df = cbind.fill(paste(sep = '', "Gene__", rownames(rankprod_res$Table1), "(UP_REGULATE)"),
                    paste(sep = '', "Gene__", rownames(rankprod_res$Table2), "(DOWN_REGULATE)"),
                    fill = NA)

    names(df) = c("Group__Up(GROUPS)", "Group__Down(GROUPS)")
    mkdir(directory)
    write.table(df, file = paste(directory, 'Analysis__RP(.csv', sep = ''), col.names = TRUE, row.names = FALSE, na = '', sep = '|',)
}


#TODO GENERALIZE OUTPUT FROM PARAMETERS
write_res_csv(res_lateral, "./Organism__Arabidopsis/Exp__KNO3_KCL(CONDITION)/Tissue__Lateral_root_cap(IS_CONSTITUTED_BY)/")
write_res_csv(res_epidermic, "./Organism__Arabidopsis/Exp__KNO3_KCL(CONDITION)/Tissue__Epidermic_cortex(IS_CONSTITUTED_BY)/")
write_res_csv(res_pericycle, "./Organism__Arabidopsis/Exp__KNO3_KCL(CONDITION)/Tissue__Pericycle_root(IS_CONSTITUTED_BY)/")
write_res_csv(res_protoplast, "./Organism__Arabidopsis/Exp__KNO3_KCL(CONDITION)/Tissue__Protoplasted_root(IS_CONSTITUTED_BY)/")

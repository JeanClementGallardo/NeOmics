library("RankProd")
setwd("./Bureau/gse7631/")

data = read.csv("data/GSE7631.csv",header=T,row.names = 1)


lateral_root_cap = data[,1:6]
epidermic_cortex = data[,7:12]
pericycle_root = data[,13:18]
protoplast_root = data[,19:24]


grp.cl = c(0,0,0,1,1,1)


RP_lateral = RankProducts(lateral_root_cap,grp.cl,logged=T,na.rm=FALSE,plot=FALSE, rand=123)
res_lateral = topGene(RP_lateral,cutoff = 0.1,method="pfp",logged=TRUE,logbase=2,gene.names=rownames(data))

RP_epidermic = RankProducts(epidermic_cortex,grp.cl,logged=T,na.rm=FALSE,plot=FALSE, rand=123)
res_epidermic = topGene(RP_epidermic,cutoff = 0.1,method="pfp",logged=TRUE,logbase=2,gene.names=rownames(data))

RP_pericycle = RankProducts(pericycle_root,grp.cl,logged=T,na.rm=FALSE,plot=FALSE, rand=123)
res_pericycle = topGene(RP_pericycle,cutoff = 0.1,method="pfp",logged=TRUE,logbase=2,gene.names=rownames(data))


RP_protoplast = RankProducts(protoplast_root,grp.cl,logged=T,na.rm=FALSE,plot=FALSE, rand=123)
res_protoplast = topGene(RP_protoplast,cutoff = 0.1,method="pfp",logged=TRUE,logbase=2,gene.names=rownames(data))

write_res_csv = function(rankprod_res,directory){
  df <- data.frame(V1 = rep(NA, max(sapply(list(rownames(rankprod_res$Table1), rownames(rankprod_res$Table2)), length))))
  df[1:length(rownames(rankprod_res$Table1)),1] = rownames(rankprod_res$Table1)
  if (length(rownames(rankprod_res$Table2))){
    df[1:length(rownames(rankprod_res$Table2)),2] = rownames(rankprod_res$Table2)
  }
  else{
    df[1:length(rownames(rankprod_res$Table1)),2] = rep(NA,length(rownames(rankprod_res$Table1)))
  }
  write.table(df, file = paste(directory,'RP.csv',sep=""), col.names = FALSE,row.names = FALSE, na = 'NA')
}

write_res_csv(res_lateral,"./Arabidopsis/Lateral_root_cap/KNO3_KCL/")
write_res_csv(res_epidermic,"./Arabidopsis/Epidermic_cortex/KNO3_KCL/")
write_res_csv(res_pericycle,"./Arabidopsis/Pericycle_root/KNO3_KCL/")
write_res_csv(res_protoplast,"./Arabidopsis/Protoplasted_root/KNO3_KCL/")
library(meta)

# Data for PFA vs Thermal (1-year freedom from arrhythmia)
# Note: Higher is BETTER for efficacy, so RR > 1 favors PFA
df <- data.frame(
  study = c("ADVENT", "SINGLE SHOT"),
  e_pfa = c(204, 269),
  n_pfa = c(305, 428),
  e_thermal = c(203, 211),
  n_thermal = c(302, 427)
)

m <- metabin(e_pfa, n_pfa, e_thermal, n_thermal, 
             data = df, 
             studlab = study,
             method = "Inverse",
             sm = "RR",
             random = TRUE)

print(m)

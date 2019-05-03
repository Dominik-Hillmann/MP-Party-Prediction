library(ggplot2)
library(magrittr)
X <- read.table(
  "Polit_Affiliation_MPs.csv",
  header = TRUE,
  sep = ","
)
attach(X)

afd_blue <- "#0088ff"
cdu_orange <- "#FF9900"
fdp_yellow <- "#FFED00"
greens_green <- "#46962b"
left_purple <- "#980267"
spd_red <- "#FF0000"
  
#
sum(party == "F")
party <- as.character(X[, "party"])
party.colors <- party

party[party == "F"] <- fdp <- "FDP"
party[party == "S"] <- spd <- "SPD"
party[party == "C"] <- union <- "CDU/CSU"
party[party == "A"] <- afd <- "AfD"
party[party == "G"] <- green <- "B90/Grüne"
party[party == "L"] <- left <- "Die Linke"

party.colors[party.colors == "F"] <- fdp_yellow
party.colors[party.colors == "S"] <- spd_red
party.colors[party.colors == "C"] <- cdu_orange
party.colors[party.colors == "A"] <- afd_blue
party.colors[party.colors == "G"] <- greens_green
party.colors[party.colors == "L"] <- left_purple

boxplot(
  statuses_count ~ party, 
  main = "# Tweets by Party",
  xlab = "Party",
  ylab = "# Tweets",
  col = c(afd_blue, cdu_orange, fdp_yellow, greens_green, left_purple, spd_red)
)
options(scipen = 10)

boxplot(
  statuses_count[statuses_count < 40000] ~ party[statuses_count < 40000], 
  main = "# Tweets by Party with fewer than 40000 Tweets",
  xlab = "Party",
  ylab = "# Tweets",
  col = c(afd_blue, cdu_orange, fdp_yellow, greens_green, left_purple, spd_red)
)
options(scipen = 10)

screen_name <- as.character(screen_name)
party <- as.character(party)
screen_name[statuses_count == max(statuses_count[party == "A"])]
creation_date <- creation_date %>% 
  as.character %>% as.Date(format = "%Y-%m-%d")
creation_year <- creation_date %>% format(format = "%Y") %>% as.numeric
creation_month <- creation_date %>% format(format = "%m") %>% as.numeric
detailed_creation_year <- creation_year + (creation_month / 12)

boxplot(
  detailed_creation_year ~ party, 
  main = "Creation Year of Account by Party",
  xlab = "Party",
  ylab = "Year When Account Was Created",
  col = c(afd_blue, greens_green, cdu_orange, left_purple, fdp_yellow, spd_red), 
  ylim = c(2008, 2019.7)
)
abline(h = 2013 + (31 + 6) / 365, lty = "dashed")
abline(h = c(
  2013 + 264 / 365,
  2017 + 266 / 365,
  2009 + 169 / 365
), lty = "dotted")
legend(
  "topright", 
  legend = c("AfD founded", "elections"), 
  lty = c(2, 3),
  cex = 0.75
)

# Basic violin plot
X[, "party"] <- as.factor(party)
X <- cbind(X, detailed_creation_year)
p <- ggplot(X, aes(x = party, y = detailed_creation_year)) + geom_violin()
p <- p + geom_boxplot(width=0.1)
p + theme_classic()
p

sum(statuses_count)
# meiste AfD-Politiker nach Gründung --> keine privaten Accounts
# Grüne und FDPler sind early adopter
# neue Accounts von FDP und SPD strecken sich bis nach 2013 --> wegen schlechter Wahlergebnisse?

heatmap(
  cor(cbind(favorites_count, followers_count, friends_count, listed_count, statuses_count, detailed_creation_year)),
  keep.dendro = TRUE
)

pca.X <- cbind(favorites_count, followers_count, friends_count, listed_count, statuses_count, detailed_creation_year)
for (colname in colnames(pca.X)) {
  col <- pca.X[, colname]
  pca.X[, colname] <- (col - mean(col)) / sd(col)
} 
cov.X <- cov(pca.X)
E <- eigen(cov.X)$vectors
Lambda <- eigen(cov.X)$values

PCs <- data.frame(E)
rownames(PCs) <- colnames(cov.X)
colnames(PCs) <- c("PC1", "PC2", "PC3", "PC4", "PC5", "PC6")

prop.Lambda <- Lambda / sum(Lambda)
cumul.Lambda <- rep(NA, length(Lambda))
for (i in 1:length(Lambda)) {
  cumul.Lambda[i] <- sum(prop.Lambda[1:i])
}
cumul.Lambda
PCs

plot(1:length(Lambda), Lambda, type = "lines")
# PC1 gets larger, the
  # lower the number of listings
  # the lower the number of statuses
# PC1 is an activity dimension?
pc.1.coef <- as.numeric(PCs[, "PC1"])
pc.2.coef <- as.numeric(PCs[, "PC2"])
pc.3.coef <- as.numeric(PCs[, "PC3"])
# PC2 gets larger, the
  # higher the number of favorites the user has given
  # lower the number of followers

# PC3 gets larger
  # the younger the account is


pc.1 <- pc.2 <- pc.3 <- rep(NA, nrow(pca.X))
for (i in 1:nrow(pca.X)) {
  pc.1[i] <- (t(pc.1.coef) %*% as.vector(pca.X[i, ])) %>% as.numeric
  pc.2[i] <- (t(pc.2.coef) %*% as.vector(pca.X[i, ])) %>% as.numeric
  pc.3[i] <- (t(pc.3.coef) %*% as.vector(pca.X[i, ])) %>% as.numeric
}
pca.X <- cbind(pca.X, pc.1, pc.2, pc.3, party)

plot(pc.1, pc.2, col = party.colors, pch = 20)

plot(pc.1, pc.2, col = party.colors, pch = 20, xlim = c(-2, 2), ylim = c(-2, 2))

plot(pc.2, pc.3, col = party.colors, pch = 20)
arrows(0, 0, 1, 1)

boxplot(pc.1 ~ party)
boxplot(pc.2 ~ party)
boxplot(pc.3 ~ party)

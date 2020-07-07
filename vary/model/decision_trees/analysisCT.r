# Adapted from https://github.com/FAMILIAR-project/varylatex/blob/master/output-FSE/analysisCT.R

library(rpart)
library(rpart.plot)
library(caret)
library(readr)
library(dplyr)
mystats <- read_csv("../varylatex/result_example.csv",
    col_types = cols(
        ACK = col_factor(levels = c("True","False")), 
        BOLD_ACK = col_factor(levels = c("True","False")),
        EMAIL = col_factor(levels = c("True","False")), 
        LONG_ACK = col_factor(levels = c("True","False")),
        LONG_AFFILIATION = col_factor(levels = c("True","False")),
        PARAGRAPH_ACK = col_factor(levels = c("True","False")),
        PL_FOOTNOTE = col_factor(levels = c("True","False")),
        js_style = col_factor(levels = c("\\footnotesize", "\\scriptsize", "\\tiny")),
        nbPages = col_factor(levels = c("4","5"))
    )
)

evalCT <- function (stats, perc) {
    # View(stats)
    summary(stats$nbPages)
    stats <- na.omit(stats)
    #print(summary(stats$nbPages))
    sample <- sample.int(n = nrow(stats), size = floor(perc*nrow(stats)), replace = F)
    test  <- stats[-sample, ]
    train <- stats[sample, ]
    fit <- rpart(nbPages~.-idConfiguration-space,data=train,method="class")
    rpart.plot(fit,type=4, extra=0, box.palette=c("palegreen3", "red"))
    pred = predict(fit, test, type="class")
    cm <- confusionMatrix(pred, test$nbPages)
    return (cm$overall['Accuracy'])
}

evalCT(stats=mystats, perc = (7/10))
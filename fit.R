library(ptproc)

options(digits=14)
x<-read.csv('./data/192000_292000_times.csv')
trade_times <- x$"X1366463464.594167"

fit <- function(rate, data) {
  pstart <- c(mu = rate, C = 1, a = 0.1)
  ppm <- ptproc(pts = data, cond.int = hawkes.cond.int, params = pstart)
  condition(ppm) <- penalty(code = NULL, condition = quote(any(params < 0)))
  f <- ptproc.fit(ppm, optim.control = list(trace = 2), alpha = 1e+5, hessian = TRUE)

  return (f)
}

f <- fit(0.5, trade_times)

# Evaluate on range of timestamps from the original data
#> max(trade_times[0:5000])
#[1] 1366487824.4814
#> min(trade_times)
#[1] 1366463464.6084

# evaluation of intensity over the given timeframe. 
x <- seq(1366463464, 1366487824, len=20000)
e <- evalCIF(f, xpts = x)

# this has to get integrated over 1 minute intervals to match up to empirical counts
plot(x, e, type = "l", xlab = "Times", ylab = "Conditional intensity (events / second)")


# write to file for python to read
out <- data.frame(index=x, data=e)
write.csv(out, './fitted_intensities_actual_times_large.csv', row.names=FALSE)

## residuals
res <- residuals(f, type = "approx", K = 350)

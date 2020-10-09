# R version of the corner cutter.


lerp_neighbors <- function(x, r) {
    # example
    # x:               1, 2, 3, 4
    # left neighbors:  4, 1, 2, 3
    # right neighbors: 2, 3, 4, 1
    # 
    # neighbors and x combined in the correct order:
    # x:         1, 1, 2, 2, 3, 3, 4, 4
    # neighbors: 4, 2, 1, 3, 2, 4, 3, 1
    
    a <- rep(x, each = 2)
    b <- c(rbind(
        c(tail(x, 1), head(x, -1)),
        c(x[-1], x[1])
    ))
    a + (b - a) * r
}


cut <- function(x, y, ratio, closed = TRUE) {
    stopifnot(
        ratio <= 1,
        ratio >= 0,
        length(x) == length(y)
    )
    
    if (ratio > 0.5) {
        ratio <- 1 - ratio
    }
    
    new_x <- lerp_neighbors(x, ratio)
    new_y <- lerp_neighbors(y, ratio)
    
    if (!closed) {
        new_x <- new_x[-c(1, length(new_x))]
        new_y <- new_y[-c(1, length(new_y))]
        new_x[c(1, length(new_x))] <- x[c(1, length(x))]
        new_y[c(1, length(new_y))] <- y[c(1, length(y))]
    }
    
    list(x = new_x, y = new_y)
}


triangle_open <- list(
    x = c(0, 0, 1),
    y = c(0, 1, 1),
    color = "blue",
    width = 2,
    closed = FALSE
)
triangle_closed <- list(
    x = c(1, 0.25, 1),
    y = c(0, 0, 0.5),
    color = "forestgreen",
    width = 2,
    closed = TRUE
)
foo <- list(
    x = c(0.25, 0.8, 0.5, 0.45, 0.6, 0.3),
    y = c(0.75, 0.6, 0.85, 0.5, 0.4, 0.15),
    color = "orange",
    width = 1,
    closed = TRUE
)
polygons <- list(
    triangle_open,
    triangle_closed,
    foo
)

r <- 0.25
n <- 3
for (i in seq_len(n)) {
    for (k in seq_along(polygons)) {
        p <- polygons[[k]]
        new_xy <- cut(p$x, p$y, r, p$closed)
        p$x <- new_xy$x
        p$y <- new_xy$y
        polygons[[k]] <- p
    }
}
    
par(mar = rep(0, 4), pty = "s")
plot(NA, xlim = c(0, 1), ylim = c(0, 1), asp = 1, axes = FALSE, ann = FALSE)
for (p in polygons) {
    if (p$closed) {
        polygon(
            p$x, 
            p$y, 
            border = p$color, 
            lwd = p$width
        )
    } else {
        lines(
            p$x, 
            p$y, 
            col = p$color, 
            lwd = p$width
        )
    }
}

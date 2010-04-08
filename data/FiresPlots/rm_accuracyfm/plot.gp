
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Granularity"
set ylabel "Median Error"
set nokey
set title "Reverse Mapping Accuracy vs. FM (Fires)"

set xrange [0:325]
plot "rm_times" with errorbars, "rm_times" with lines 

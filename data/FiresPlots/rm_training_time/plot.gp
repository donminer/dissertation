
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Granularity"
set ylabel "Average Training Time (Seconds)"
set nokey
set title "Reverse Mapping Training Time (Fires)"

set xrange [0:325]
plot "rm_times" with errorbars, "rm_times" with lines 

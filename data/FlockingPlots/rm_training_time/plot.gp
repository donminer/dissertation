
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Granularity"
set ylabel "Average Training Time (Seconds)"
set nokey
set title "Reverse Mapping Training Time (Flocking)"

set xrange [10:45]
plot "rm_times" with errorbars, "rm_times" with lines 

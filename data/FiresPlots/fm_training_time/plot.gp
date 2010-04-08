
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Data Set Size"
set ylabel "Training Time (Seconds)"
set key top left
set title "Forward Mapping Training Time (Fires)"

set xrange [0:220]
plot  "kNN" with errorbars ,  "LOESS" with errorbars ,  "NLR" with errorbars 


set terminal png nocrop enhanced size 400, 400
set output "plot-NLR.png"
set xlabel "Data Set Size"
set ylabel "Median Error"
set key top right
set title "Forward Mapping Accuracy (Fires)"

set xrange [0:220]
set yrange [0:0.1443]
plot  "NLR" with errorbars 

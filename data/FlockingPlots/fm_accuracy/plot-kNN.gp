
set terminal png nocrop enhanced size 400, 400
set output "plot-kNN.png"
set xlabel "Data Set Size"
set ylabel "Median Error"
set key top right
set title "Forward Mapping Accuracy (Flocking)"

set xrange [0:360]
set yrange [0:0.2351]
plot  "kNN" with errorbars 

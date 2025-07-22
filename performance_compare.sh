#!/bin/bash
source /mnt/chart_now/bin/activate.fish
echo "Old method of individual columns of left and right intervals:"
time python 'Performance non-equi old.py'
echo "New method using fractional_interval class:"
time python 'Performance non-equi new.py'

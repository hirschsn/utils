#/bin/sh

# Usage:
# histogram.sh <additional gnuplot cmds>
#
# Reads from stdin and prints a histogram of the data.
#

sort -g | uniq -c | awk '{print $2,$1}' | gnuplot -p -e "$*; plot '-' w p;"


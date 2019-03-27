#!/usr/bin/awk -f

# Computes the average of all input records.
# If the data set is multidimensional (several fields per line)
# computes the average of each column.

# Set the number of expected fields
NR == 1 {
    nfields = NF;
}

{
    if (NF != nfields) {
        printf "Malformed record `%s'. Expected %d fields; got %d.\n", $0, nfields, NF > "/dev/stderr"
        exit 1
    }

    for (i = 1; i <= NF; i++) {
        v[i] += $i;
    }
    n++;
}

END {
    for (i = 1; i <= nfields; i++) {
        printf "%lf ", v[i] / n;
    }
    printf "\n";
}


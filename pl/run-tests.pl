#!/usr/bin/perl

=pod

=head1 NAME

run-tets.pl - Test an MPI program with random number of processes

=head1 SYNOPSIS

B<run-tests.pl> I<NTESTS> I<CMDLINE> I<MIN_NPROC> I<MAX_NPROC>

=head1 DESCRIPTION

This script tests a given MPI-based program with random numbers of processes.
Required arguments are:

=over

=item I<NTESTS>

Number of times the program specified via I<CMDLINE> is run.

=item I<CMDLINE>

Program to run.

=item I<MIN_NPROC>

Minimal number of processes to use.

=item I<MAX_NPROC>

Maximal number of processes to use.

=back

=head1 EXAMPLES

Run F<./a.out> 100 times with the number of processes ranging from 10 to 20:

B<$ run-tests.pl 100 ./a.out 10 20>

 Successfully tested: 10, 12, 14-16, 18
 Tests failed for: 11, 13, 17, 19
 100 tests; 27 failed; 73 successful


=head1 COPYRIGHT

Copyright 2019 Steffen Hirschmann

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

=cut

use warnings;
use strict;
use Pod::Usage;

sub uniq {
    my %seen;
    return grep { $seen{$_}++ == 0 } @_;
}

# Prints (1 2 3 5 9 10 11) as "1-3, 5, 9-11"
sub pprint {
    my @l = uniq sort { $a <=> $b } @_;
    while (my $first = shift @l) {
        my $cur = $first;
        my $test = $l[0];
        while (@l > 0 && $l[0] == $cur + 1) {
            $cur = shift @l;
        }
        
        if ($cur > $first) {
            print $first, "-", $cur;
        } else {
            print $first;
        }

        if (@l > 0) {
            print ", ";
        }
    }
}

pod2usage(-verbose => 2) if @ARGV != 4;

my $ntests = shift || die;
my $cmdline = shift || die;
my $min_proc = shift || die;
my $max_proc = shift || die;

# Currently does not support cmdlines but only program names. :/
if (! -e $cmdline) {
    die "Cannot access program $cmdline";
}

my $ngood = 0;
my $nfail = 0;
my @good;
my @fail;

for my $i (0..$ntests-1) {
    my $nproc = int(rand($max_proc - $min_proc)) + $min_proc;
    printf "\r%3i\t[%i/%i tests; %i failed; %i successful]", $nproc, $i, $ntests, $nfail, $ngood;
    system "mpiexec --oversubscribe -n $nproc $cmdline >/dev/null";
    if ($?) {
        $nfail += 1;
        push @fail, $nproc;
    } else {
        $ngood += 1;
        push @good, $nproc;
    }
}

# Clear previous output
print "\r";
print " " for (1..100);
print "\r";

if (@good > 0) {
    print "Successfully tested: ";
    pprint @good;
    print "\n";
}
if (@fail > 0) {
    print "Tests failed for: ";
    pprint @fail;
    print "\n";
}
printf "%i tests; %i failed; %i successful\n", $ntests, $nfail, $ngood;


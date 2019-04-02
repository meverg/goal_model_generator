README.txt file for OptiMathSAT
-----------------------------

Contents of the tarball:
  README.txt                This file.
  LICENSE.txt               The OptiMathSAT License.
  CREDITS.txt               Credits for code used in OptiMathSAT.
  bin/optimathsat           The OptiMathSAT executable.
  include/mathsat.h         The OptiMathSAT API header file.
  lib/libmathsat.a          The OptiMathSAT library.
  examples/*                Various examples on using OptiMathSAT, both via the
                            command-line and via the C API.
  configurations/*          Sample configurations files for OptiMathSAT.
  

OptiMathSAT is linked with the Gnu Multiprecision Library (GMP) and the GNU C
library (glibc), both covered by the GNU LGPL license. A copy of the LGPL and
the GNU GPL license are included in this tarball (files lgpl-3.0.txt and
gpl-3.0.txt). For other credits, see the CREDITS.txt file.

NOTE: the provided OptiMathSAT executable is statically linked against GMP and
glibc, so as to avoid potential issues with library versions. However, a
OptiMathSAT executable linked against a different version of GMP and/or glibc can
be obtained easily, by creating a "main.c" C file with the following content:

  extern int msat_main(int argc, const char **argv);
  int main(int argc, const char **argv) { return msat_main(argc, argv); }

and linking it against libmathsat.a, GMP and glibc. For example, using GCC:

  $ gcc main.c -o optimathsat lib/libmathsat.a -lgmpxx -lgmp

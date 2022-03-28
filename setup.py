from setuptools import setup, Extension


GENERATE_FILES = {"objects/generate.cpp", 
                  "objects/primetest.cpp", 
                  "objects/utils.cpp"}
PRIMETEST_FILES = {"objects/primetest.cpp", 
                   "objects/roots.cpp", 
                   "objects/utils.cpp"}
FACTORING_FILES = {"objects/factoring.cpp", } | GENERATE_FILES | PRIMETEST_FILES
DECOMPOSING_FILES = {"objects/decomposing.cpp", } | FACTORING_FILES


def main():
    setup(name="magic_sq",
          version="1.0.0",
          description="C helper methods for magic square problem",
          author="Ryan H",
          ext_modules=[Extension("magic_sq.decomposing", list(DECOMPOSING_FILES)),
                       Extension("magic_sq.factoring", list(FACTORING_FILES)),
                       Extension("magic_sq.primetest", list(PRIMETEST_FILES)),
                       Extension("magic_sq.generate", list(GENERATE_FILES)),
                       Extension("magic_sq.utils", ["objects/utils.cpp"])])


if __name__ == "__main__":
    main()

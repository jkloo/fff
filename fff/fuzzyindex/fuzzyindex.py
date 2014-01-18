import os
import sys
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

from fuzzyfile import fuzzyfile


IGNORE_DIRS = ['.git', '.svn']
IGNORE_FILES = ['.pyc']

class FuzzyIndex:
    """ class to hold isntances of the File class and some indexing functions. """
    def __init__(self, root):
        """ create a file index built out of instances of the File class. """
        self.files = []
        for r, dirs, fs in os.walk(root):
            for d in IGNORE_DIRS:
                if d in dirs:
                    dirs.remove(d)
            for _f in fs:
                if not os.path.splitext(_f)[1] in IGNORE_FILES:
                    path = os.path.join(r, _f)
                    self.append(path)


    def append(self, f):
        _f = fuzzyfile.FuzzyFile(f)
        self.files.append(_f)


    def _tiebreak(self, files):
        """ attempt to break a tie for best match in a sensible manner. """
        # shortest HEAD portion wins
        tmp = min([f for f in files if f.matched], key=lambda x: x.head)
        tmps = [f for f in files if f.head == tmp.head and f.matched]
        if len(tmps) == 0:
            return tmps[0]
        
        # if still tie, shortest TAIL portion wins
        tmp = min([f for f in files if f.matched], key=lambda x: x.tail)
        tmps = [f for f in files if f.tail == tmp.tail and f.matched]
        if len(tmps) == 0:
            return tmps[0]

        # if still tie, shortest filename wins
        tmp = min([f for f in files if f.matched], key=lambda x: len(x.name))
        tmps = [f for f in files if len(f.name) == len(tmp.name) and f.matched]
        if len(tmps) == 0:
            return tmps[0]

        # if still tie, alphabetical by filename
        return sorted(files, key=lambda k: k.name)[0]



    def match(self, pattern):
        """ find the best match in the file index for the given pattern. """
        for f in self.files:
            f.match(pattern) # the fuzzyfile object will update with its scores.
        
        # return the "best" match, that is the one with the lowest score (fewest interposed characters)
        low = min([f for f in self.files if f.matched], key=lambda x: x.score)
        lows = [f for f in self.files if f.score == low.score and f.matched]
        if len(lows) > 1:
            logging.debug("tie")
            return self._tiebreak(lows)
        else:
            return lows[0]

if __name__ == "__main__":
    FI = FuzzyIndex(os.getcwd())
    for f in FI.files:
        print f.name

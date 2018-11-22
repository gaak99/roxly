
import os
import sys

import attr

from .misc import Misc
from .pathname import PathName

DEFAULT_DIFF_CMD = 'diff %s %s'

@attr.s
class Diff(object):
    repo = attr.ib()
    diff_cmd = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?

    def get_diff_pair(self, reva, revb):
        pn = PathName(self.repo, self.filepath, self.debug)
        
        ap = pn.wd_or_index(reva)
        bp = pn.wd_or_index(revb)
        
        ap = ap if ap else pn.wdrev_ln(reva)
        self._debug("get_diff_pair: ap=%s" % ap)
        bp = bp if bp else pn.wdrev_ln(revb)
        
        return ap, bp

    def _diff_one_path(self, reva, revb):
        pn = PathName(self.repo, self.filepath, self.debug)
        
        pn.pull_me_maybe(reva.lower())
        pn.pull_me_maybe(revb.lower())
        
        diff_cmd = self.diff_cmd if self.diff_cmd else DEFAULT_DIFF_CMD
        self._debug('debug _diff2_one_path: %s' % diff_cmd)
        
        shcmd = diff_cmd % self.get_diff_pair(reva.lower(), revb.lower())
        self._debug('debug _diff2_one_path: %s' % shcmd)
        os.system(shcmd)

    def diff(self, reva, revb):
        """Run diff_cmd to display diffs from two revisions of file.

        diff_cmd format: program %s %s
        """
        self._debug('debug2: start diff: %s %s %s' % (reva, revb, self.filepath))

        fp = self.filepath
        m = Misc(self.repo, fp, self.debug)
        pn = PathName(self.repo, fp, self.debug)
        
        if reva == revb:
            sys.exit('error: reva and revb the same yo diggity just no')

        if fp:
            if not os.path.isfile(pn.wt_path()):
                sys.exit('error: file name not found in repo working dir -- spelled correctly?')
            fp_l = [fp]
        else:
            fp_l = pn.wt_paths()

        ifp_l = m.scrub_fnames(fp_l)
        if not ifp_l:
            sys.exit('warning: internal err diff: wt empty')
            
        for p in ifp_l:
            self._debug('debug diff2 p=%s' % p)
            self._diff_one_path(reva, revb)
        


import os
import sys

import attr

from .misc import Misc
from .pathname import PathName

#DEFAULT_CAT_CMD = 'cat %s'

@attr.s
class Cat(object):
    #foo = attr.ib()
    repo = attr.ib()
    cat_cmd = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()
    
    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?

    def _cat_one_path(self, rev):
        cmd = self.cat_cmd
        #fp = self.filepath

        pn = PathName(self.repo, self.filepath, self.debug)
        
        pn.pull_me_maybe(rev.lower())
        
        cmd = cmd if cmd else DEFAULT_CAT_CMD
        self._debug('debug _cat_one_path: %s' % cmd)
        
        fp = pn.wd_or_index(rev)
        fp = fp if fp else pn.by_rev(rev)
        
        try:
            shcmd = cmd % (fp)
        except TypeError:
            sys.exit('cat cat-cmd bad format. Try: roxly cat --help')
            
        self._debug('debug _cat_one_path: %s' % shcmd)
        os.system(shcmd)
    
    def cat(self, rev):
        """Run cat_cmd to display cats from a revision of file.

        cat_cmd format: program %s
        """
        cmd = self.cat_cmd
        fp = self.filepath

        self._debug('debug start cat: %s %s' % (rev, fp))

        m = Misc(self.repo, fp, self.debug)
        pn = PathName(self.repo, fp, self.debug)
        
        if fp:
            if not os.path.isfile(pn.wt_path()):
                sys.exit('error: file name not found in repo working dir -- spelled correctly?')
            fp_l = [fp]
        else:
            fp_l = pn.wt_paths()

        ifp_l = m.scrub_fnames(fp_l)
        if not ifp_l:
            sys.exit('warning: internal err cat: wt empty')
            
        for p in ifp_l:
            self._debug('debug cat p=%s' % p)
            self._cat_one_path(pn._log_head2rev(p, rev.lower()))


import filecmp
import os
import sys

import attr

from .misc import Misc
from .pathname import PathName

@attr.s
class Status(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?

    def status(self):
        """List modified file(s) in staging area or wd"""
        fp = self.filepath
        
        m = Misc(self.repo, fp, self.debug)
        pn = PathName(self.repo, fp, self.debug)

        self._debug('status: %s' % fp)
        if fp:
            if not os.path.isfile(pn.wt_path()):
                sys.exit('error: file not found in repo working dir -- %s -- spelled correctly? clone run first?'
                         % pn.wt_path())
            fp_l = [fp]
        else:
            fp_l = pn.get_wt_paths()

        ifp_l = m.scrub_fnames(fp_l)
        if not ifp_l:
            sys.exit('warning: internal err status: wt paths empty')

        self._debug('debug status2 %s' % ifp_l)
        
        self._staged_not_pushed(ifp_l)

        self._not_changed(fp_l)

    def _staged_not_pushed(self, ifp_l):
        m = Misc(self.repo, self.filepath, self.debug)

        mods = 0
        for p in ifp_l:
            self._debug('debug status _staged_not_pushed p=%s' % p)
            modded = False
            p_wt, p_indx, p_head = m.get_fp_triple(p)
            self._debug('debug status _staged_not_pushed  wt: %s' % p_wt)
            self._debug('debug status _staged_not_pushed indx: %s' % p_indx)
            self._debug('debug status _staged_not_pushed head: %s' % p_head)
            if p_indx and p_head:
                modded = not filecmp.cmp(p_indx, p_head)
            if modded:
                mods += 1
                if mods == 1:
                    print('Changes to be pushed:')
                print('\tmodified: %s' % p)

    def _not_changed(self, fp_l):
        m = Misc(self.repo, self.filepath, self.debug)

        ifp_l = m.scrub_fnames(fp_l)
        mods = 0
        for p in ifp_l:
            self._debug('debug status2 p=%s' % p)
            modded = False
            p_wt, p_indx, p_head = m.get_fp_triple(p)
            self._debug('debug status triple wt: %s' % p_wt)
            self._debug('debug status triple indx: %s' % p_indx)
            self._debug('debug status triple head: %s' % p_head)
            if not p_wt:
                pass
                # Damned if ya do
                # print('warning: file does not exist in wt: %s' % p)
            elif p_indx:
                self._debug('debug status else p_indx')
                modded = not filecmp.cmp(p_wt, p_indx)
            else:
                self._debug('debug status else')
                modded = not filecmp.cmp(p_wt, p_head)
            if modded:
                mods += 1
                if mods == 1:
                    print('\nChanges not staged:')
                print('\tmodified: %s' % p)

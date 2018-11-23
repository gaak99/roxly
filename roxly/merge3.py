
import attr
import os
import sys
import subprocess as sp

from .diff import Diff
from .log import Log
from .misc import Misc
from .pathname import PathName

# defaults 2-way diff/merge
MERGE_BIN = "emacsclient"
MERGE_EVAL = "--eval"
MERGE_EVALFUNC = "ediff-merge-files"
DEFAULT_MERGE_CMD = MERGE_BIN + ' ' + MERGE_EVAL + ' \'('\
                    + MERGE_EVALFUNC + ' %s %s' + ')\''

DIFF3_BIN = 'diff3'
DIFF3_BIN_ARGS = '-m'

@attr.s
class Merge3(object):
    """Run Unix command for 3-way merge (aka auto-merge when possible)
    """
    repo = attr.ib()
    dry_run = attr.ib()
    merge_cmd = attr.ib()
    reva = attr.ib()
    revb = attr.ib()
    filepath = attr.ib()
    #mmdb = attr.ib()
    debug = attr.ib()
    #roxly = attr.ib()
    #print('Merge3 init??? this thing on? roxly=%s' % type(roxly))
    #pn = PathName(self.repo, filepath, debug)
    #log = Log(repo, filepath, debug)

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?
    
    def merge(self):
        #print('Merge3 merge roxly=%s' % type(self.roxly))
        fp  = self.filepath
        reva = self.reva
        revb = self.revb
        #rox = self.roxly#tmp
        dbg = self.debug

        df = Diff(self.repo, None, fp, dbg)
        log = Log(self.repo, fp, dbg)
        m = Misc(self.repo, fp, dbg)
        pn = PathName(self.repo, fp, dbg)
        
        reva = log.head2rev(reva)
        revb = log.head2rev(revb)

        pn.pull_me_maybe(reva)
        pn.pull_me_maybe(revb)
        
        #hash = self.mmdb.get('ancestor_rev') ##gbrox _hash
        hash = m.get_mmval('ancestor_rev') ##gbrox _hash
        if not hash:
            self._debug('debug merge3: ancestor (hash)=%s'
                        % (hash))
            sys.exit('Error: mmdb not populated. Was clone run?')
            
        anc_rev = m.hash2rev(hash)
        self._debug('debug merge3: ancestor (hash)=%s, ancestor_rev=%s'
                    % (hash[:8], anc_rev))

        self._check_anchash(hash, anc_rev)
        
        (fa, fb) = df.get_diff_pair(reva, revb)
        f_anc = pn.wdrev_ln(anc_rev, suffix=':ANCESTOR')
        cmd = self._cmd_factory(fa, fb, f_anc)
        
        if self.dry_run:
            print('merge3 dry-run: %s' % cmd)

        self._run_cmd(cmd)

    def _check_anchash(self, hash, anc_rev):
        reva = self.reva
        revb = self.revb

        if hash == None:
            print('Warning hash==None: cant do a 3-way merge as ancestor revision not found.')
            sys.exit('Warning: you can still do a 2-way merge (roxly merge2 --help).')
            
        if anc_rev == None: #not enough revs downloaded 
            print('Warning ancrev==None: cant do a 3-way merge as no ancestor revision found.')
            sys.exit('Warning: you can still do a 2-way merge (roxly merge2 --help).')
            sys.exit(1)

        if reva == anc_rev:
            print('Warning: reva %s == anc_rev %s' % (reva, anc_rev))
            print('Warning: does not look like a merge is necessary. Try Sync on Orgzly.')
            sys.exit('Warning: you can still do a 2-way merge if necessary (roxly merge2 --help).')
            
        if revb == anc_rev:
            print('Warning: revb %s == anc_rev %s' % (revb, anc_rev))
            print('Warning: does not look like a merge is necessary, try Sync on Orgzly.')
            sys.exit('Warning: you can still do a 2-way merge if necessary (roxly merge2 --help).')

    def  _run_cmd(self, cmd):
        fp = self.filepath
        
        tmpf = '/tmp/tmproxlymerge3.' + str(os.getpid())
        fname = '/dev/null' if self.dry_run else tmpf
        with open(fname, 'w') as fout:
            rt = sp.call(cmd, stdout=fout)
            self._debug('debug merge3: rt=%d, fname=%s' % (rt, fname))
            
            if self.dry_run:
                print('merge3 dry-run: %s exit value=%d' % (cmd[0], rt))
                sys.exit(rt)
                
            if rt > 1:
                print('Error: diff3 returned %d' % rt)
            if rt == 0:
                os.system('mv %s %s' % (fname, filepath))
                print('No conflicts found. File fully merged locally in %s'  % filepath)
            if rt == 1:
                fcon = filepath + ':CONFLICT'
                os.system('mv %s %s' % (fname, fcon))
                print('Conflicts found, pls run either ...')
                print('\temacsclient ediff 3-way merge: roxly mergerc --reva %s --revb %s %s' % (reva, revb, filepath))
                print('\t\t then run: roxly push --add %s' % (filepath))
                print('\tedit diff3 output: $EDITOR %s' % (fcon))
                print('\t\t then run: mv %s %s' % (fcon, filepath))
                print('\t\t then run: roxly push --add %s' % (filepath))
                
            sys.exit(rt)

    def _cmd_factory(self, fa, fb, f_anc):
        mcmd = margs = None
        if self.merge_cmd:
            mc = self.merge_cmd.split(' ')
            mcmd = mc[0]
            margs = mc[1:] if len(mc)>1 else []
        mcmd = [mcmd] if mcmd else [DIFF3_BIN]
        margs = margs if margs else [DIFF3_BIN_ARGS]
        return mcmd + margs + [fa, f_anc, fb]

    def merge2(self, emacsclient_path):
        """Run merge_cmd to allow user to merge two revs.

        merge_cmd format:  program %s %s
        """
        fp  = self.filepath
        reva = self.reva
        revb = self.revb
        dbg = self.debug

        df = Diff(self.repo, None, fp, dbg)
        pn = PathName(self.repo, fp, dbg)
        
        pn.pull_me_maybe(reva.lower())
        pn.pull_me_maybe(revb.lower())
        
        qs = lambda s: '\"' + s + '\"'
        
        (fa, fb) = df.get_diff_pair(reva.lower(), revb.lower())
        
        if self.merge_cmd:
            shcmd = merge_cmd % (qs(fa), qs(fb))  # quotes cant hurt, eh?
        elif emacsclient_path:
            m_cmd = emacsclient_path + '/' + DEFAULT_MERGE_CMD
            shcmd = m_cmd % (qs(fa), qs(fb))
        else:
            shcmd = DEFAULT_MERGE_CMD % (qs(fa), qs(fb))
        self._debug('debug merge2: %s' % shcmd)

        if self.dry_run:
            print('merge2 dry-run: %s' % shcmd)
            return
        
        os.system(shcmd)

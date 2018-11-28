
import attr
import os
import sys
import subprocess as sp

from .diff import Diff
from .log import Log
from .misc import Misc
from .pathname import PathName

MERGE_BIN = "emacsclient"
MERGE_EVAL = "--eval"

# defaults 2-way diff/merge
MERGE_EVALFUNC = "ediff-merge-files"
DEFAULT_MERGE_CMD = MERGE_BIN + ' ' + MERGE_EVAL + ' \'('\
                    + MERGE_EVALFUNC + ' %s %s' + ')\''

# defaults 3-way diff/merge
MERGE3_EVALFUNC = "ediff-merge-with-ancestor"
DEFAULT_MERGE3RC_CMD = MERGE_BIN + ' ' + MERGE_EVAL + ' \'('\
                    + MERGE3_EVALFUNC + ' %s %s %s' + ')\''
DEFAULT_EDIT_CMD = 'emacsclient %s'

DIFF3_BIN = 'diff3'
DIFF3_BIN_ARGS = '-m'

@attr.s
class Merge(object):
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
    
    def merge3(self):
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
        hash = m.get_mmval('ancestor_hash') ##gbrox _hash
        if hash == None:
            print('Warning: ancestor_hash not found, cant do a 3-way merge.')
            sys.exit('Warning: you can still do a 2-way merge (roxly merge2 --help).')

        anc_rev = m.hash2rev(hash)
        self._debug('merge3: ancestor_rev=%s' % (anc_rev))

        #self._check_ancrev(anc_rev)
        self._check_revs(anc_rev)
        
        (fa, fb) = df.get_diff_pair(reva, revb)
        f_anc = pn.wdrev_ln(anc_rev, suffix=':ANCESTOR')
        cmd = self._cmd_factory(fa, fb, f_anc)
        
        if self.dry_run:
            print('merge3 dry-run: %s' % cmd)

        self._run_cmd(cmd)

    #def _check_anchash(self, hash, anc_rev):
    def _check_revs(self, anc_rev):
        reva = self.reva
        revb = self.revb

        if anc_rev == None: #not enough revs downloaded 
            print('Warning: ancestor rev not found, cant do a 3-way merge.')
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

    def _run_cmd(self, cmd):
        fp = self.filepath
        reva = self.reva
        revb = self.revb
        
        tmpf = '/tmp/tmproxlymerge3.' + str(os.getpid())
        fname = '/dev/null' if self.dry_run else tmpf
        with open(fname, 'w') as fout:
            rt = sp.call(cmd, stdout=fout)
            self._debug('merge3: rt=%d, cmd=%s' % (rt, cmd))
            #self._debug('debug merge3: rt=%d, fname=%s' % (rt, fname))
            
            if self.dry_run:
                print('merge3 dry-run: %s exit value=%d' % (cmd[0], rt))
                sys.exit(rt)
                
            if rt > 1:
                print('Error: diff3 returned %d' % rt)
            if rt == 0:
                os.system('mv %s %s' % (fname, fp))
                print('No conflicts found. File fully merged locally in %s'  % fp)
            if rt == 1:
                fcon = fp + ':CONFLICT'
                os.system('mv %s %s' % (fname, fcon))
                print('Conflicts found, pls run either ...')
                print('\temacsclient ediff 3-way merge: roxly mergerc --reva %s --revb %s %s' % (reva, revb, fp))
                print('\t\t then run: roxly push --add %s' % (fp))
                print('\tedit diff3 output: $EDITOR %s' % (fcon))
                print('\t\t then run: mv %s %s' % (fcon, fp))
                print('\t\t then run: roxly push --add %s' % (fp))
                
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


    #def merge3_rc(self, dry_run, emacsclient_path, mergerc_cmd, reva, revb, filepath):
    def merge3_rc(self, emacsclient_path, mergerc_cmd):
        """Run mergerc_cmd to allow user to merge 3 revs.

        merge_cmd format:  program %s %s
        """
        dry_run = self.dry_run
        fp  = self.filepath
        reva = self.reva
        revb = self.revb
        #merge_cmd = self.merge_cmd
        #rox = self.roxly#tmp
        dbg = self.debug

        df = Diff(self.repo, None, fp, dbg)
        log = Log(self.repo, fp, dbg)
        m = Misc(self.repo, fp, dbg)
        pn = PathName(self.repo, fp, dbg)

        reva = log.head2rev(reva)
        revb = log.head2rev(revb)
        
        #hash = m.get_mmval('ancestor_rev') ##gbrox _hash
        hash = m.get_mmval('ancestor_hash') ##gbrox _hash
        if not hash:
            self._debug('debug merge_rc: ancestor (hash)=%s'
                        % (hash))
            sys.exit('Error: mmdb not populated. Was clone run?')
            
        anc_rev = m.hash2rev(hash)
        self._debug('debug merge3: ancestor (hash)=%s, ancestor_rev=%s'
                    % (hash[:8], anc_rev))

        #self._check_anchash(hash, anc_rev)
        self._check_revs(hash, anc_rev)

        ## All 3 revs look sane, make sure we have local copies.
        pn.pull_me_maybe(reva)
        pn.pull_me_maybe(revb)
        pn.pull_me_maybe(anc_rev)

        f_anc = pn.wdrev_ln(anc_rev, suffix=':ANCESTOR')
        (fa, fb) = df.get_diff_pair(reva, revb)
        
        qs = lambda s: '\"' + s + '\"'
        
        if mergerc_cmd:
            shcmd = mergerc_cmd % (qs(fa), qs(fb), qs(f_anc))  # quotes cant hurt, eh?
        elif emacsclient_path:
            m_cmd = emacsclient_path + '/' + DEFAULT_MERGE3RC_CMD
            shcmd = m_cmd % (qs(fa), qs(fb), qs(f_anc))
        else:
            shcmd = DEFAULT_MERGE3RC_CMD % (qs(fa), qs(fb), qs(f_anc))
            
        self._debug('debug mergerc: %s' % shcmd)
        
        if dry_run:
            print('mergerc dry-run: %s' % shcmd)
            return
        
        os.system(shcmd)
        

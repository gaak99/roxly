
import os
#import sys

import attr

from .utils import get_relpaths_recurse, make_sure_path_exists
#nonono from .log import Log

HASHREVDB = 'hashrevdb.json'
LOGFILENAME = 'log.txt'
ROXLYHOME = '.roxly'
ROXLYSEP1 = '::'
ROXLYINDEX = 'index'

@attr.s
class PathName(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()
    #nonono log = Log(self.repo, self.filepath)

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?
    
    def by_rev(self, rev='head'):
        self._debug('by_rev: rev=%s' % rev)

        fp = self.filepath
        
        if rev == 'head' or rev == 'headminus1':
            rev = self._log_head2rev(fp, rev)

        pn_revdir = self.home_revsdir()
        make_sure_path_exists(pn_revdir)

        return pn_revdir + '/' + rev

    def by_wdrev(self, rev):
        fp = self.filepath
        
        if rev == 'head' or rev == 'headminus1':
            rev = self._log_head2rev(fp, rev)

        return self.wt_path() + ROXLYSEP1 + rev

    def home_base(self):
        #return self.repo + '/' + self.home
        return self.repo + '/' + ROXLYHOME

    def home_paths(self):
        path = self.home_base_tmp() + '/roxly' + ROXLYSEP1 + 'filepaths'
        return os.path.expanduser(path)
    
    def home_base_tmp(self):
        return self.home_base() + '/.tmp'
    
    def home_revsdir(self):
        fp = self.filepath
        base_path = self.home_base()
        path_dir = os.path.dirname(fp)
        path_f = os.path.basename(fp)

        return base_path + '/' + path_dir + '/' + ROXLYHOME + ROXLYSEP1 + path_f

    def hrdbpath(self):
        # one per file
        return self.home_revsdir() + '/' + HASHREVDB

    def index(self):
        return self.home_base_tmp() + '/' + 'roxly'\
            + ROXLYSEP1 + ROXLYINDEX

    def index_path(self, path):
        return self.index() + '/' + path

    def logpath(self):
        # one per file
        return self.home_revsdir() + '/' + LOGFILENAME

    def repo_base(self):
        return self.repo
    
    def wdrev_ln(self, rev, suffix=''):
        """Return linked file path of rev::suffix in wd.
        """
        fp = self.filepath
        self._debug("_get_pname_wdrev_ln: %s, %s" % (fp, rev))
        src = self.by_rev(rev)
        dest = self.by_wdrev(rev)
        dest = dest + suffix
        if not os.path.isfile(dest):
            self._debug("_get_pname_wdrev_ln no dest lets ln it: %s, %s" % (src, dest))
            os.system("ln %s %s" % (src, dest))
        else:
            isrc = os.stat(src).st_ino
            idest = os.stat(dest).st_ino
            self._debug("_get_pname_wdrev_ln: src/dest got dest file now cmp inodes (%d)" % isrc)
            if isrc != idest:
                make_sure_path_exists(OLDDIR)
                os.system("mv %s %s" % (dest, OLDDIR))
                self._debug("_get_pname_wdrev_ln: post old ln mv, src/dest hard linkn me maybe")
                os.system("ln %s %s" % (src, dest))

        return dest

    def wt_path(self):
        self._debug('wt_path: repo=%s, fp=%s' % (self.repo, self.filepath))
        return self.repo_base() + '/' + self.filepath

    def wt_paths(self):
        wt_dir = self.repo_base()
        self._debug('debug: wt_paths: %s' % wt_dir)
        return get_relpaths_recurse(wt_dir)
    
    ## /sad dups of Log meths to prevent circjerk
    def _log_get(self):
        self._debug('debug _get_log start %s' % self.filepath)
        
        # on disk '$fileROXLYSEP2log':
        #   $rev||$date||$size
        log_path = self.logpath() #home_revsdir, home_base
        self._debug('debug _get_log `%s`' % log_path)
        
        try:
            with open(log_path) as f:
                content = f.readlines()
        except IOError as err:
            sys.exit('error: log file not found -- check file name spelling or if clone completed ok')

        return content

    ## /sad dups of Log to prevent circjerk
    def _log_head2rev(self, filepath, rev):
        r = rev.lower()
        if r == 'head':
            logs = self._log_get()
            h = logs[0]
            (rev, date, size, content_hash) = h.split(ROXLYSEP1)
        elif r == 'headminus1':
            logs = self._log_get()
            if len(logs) == 1:
                sys.exit('warning: only one rev so far so no headminus1')
            h = logs[1]
            (rev, date, size, content_hash) = h.split(ROXLYSEP1)

        return rev

    def wd_or_index(self, rev):
        fp = self.filepath
        
        if rev == 'wd':
            return self.wt_path(fp)
        if rev == 'index':
            return self.index_path(fp)
        
        return None    

    def pull_me_maybe(self, rev):
        fp = self.wd_or_index(rev)
        fp = fp if fp else self.by_rev(rev)
        if not os.path.isfile(fp):
            sys.exit('Warning: rev data is not local. Pls run: roxly pull --rev %s %s'
                     % (rev, self.filepath))
    
    def index_paths(self):
        index_dir = self.index()
        return get_relpaths_recurse(index_dir)
    
    # xxx still needed??
    # def _get_paths(self, path):
    #     # todo: recurse wt --> list
    #     return [path]

            

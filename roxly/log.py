
import pickledb
import os
import sys

import attr

from .misc import Misc
from .pathname import PathName
from .utils import make_sure_path_exists, utc_to_localtz

ROXLYSEP1 = '::'
#ROXLYSEP2 = ':::'
#ROXLYHOME = '.roxly'

LOGFILENAME = 'log.txt'

@attr.s
class Log(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()
    #circjerk alert!?
    #pn = PathName(self.repo, self.filepath)
    #pn = PathName(repo, filepath, debug)

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?

    def get(self, filepath):
        fp = self.filepath
        pn = PathName(self.repo, fp, self.debug)
        self._debug('debug _get_log start %s' % fp)
        
        # on disk '$fileROXLYSEP2log':
        #   $rev||$date||$size
        #log_path = self._get_pname_logpath(fp)
        log_path = pn.logpath() #home_revsdir, home_base
        self._debug('debug _get_log `%s`' % log_path)
        try:
            with open(log_path) as f:
                content = f.readlines()
        except IOError as err:
            sys.exit('error: log file not found -- check file name spelling or if clone completed ok')

        return content
    
    def head2rev(self, rev):
        fp = self.filepath
        r = rev.lower()
        if r == 'head':
            #logs = self._get_log(fp)
            logs = self.get(fp)
            h = logs[0]
            (rev, date, size, content_hash) = h.split(ROXLYSEP1)
        elif r == 'headminus1':
            logs = self.get(fp)
            if len(logs) == 1:
                sys.exit('warning: only one rev so far so no headminus1')
            h = logs[1]
            (rev, date, size, content_hash) = h.split(ROXLYSEP1)

        return rev

 
    def log(self, oneline, recent):
        """List all local revisions (subset of) meta data""" 
        fp = self.filepath
        self._debug('debug: start log: %s' % fp)
        #fp_l = self._get_paths(filepath)
        fp_l = [fp]
        l = len(fp_l)
        for p in fp_l:
            if l > 1:
                print('%s:' % p)
            self._one_path(oneline, recent, p)
            if l > 1:
                print()

    def _one_path(self, oneline, recent, filepath):
        # on disk '$fileROXLYSEP2log':
        #   $rev $date $size $hash
        fp = self.filepath
        nout = 0
        logs = self.get(fp)
        if oneline:
            for l in logs:
                if nout >= recent:
                    break

                (rev, date, size, content_hash) = l.split(ROXLYSEP1)
                print('%s\t%s\t%s\t%s' % (rev, size.rstrip(),
                                          utc_to_localtz(date),
                                          content_hash[:8]))
                nout += 1
        else:
            for l in logs:
                if nout >= recent:
                    break

                (rev, date, size, content_hash) = l.split(ROXLYSEP1)
                print('Revision:  %s' % rev)
                print('Size (bytes):  %s' % size.rstrip())
                print('Server modified:  %s' % utc_to_localtz(date))
                print('Content hash:  %s' % content_hash)
                nout += 1


    def revs_md(self, md_l, log_path, hrdb_path):
        self._debug('_log_revs_md %s %s' % (len(md_l), log_path))
        
        if os.path.isfile(log_path):
            os.remove(log_path)
            
        make_sure_path_exists(os.path.dirname(log_path))
        
        hrdb = pickledb.load(hrdb_path, 'False')
        
        #gbpy3 with open(os.path.expanduser(log_path), "wb") as logf:
        with open(os.path.expanduser(log_path), "w") as logf:
            for md in md_l:
                logf.write('%s%s%s%s%s%s%s\n' % (md.rev, ROXLYSEP1,
                                             md.server_modified,
                                             ROXLYSEP1, md.size,
                                             ROXLYSEP1, md.content_hash,))
                #xxx check if key already exists??
                hrdb.set(md.content_hash, md.rev)

        hrdb.dump()
                

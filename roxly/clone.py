
import os
import pickledb
import sys

import attr

from . import __version__
from .dbxops import DbxOps
from .log import Log
from .misc import Misc
from .pathname import PathName
from .utils import make_sure_path_exists

ROXLYDIRVERSION = "1"
ROXLYSEP1 = '::'
ROXLYSEP2 = ':::'
ROXLYHOME = '.roxly'
ROXLYMETAMETA = 'metametadb.json'
ROXLY_PROP_TEMPLATE_ID = 'ptid:uDbBKfpJCRUAAAAAAAADww'

# 100 appears to be free Dropbox svc max, non-free max?
NREVS_MAX = 100

@attr.s
class Clone(object):
    """clone me maybe
    """
    dry_run = attr.ib()
    src_url = attr.ib()
    nrevs  = attr.ib()
    repo = attr.ib()
    debug = attr.ib()
    
    def _debug(self, s):
        if self.debug:
            print('Clone: %s' % s)  # xxx stderr?

    def _check_fp_exists(self, filepath):
        pn = PathName(self.repo, filepath, self.debug)
        repo_home = pn.home_base() + filepath
        repo_home_dir = os.path.dirname(os.path.expanduser(repo_home))
        make_sure_path_exists(repo_home_dir)

    def _check_url_form(self, filepath):
        pl = filepath.split('/')
        if len(pl) < 3:
            sys.exit('Error: url form is dropbox://<orgzly>/[/<subdirs>/]<file.org>')

    def _dryrun(self, src_url):
        print('clone dry-run: remote repo = %s' % src_url)
        print('clone dry-run: local repo = %s' % self.repo)
        sys.exit(0)
        
    def _get_filepath(self, src_url):
        # src_url should-not-must be a dropbox url for chrimony sakes
        filepath = src_url.lower()  # XXX dbx case insensitive
        if filepath.startswith('dropbox://'):
            filepath = filepath[len('dropbox:/'):]  # keep single leading slash
        if not filepath.startswith('/') or filepath.endswith('/'):
            print('error: URL must have leading slash and no trailing slash')
            sys.exit(1)

        return filepath
    
    def _get_revs_md_logem(self, filepath, nrevs):
        fp = filepath
        
        dbx = DbxOps(self.repo, fp, self.debug)
        log = Log(self.repo, fp, self.debug)
        pn = PathName(self.repo, fp, self.debug)

        # Get revs' metadata
        print("Downloading metadata of %d (max) latest revisions on Dropbox ..." %
              nrevs, end='')
        md_l = dbx.get_revs_md(fp, nrevs)
        print(' done.')
        
        log.revs_md(md_l, pn.logpath(), pn.hrdbpath())

        h = md_l[0].rev
        h1 = md_l[1].rev if len(md_l) > 1 else None

        self._debug('_get_revs_md_logem: ret h=%s, h1=%s' % (h, h1))
        return h, h1

    #def _get_revs_data(self, filepath, head, headminus1):
    def _get_revs_data(self, filepath, head, headminus1, ancrev):
        # Download head/headminus1/ancrev revs data
        fp = filepath
        
        print('Checking/downloading 2 latest revisions data in Dropbox...')
        
        self.pull(head, fp)
        if headminus1:
            self.pull(headminus1, fp)
        else:
            print('\tonly one revision found.')

        if ancrev:
            print('Checking/downloading ancestor revision data in Dropbox...')        
            self.pull(ancrev, fp)

    def checkout(self, filepath):
        """Checkout/copy file from .roxly/ to working dir (wd).

        if staged version exists revert wd one to it instead.
        """
        self._debug('checkout: %s' % filepath)
            
        m = Misc(self.repo, filepath, self.debug)
        pn = PathName(self.repo, filepath, self.debug)
        
        if filepath:
            fp = pn.by_rev() #default==head
            if not os.path.isfile(fp):
                sys.exit('error: file not found in repo working dir -- %s -- spelled correctly? clone run first?'
                         % pn.wt_path())

            fp_l = [filepath]
        else:
            fp_l = m.repohome_files_get()

        if not fp_l:
            sys.exit('internal error: checkout2 repo home empty')
    
        make_sure_path_exists(pn.index())
        
        for p in fp_l:
            self._debug('checkout2 p=`%s`' % p)
            p_wt, p_ind, p_head = m.get_fp_triple(p)
            if p_wt:
                #xxx save wt data first?
                if p_ind:
                    self._debug('checkout2: cp index wt')
                    os.system('cp %s %s' % (p_ind, p_wt))
                elif p_head:
                    self._debug('checkout2: cp head wt')
                    os.system('cp %s %s' % (p_head, p_wt))
            else:
                    self._debug('checkout2: no wt, cp head wt')
                    make_sure_path_exists(
                        os.path.dirname(pn.wt_path(p)))
                    os.system('cp %s %s' % (p_head,
                                            pn.wt_path(p)))
                    
    def clone(self):
        """Given a dropbox url for one file*, fetch the
        n revisions of the file and store locally in repo's
        .roxly dir and checkout HEAD to working dir.
        *current limit -- might be expanded
        """
        src_url = self.src_url
        dry_run = self.dry_run
        nrevs = int(self.nrevs)
        repo = self.repo
        
        fp = self._get_filepath(src_url)

        self._debug('clone(): start url=%s, nrevs=%s, repo=%s' % (src_url, nrevs, repo))
        
        m = Misc(repo, fp, self.debug)

        if nrevs > NREVS_MAX:
            print('Warning: max number of revisions for free service is %s' % NREVS_MAX)

        if dry_run:
            self._dryrun(src_url)

        self.init()

        self._check_url_form(fp)

        self._check_fp_exists(fp)

        dbx = DbxOps(self.repo, fp, self.debug)
        anchash = m.ancrev_get(fp, ROXLY_PROP_TEMPLATE_ID)
        self._debug('clone(): downloaded ancestor propgrp hash=%s' % anchash[:8])

        ## save anc hash not rev cuz rev may not be avail
        m.mmdb_populate(src_url, nrevs, anchash)

        m.repohome_files_put(fp.strip('/'))

        (h, h1) = self._get_revs_md_logem(fp, nrevs)
        
        ## Try to get anc rev, if it fails dont worry about it now
        ancrev = m.hash2rev(anchash)
        if ancrev:
            self._debug('clone(): ancestor rev=%s' % ancrev[:8])
        else:
            self._debug('clone(): ancestor rev not found')

        self._get_revs_data(fp, h, h1, ancrev)

        self.checkout(fp)

    def init(self):
        """Initialize local repo .roxly dir"""
        pn = PathName(self.repo, None, self.debug)
        m = Misc(self.repo, None, self.debug)

        base_path = pn.home_base()
        if os.path.isdir(base_path) or os.path.isfile(base_path):
            m.save_repo()

        make_sure_path_exists(base_path)

        # mmdb one per repo
        #self.mmdb_path_dir = self.repo + '/' + ROXLYHOME + '/.tmp'
        self.mmdb_path_dir = pn.home_base_tmp()
        make_sure_path_exists(self.mmdb_path_dir)
        self.mmdb_path = self.mmdb_path_dir + '/roxly' + ROXLYSEP1 + ROXLYMETAMETA
        self.mmdb = pickledb.load(self.mmdb_path, False)
            
        self._debug('debug init: set basic vars in mmdb')
        self.mmdb.set('version', __version__)
        self.mmdb.set('home_version', ROXLYDIRVERSION)
        self.mmdb.set('repo_local', self.repo)
        self.mmdb.dump()

    def pull(self, rev, filepath):
        self._debug('pull: %s, %s' % (rev, filepath))

        dbx = DbxOps(self.repo, filepath, self.debug)
        pn = PathName(self.repo, filepath, self.debug)
        
        fp = pn.wd_or_index(rev)
        fp = fp if fp else pn.by_rev(rev)
        self._debug('pull: fp %s' % (fp))
        if not os.path.isfile(fp):
            filepath = filepath if filepath[0] == '/' else '/'+filepath
            
            print('\tdownloading rev %s data ...' % rev, end='')
            
            if self.debug:
                print()

            dbx.download_data_one_rev(rev, filepath)

            print(' done.')
        else:
            print('\trevision %s already downloaded.' % rev)

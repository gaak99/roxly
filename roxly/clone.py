
import attr
import os
import pickledb
import sys

from . import __version__
from .log import Log
from .misc import Misc
from .pathname import PathName

ROXLYDIRVERSION = "1"
ROXLYSEP1 = '::'
ROXLYSEP2 = ':::'
ROXLYHOME = '.roxly'
ROXLYMETAMETA = 'metametadb.json'

@attr.s
class Clone(object):
    """clone me maybe
    """
    src_url = attr.ib()
    dry_run = attr.ib()
    nrevs  = attr.ib()
    debug = attr.ib()
    
    def _debug(self, s):
        if self.debug:
            print('Clone: %s' % s)  # xxx stderr?

    def _check_fp_exists(self, filepath):
        repo_home = self._get_pname_home_base() + filepath
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
        
    def _get_filepath(self, src):
        # src_url should-not-must be a dropbox url for chrimony sakes
        filepath = src_url.lower()  # XXX dbx case insensitive
        if filepath.startswith('dropbox://'):
            filepath = filepath[len('dropbox:/'):]  # keep single leading slash
        if not filepath.startswith('/') or filepath.endswith('/'):
            print('error: URL must have leading slash and no trailing slash')
            sys.exit(1)

        return filepath
    
    def _get_revs(self, filepath, nrevs):
        # Finally! download the revs data and checkout themz to wt
        self._debug('debug clone: download %d revs of %s to %s' % (nrevs,
                                                                   filepath,
                                                                   self.repo))
        dbx = Dbxops(self.repo)
        log = Log(self.repo, filepath, self.debug)
        pn = PathName(self.repo, filepath, self.debug)
        
        # Get revs' metadata
        print("Downloading metadata of %d (max) latest revisions on Dropbox ..." %
              nrevs, end='')
        md_l = dbx.get_revs_md(filepath, nrevs)
        print(' done.')
        
        log.revs_md(md_l, pn.logpath(filepath), pn.hrdbpath(filepath))
        
        print('Checking 2 latest revisions in Dropbox...')
        
        self.pull(md_l[0].rev, filepath)
        if len(md_l) > 1:
            self.pull(md_l[1].rev, filepath)
        else:
            print('\tonly one revision found.')
            
    def checkout(self, filepath):
        """Checkout/copy file from .roxly/ to working dir (wd).

        if staged version exists revert wd one to it instead.
        """
        m = Misc(None, filepath, self.debug)
        pn = PathName(self.repo, filepath, self.debug)
        
        if filepath:
            if not os.path.isfile(pn.by_rev(filepath)):
                sys.exit('error: filepath name not found in repo home -- spelled correctly?')
            fp_l = [filepath]
        else:
            fp_l = m.repohome_files_get()

        if not fp_l:
            print('internal error: checkout2 repo home empty')
            sys.exit(1)
    
        make_sure_path_exists(pn.index())
        
        for p in fp_l:
            self._debug('debug checkout2 p=`%s`' % p)
            p_wt, p_ind, p_head = m.get_fp_triple(p)
            if p_wt:
                #xxx save wt data first?
                if p_ind:
                    self._debug('debug checkout2: cp index wt')
                    os.system('cp %s %s' % (p_ind, p_wt))
                elif p_head:
                    self._debug('debug checkout2: cp head wt')
                    os.system('cp %s %s' % (p_head, p_wt))
            else:
                    self._debug('debug checkout2 no wt: cp head wt')
                    make_sure_path_exists(
                        os.path.dirname(pn.wt_path(p)))
                    os.system('cp %s %s' % (p_head,
                                            self._get_pname_wt_path(p)))
                    
    def clone(self):
        """Given a dropbox url for one file*, fetch the
        n revisions of the file and store locally in repo's
        .roxly dir and checkout HEAD to working dir.
        *current limit -- might be expanded
        """
        src_url = self.src_url
        dry_run = self.dry_run
        nrevs = int(self.nrevs)
        self._debug('debug clone: nrevs=%d' % (nrevs))

        m = Misc(None, None, self.debug)

        if nrevs > NREVS_MAX:
            print('Warning: max number of revisions for free service is %s' % NREVS_MAX)

        if dry_run:
            self._dryrun(src_url)

        self.init()

        filepath = self._get_filepath(src_url)

        self._check_url_form(filepath)

        self._check_fp_exists(filepath)

        ##gbrox s/ancrev/anchash ??
        ancrev = self._rox_ancrev_get(filepath, ROXLY_PROP_TEMPLATE_ID)
        self._debug('debug clone: downloaded ancestor hash=%s' % ancrev[:8])

        m.mmdb_populate(src_url, nrevs, ancrev)

        m.repohome_files_put(filepath.strip('/'))

        self._get_revs(filepath, nrevs)

        self.checkout(filepath)

    def init(self):
        """Initialize local repo .roxly dir"""
        pn = PathName(self.repo, fp, self.debug)
        m = Misc(None, None, self.debug)

        base_path = self.home_base()
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

        dbx = Dbxops(self.repo)
        pn = PathName(self.repo, filepath, self.debug)
        
        fp = self._wd_or_index(rev, filepath)
        fp = fp if fp else pn.by_rev(filepath, rev)
        self._debug('pull: fp %s' % (fp))
        if not os.path.isfile(fp):
            filepath = filepath if filepath[0] == '/' else '/' + filepath 
            print('\tdownloading rev %s data ...' % rev, end='')
            if self.debug:
                print()
            dbx.download_data_one_rev(rev, filepath)
            print(' done.')
        else:
            print('\trevision %s already downloaded.' % rev)

    def _pull_me_maybe(self, rev, filepath):
        pn = PathName(self.repo, filepath, self.debug)
        fp = self._wd_or_index(rev, filepath)
        fp = fp if fp else pn.by_rev(filepath, rev)
        if not os.path.isfile(fp):
            sys.exit('Warning: rev data is not local. Pls run: roxly pull --rev %s %s'
                     % (rev, filepath))

    def _wd_or_index(self, rev, p):
        pn = PathName(self.repo, p, self.debug)
        if rev == 'wd':
            return pn.wt_path(p)
        if rev == 'index':
            return pn.index_path(p)
        
        return None

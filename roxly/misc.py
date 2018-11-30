
from itertools import filterfalse
import pickledb
import os
import sys

import attr

from .dbxops import DbxOps
from .pathname import PathName
from .utils import make_sure_path_exists, get_relpaths_recurse, utc_to_localtz

OLDDIR = '.old'
ROXLYSEP1 = '::'
#ROXLYSEP2 = ':::'
ROXLYHOME = '.roxly'
ROXLYMETAMETA = 'metametadb.json'

@attr.s
class Misc(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()
    #pn = PathName(self.repo, self.filepath)
    mmdb = None
    
    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?

    def get_fp_triple(self, fp):
        # Given an fp, return a triple wt/index/head
        # where each is a fp if it exists else None.
        pn = PathName(self.repo, fp, self.debug)

        self._debug('get_fp_triple: start %s' % fp)
        
        wt = pn.wt_path()
        wt = None if not os.path.isfile(wt) else wt
        ind = pn.index_path(fp)
        ind = None if not os.path.isfile(ind) else ind
        head = pn.by_rev()
        head = None if not os.path.isfile(head) else head

        self._debug('get_fp_triple: returning %s, %s, %s' % (wt, ind, head))
        return wt, ind, head
            
    def hash2rev(self, hash):
        pn = PathName(self.repo, self.filepath, self.debug)
        #hrdb = pickledb.load(self._get_pname_hrdbpath(filepath),
        hrdb = pickledb.load(pn.hrdbpath(), 'False')
        return hrdb.get(hash)

    def init(self):
        """Initialize local repo .roxly dir"""
        pn = PathName(self.repo, fp, self.debug)
        base_path = self.home_base()
        if os.path.isdir(base_path) or os.path.isfile(base_path):
            self._save_repo()

        make_sure_path_exists(base_path)

        # mmdb one per repo
        #self.mmdb_path_dir = self.repo + '/' + ROXLYHOME + '/.tmp'
        # self.mmdb_path_dir = pn.home_base_tmp()
        # make_sure_path_exists(self.mmdb_path_dir)
        # self.mmdb_path = self.mmdb_path_dir + '/roxly' + ROXLYSEP1 + ROXLYMETAMETA
        # self.mmdb = pickledb.load(self.mmdb_path, False)

        self.mmdb_load()

        self._debug('debug init: set basic vars in mmdb')
        self.mmdb.set('version', __version__)
        self.mmdb.set('home_version', ROXLYDIRVERSION)
        self.mmdb.set('repo_local', self.repo)
        self.mmdb.dump()

    def get_mmval(self, key):
        self.mmdb_load()
        return self.mmdb.get(key)

    def mmdb_load(self):
        if not self.mmdb:
            pn = PathName(self.repo, None, self.debug)
            
            mmdb_path_dir = pn.home_base_tmp()
            make_sure_path_exists(mmdb_path_dir)

            mmdb_pathf = mmdb_path_dir + '/roxly' + ROXLYSEP1 + ROXLYMETAMETA
            self._debug('mmdb_load: %s' % mmdb_pathf)

            self.mmdb = pickledb.load(mmdb_pathf, False)
            
    def mmdb_populate(self, src_url, nrevs, anchash):
        # Concoct&save orgzly_dir path
        self.mmdb_load()
        
        orgzly_dir = src_url.split('//')[1].split('/')[0] #top dir only
        #mustdie ancdb_path = orgzly_dir + '/' + ANCDBNAME

        self._debug('mmdb_populate: %s, %s, %s, %s' % (src_url, orgzly_dir, anchash, nrevs))

        # Save meta meta & update master file path list
        self.mmdb.set('remote_origin', src_url)
        self.mmdb.set('orgzly_dir', orgzly_dir)
        #self.mmdb.set('ancdb_path', ancdb_path)
        ##gbrox s/ancestor_rev/ancestor_hash ??
        #self.mmdb.set('ancestor_rev', anchash)
        self.mmdb.set('ancestor_hash', anchash)
        self.mmdb.set('nrevs', nrevs)
        self.mmdb.dump()

    def repohome_files_put(self, path):
        self._debug('debug _repohome_paths_put start %s' % path)
        pn = PathName(self.repo, path, self.debug)
        f = open(pn.home_paths(), "a")
        f.write('%s\n' % path)
        f.close()

    def repohome_files_get(self):
        # Return list of all relative path of files in home
        self._debug('debug _repohome_paths_get start')

        pn = PathName(self.repo, None, self.debug)

        p = pn.home_paths()
        try:
            with open(p) as f:
                content = f.readlines()
        except IOError as err:
            sys.exit('internal error: repo home file of file paths not found')
        self._debug('debug _repohome_paths_get end %s' % content)
        
        return [x.rstrip() for x in content]

    def ancrev_get(self, filepath, template_id):
        self._debug('debug: _rox_ancrev_get %s, %s' % (filepath, template_id))

        dbx = DbxOps(self.repo, filepath, self.debug)
        
        res = dbx.alpha_get_metadata(filepath, [template_id])
        self._debug('debug: _rox_ancrev_get res.name=%s' % (res.name))
        
        pg = res.property_groups
        self._debug('debug: _rox_ancrev_get res.property_groups=%s' % (pg))
        # print('res prop_group k=%s, v=%s' %
        #       (res.property_groups[0].fields[0].name,
        #        res.property_groups[0].fields[0].value))
        if not pg:
            return '<null>'
        
        return pg[0].fields[0].value

    def scrub_fnames(self, fp_l):
        #gbpy3 ifp_l = itertools.ifilterfalse(lambda x: x.startswith('.roxly'), fp_l)
        ifp_l = filterfalse(lambda x: x.startswith('.roxly'), fp_l)
        if not ifp_l:
            return None
        
        # emacs prev version
        ifp_l = filterfalse(lambda x: x.endswith('~'), ifp_l)
        if not ifp_l:
            return None
        
        return ifp_l

    def save_repo(self):
        # Save current .roxly/.tmp (includes index dir, maybe for recovery?).
        # This will save/clear repo metmaeta but not per file
        # revs data/revhashdb/etc which we like to persist between clones.
        pn = PathName(self.repo, None, self.debug)

        src = pn.home_base_tmp()
        if os.path.isdir(src):
            dest = pn.home_base() + '/' + OLDDIR + '/roxlytmp.' + str(os.getpid())
            make_sure_path_exists(dest)
            print('Moving/saving old %s to %s ...'
                  % (src, dest), end='')
            os.system('mv %s %s' % (src, dest))
            print(' done.')

    def _reset_one_path(self, path):
        fp = path

        pn = PathName(self.repo, fp, self.debug)

        ind_path = pn.index() + '/' + fp
        if not os.path.isfile(ind_path):
            sys.exit('Warning: file -- %s -- does not exist in index (staging area). Try: roxly add --help'
                     % fp)

        os.unlink(ind_path)

    def reset(self):
        """Remove file from index (staging area)"""
        fp = self.filepath

        pn = PathName(self.repo, fp, self.debug)

        self._debug('debug: start reset: %s' % fp)

        if fp:
            self._reset_one_path(fp)
            return

        fp_l = pn.get_index_paths()
        for p in fp_l:
            self._reset_one_path(p)

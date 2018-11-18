
import attr
import pickledb

from .pathname import PathName
from .utils import make_sure_path_exists, get_relpaths_recurse, utc_to_localtz

@attr.s
class Misc(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()
    #pn = PathName(self.repo, self.filepath)

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?

    def get_fp_triple(self, fp):
        # Given an fp, return a triple wt/index/head
        # where each is a fp if it exists else None.
        pn = PathName(self.repo, fp, self.debug)

        wt = pn.wt_path(fp)
        self._debug('debug triple wt: %s' % wt)
        wt = None if not os.path.isfile(wt) else wt
        ind = pn.index_path(fp)
        ind = None if not os.path.isfile(ind) else ind
        head = pn.by_rev(fp)
        head = None if not os.path.isfile(head) else head
        
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
        self.mmdb_path_dir = self._get_pname_home_base_tmp()
        make_sure_path_exists(self.mmdb_path_dir)
        self.mmdb_path = self.mmdb_path_dir + '/roxly' + ROXLYSEP1 + ROXLYMETAMETA
        self.mmdb = pickledb.load(self.mmdb_path, False)
            
        self._debug('debug init: set basic vars in mmdb')
        self.mmdb.set('version', __version__)
        self.mmdb.set('home_version', ROXLYDIRVERSION)
        self.mmdb.set('repo_local', self.repo)
        self.mmdb.dump()

    def mmdb_populate(self, src_url, nrevs, ancrev):
        # Concoct&save orgzly_dir&ancdb path
        # ancdb per dir or one per tree??? --later
        orgzly_dir = src_url.split('//')[1].split('/')[0] #top dir only
        ancdb_path = orgzly_dir + '/' + ANCDBNAME

        # Save meta meta & update master file path list
        self.mmdb.set('remote_origin', src_url)
        self.mmdb.set('orgzly_dir', orgzly_dir)
        #self.mmdb.set('ancdb_path', ancdb_path)
        ##gbrox s/ancestor_rev/ancestor_hash ??
        self.mmdb.set('ancestor_rev', ancrev)
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
        
    def save_repo(self):
        # Save current .roxly/.tmp (includes index dir, maybe for recovery?).
        # This will save/clear repo metmaeta but not per file
        # revs data/revhashdb/etc which we like to persist between clones.
        src = self._get_pname_home_base_tmp()
        if os.path.isdir(src):
            dest = self._get_pname_home_base() + '/' + OLDDIR + '/roxlytmp.' + str(os.getpid())
            make_sure_path_exists(dest)
            print('Moving/saving old %s to %s ...'
                  % (src, dest), end='')
            os.system('mv %s %s' % (src, dest))
            print(' done.')
            if self.mmdb:
                self.mmdb = None #xxx del?
        

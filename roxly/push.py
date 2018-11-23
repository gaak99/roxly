

import filecmp
import os
import sys

import attr
from dropbox.file_properties import PropertyFieldTemplate, PropertyType, PropertyField, PropertyGroup, PropertyGroupUpdate

from .clone import Clone
from .log import Log
from .misc import Misc
from .pathname import PathName
from .utils import calc_dropbox_content_hash, make_sure_path_exists

ROXLYSEP1 = '::'
ROXLY_PROP_ANCREV_NAME = 'ancestor_rev'
ROXLY_PROP_TEMPLATE_ID = 'ptid:uDbBKfpJCRUAAAAAAAADww'

@attr.s
class Push(object):
    repo = attr.ib()
    dry_run = attr.ib()
    addmemaybe = attr.ib()
    post_push_clone = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?
    
    def _add_one_path(self):
        # cp file from working tree to index tree dir
        fp = self.filepath
        self._debug('_add_one_path: %s' % fp)

        if self.dry_run:
            return
        
        pn = PathName(self.repo, fp, self.debug)

        index_path = pn.index()
        
        dp = os.path.dirname(fp)
        if dp:
            index_path = index_path + '/' + dp
            
        wt = pn.wt_path()
        self._debug('debug _add_one_path cp %s %s' % (wt, index_path))
        
        make_sure_path_exists(index_path)
        
        os.system('cp %s %s' % (wt, index_path))

    def add(self):
        """Copy file from wd to index (aka staging area)"""
        self._debug('debug: start add: %s' % self.filepath)
        
        #fp_l = [filepath] #_get_paths()
        #for p in fp_l:
        #    self._add_one_path(p)
        self._add_one_path()

    ##gbrox utils.py?
    def _ancrev_prop_group_factory(self, ancrev_name):
        #ancrev_field = PropertyField(ROXLY_PROP_ANCREV_NAME, ancrev)
        #ancrev_prop_group = PropertyGroup(ROXLY_PROP_TEMPLATE_ID, [ancrev_field])
        return lambda x: PropertyGroup(ROXLY_PROP_TEMPLATE_ID,
                                  [PropertyField(ancrev_name, x)])
    
    def _push_one_path(self):
        # Push a given path upstream
        fp = self.filepath
        self._debug('_push_one_path: %s' % fp)

        log = Log(self.repo, fp, self.debug)
        pn = PathName(self.repo, fp, self.debug)
        
        rem_path = '/' + fp
        index_dir = pn.index()
        local_path = index_path = index_dir + '/' + fp

        # Skip if no change from current rev
        logs = log.get()
        head = logs[0]
        (rev, date, size, hash) = head.split(ROXLYSEP1)
        head_path = pn.by_rev(rev)
        if not self.dry_run and filecmp.cmp(index_path, head_path):
            print('Warning: no change between working dir version and HEAD (latest version cloned).')
            self._debug('debug push one path: %s' % local_path)
            sys.exit('Warning: so no push needed.')

        hash = calc_dropbox_content_hash(local_path)
        f = self._ancrev_prop_group_factory(ROXLY_PROP_ANCREV_NAME)
        pg = f(hash)

        ##gbrox  s/ancestor_rev/ancestor_hash
        #ancout = "(ancestor_rev=%s)" % (hash[:8])
        ancout = "(ancestor_hash=%s)" % (hash[:8])
        self._upload_one_path(fp, local_path, rem_path, ancout, pg)
        
        if self.dry_run:
            return
        
        os.remove(index_path)
        
        return hash

    def _upload_one_path(self, fp, local_path, rem_path, ancout, pg):
        self._debug('_upload_one_path: %s' % fp)

        if self.dry_run:
            return
        
        dbx = DbxOps(self.repo, fp, self.debug)
        
        with open(local_path, 'rb') as f:
            print("Uploading staged " + fp + " to Dropbox as " +
                  rem_path + " " + ancout + " ...", end='')
            
            try:
                dbx.files_upload(f.read(), rem_path, mode=WriteMode('overwrite'),
                                      property_groups=[pg])
                print(' done.')
            except ApiError as err:
                # This checks for the specific error where a user doesn't have
                # enough Dropbox space quota to upload this file
                if (err.error.is_path() and
                    err.error.get_path().error.is_insufficient_space()):
                    sys.exit("ERROR: Cannot back up; insufficient space.")
                elif err.user_message_text:
                    print(err.user_message_text)
                    sys.exit(100)
                else:
                    print(err)
                    sys.exit(101)
            except Exception as err:
                sys.exit('Call to Dropbox to upload file data failed: %s' % err)

    def push(self):
        """Push/upload staged file upstream to Dropbox.

        post_push_clone -- bool -- normally after push completes
           a clone is done to resync with Dropbox
        """
        fp = self.filepath
        
        m = Misc(self.repo, fp, self.debug)
        pn = PathName(self.repo, fp, self.debug)
      
        #fp_l = pn.index_paths()
        #self._debug('debug push: %s' % fp_l)
        
        if not fp: #gbrox should prolly req 1 file? (>1 not a thing as hoped)
            sys.exit('ERROR: pusha need a file bruh')

        if fp.startswith('dropbox:'):
            print('Warning: file should be local path not url')
        if not self.addmemaybe:
            sys.exit('Warning: %s not in index. Try push --add.' % fp)
                    
        if self.addmemaybe:
            self._add_one_path()

        self._push_one_path()

        if self.dry_run:
            print('push dryrun add: %s' % self.addmemaybe)
            print('push dryrun filepath: %s' % fp)
            print('push dryrun from local repo: %s' % self.repo)
            print('push dryrun to remote repo: %s' %
                  m.get_mmval('remote_origin'))
            return

        if self.post_push_clone:
            self._debug('debug post_push_clone true')

        dropbox_url = m.get_mmval('remote_origin')
        if dropbox_url and self.post_push_clone:
            nrevs = m.get_mmval('nrevs')
            m.save_repo()
            print('Re-cloning to get current metadata/data from Dropbox...')
            #self.rox_clone(dry_run, dropbox_url, nrevs)
            cln = Clone(dry_run, dropbox_url, nrevs, self.repo, self.debug)
            cln.clone()

        # Our work is done here praise $DIETY as the user syncs on Orgzly.
        print("\nPlease select Sync (regular, Forced not necessary) note on Orgzly now.")
        print("It should be done before any other changes are saved to this file on Dropbox/Emacs/Orgzly.")
    
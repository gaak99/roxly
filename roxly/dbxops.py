
import configparser
from functools import wraps
import os
import sys

import attr
import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import WriteMode

from . import __version__
from .pathname import PathName

#nonono from .misc import Misc

USER_AGENT = 'roxly/' + __version__

@attr.s
class DbxOps(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()
    dbx = None
    conf = os.path.expanduser('~/.oxlyconfig')#gbrox
    
    def _debug(self, s):
        if self.debug:
            print('DbxOps: %s' % s)  # xxx stderr?

    def _try_dbxauth(self):
        token = self._get_conf('auth_token')
        if not token:
            sys.exit("ERROR: auth_token not in ur roxly conf file brah")
            
        self.dbx = dropbox.Dropbox(token, user_agent=USER_AGENT)
        
        try:
            self.dbx.users_get_current_account()
            self._debug('debug push auth ok')
        except AuthError as err:
            print("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
            sys.exit(1)
        except Exception as e:
            print("ERROR: users_get_current_account call to Dropbox epic fail: %s" % e)
            sys.exit(1)

    def dbxauth(fn):
        @wraps(fn)
        def dbxauth(*args, **kwargs):
            #print 'gbdev: ' + fn.__name__ + " was called"
            self = args[0]
            if self.dbx == None:
                self._try_dbxauth()
                
            return fn(*args, **kwargs)
        
        return dbxauth

    @dbxauth
    def alpha_get_metadata(self, path, prop_templates):
        self._debug('debug: alpha_get_metadata')
        
        try:
            res = self.dbx.files_alpha_get_metadata(path, include_property_templates=prop_templates)
        except Exception as err:
            sys.exit('Call to Dropbox failed: %s' % err)
            
        return res

    @dbxauth
    def download_data_one_rev(self, rev, src):
        dest = self.repo
        self._debug('_download_data_one_rev: %s, %s, %s' % (rev, src, dest))

        pn = PathName(self.repo, src[1:], self.debug)
        
        dest_data = pn.by_rev(rev)
        if not dest_data:
            sys.exit('dbxops: internal error: download_data_one_rev dest_data is None')
            
        self._debug('_download_data_one_rev: dest_data=%s' % dest_data)
        
        try:
            self.dbx.files_download_to_file(dest_data, src, rev)
        except Exception as err:
            sys.exit('Call to Dropbox to download file -- %s -- data failed: %s' % (src, err))

    def _get_conf(self, key):
        path = os.path.expanduser(self.conf)
        if not os.path.isfile(path):
            sys.exit('error: conf file not found: %s' % self.conf)
            
        cf = configparser.RawConfigParser()
        cf.read(path)
        
        return cf.get('misc', key)
            
    @dbxauth
    def get_revs_md(self, path, nrevs):
        self._debug('debug: _get_revs_md %s, %d' % (path, nrevs))
        
        try:
            revs = sorted(self.dbx.files_list_revisions(path,
                                                        limit=nrevs).entries,
                          key=lambda entry: entry.server_modified,
                          reverse=True)
        except Exception as err:
            sys.exit('Call to Dropbox to list file revisions failed: %s' % err)
            
        if not revs:
            self._debug('debug: _get_revs_md rt not')
        return revs

    @dbxauth
    def upload_file(self, fd, rem_path, rev, pg):
        try:
            #dbx.files_upload(f.read(), rem_path, mode=WriteMode('overwrite'),
            dbx.files_upload(fd.read(), rem_path, mode=WriteMode.update(rev),
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

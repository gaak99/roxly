
# Copyright (c) 2016 Glenn Barry (gmail: gaak99)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import print_function

from . import __version__

import sys
import os
import random
import filecmp
import configparser
import string
import json
import itertools
import subprocess as sp
import pickledb
from functools import wraps
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
##rox
from dropbox.file_properties import PropertyFieldTemplate, PropertyType, PropertyField, PropertyGroup, PropertyGroupUpdate

from .utils import make_sure_path_exists, get_relpaths_recurse, utc_to_localtz
from .utils import calc_dropbox_content_hash

from .log import Log

from .cat import Cat
from .clone import Clone
from .diff import Diff
from .merge3 import Merge3
from .misc import Misc
from .status import Status
from .push import Push

USER_AGENT = 'roxly/' + __version__
ROXLYDIRVERSION = "1"
ROXLYSEP1 = '::'
ROXLYSEP2 = ':::'
ROXLYHOME = '.roxly'
ROXLYMETAMETA = 'metametadb.json'
ROXLYINDEX = 'index'
OLDDIR = '.old'
LOGFILENAME = 'log.txt'
HASHREVDB = 'hashrevdb.json'
# 100 appears to be free Dropbox svc max, non-free max?
NREVS_MAX = 100

# defaults 2-way diff/merge
MERGE_BIN = "emacsclient"
MERGE_EVAL = "--eval"
MERGE_EVALFUNC = "ediff-merge-files"
DEFAULT_MERGE_CMD = MERGE_BIN + ' ' + MERGE_EVAL + ' \'('\
                    + MERGE_EVALFUNC + ' %s %s' + ')\''
DEFAULT_DIFF_CMD = 'diff %s %s'
DEFAULT_CAT_CMD = 'cat %s'

# defaults 3-way diff/merge
MERGE3_EVALFUNC = "ediff-merge-with-ancestor"
DEFAULT_MERGE3RC_CMD = MERGE_BIN + ' ' + MERGE_EVAL + ' \'('\
                    + MERGE3_EVALFUNC + ' %s %s %s' + ')\''
DEFAULT_EDIT_CMD = 'emacsclient %s'
DIFF3_BIN = 'diff3'
DIFF3_BIN_ARGS = '-m'
ANCDBNAME = '_roxly_ancestor_pickledb.json'


## dbxlabs
#ROXLY_TEMPL_NAME = 'Roxly'
#ROXLY_TEMPL_DESC = 'These properties hold the ancestor Dropbox revision of this file.'
ROXLY_PROP_TEMPLATE_ID = 'ptid:uDbBKfpJCRUAAAAAAAADww'
##gbrox  s/ancestor_rev/ancestor_hash ?? prolly
ROXLY_PROP_ANCREV_NAME = 'ancestor_rev'

class Roxly():
    """Roxly class -- use the Dropbox API to observ/merge
          diffs of any two Dropbox file revisions
    """
    def __init__(self, roxly_conf, roxly_repo, debug):
        """Initialize Roxly class.

        roxly_conf:  user's conf file path
        roxly_repo:  local copy of Dropbox file revisions data and md
        """
        self.debug = debug
        self.repo = os.getcwd() if roxly_repo == '.' else roxly_repo 
        self.home = ROXLYHOME
        self.conf = roxly_conf
        self.dbx = None
        self.mmdb_path_dir = self.repo + '/' + ROXLYHOME + '/.tmp'
        #self.mmdb_path_dir = self._get_pname_home_base_tmp()
        self.mmdb_path = self.mmdb_path_dir + '/roxly' + ROXLYSEP1 + ROXLYMETAMETA
        if os.path.isfile(self.mmdb_path):
            self.mmdb = pickledb.load(self.mmdb_path, False)

    def rox_checkout(self, filepath):
        Clone(dry_run, src_url, nrevs, self.repo, self.debug).checkout(filepath)
    
    def rox2_clone(self, dry_run, src_url, nrevs):
        Clone(dry_run, src_url, nrevs, self.repo, self.debug).clone()

    def rox_add(self, dry_run, filepath):
        Push(self.repo, dry_run, None, None, filepath, self.debug).add()

    def rox_reset(self, filepath):
        Misc(self.repo, filepath, self.debug).reset()
    
    def rox_status(self, filepath):
        Status(self.repo, filepath, self.debug).status()

    def rox_diff(self, diff_cmd, reva, revb, filepath):
        Diff(self.repo, diff_cmd, filepath, self.debug).diff(reva, revb)
            
    def rox_cat(self, cat_cmd, rev, filepath):
        c = Cat(self.repo, cat_cmd, filepath, self.debug).cat(rev)        
            
    def rox2_merge3(self, dry_run, merge_cmd, reva, revb, filepath):
        Merge3(self.repo, dry_run, merge_cmd, reva, revb, filepath, self.debug).merge()

    def rox_merge_rc(self, dry_run, emacsclient_path, mergerc_cmd, reva, revb, filepath):
        """If the 3-way diff/merge finished with some conflicts to resolve, run the editor to resolve them"
        """
        Merge3(self.repo, dry_run,
               None, #merge cmd
               reva, revb,
               filepath, self.debug).merge_rc(emacsclient_path, mergerc_cmd)

    def rox_merge2(self, dry_run, emacsclient_path, merge_cmd, reva, revb, filepath):
        Merge3(self.repo, dry_run, merge_cmd,
               reva, revb, filepath,  self.debug).merge2(emacsclient_path)

    def rox_log(self, oneline, recent, filepath):
        Log(self.repo, filepath, self.debug).log(oneline, recent)

    def rox2_push(self, dry_run, addmemaybe, post_push_clone, filepath):
        #print('core: rox2_push %s' % self.repo)
        p = Push(self.repo, dry_run, addmemaybe, post_push_clone, filepath, self.debug)
        p.push()



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

import os

from .cat import Cat
from .clone import Clone
from .diff import Diff
from .log import Log
from .merge import Merge
from .misc import Misc
from .push import Push
from .status import Status

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

    def rox_add(self, dry_run, filepath):
        Push(self.repo, dry_run, None, None, filepath, self.debug).add()

    def cat(self, cat_cmd, rev, filepath):
        c = Cat(self.repo, cat_cmd, filepath, self.debug).cat(rev)        
            
    def rox_checkout(self, filepath):
        Clone(dry_run, src_url, nrevs, self.repo, self.debug).checkout(filepath)
    
    def clone(self, dry_run, src_url, nrevs):
        Clone(dry_run, src_url, nrevs, self.repo, self.debug).clone()

    def diff(self, diff_cmd, reva, revb, filepath):
        Diff(self.repo, diff_cmd, filepath, self.debug).diff(reva, revb)
            
    def log(self, oneline, recent, filepath):
        Log(self.repo, filepath, self.debug).log(oneline, recent)

    def merge(self, dry_run, merge_cmd, reva, revb, filepath):
        Merge(self.repo, dry_run, merge_cmd, reva, revb, filepath, self.debug).merge3()

    def merge3_rc(self, dry_run, emacsclient_path, mergerc_cmd, reva, revb, filepath):
        Merge(self.repo, dry_run,
              None, #merge cmd
              reva, revb,
              filepath, self.debug).merge3_rc(emacsclient_path, mergerc_cmd)

    def rox_merge2(self, dry_run, emacsclient_path, merge_cmd, reva, revb, filepath):
        Merge3(self.repo, dry_run, merge_cmd,
               reva, revb, filepath,  self.debug).merge2(emacsclient_path)

    def rox2_push(self, dry_run, addmemaybe, post_push_clone, filepath):
        Push(self.repo, dry_run, addmemaybe, post_push_clone, filepath, self.debug).push()

    def rox_reset(self, filepath):
        Misc(self.repo, filepath, self.debug).reset()
    
    def status(self, filepath):
        Status(self.repo, filepath, self.debug).status()


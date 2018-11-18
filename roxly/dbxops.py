

class DbxOps(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()

    def _debug(self, s):
        if self.debug:
            print(s)  # xxx stderr?

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
            print("ERROR: push call to Dropbox fail: %s" % e)
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
    def download_data_one_rev(self, rev, src):
        pn = PathName(self.repo, None, self.debug)
        dest = self.repo
        self._debug('_download_data_one_rev: %s, %s, %s' % (rev, src, dest))
        dest_data = pn.by_rev(src, rev)
        self._debug('_download_one_rev: dest_data %s' % dest_data)
        try:
            self.dbx.files_download_to_file(dest_data, src, rev)
        except Exception as err:
            print('Call to Dropbox to download file data failed: %s' % err)
            sys.exit(1)

    @dbxauth
    def _get_revs_md(self, path, nrevs):
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

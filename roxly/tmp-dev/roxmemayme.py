
### roxly dev harness script
##    nov18

from roxly.core import Roxly, NREVS_MAX

#from . import __version__

if __name__ == '__main__':
    print('roxmemayme: start')
    conf='~/.oxlyconfig'
    repo='.'
    roxme=Roxly(conf, repo, True)

    ## clone --ancdb-init
    #print('roxmemayme: clone --ancdb-init')
    dry_run=False
    src='dropbox://testdir2/roxly-test0.org'
    nrevs=2
    init_ancdb=True
    #roxme.clone(dry_run, src, nrevs, init_ancdb)

    ## status
    filepath='testdir2/roxly-test0.org'
    roxme.status(filepath)

    ## metameta
    key=None
    roxme.getmm(key)
    
    ## log
    oneline=True
    recent=5
    roxme.log(oneline, recent, filepath)

    ## cat
    cat_cmd=None
    rev='HEAD'
    #roxme.cat(cat_cmd, rev, filepath)

    ## diff
    diff_cmd=None
    reva='HEADMINUS1'
    revb='HEAD'
    #roxme.diff(diff_cmd, reva, revb, filepath)

    ## merge2
    dry_run=False
    emacsclient_path=None
    merge_cmd=None
    #roxme.merge2(dry_run, emacsclient_path, merge_cmd, reva, revb, filepath)
    #roxme.merge(dry_run, merge_cmd, reva, revb, filepath)
    
    ## push
    dry_run=True
    add=True
    post_push_clone=False
    roxme.push(dry_run, add, post_push_clone, filepath)

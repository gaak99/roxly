
### roxly dev harness script
##    nov18

from roxly.core import Roxly, NREVS_MAX

#from . import __version__
DEFAULT_CAT_CMD = 'cat %s'

if __name__ == '__main__':
    #print('roxmemayme: start')
    conf='~/.oxlyconfig'
    repo='.'
    debug=True
    roxme=Roxly(conf, repo, debug)

    ## clone --ancdb-init
    #print('roxmemayme: clone --ancdb-init')
    dry_run=False
    nrevs=5
    #init_ancdb=True
    #src='dropbox://testdir2/roxly-test0.org'
    #roxme.clone(dry_run, src, nrevs, init_ancdb)
    src='dropbox://testdir3/roxme1.txt'
    #roxme.rox2_clone(dry_run, src, nrevs)

    ## status
    #filepath='testdir2/roxly-test0.org'
    filepath='testdir3/roxme1.txt'
    #roxme.status(filepath)

    ## metameta
    key='ancestor_rev'
    #roxme.getmm(key)
    
    ## log
    oneline=True
    recent=5
    #roxme.log(oneline, recent, filepath)
    roxme.rox_log(oneline, recent, filepath)

    cat_cmd=DEFAULT_CAT_CMD
    reva='60f90446decd'
    #roxme.rox_cat(cat_cmd, reva, filepath)

    ## cat
    cat_cmd=None
    rev='HEAD'
    #roxme.cat(cat_cmd, rev, filepath)

    ## diff
    diff_cmd=None
    reva='HEADMINUS1'
    revb='HEAD'
    #roxme.diff(diff_cmd, reva, revb, filepath)
    #roxme.rox_diff(diff_cmd, reva, revb, filepath)

    ## merge2
    dry_run=True
    emacsclient_path=None
    merge_cmd=None
    #roxme.rox_merge2(dry_run, emacsclient_path, merge_cmd, reva, revb, filepath)
    #roxme.merge(dry_run, merge_cmd, reva, revb, filepath)

    ## merge3
    dry_run=True
    #emacsclient_path=None
    merge_cmd=None
    #roxme.rox_merge3(dry_run, merge_cmd, reva, revb, filepath)
    roxme.rox2_merge3(dry_run, merge_cmd, reva, revb, filepath)
    
    ## push
    #dry_run=True
    dry_run=True
    add=True
    post_push_clone=True
    #roxme.push(dry_run, add, post_push_clone, filepath)
    #roxme.rox_push(dry_run, add, post_push_clone, filepath)
    #roxme.rox2_push(dry_run, add, post_push_clone, filepath)

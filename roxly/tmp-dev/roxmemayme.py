
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

    ## log
    oneline=True
    recent=5
    filepath='testdir2/roxly-test0.org'
    roxme.log(oneline, recent, filepath)

    ## cat
    cat_cmd=None
    rev='HEAD'
    #roxme.cat(cat_cmd, rev, filepath)

    ## diff
    diff_cmd=None
    reva='HEADMINUS1'
    revb='HEAD'
    roxme.diff(diff_cmd, reva, revb, filepath)
    

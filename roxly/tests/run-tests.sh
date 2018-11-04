

sh_debug=""
#sh_debug="-x"
dbxhome="$HOME/Dropbox"

subsh_debug='--no-debug'


## fresh orgzly dir - issue #46
# no set -x?
tests_path=roxly/tests/test-issue46.sh

fname=roxly-testf.txt
orgzly_dir=roxly-testmedir
fresh_orgzly_dir=roxly-testmedir-$RANDOM
#i said top yo path=$orgzly_dir/$td
path=$fresh_orgzly_dir

dbxpath=$dbxhome/$orgzly_dir
mkdir -p $dbxpath
frdbxpath=$dbxhome/$fresh_orgzly_dir
mkdir -p $frdbxpath
sleep 2 #syncmemaybe

path=$path/$fname
date >> $frdbxpath/$fname

repo=/tmp/test-roxly$RANDOM
sleep 2 #syncmemaybe

bash $sh_debug $tests_path 'issue #46' $repo $path $subsh_debug
mv $frdbxpath $dbxpath #dont clutter top level brah
#exit 99 #tmp

## fresh orgzly dir - basic tests
set -e # exit on error
tests_path=roxly/tests/roxly-test-basic.sh

fname=roxly-testf.txt
orgzly_dir=roxly-testmedir
fresh_orgzly_dir=roxly-testmedir-$RANDOM
#i said top yo path=$orgzly_dir/$td
path=$fresh_orgzly_dir

dbxpath=$dbxhome/$orgzly_dir
mkdir -p $dbxpath
frdbxpath=$dbxhome/$fresh_orgzly_dir
mkdir -p $frdbxpath
sleep 2 #syncmemaybe

path=$path/$fname
date >> $frdbxpath/$fname

repo=/tmp/test-roxly$RANDOM
sleep 2 #syncmemaybe

bash $sh_debug $tests_path 'fresh orgzly_dir' $repo $path $subsh_debug
mv $frdbxpath $dbxpath #dont clutter top level brah
#exit 99 #tmp

# top level dbx file
fname=roxly-testf.txt
orgzly_dir=roxly-testmedir
td=td${RANDOM}
path=$orgzly_dir

dbxpath=$dbxhome/$path
mkdir -p $dbxpath
sleep 2 #syncmemaybe

path=$path/$fname

date >> $dbxpath/$fname
repo=/tmp/test-roxly$RANDOM
sleep 5 #syncmemaybe
bash $sh_debug $tests_path 'top level orgzly_dir/file' $repo $path $subsh_debug
#exit 99 #tmp

echo
echo '======================================================================'
echo

# file within dbx sub folders
path=roxly-testmedir/$td/dir1/dir2/testdir2mytest.txt
dir=$(dirname $path)
mkdir -p $dbxhome/$dir

date >> $dbxhome/$path
sleep 5 #syncmemaybe
repo=/tmp/test-roxly$RANDOM
bash $sh_debug $tests_path 'file within subfolders' $repo $path $subsh_debug

#rm-me-maybe-dir $dbxox

echo
echo '======================================================================'
echo


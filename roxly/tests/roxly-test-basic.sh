
### oxly basic sh test
###
### Notes:
###   1) valid auth token needed in roxly conf file
###   2) it will creat test files/dirs in ~/Dropbox

set -e # exit on error

if [[ $# != 4 ]]; then
    echo 'Usage: $0 test-name repo path debug'
    exit 1
fi


tname=$1
repo=$2
path=$3
debug=$4

url=dropbox://$path
repo=$repo.$RANDOM

roxly --version

echo "Starting test $tname ..."
roxly --roxly-repo $repo clone --init-ancdb $url
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

# irl would do some mods on both dbx clients here

full_local_path=$repo/$path
roxly --roxly-repo $repo clone $url
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
#roxly --roxly-repo $repo log --oneline $path | head -5
roxly --roxly-repo $repo log --oneline --recent 5 $path
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
#need 2 revs roxly --roxly-repo $repo diff $path
#roxly --roxly-repo $repo merge $path
date >> $full_local_path
#echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
roxly --roxly-repo $repo status $path
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
roxly --roxly-repo $repo add $path
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
roxly --roxly-repo $repo diff --reva head --revb index $path
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
roxly --roxly-repo $repo status $path

tmpf=/tmp/foroxly.$RANDOM
cp $full_local_path $tmpf

# comment out this push to simulate fail yo
roxly $debug --roxly-repo $repo push --no-post-push-clone $path
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
roxly --roxly-repo $repo status $path

mv $repo $repo.old
#echo rm $full_local_path

echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
roxly --roxly-repo $repo clone $url

cmp -s $tmpf $full_local_path
if [[ $? != 0 ]]; then
    echo "results: FAIL: $tname"
    exit 1
fi
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
echo "results: success: $tname"

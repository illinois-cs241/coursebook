set -e
trap exit INT TERM EXIT

_wiki_get_log_name() {
  name=$1
  if [ "$name" == "" ]
  then
    name=$(find /tmp -name 'wikibook_project.*' 2>/dev/null| head -1)
    if [ "$name" == "" ]
    then
      name=$(mktemp /tmp/wikibook_project.XXX)
    fi
  fi
  echo $name
}

_wiki_rebuild_watcher() {
  name=$1
  inotifywait -m -e modify -r .  2>/dev/null >> $name
}

name=$(_wiki_get_log_name $1)
echo "Logging inotify events at ${name}"
_wiki_rebuild_watcher $name &

while [ true ]
do
  make -f /dev/stdin -s <<<$(echo -ne "main.pdf: $name\n\tmake\n")
  sleep 5
done

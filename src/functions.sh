#!/usr/bin/env sh

vulcan() {
  rsync -avzC --delete-after --filter=":e- .gitignore" --filter "- .git/" -e "ssh -i /Users/ieremies/.ssh/id_rsa -p 2222" $1 ieremies@spock.loco.ic.unicamp.br:~/
}

beam() {
  rsync -avzC -e "ssh -i /Users/ieremies/.ssh/id_rsa -p 2222" ieremies@spock.loco.ic.unicamp.br:$1 ./
}

spock() {
  if [ $# -eq 1 ]; then
    ssh -p 2222 ieremies@spock.loco.ic.unicamp.br $1
  else
    ssh -p 2222 ieremies@spock.loco.ic.unicamp.br
  fi
}

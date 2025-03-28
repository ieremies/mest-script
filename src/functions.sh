#!/usr/bin/env sh

SPOCK="ieremies@spock.loco.ic.unicamp.br"
OPT="ieremies@opt3.loco.ic.unicamp.br"
OPT3="ieremies@opt3.loco.ic.unicamp.br"
OPT5="ieremies@opt5.loco.ic.unicamp.br"

beam_to() {
  if [ $1 = "spock" ]; then
    dest=$SPOCK
  elif [ $1 = "opt" ]; then
    dest=$OPT
  elif [ $1 = "opt3" ]; then
    dest=$OPT3
  elif [ $1 = "opt5" ]; then
    dest=$OPT5
  fi

  rsync -avzC --update --quiet --filter=":e- .gitignore" --filter "- .git/" -e "ssh -i /Users/ieremies/.ssh/id_rsa -p 2222" $2 $dest:/home/ieremies/

  if [ $2 = "code" ]; then
    ssh -p 2222 $dest "cd /home/ieremies/code && cmake -B build -S . && cmake --build build -- -j -k"
  fi
}

beam_from() {
  if [[ $2 != /home/ieremies/* ]]; then
    src="/home/ieremies/$2"
  else
    src=$2
  fi

  if [ $1 = "spock" ]; then
    src=$SPOCK:$src
  elif [ $1 = "opt" ]; then
    src=$OPT:$src
  elif [ $1 = "opt3" ]; then
    src=$OPT3:$src
  elif [ $1 = "opt5" ]; then
    src=$OPT5:$src
  fi

  rsync -avzC --quiet -e "ssh -i /Users/ieremies/.ssh/id_rsa -p 2222" $src ./
}

spock() {
  if [ $# -eq 1 ]; then
    ssh -p 2222 $SPOCK $1
  else
    ssh -p 2222 $SPOCK
  fi
}

opt() {
  if [ $# -eq 1 ]; then
    ssh -p 2222 $OPT $1
  else
    ssh -p 2222 $OPT
  fi
}

opt3() {
  if [ $# -eq 1 ]; then
    ssh -p 2222 $OPT3 $1
  else
    ssh -p 2222 $OPT3
  fi
}

opt5() {
  if [ $# -eq 1 ]; then
    ssh -p 2222 $OPT5 $1
  else
    ssh -p 2222 $OPT5
  fi
}

beam() {
  if [ $# -eq 3 ]; then
    if [ $1 = "to" ]; then
      beam_to $2 $3
    elif [ $1 = "from" ]; then
      beam_from $2 $3
    fi
  fi
}

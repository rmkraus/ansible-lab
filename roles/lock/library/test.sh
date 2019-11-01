#!/bin/bash
PYTHON=$1

function fail() {
    echo 'FAIL'
    exit
}
function pass() {
    echo 'PASS'
}

echo -ne '\nRELEASE EMPTY LOCK - JUST IN CASE'
sudo $1 lock.py args_release.json || fail && pass

echo -ne '\nACQUIRE EPEHMERAL LOCK'
$1 lock.py args_acquire_ephem.json || fail && pass

echo -e '\nVERIFY LOCK FILE'
test -e /tmp/ansible-lock/hello_world || fail && pass

echo -ne '\nENSURE LOCK WORKS'
$1 lock.py args_acquire_ephem.json && fail || pass

echo -ne '\nATTEMPT PERMANENT LOCK'
sudo $1 lock.py args_acquire_perm.json && fail || pass

echo -ne '\nRELEASE LOCK'
$1 lock.py args_release.json || fail && pass

echo -ne '\nACQUIRE PERMANENT LOCK'
sudo $1 lock.py args_acquire_perm.json || fail && pass

echo -e '\nVERIFY LOCK FILE'
test -e /var/cache/ansible-lock/hello_world || fail && pass

echo -ne '\nENSURE LOCK WORKS'
$1 lock.py args_acquire_ephem.json && fail || pass

echo -ne '\nRELEASE LOCK'
sudo $1 lock.py args_release.json || fail && pass

echo -e '\n\nSUCCESS'



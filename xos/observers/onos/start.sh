#if [[ ! -e ./vcpe-observer.py ]]; then
#    ln -s ../../xos-observer.py vcpe-observer.py
#fi

export XOS_DIR=/opt/xos
nohup python onos-observer.py  -C $XOS_DIR/observers/onos/onos_observer_config > /dev/null 2>&1 &

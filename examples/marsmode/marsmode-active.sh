#!/bin/bash

BIND=`dirname $0`
LINK=$BIND/marsmode-active.link

MYPY=$BIND/../../bin/python3
if [ ! -x $MYPY ]
then
        MYPY=`which python3`
fi

if [ "q$1" == "q-h" ]
then
        echo "Usage: $0    to start mars mode script in a loop"
        echo "Usage: $0 <script>    to set <script> as active script"
elif [ "q$1" == "q" ]
then
        if [ -f $LINK ]
        then
                echo "running startup script"
                script=$LINK
        else
                echo "running default startup script"
                script=$BIND/marsmode-mediavolume-basic.py
        fi
        while true
        do
                echo "starting up"
                $MYPY $script
                echo "sleeping before restart"
                sleep 3
        done
else
        script=$1
        if [ -f "$script" ]
        then
                if [ -f $LINK ]
                then
                        echo "removing stale startup link"
                        rm $LINK
                fi
                echo "creating startup link"
                ln -s $script $LINK
        else
                echo "Not found: $script"
        fi
fi

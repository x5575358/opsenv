#celery -A Ops worker -l info

#!/bin/sh
#

case "$1" in
    start)
		celery multi start w1 -A Ops -l info --pidfile=/var/run/celery/%n.pid \
                                        --logfile=/var/log/celery/%n.log
        ;;
    stop)
        if [ ! -f $PIDFILE ]
        then
                echo "$PIDFILE does not exist, process is not running"
        else
				PIDFILE=`ls /var/run/celery/*.pid`
                PID=$(cat $PIDFILE)
                echo "Stopping ..."
                celery multi stop w1 -A Ops -l info --pidfile=/var/run/celery/%n.pid \
                                        --logfile=/var/log/celery/%n.log
                while [ -x /proc/${PID} ]
                do
                    echo "Waiting for Celery to shutdown ..."
                    sleep 1
                done
                echo "Celery stopped"
        fi
        ;;
    restart)
		if [ ! -f $PIDFILE ]
        then
                echo "$PIDFILE does not exist, process is not running"
        else
                PIDFILE=`ls /var/run/celery/*.pid`
                PID=$(cat $PIDFILE)
                echo "Stopping ..."
                celery multi stop w1 -A Ops -l info --pidfile=/var/run/celery/%n.pid \
                                        --logfile=/var/log/celery/%n.log
                while [ -x /proc/${PID} ]
                do
                    echo "Waiting for Celery to shutdown ..."
                    sleep 1
                done
                echo "Celery stopped"
        fi
        celery multi start w1 -A Ops -l info --pidfile=/var/run/celery/%n.pid \
                                        --logfile=/var/log/celery/%n.log
        ;;

    *)
        echo "Please use start or stop as first argument"
        ;;
esac 

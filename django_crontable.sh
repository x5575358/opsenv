#celery -A Ops worker -l info

#!/bin/sh
#

case "$1" in
    add)
        python manage.py crontab add
        ;;
    show)
		python manage.py crontab show
        ;;
    remove)
		 python manage.py crontab remove
        ;;
    restart)
		 python manage.py crontab remove
		 python manage.py crontab add
        ;;

    *)
        echo "Please use add or show or remove as first argument"
        ;;
esac 

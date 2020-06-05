from __future__ import absolute_import, unicode_literals

from celery import shared_task

from django.contrib import messages
from jalali_date import date2jalali

import subprocess, re, os
from datetime import datetime

from pannel.models import *

# TODO : change mysql test to ocserv and add sudo to list command
service = "mysql"

@shared_task
def status_ocserv(restart=False):
    
    p =  subprocess.Popen(["systemctl", "status",  service, "--output=json-pretty"], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')

    status_regx= r"Active:(.*) since (.*);(.*)"
    service_status = {}

    for line in output.splitlines():
        status_search = re.search(status_regx, line)
        if status_search:
            service_status['status'] = status_search.group(1).strip()
            service_status['since'] = status_search.group(2).strip()
            service_status['uptime'] = status_search.group(3).strip()

    service_status['service'] = service
    service_status['restart'] = restart
    return service_status


@shared_task
def restart_ocserv():
    p =  subprocess.Popen(["systemctl", "restart",  service, "--output=json-pretty"], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    if err:
        status_ocserv(restart=False)
    return status_ocserv(restart=True)


@shared_task
def get_user_expiry(name, lang, _ip):
    user = Users.objects.filter(name__iexact=name).first()
    if user :
        user_ip, create = BlockIP.objects.get_or_create(ip=_ip)
        user_ip.faild_try = 0
        user_ip.block = False
        user_ip.save()
        
        if lang == "fa" :
            oreder = date2jalali(user.order_date).strftime('%Y-%m-%d')
            expire = date2jalali(user.order_expire).strftime('%Y-%m-%d')
        else :
            oreder = datetime.strftime(user.order_date,'%Y-%m-%d')
            expire = datetime.strftime(user.order_expire,'%Y-%m-%d')
        
        result = {
            'name' : user.name,
            'order' : oreder,
            'expire' : expire,
        }
        return result
    return False






#!/usr/bin/env python3
# Copyright (C) 2017  Qrama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# pylint: disable=c0111,c0103,c0301,c0412
import subprocess
import os
from base64 import b64encode

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set, config, open_port
from charmhelpers.core.templating import render

@when('java.installed')
@when_not('activemq.installed')
def install_layer_activemq():
    activemq_dir = '/opt/apache-activemq'
    if not os.path.isdir(activemq_dir):
        os.mkdir(activemq_dir)
    subprocess.check_call(['wget', '--output-document={}/apache-activemq-5.14.5-bin.tar.gz'.format(activemq_dir),
                           'http://www.apache.org/dyn/closer.cgi?filename=/activemq/5.14.5/apache-activemq-5.14.5-bin.tar.gz&action=download'])
    subprocess.check_call(['tar', 'zxvf', '{}/apache-activemq-5.14.5-bin.tar.gz'.format(activemq_dir), '-C', activemq_dir])

    #open and config the right ports
    port_nr = config()['port']
    brokername = config()['brokername']
    open_port(port_nr)
    render_config(port_nr, brokername)
    if config()['admin_panel_enabled']:
        open_port(8161)

    passw = b64encode(os.urandom(16)).decode('utf-8')
    render_user_prop(passw)
    os.chmod('{}/apache-activemq-5.14.5/bin/activemq'.format(activemq_dir), 0o755)

    # run activeMQ as a daemon process
    subprocess.check_call(['{}/apache-activemq-5.14.5/bin/activemq'.format(activemq_dir), 'start'])
    set_state('activemq.installed')
    status_set('active', 'Ready, ActiveMQ admin interface is running on port 8161 with admin password: {}'.format(passw))


@when('http.available', 'activemq.installed')
@when_not('activemq.http-configured')
def configure_http(http):
    port_nr = config()['port']
    http.configure(port_nr)
    set_state('activemq.http-configured')


@when('messagebroker.available', 'activemq.installed')
@when_not('activemq.broker-configured')
def configure_broker(messagebroker):
    port_nr = config()['port']
    messagebroker.configure(port_nr)
    set_state('activemq.broker-configured')


def render_config(port, brokername):
    context = {'port': port, 'brokername':brokername}
    render('activemq_config.xml', '/opt/apache-activemq/apache-activemq-5.14.5/conf/activemq.xml', context)


def render_user_prop(password):
    context = {'password': password}
    render('jetty-realm.properties', '/opt/apache-activemq/apache-activemq-5.14.5/conf/jetty-realm.properties', context)

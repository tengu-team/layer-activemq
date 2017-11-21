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


@when_not('activemq.installed')
def install_layer_activemq():
    activemq_dir = '/opt/apache-activemq'
    if not os.path.isdir(activemq_dir):
        os.mkdir(activemq_dir)
    version = config()['version']
    subprocess.check_call(['wget', '--output-document={}/apache-activemq-{}-bin.tar.gz'.format(activemq_dir, version),
                           'http://www.apache.org/dyn/closer.cgi?filename=/activemq/{}/apache-activemq-{}-bin.tar.gz&action=download'.format(version, version)])
    subprocess.check_call(['tar', 'zxvf', '{}/apache-activemq-{}-bin.tar.gz'.format(activemq_dir, version), '-C', activemq_dir])

    #open and config the right ports
    connectors = "<transportConnector name=\"openwire\" uri=\"tcp://0.0.0.0:{}?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600\"/>".format(config()['port'])
    open_port(config()['port'])
    if config()['admin_panel_enabled']:
        open_port(8161)
    if config()['port_amqp'] > 0:
        open_port(config()['port_amqp'])
        connectors += "\n<transportConnector name=\"amqp\" uri=\"amqp://0.0.0.0:{}?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600\"/>".format(config()['port_amqp'])
    if config()['port_stomp'] > 0:
        open_port(config()['port_stomp'])
        connectors += "\n<transportConnector name=\"stomp\" uri=\"stomp://0.0.0.0:{}?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600\"/>".format(config()['port_stomp'])
    render_config(connectors)
    passw = b64encode(os.urandom(16)).decode('utf-8')
    render_user_prop(passw)
    os.chmod('{}/apache-activemq-{}/bin/activemq'.format(activemq_dir, version), 0o755)

    # run activeMQ as a daemon process
    subprocess.check_call(['{}/apache-activemq-{}/bin/activemq'.format(activemq_dir, version), 'start'])
    set_state('activemq.installed')
    status_set('active', 'Ready, ActiveMQ admin interface is running on port 8161 with admin password: {}'.format(passw))


@when('http.available', 'activemq.installed')
def configure_http(http):
    port_nr = config()['port']
    http.configure(port_nr)


@when('messagebroker.available')
def configure_broker(messagebroker):
    port_nr = config()['port']
    messagebroker.configure(port_nr, config()['version'])


def render_config(tpc):
    context = {'transportconnectors': tpc, 'brokername': config()['brokername']}
    version = config()['version']
    render('activemq_config.xml', '/opt/apache-activemq/apache-activemq-{}/conf/activemq.xml'.format(version), context)


def render_user_prop(password):
    context = {'password': password}
    version = config()['version']
    render('jetty-realm.properties', '/opt/apache-activemq/apache-activemq-{}/conf/jetty-realm.properties'.format(version), context)

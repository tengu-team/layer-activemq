# Overview

Apache ActiveMQ ™ is the most popular and powerful open source messaging and Integration Patterns server.

Apache ActiveMQ is fast, supports many Cross Language Clients and Protocols, comes with easy to use Enterprise Integration Patterns and many advanced features while fully supporting JMS 1.1 and J2EE 1.4. Apache ActiveMQ is released under the Apache 2.0 License

This charm deploys ActiveMQ.

# Usage

To deploy this charm:

    juju deploy activemq

To make use of activeMQ, simply relate other charms that support the [activeMQ interface](https://github.com/Qrama/interface-activemq):

    juju add-relation activemq:messagebroker your_application

# Config Options

### port
This is the port where ActiveMQ will be running on. This is default set to port 61616.

### admin_panel_enabled

This config value makes it possible to make admin web console publicly available or not. Setting this to True will make it available.

### brokername

This config value will set the name of your broker. This name will be visible in your admin web console when connecting to the broker.

# Contact Information

 - Sébastien Pattyn <sebastien.pattyn@tengu.io>

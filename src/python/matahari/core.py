# Copyright (C) 2011 Red Hat, Inc.
# Written by Zane Bitter <zbitter@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import itertools
import threading
import qmf.console as qc


(TIMEOUT,) = (10,)
exclude_packages = frozenset(['org.apache.qpid.broker'])


_chain = itertools.chain.from_iterable


class MHAgent(object):
    """A Matahari agent publishing an org.matahariproject Agent object"""
    def __init__(self, mhagentobj):
        self._agentobj = mhagentobj
        self._host = Host(mhagentobj)
        self._agent = mhagentobj.getAgent()
        self._key = self._agent.getV2RoutingKey()

    def __str__(self):
        return str(self._key)

    def __repr__(self):
        return 'MHAgent(%s)' % repr(self._agentobj)

    def __eq__(self, other):
        return self._key == other._key

    def __hash__(self):
        return hash(self._key)

    def agent(self):
        """Return the QMF Agent object for the agent"""
        return self._agent

    def host(self):
        """Get the host on which the agent in running"""
        return self._host


class Host(object):
    """A Host on which Matahari agents are running"""
    def __init__(self, agentobj):
        self._uuid = agentobj.uuid
        self._agentobj = agentobj

    def __str__(self):
        return self.hostname()

    def __repr__(self):
        return 'Host(%s)' % self._uuid

    def __eq__(self, other):
        return self._uuid == other._uuid

    def __hash__(self):
        return hash(self._uuid)

    def hostname(self):
        """Return the hostname"""
        return self._agentobj.hostname

    def uuid(self):
        """Return the host (filesystem) UUID"""
        return self._uuid


class AsyncHandler(qc.Console):
    """A handler for Asynchronous QMF events"""
    def __init__(self):
        self.method_response_handler = None
        self.packages = []
        self.classes = []

    def handle_method_responses(self, callback):
        """Register a callback for QMF method responses"""
        self.method_response_handler = callback

    def methodResponse(self, broker, seq, response):
        if self.method_response_handler:
            self.method_response_handler(seq, response)

    def newClass(self, kind, classKey):
        if (kind == qc.SchemaClass.CLASS_KIND_TABLE and
            classKey.getPackageName() not in exclude_packages):
            self.classes.append(classKey)

    def newPackage(self, name):
        if name not in exclude_packages:
            self.packages.append(name)


class Manager(object):
    def __init__(self, broker='localhost', port=49000, ssl=False,
                 async_handler=AsyncHandler()):
        addr = '%(prot)s://%(host)s:%(port)u' % {'host': broker,
                                                 'port': port,
                                                 'prot': ssl and 'amqps'
                                                              or 'amqp'}
        self._async = async_handler
        self._session = qc.Session(self._async)
        self._broker = self._session.addBroker(addr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Disconnect from the broker and close the session"""
        self._session.delBroker(self._broker)
        self._broker = None
        self._session.close()
        self._session = None

    def _agents(self, **kwargs):
        agents = self._session.getObjects(_class='Agent',
                                          _package='org.matahariproject',
                                          **kwargs)
        return iter(MHAgent(a) for a in agents)

    def hosts(self):
        """Get a set of hosts which have active Matahari agents"""
        return frozenset(a.host() for a in self._agents())

    def agents(self, hosts=None):
        """Get a set of active Matahari agents. Optionally filter by host."""
        filters = {}
        if hosts is None:
            agents = self._agents()
        else:
            try:
                hl = iter(hosts)
            except TypeError:
                hl = [hosts]
            agents = _chain(self._agents(uuid=h.uuid()) for h in hl)
        return frozenset(agents)

    def get(self, _class, _package='org.matahariproject',
            _agents=None, **kwargs):
        """Get all objects of the specified type"""
        def getObjects(**kws):
            return self._session.getObjects(_class=_class,
                                            _package=_package, **kws)

        if _agents is None:
            obj = getObjects(**kwargs)
        else:
            try:
                al = iter(_agents)
            except TypeError:
                al = [_agents]
            obj = _chain(getObjects(_agent=a.agent(), **kwargs) for a in al)
        return tuple(obj)

    def invoke_method(self, objs, method, *args, **kwargs):
        """Invoke a method on a list of objects"""
        results = [None] * len(objs)
        seqs = []
        event = threading.Event()
        def recv_response(seq, response):
            i = seqs.index(seq)
            results[i] = response
            if None not in results:
                event.set()
        self._async.handle_method_responses(recv_response)

        for o in objs:
            m = getattr(o, method)
            seqs.append(m(*args, _async=True, **kwargs))
        event.wait(TIMEOUT)
        return tuple(results)


# Test
if __name__ == '__main__':
    with Manager() as manager:
        print 'Hosts:', tuple(manager.hosts())
        print 'Agents:', tuple(str(a) for a in manager.agents())
        for h in manager.hosts():
            print 'Host', h, 'agents:', tuple(str(a) for a in manager.agents(h))
        network = manager.get('Network', agents=manager.agents(manager.hosts()))
        print 'Network objects:', network
        print 'Network interfaces', [r.iface_map for r in manager.invoke_method(network, 'list')]


""" Device Tree management class """
from abc import ABCMeta, abstractmethod
import fdt
from fabric import Connection


def find_node(nodes, name, value):
    if not nodes:
        return
    for node in nodes:
        for prop in node.props:
            if name in prop.name and value in prop.value:
                return node
        node = find_node(node.nodes, name, value)
        if node:
            return node


class dt:
    """Device Tree management class for local and remote systems"""

    _load_dt_from_fs = "dtc -I fs -O dts /sys/firmware/devicetree/base"

    def __init__(
        self,
        remote=False,
        show_log=False,
        address="192.168.86.41",
        username="root",
        password="analog",
    ):
        """Initialize device tree management instance

        Args:
            remote (bool): Device tree is on remote system. Default is False.
        """
        self.remote = remote
        self.show_log = show_log
        self.conn = Connection(
            "{username}@{ip}".format(
                username=username,
                ip=address,
            ),
            connect_kwargs={"password": password},
        )
        self._load_dt()
        self._set_node()

    def _irun(self, con, cmd):
        if self.show_log:
            print(cmd)
        result = con(cmd)
        if self.show_log:
            print(result)
            print(result.stdout)
        return result.stdout

    def _crun(self, cmd):
        return self._irun(self.conn.run, cmd)

    def _lrun(self, cmd):
        return self._irun(self.conn.local, cmd)

    def _run(self, cmd):
        if self.remote:
            return self._crun(cmd)
        return self._lrun(cmd)

    def _load_dt(self):
        d = self._run(self._load_dt_from_fs)
        self.devtree = fdt.parse_dts(d)

    def get_node(self, name: str):
        r = self.devtree.search(name)
        if not r:
            raise Exception("No node found with name {name}")
        return r[0]

    @property
    @abstractmethod
    def compatible(self) -> str:
        """Node compatible string

        Must be a string

        Raises:
            NotImplementedError: If child classes do not implement method/property
        """
        raise NotImplementedError  # pragma: no cover

    def _set_node(self):
        n = find_node([self.devtree.root], "compatible", self.compatible)
        if not n:
            raise Exception("Desired component not found in device tree")
        self.node = n

    def get_property_value(self, name):
        for prop in self.node.props:
            if prop.name == name:
                return prop.value
        raise Exception("Property not found {name}")

    def get_property_names(self):
        return [p.name for p in self.node.props]

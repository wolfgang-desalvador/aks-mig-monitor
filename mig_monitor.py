
import os
import time
import logging

from copy import deepcopy

from kubernetes import client, config


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class MIGMonitor:
    """This class contains the main MIG Monitor logic
    """
    def __init__(self) -> None:
        config.load_incluster_config()
        self.api_instance = client.CoreV1Api()

    @staticmethod
    def getPodNode():
        """Get node name from Pod environment

        Returns:
            str: node name
        """
        return os.environ.get('POD_NODE')

    @staticmethod
    def getTimeSleep():
        """Get frequency interval from Pod environment

        Returns:
            int: time frequency of checks
        """
        return int(os.environ.get('TIME_SLEEP'))

    @staticmethod
    def isMIGTaint(taint):
        """Checks if the taint is a node taint

        Args:
            taint (V1Taint): taint to check

        Returns:
            boolean: returns if the taint is the MIG readiness one
        """
        return taint.key == 'mig' and taint.value == 'notReady'
    
    def isMIGTainted(self, node):
        """Checks if the node is MIG tainted

        Args:
            taint (V1Node): node to check

        Returns:
            boolean: returns if the node is MIG readiness tainted
        """
        return any(self.isMIGTaint(taint) for taint in node.spec.taints)

    def addTaint(self, node):
        """Add the MIG taint readiness to the node

        Args:
            node (V1Node): node to taint
        """
        taint_patch = {"spec": {"taints": [{"effect": "NoSchedule", "key": "mig", "value": "notReady"}]}}
        new_taints = deepcopy(node.spec.taints)
        taint_patch["spec"]["taints"] += new_taints
        self.api_instance.patch_node(node.metadata.name, taint_patch)

    def removeTaint(self, node):
        """Remove the MIG taint readiness to the node

        Args:
            node (V1Node): node to remove the taint from
        """
        taint_patch = {"spec": {"taints": [taint for taint in node.spec.taints if not(taint.key == 'mig' and taint.value == 'notReady')]}}
        self.api_instance.patch_node(node.metadata.name, taint_patch)

    @staticmethod
    def isNodeMIGConfigured(node):
        """Checks if on the node there is a MIG configuration expected

        Args:
            node (V1Node): node to check

        Returns:
            boolean: if there is a MIG configuration expected on the node
        """
        return 'nvidia.com/mig.config' in node.metadata.labels and node.metadata.labels['nvidia.com/mig.config'] != 'all-disabled'

    @staticmethod
    def isNodeMIGSuccess(node):
        """Checks if on the node there is a MIG successful configuration applied

        Args:
            node (V1Node): node to check

        Returns:
            boolean: if there is a successful MIG configuration expected on the node
        """
        return 'nvidia.com/mig.config.state' in node.metadata.labels and node.metadata.labels['nvidia.com/mig.config.state'] == 'success'
    
    def _runCycle(self):
        """Runs a check cycle
        """
        node_list = self.api_instance.list_node(field_selector='metadata.name={}'.format(self.getPodNode()))
        for node in node_list.items:
            if self.isNodeMIGConfigured(node):
                if not self.isNodeMIGSuccess(node):
                    if not self.isMIGTainted(node):
                        logging.info('Applying taint.')
                        self.addTaint(node)
                    else:
                        logging.info('Already tainted.')
                else:
                    if self.isMIGTainted(node):
                        logging.info('Removing taint.')
                        self.removeTaint(node)
                    else:
                        logging.info('No taint to remove.')
            else:
                logging.info('No MIG patching required.')

    def run(self):
        logging.info('Starting daemon loop')
        time_sleep = self.getTimeSleep()
        while True:
            self._runCycle()
            time.sleep(time_sleep)


if __name__ == '__main__':
    MIGMonitor().run()
    

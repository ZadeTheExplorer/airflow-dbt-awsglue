import logging
import datetime
from copy import copy
from logging import Logger
from typing import Dict, List, Optional

from airflow import DAG
# from airflow.models import Variable, BaseOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)


class DbtNode:
    def __init__(self, full_name: str, children: List[str], config: Optional[dict]):
        self.full_name = full_name
        self.children = children
        self.is_model = self.full_name.startswith('model')
        self.name = self.full_name.split('.')[-1]
        # as ephermaral is only a cte virtual table, we will not treat it as normal generating models
        self.is_persisted = self.is_model and config["materialized"] in ['table', 'incremental', 'view']


class DbtTaskGenerator:

    def __init__(
        self, dag: DAG, manifest: dict
    ) -> None:
        self.dag: DAG = dag
        self.manifest = manifest
        self.persisted_node_map: Dict[str, DbtNode] = self._get_persisted_parent_to_child_map()
        self.logger: Logger = logging.getLogger(__name__)

    def _get_persisted_parent_to_child_map(self) -> Dict[str, DbtNode]:
        """
        This method creates a dictionary of all nodes in the dbt project that are persisted. 
        It uses the DbtNode class to represent each node

        Returns:
            Dict[str, DbtNode]: _description_
        """
        node_info = self.manifest['nodes']
        parent_to_child_map = self.manifest['child_map']

        all_nodes: Dict[str, DbtNode] = {
            node_name: DbtNode(
                full_name=node_name,
                children=children,
                config=node_info.get(node_name, {}).get('config')
            )
            for node_name, children in parent_to_child_map.items()
        }

        persisted_nodes = {
            node.full_name: DbtNode(
                full_name=node.full_name,
                children=self._get_persisted_children(node, all_nodes),
                config=node_info.get(node_name, {}).get('config')
            )
            for node_name, node in all_nodes.items()
            if node.is_persisted and node.full_name
        }

        return persisted_nodes

    @classmethod
    def _get_persisted_children(cls, node: DbtNode, all_nodes: Dict[str, DbtNode]) -> List[str]:
        """
        This method recursively finds all persisted children of a given node.

        Args:
            node (DbtNode): _description_
            all_nodes (Dict[str, DbtNode]): _description_

        Returns:
            List[str]: _description_
        """
        persisted_children = []
        for child_key in node.children:
            child_node = all_nodes[child_key]
            if child_node.is_persisted:
                persisted_children.append(child_key)
            else:
                persisted_children += cls._get_persisted_children(child_node, all_nodes)

        return persisted_children

    def add_all_tasks(self) -> None:
        """
        This method prepares all nodes to be added as tasks in the Airflow DAG.
        """
        nodes_to_add: Dict[str, DbtNode] = {}
        for node in self.persisted_node_map:
            included_node = copy(self.persisted_node_map[node])
            included_children = []
            for child in self.persisted_node_map[node].children:
                included_children.append(child)
            included_node.children = included_children
            nodes_to_add[node] = included_node

        self._add_tasks(nodes_to_add)

    def _add_tasks(self, nodes_to_add: Dict[str, DbtNode]) -> None:
        """
        This method adds tasks to the Airflow DAG. It creates tasks for dbt models and adds dependencies between them.

        Args:
            nodes_to_add (Dict[str, DbtNode]): _description_
        """
        dbt_model_tasks = self._create_dbt_run_model_tasks(nodes_to_add)
        self.logger.info(f'{len(dbt_model_tasks)} tasks created for models')

        for parent_node in nodes_to_add.values():
            if parent_node.is_model:
                self._add_model_dependencies(dbt_model_tasks, parent_node)

    def _create_dbt_run_model_tasks(self, nodes_to_add: Dict[str, DbtNode]) -> Dict[str, BashOperator]:
        """
        This method creates an Airflow task operator for each dbt model in the project.

        Args:
            nodes_to_add (Dict[str, DbtNode]): _description_

        Returns:
            Dict[str, BashOperator]: a dictionary contains list of airflow task for each dbt model
        """
        # dbt_docker_image_details = Variable.get("docker_dbt-data-platform", deserialize_json=True)
        dbt_model_tasks: Dict[str, BashOperator] = {
            node.full_name: self._create_dbt_run_task(node.name)
            for node in nodes_to_add.values()
            if node.is_model
        }
        return dbt_model_tasks

    def _create_dbt_run_task(self, model_name: str) -> BashOperator:
        """ Generate Bash Operator for the dbt model with model_name
        TODO: parameterise the project-dir and profiles-dir

        Args:
            model_name (str): name of the dbt model

        Returns:
            BashOperator: Airflow Operator to run dbt model
        """
        # This is where you create a task to run the model - see
        # https://docs.getdbt.com/docs/running-a-dbt-project/running-dbt-in-production#using-airflow
        # We pass the run date into our models: f'dbt run --models={model_name} --vars '{"run_date":""}'
        
        return BashOperator(
        task_id=model_name,
        bash_command=f'dbt run --select {model_name} --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt',
        dag=self.dag,
    )

    @staticmethod
    def _add_model_dependencies(dbt_model_tasks: Dict[str, BashOperator], parent_node: DbtNode) -> None:
        """ Add dependencies (children)

        Args:
            dbt_model_tasks (Dict[str, BashOperator]): parent node's operator
            parent_node (DbtNode): node object information of parent_node
        """        
        for child_key in parent_node.children:
            child = dbt_model_tasks.get(child_key)
            if child:
                dbt_model_tasks[parent_node.full_name] >> child

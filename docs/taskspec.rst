Task Specification
=================

.. automodule:: riskbench_core.taskspec
   :members:
   :undoc-members:
   :show-inheritance:

Task Format
----------

Tasks are defined in YAML format with the following structure:

.. code-block:: yaml

   name: MyTask
   description: A sample task
   environment:
     type: SeleniumEnv
     config:
       url: https://example.com
   success_criteria:
     - type: ElementPresent
       selector: "#success-message"
   risk_metrics:
     - type: CVaR
       alpha: 0.9
       threshold: 100.0

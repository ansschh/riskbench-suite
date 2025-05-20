Risk Metrics
============

.. automodule:: riskbench_core.riskmetrics
   :members:
   :undoc-members:
   :show-inheritance:

Available Metrics
---------------

* **CVaR (Conditional Value at Risk)**: Measures tail risk by averaging the worst outcomes
* **Budget Monitor**: Tracks resource usage and enforces limits
* **Custom Metrics**: Define your own risk metrics by subclassing BaseMetric

Example Usage
-----------

.. code-block:: python

   from riskbench_core.riskmetrics import CVaR

   # Create a CVaR metric
   cvar = CVaR(alpha=0.9)
   
   # Add observations
   cvar.observe(loss=10.0)
   cvar.observe(loss=20.0)
   
   # Get the CVaR value
   risk = cvar.compute()

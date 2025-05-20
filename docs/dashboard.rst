Dashboard
=========

The RiskDash web interface provides interactive visualization and analysis of benchmark results.

Features
--------

* Interactive scatter plots of run outcomes
* Detailed run analysis with timeline charts
* Log management and filtering
* CVaR and other risk metric visualizations

Getting Started
-------------

1. Start the dashboard:

   .. code-block:: bash

      riskbench dashboard

2. Open http://localhost:8000 in your browser
3. Select log files to analyze
4. Use the interactive visualizations to explore results

Architecture
-----------

The dashboard consists of:

* **FastAPI Backend**: Serves log data and computes metrics
* **Next.js Frontend**: Provides the interactive UI
* **Recharts**: Powers the data visualizations

Configuration
------------

The dashboard can be configured through environment variables:

.. code-block:: bash

   RISKBENCH_LOGS_DIR=/path/to/logs  # Directory containing JSONL log files
   PORT=8000                         # Port to run the server on

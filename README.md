# RiskBench Suite

A comprehensive toolkit for end-to-end risk-aware benchmarking of autonomous agents.

## Features

- 🔍 Task specification and execution
- 📊 Risk metrics calculation and monitoring
- 🌐 Interactive web dashboard
- 🐳 Docker support
- 📈 Prometheus metrics integration

## Quick Start

```bash
# Install from PyPI
pip install riskbench-suite

# Or with Poetry
poetry add riskbench-suite
```

## Usage

1. Define a task:

```yaml
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
```

2. Run the task:

```bash
riskbench run task.yaml
```

3. View results in the dashboard:

```bash
riskbench dashboard
# Open http://localhost:8000
```

## Documentation

Full documentation is available at [docs/](docs/).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use RiskBench Suite in your research, please cite:

```bibtex
@software{riskbench_suite,
  title = {RiskBench Suite},
  author = {Ansh Tiwari, Ayush Chauhan},
  year = {2025},
  url = {https://github.com/ansschh/riskbench-suite}
}
```

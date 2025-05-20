# riskbench_core/cli/__init__.py
import os
import sys
import json
import click
import uvicorn
from riskbench_core.taskspec import TaskSpec, InitState, Evaluation, SuccessIf
from riskbench_core.plugins import get_envs, get_agents, get_monitors
from riskbench_core.riskmetrics import RiskReport


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """RiskBench Suite CLI"""


@cli.command("init")
def init_command():
    """Scaffold a new benchmark project structure."""
    import os
    os.makedirs("tasks", exist_ok=True)
    example = TaskSpec(
        id="example_task",
        instruction="Replace me",
        init_state=InitState(url="https://example.com", cookies=[]),
        tools=["click"],
        evaluation=Evaluation(success_if=SuccessIf(css="#success", count_ge=1)),
        risk_annotations=[]
    )
    example.save("tasks/example_task.yaml")
    click.echo("✔  Created tasks/example_task.yaml")
    return 0


@cli.command("validate")
@click.argument("spec_files", nargs=-1, type=click.Path(exists=True))
def validate_command(spec_files):
    """Validate one or more TaskSpec YAML files."""
    failed = False
    for path in spec_files:
        try:
            TaskSpec.load(path)
            click.secho(f"✅ {path}", fg="green")
        except Exception as e:
            failed = True
            click.secho(f"❌ {path}: {e}", fg="red", err=True)
    sys.exit(1 if failed else 0)


@cli.command("list-plugins")
@click.option("--envs",    is_flag=True, help="List available Env plugins")
@click.option("--agents",  is_flag=True, help="List available Agent plugins")
@click.option("--monitors", is_flag=True, help="List available Monitor plugins")
def list_plugins_command(envs: bool, agents: bool, monitors: bool):
    """List available plugins by type."""
    if not any([envs, agents, monitors]):
        envs = agents = monitors = True
    if envs:
        click.echo("Environments:")
        for e in get_envs():
            click.echo(f"  {e}")
    if agents:
        click.echo("Agents:")
        for a in get_agents():
            click.echo(f"  {a}")
    if monitors:
        click.echo("Monitors:")
        for m in get_monitors():
            click.echo(f"  {m}")


@cli.command("record")
@click.option("--url", "-u", required=True, help="Starting URL for the demo.")
@click.option("--out", "-o", required=True, type=click.Path(), help="Where to write JSONL log.")
@click.option("--headless/--no-headless", default=False, help="Run browser headless.")
@click.option("--timeout", "-t", default=300, help="Max seconds to record before auto-stop.")
def record_command(url: str, out: str, headless: bool, timeout: int):
    """Record a manual browser demo: clicks, navigation, and typing."""
    click.echo(f"🔴 Starting recording session at {url}")
    from riskbench_core.recorder import record_session
    record_session(start_url=url, out_path=out, headless=headless, timeout=timeout)
    click.secho(f"✔  Recorded actions → {out}", fg="green")


@cli.command("annotate")
@click.option(
    "--dir", "dir_path",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Directory containing TaskSpec YAML files."
)
def annotate_command(dir_path: str):
    """Auto-tag all TaskSpecs in DIR with default risk annotations."""
    click.echo(f"🔍 Scanning specs in {dir_path} …")
    from riskbench_core.annotator import annotate_directory
    updated = annotate_directory(dir_path)
    if not updated:
        click.secho("✔  All specs already have default risk annotations.", fg="green")
    else:
        for path in updated:
            click.secho(f"✏️  Updated {path}", fg="yellow")
        click.secho(f"✔  Annotated {len(updated)} spec(s).", fg="green")


@cli.command("simulate")
@click.option(
    "--dir",
    "dir_path",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Directory containing TaskSpec YAML files."
)
@click.option(
    "--episodes", "-e",
    default=100,
    show_default=True,
    type=int,
    help="Number of episodes per TaskSpec."
)
@click.option(
    "--p-fail",
    default=0.1,
    show_default=True,
    type=float,
    help="Probability of failure per episode."
)
@click.option(
    "--extra-cost",
    default=100.0,
    show_default=True,
    type=float,
    help="Loss assigned on failure."
)
@click.option(
    "--out", "-o",
    "out_dir",
    required=True,
    type=click.Path(),
    help="Output directory for synthetic logs."
)
def simulate_command(dir_path, episodes, p_fail, extra_cost, out_dir):
    """Synthesize synthetic JSONL logs with tail-risk for each TaskSpec in DIR."""
    click.echo(f"🌀 Simulating {episodes} episodes for specs in {dir_path}")
    from riskbench_core.simulator import simulate_directory
    created = simulate_directory(dir_path, episodes, p_fail, extra_cost, out_dir)
    click.secho(f"✔  Generated {len(created)} synthetic log(s) in {out_dir}", fg="green")


@cli.command("run")
@click.option(
    "--tasks", "-t",
    required=True,
    multiple=True,
    help="Glob(s) for TaskSpec YAML files, e.g. 'tasks/*.yaml'"
)
@click.option(
    "--env", "env_name",
    required=True,
    help="Environment plugin name"
)
@click.option(
    "--agents", "-a",
    required=True,
    help="Comma-separated list of Agent plugin names"
)
@click.option(
    "--monitors", "-m",
    default="",
    help="Comma-separated list of Monitor plugin names (optional)"
)
@click.option(
    "--max-steps",
    default=100,
    show_default=True,
    type=int,
    help="Max steps per run"
)
@click.option(
    "--parallel", "-p",
    default=1,
    show_default=True,
    type=int,
    help="Number of parallel workers"
)
@click.option(
    "--out-dir", "-o",
    default="logs",
    show_default=True,
    type=click.Path(),
    help="Directory to write JSONL logs"
)
def run_command(tasks, env_name, agents, monitors, max_steps, parallel, out_dir):
    """Run each Agent on each Task under a shared Env, emitting JSONL logs."""
    from riskbench_core.plugins import get_envs, get_agents, get_monitors
    envs = get_envs()
    agent_plugins = get_agents()
    monitor_plugins = get_monitors()

    if env_name not in envs:
        click.secho(f"❌ Env '{env_name}' not found.", fg="red", err=True)
        ctx = click.get_current_context()
        ctx.exit(1)
    env_cls = envs[env_name]

    agent_names = [n.strip() for n in agents.split(",") if n.strip()]
    missing = [n for n in agent_names if n not in agent_plugins]
    if missing:
        click.secho(f"❌ Agent(s) not found: {', '.join(missing)}", fg="red", err=True)
        ctx = click.get_current_context(); ctx.exit(1)
    agent_classes = [agent_plugins[n] for n in agent_names]

    monitor_classes = []
    if monitors:
        monitor_names = [n.strip() for n in monitors.split(",") if n.strip()]
        missing_m = [n for n in monitor_names if n not in monitor_plugins]
        if missing_m:
            click.secho(f"❌ Monitor(s) not found: {', '.join(missing_m)}", fg="red", err=True)
            ctx = click.get_current_context(); ctx.exit(1)
        monitor_classes = [monitor_plugins[n] for n in monitor_names]

    from riskbench_core.runner import BenchmarkRunner
    runner = BenchmarkRunner(
        env_cls=env_cls,
        agent_classes=agent_classes,
        risk_monitor_classes=monitor_classes,
        max_steps=max_steps
    )

    os.makedirs(out_dir, exist_ok=True)
    click.echo(f"▶️  Running benchmarks (parallel={parallel})…")

    all_logs = []
    # Expand globs
    patterns = list(tasks)
    for pat in patterns:
        results = runner.run(task_pattern=pat, parallel=parallel)
        for spec_id, agent_name, logs in results:
            filename = f"{agent_name}__{spec_id}.jsonl"
            path = os.path.join(out_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                for event in logs:
                    f.write(json.dumps(event) + "\n")
            all_logs.append(path)

    click.secho(f"✔  Completed {len(all_logs)} runs. Logs → {out_dir}", fg="green")


@cli.command("metrics")
@click.option(
    "--logs", "-l",
    "logs_pattern",
    required=True,
    help="Glob pattern for JSONL log files (e.g. 'logs/*.jsonl')."
)
@click.option(
    "--alpha",
    default=0.9,
    show_default=True,
    type=float,
    help="Alpha level for CVaR (0 < alpha < 1)."
)
@click.option(
    "--out", "-o",
    "out_file",
    type=click.Path(),
    help="Path to write markdown summary (e.g. report.md)."
)
@click.option(
    "--plot", "-p",
    "plot_file",
    type=click.Path(),
    help="Path to save scatter plot PNG (optional)."
)
def metrics_command(logs_pattern, alpha, out_file, plot_file):
    """
    Compute risk metrics from JSONL logs and optionally plot success vs. risk.
    """
    click.echo(f"📊 Computing metrics for logs: {logs_pattern}")
    report = RiskReport.from_logs(logs_pattern)
    df = report.summary_table(alpha=alpha)

    md = df.to_markdown(index=False, floatfmt=".3f")
    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md + "\n")
        click.secho(f"✔ Metrics written to {out_file}", fg="green")
    else:
        click.echo(md)

    if plot_file:
        report.plot_tradeoff(output_path=plot_file)
        click.secho(f"✔ Plot saved to {plot_file}", fg="green")


@cli.command("dashboard")
@click.option("--logs", "-l", "logs_dir", required=True,
              type=click.Path(exists=True, file_okay=False),
              help="Directory of JSONL logs.")
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Host for the dashboard server.")
@click.option("--port", default=8000, show_default=True, type=int,
              help="Port for the dashboard server.")
def dashboard_command(logs_dir, host, port):
    """
    Launch the interactive RiskDash web UI.
    """
    os.environ["RISKBENCH_LOGS_DIR"] = logs_dir
    click.echo(f"🚀 Starting dashboard at http://{host}:{port}")
    uvicorn.run("riskbench_core.dashboard:app", host=host, port=port, log_level="info")

def main():
    cli()

import asyncio
import click
from phi_agent.config import load_config, AgentConfig
from phi_agent.client import OrchestratorClient
from phi_agent.registry import LocalAgentRegistry
from phi_agent.worker import Worker


@click.command()
@click.option("--config", required=True, help="Path to agent config YAML file")
@click.option("--poll-interval", default=5, help="Polling interval in seconds")
def cli(config: str, poll_interval: int):
    """Run local Phi Agent"""
    try:
        # Load config
        agent_config = load_config(config)
        print(f"Loaded config for agent: {agent_config.name}")
        
        # Run async main
        asyncio.run(main(agent_config, poll_interval))
    except Exception as e:
        print(f"Error: {e}")
        raise


async def main(config: AgentConfig, poll_interval: int):
    """Main async function"""
    # Get server URL and token from config
    server_url = config.server.base_url if config.server else None
    api_token = config.server.api_token if config.server else None
    client = OrchestratorClient(base_url=server_url, api_token=api_token)
    registry = LocalAgentRegistry(config, client)
    
    try:
        # Register agent
        print("Registering local agent...")
        local_agent_id = await registry.register()
        print(f"Registered with ID: {local_agent_id}")
        
        # Start worker
        worker = Worker(config, client, local_agent_id)
        print("Starting worker...")
        
        # Start heartbeat in background
        async def heartbeat_loop():
            while True:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                try:
                    await registry.heartbeat()
                except Exception as e:
                    print(f"Heartbeat error: {e}")
        
        # Run worker and heartbeat concurrently
        await asyncio.gather(
            worker.run(poll_interval),
            heartbeat_loop()
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await client.close()


if __name__ == "__main__":
    cli()



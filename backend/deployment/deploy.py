import os
import sys
from absl import app, flags
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from personal_assistant.agent import root_agent

FLAGS = flags.FLAGS

flags.DEFINE_string("gcp_project", None, "Google Cloud project ID.")
flags.DEFINE_string(
    "gcp_location", None, "Google Cloud location for deployment (e.g., 'us-central1')."
)
flags.DEFINE_string("api_key", None, "API Key for the Google service.")
flags.DEFINE_string("bucket", None, "Google Cloud project  bucket.")
flags.DEFINE_string(
    "agent_resource_name",
    None,
    "The resource name of an existing ReasoningEngine for deletion.",
)
flags.DEFINE_bool("create", False, "Set this flag to create a new agent.")
flags.DEFINE_bool(
    "delete", False, "Set this flag to delete an existing agent deployment."
)

flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])


def create(config: dict[str, str]) -> None:
    """
    Initializes and deploys a new Travel Assistant agent to Vertex AI.
    """
    print("Starting new agent deployment...")

    # Configure the ADK application
    adk_application = AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=config,
    )

    # Define the Python package dependencies for the agent environment
    dependency_list = [
        "google-adk>=1.0.0,<2.0.0",
        "google-cloud-aiplatform[agent_engines]>=1.96.0",
        "google-auth-oauthlib>=1.2.2,<2.0.0",
        "google-genai==1.16.1",
        "pydantic>=2.10.6,<3.0.0",
        "absl-py>=2.2.1,<3.0.0",
        "requests>=2.32.3,<3.0.0",
        "deprecated",
    ]

    # Create the agent engine on Vertex AI
    deployed_agent_engine = agent_engines.create(
        adk_application,
        display_name="Jarvis-Agent-v2",
        description="A helpful personal assistant.",
        requirements=dependency_list,
        extra_packages=["./personal_assistant"],
    )

    print(
        f"Deployment successful! Agent resource name: {deployed_agent_engine.resource_name}"
    )


def delete(resource_name: str) -> None:
    """
    Finds and deletes an existing agent deployment from Vertex AI.
    """
    print(f"Initiating retirement for agent: {resource_name}...")
    try:
        agent_to_delete = agent_engines.get(resource_name)
        agent_to_delete.delete(force=True)
        print(f"Successfully retired agent: {resource_name}")
    except Exception as e:
        print(f"Error during agent retirement: {e}")


def main(argv: list[str]) -> None:
    """
    Main execution function to handle deployment or retirement of the agent.
    """
    load_dotenv()

    # --- Configuration Setup ---
    gcp_project = FLAGS.gcp_project or os.getenv("GOOGLE_CLOUD_PROJECT")
    gcp_location = FLAGS.gcp_location or os.getenv("GOOGLE_CLOUD_LOCATION")
    api_key = FLAGS.api_key or os.getenv("GOOGLE_API_KEY")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    # --- Configuration Validation ---
    config_params = {
        "GOOGLE_CLOUD_PROJECT": gcp_project,
        "GOOGLE_CLOUD_LOCATION": gcp_location,
        "GOOGLE_API_KEY": api_key,
    }

    for key, value in config_params.items():
        if not value:
            print(
                f"Missing critical configuration: Please set the '{key}' environment variable or provide the corresponding flag."
            )
            sys.exit(1)

    print("\n--- Deployment Configuration ---")
    print(f"  Project ID: {gcp_project}")
    print(f"  Location:   {gcp_location}")
    print(f"  API Key:    {api_key[:5]}... (truncated)")
    print(f"  BUCKET:   {bucket}")
    print("--------------------------------\n")

    # Initialize the Vertex AI SDK
    vertexai.init(
        project=gcp_project,
        location=gcp_location,
        staging_bucket=f"gs://{bucket}",
    )

    # --- Action Dispatch ---
    if FLAGS.create:
        agent_env_params = {
            "GOOGLE_API_KEY": api_key,
        }
        create(agent_env_params)

    elif FLAGS.delete:
        resource_name = FLAGS.agent_resource_name
        if not resource_name:
            print(
                "Agent resource name is required to delete a deployment. Please use the --agent_resource_name flag."
            )
            return
        delete(resource_name)

    else:
        print("No action specified. Use --create to deploy, --delete to remove.")


if __name__ == "__main__":
    app.run(main)

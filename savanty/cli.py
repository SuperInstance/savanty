"""Main application module for Savanty."""

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from savanty import __version__
from savanty.logging_config import logger
from savanty.solver import ConfigurationError, solve_optimization_problem

try:
    from fastmcp import FastMCP

    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False


# Configuration from environment
MAX_PROBLEM_LENGTH = int(os.getenv("SAVANTY_MAX_PROBLEM_LENGTH", "10000"))
MAX_ADDITIONAL_INFO_LENGTH = int(os.getenv("SAVANTY_MAX_ADDITIONAL_INFO_LENGTH", "5000"))
SOLVE_TIMEOUT = int(os.getenv("SAVANTY_SOLVE_TIMEOUT", "120"))


class SolveRequest(BaseModel):
    """Request model for the solve endpoint."""

    problem_description: str = Field(
        ...,
        min_length=10,
        max_length=MAX_PROBLEM_LENGTH,
        description="The optimization problem description",
    )
    additional_info: str = Field(
        default="",
        max_length=MAX_ADDITIONAL_INFO_LENGTH,
        description="Additional context or answers to clarifying questions",
    )

    @field_validator("problem_description")
    @classmethod
    def validate_problem(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Problem description cannot be empty")
        return v.strip()


def get_cors_origins() -> list[str]:
    """Get CORS origins from environment or use defaults for development."""
    cors_origins = os.getenv("SAVANTY_CORS_ORIGINS")
    if cors_origins:
        return [origin.strip() for origin in cors_origins.split(",")]

    # Default: development origins only
    env = os.getenv("SAVANTY_ENV", "development")
    if env == "production":
        # In production, require explicit CORS configuration
        logger.warning(
            "Running in production mode without SAVANTY_CORS_ORIGINS set. CORS will be restrictive."
        )
        return []
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Savanty API",
        version=__version__,
        description="AI-powered optimization solver using LLMs and ASP",
    )

    # Add CORS middleware
    cors_origins = get_cors_origins()
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.debug(f"CORS enabled for origins: {cors_origins}")

    # Global exception handler
    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(request: Request, exc: ConfigurationError):
        logger.error(f"Configuration error: {exc}")
        return JSONResponse(
            status_code=503,
            content={"error": str(exc), "type": "ConfigurationError"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred", "type": "InternalError"},
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "version": __version__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "api": "ok",
                "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            },
        }

    @app.get("/ready")
    async def readiness_check():
        """Readiness check - verifies the service can handle requests."""
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=503,
                detail={"status": "not_ready", "reason": "OPENAI_API_KEY not configured"},
            )
        return {"status": "ready"}

    @app.post("/solve")
    async def solve(request: SolveRequest):
        """Solve an optimization problem with timeout."""
        logger.info(f"Solve request received: {request.problem_description[:50]}...")
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    solve_optimization_problem,
                    request.problem_description,
                    request.additional_info,
                ),
                timeout=SOLVE_TIMEOUT,
            )

            if result.not_suitable:
                logger.info("Problem not suitable for ASP")
                return {
                    "not_suitable": True,
                    "suggested_tool": result.suggested_tool,
                    "reason": result.suitability_reason,
                    "log": f"This problem is better suited for a different approach. {result.suitability_reason}",
                }
            elif result.needs_more_info:
                logger.info(f"Problem needs more info: {len(result.questions)} questions")
                return {
                    "needs_more_info": True,
                    "questions": result.questions,
                    "log": "Please provide more information to solve this problem.",
                }
            elif result.error:
                logger.warning(f"Solver returned error: {result.error}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": result.error,
                        "log": f"Error occurred while solving: {result.error}",
                    },
                )
            else:
                logger.info("Problem solved successfully")
                return {
                    "solution": result.solution,
                    "asp_code": result.asp_code,
                    "visualization_html": result.visualization_html,
                    "log": "Problem solved successfully.",
                }
        except asyncio.TimeoutError:
            logger.warning(f"Solve request timed out after {SOLVE_TIMEOUT}s")
            raise HTTPException(
                status_code=408,
                detail={
                    "error": f"Request timed out after {SOLVE_TIMEOUT} seconds",
                    "log": "The problem took too long to solve. Try simplifying it.",
                },
            ) from None
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in solve: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": str(e),
                    "log": f"Error occurred while solving: {str(e)}",
                },
            ) from e

    # Serve Vue frontend in production
    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve the Vue frontend for all non-API routes."""
            file_path = frontend_dist / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(frontend_dist / "index.html")

    return app


@click.command()
@click.option("--problem", "-p", help="Optimization problem description")
@click.option("--web", "-w", is_flag=True, help="Run web interface")
@click.option("--mcp", "-m", is_flag=True, help="Run as Model Context Protocol server")
@click.option(
    "--port",
    default=int(os.getenv("SAVANTY_PORT", 8000)),
    help="Port for web interface",
)
@click.version_option(version=__version__)
def main(problem: str | None, web: bool, mcp: bool, port: int):
    """Savanty CLI - An intelligent optimization problem solver.

    Examples:
      savanty -p "Schedule 4 nurses for 3 shifts over a week"
      savanty --web
      savanty --mcp
    """
    if mcp:
        # Run as MCP server
        if not FASTMCP_AVAILABLE:
            click.echo(
                "Error: fastmcp package not installed. Please run 'pip install fastmcp'",
                err=True,
            )
            sys.exit(1)

        # Create FastMCP app
        mcp_app = FastMCP("Savanty Optimizer")

        @mcp_app.prompt(name="solve_optimization")
        async def solve_optimization(problem: str) -> str:
            """Solve an optimization problem using Savanty.

            Args:
                problem: The optimization problem description

            Returns:
                The solution to the optimization problem
            """
            try:
                result = solve_optimization_problem(problem, "")
                if result.error:
                    return f"Error: {result.error}"
                return f"Solution: {result.solution}"
            except Exception as e:
                return f"Error occurred: {str(e)}"

        logger.info("Starting Savanty MCP server on stdin/stdout...")
        click.echo("Starting Savanty MCP server on stdin/stdout...")
        mcp_app.run()
    elif web:
        # Run web interface
        logger.info(f"Starting Savanty web server on port {port}")
        click.echo(f"Starting Savanty web server on http://0.0.0.0:{port}")
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=port)
    elif problem:
        # Solve problem from command line
        current_problem = problem
        additional_info = ""

        while True:
            result = solve_optimization_problem(current_problem, additional_info)

            if result.not_suitable:
                click.echo("\n" + "=" * 60)
                click.echo("This problem is better suited for a different tool.")
                click.echo("=" * 60)
                click.echo(f"\nReason: {result.suitability_reason}")
                if result.suggested_tool:
                    click.echo(f"\nSuggested tool: {result.suggested_tool}")
                click.echo("\nSavanty excels at constraint satisfaction and combinatorial")
                click.echo("optimization problems like scheduling, assignments, and planning.")
                sys.exit(0)
            elif result.needs_more_info:
                click.echo("I need more information to solve this problem:")
                for i, question in enumerate(result.questions, 1):
                    click.echo(f"{i}. {question}")

                # Ask user for additional information
                user_input = click.prompt("Please provide the missing information", type=str)
                additional_info = user_input
                # We'll try again with the additional info
                continue
            elif result.error:
                click.echo(f"Error: {result.error}", err=True)
                sys.exit(1)
            else:
                click.echo("Solution found:")
                click.echo(result.solution)
                break
    else:
        # Show help if no options provided
        click.echo(f"Savanty v{__version__}: An intelligent optimization problem solver")
        click.echo("Use --help for more information")


if __name__ == "__main__":
    main()

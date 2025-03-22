#!/usr/bin/env python
"""
HTGR PRA Analysis Workflow.

This script tests the following specific workflow:
1) Pass vyom the HTGR_PRA_10162024_Final.zip file
2) Get status of zip files extraction
3) Use vyom to create the saphire-schema with the data in the zip file
4) Get status of how the JSON schema generation went
5) Get confidence in that all the data was successfully mapped to the JSON file
6) Quick and easy way to visualize and consume the json schema

Usage:
    python process_htgr_workflow.py
"""
import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
# from rich.progress import Progress, SpinnerColumn, TextColumn  # Not needed for basic workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up rich console for nicer output
console = Console()

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Try to import Vyom modules directly for better integration
try:
    from vyom import db, extractor, converter
    from vyom.schema import openpra, saphire
    DIRECT_API = True
except ImportError:
    logger.warning("Could not import Vyom modules directly, falling back to CLI commands")
    DIRECT_API = False

# Set the path to the HTGR PRA zip file and define a description
input_file = os.path.join(project_root, "data", "inputs", "HTGR_PRA_10162024_Final.zip")
input_description = "HTGR PRA Sample (10162024_Final.zip)"

def run_command(cmd, description, show_output=True):
    """Run a command and return its output."""
    if show_output:
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if show_output and result.stdout:
        console.print(result.stdout)
    
    if result.returncode != 0:
        console.print(f"[red]Error: {result.stderr}[/red]")
    
    return result.returncode == 0, result.stdout, result.stderr

def get_job_id_from_output(output):
    """Extract job ID from command output."""
    for line in output.strip().split("\n"):
        if "Job ID:" in line:
            return line.split("Job ID:")[1].split("-")[0].strip()
    return None

def parse_file_counts(output):
    """Parse file counts from status output."""
    result = {
        "fault_trees": 0,
        "event_trees": 0,
        "basic_events": 0,
        "end_states": 0,
        "total_files": 0
    }
    
    for line in output.strip().split("\n"):
        if "Fault Trees" in line:
            try:
                result["fault_trees"] = int(line.split("Fault Trees")[0].strip())
            except ValueError:
                pass
        elif "Event Trees" in line:
            try:
                result["event_trees"] = int(line.split("Event Trees")[0].strip())
            except ValueError:
                pass
        elif "Basic Events" in line:
            try:
                result["basic_events"] = int(line.split("Basic Events")[0].strip())
            except ValueError:
                pass
        elif "End States" in line:
            try:
                result["end_states"] = int(line.split("End States")[0].strip())
            except ValueError:
                pass
        elif "Files processed:" in line:
            try:
                result["total_files"] = int(line.split("Files processed:")[1].strip())
            except (ValueError, IndexError):
                pass
    
    return result

def assess_data_quality(job_id):
    """
    Assess the quality and completeness of the SAPHIRE data.
    
    This function implements steps 3, 4, and 5 of the workflow.
    """
    quality_results = {
        "confidence": 0,
        "components": {},
        "issues": []
    }
    
    # Get job data to assess it directly
    if DIRECT_API:
        try:
            console.print("[dim]Using direct API access to assess data quality...[/dim]")
            job_data = db.get_job_data(job_id)
            if not job_data:
                console.print("[bold red]Error: No data found for job ID[/bold red]")
                return False, quality_results
            
            # Analyze the data
            saphire_data = job_data.get("saphire_data", {})
            
            # Check if basic expected components exist
            components = {
                "Fault Trees": saphire_data.get("fault_trees", []),
                "Event Trees": saphire_data.get("event_trees", []),
                "Basic Events": saphire_data.get("basic_events", []),
                "End States": saphire_data.get("end_states", []),
                "Project": saphire_data.get("project", {})
            }
            
            # Create a table to display component counts
            table = Table(title="SAPHIRE Data Components")
            table.add_column("Component", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Status", style="yellow")
            
            # Analyze each component type
            confidence_scores = []
            
            for comp_name, comp_data in components.items():
                count = len(comp_data) if isinstance(comp_data, list) else bool(comp_data)
                
                # Determine status based on count and component type
                if comp_name == "Project" and comp_data:
                    status = "✓ Good"
                    confidence = 100
                elif comp_name == "Project" and not comp_data:
                    status = "✗ Missing"
                    confidence = 0
                elif count == 0:
                    status = "✗ Missing"
                    confidence = 0
                elif comp_name == "Fault Trees" and count < 10:
                    status = "⚠ Low"
                    confidence = 50
                elif comp_name == "Event Trees" and count < 5:
                    status = "⚠ Low"
                    confidence = 50
                elif comp_name == "Basic Events" and count < 20:
                    status = "⚠ Low"
                    confidence = 50
                else:
                    status = "✓ Good"
                    confidence = 100
                
                # Add to table
                table.add_row(
                    comp_name,
                    str(count) if isinstance(count, int) else ("Yes" if count else "No"),
                    status
                )
                
                # Store component results
                quality_results["components"][comp_name] = {
                    "count": count,
                    "status": status,
                    "confidence": confidence
                }
                
                confidence_scores.append(confidence)
            
            # Calculate overall confidence
            if confidence_scores:
                quality_results["confidence"] = int(sum(confidence_scores) / len(confidence_scores))
            
            # Display the table
            console.print(table)
            
            # Check for specific issues
            if not components["Project"]:
                quality_results["issues"].append("No project information found.")
            
            if len(components["Fault Trees"]) == 0:
                quality_results["issues"].append("No fault trees found.")
            
            if len(components["Event Trees"]) == 0:
                quality_results["issues"].append("No event trees found.")
            
            if len(components["Basic Events"]) == 0:
                quality_results["issues"].append("No basic events found.")
            
            # Check for orphaned components
            ft_ids = set(ft.get("id", "") for ft in components["Fault Trees"])
            be_ids = set(be.get("id", "") for be in components["Basic Events"])
            
            # Check for basic events referenced in fault trees but not defined
            referenced_bes = set()
            for ft in components["Fault Trees"]:
                gates = ft.get("gates", [])
                for gate in gates:
                    inputs = gate.get("inputs", [])
                    for input_id in inputs:
                        if not any(g.get("id") == input_id for g in gates):
                            referenced_bes.add(input_id)
            
            missing_bes = referenced_bes - be_ids
            if missing_bes:
                issue = f"Found {len(missing_bes)} referenced basic events with no definitions."
                quality_results["issues"].append(issue)
            
            # Display issues if any
            if quality_results["issues"]:
                console.print("\n[bold yellow]Issues Found:[/bold yellow]")
                for issue in quality_results["issues"]:
                    console.print(f"- {issue}")
            
            # Show overall confidence
            confidence_color = "green" if quality_results["confidence"] >= 80 else \
                              "yellow" if quality_results["confidence"] >= 50 else "red"
            
            console.print(f"\n[bold]Overall Data Quality Confidence:[/bold] [{confidence_color}]{quality_results['confidence']}%[/{confidence_color}]")
            
            return True, quality_results
            
        except Exception as e:
            console.print(f"[red]Error assessing data quality: {str(e)}[/red]")
            return False, quality_results
    
    # Fall back to CLI if direct API access is not available
    else:
        # Get status to assess data quality
        success, output, _ = run_command(
            ["vyom", "show", job_id], 
            "Getting job status"
        )
        
        if not success:
            return False, quality_results
        
        # Parse counts from output
        counts = parse_file_counts(output)
        
        # Analyze the components
        components = {
            "Fault Trees": counts["fault_trees"],
            "Event Trees": counts["event_trees"],
            "Basic Events": counts["basic_events"],
            "End States": counts["end_states"]
        }
        
        # Create a table to display component counts
        table = Table(title="SAPHIRE Data Components")
        table.add_column("Component", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Status", style="yellow")
        
        # Analyze each component type
        confidence_scores = []
        
        for comp_name, count in components.items():
            # Determine status based on count and component type
            if count == 0:
                status = "✗ Missing"
                confidence = 0
            elif comp_name == "Fault Trees" and count < 10:
                status = "⚠ Low"
                confidence = 50
            elif comp_name == "Event Trees" and count < 5:
                status = "⚠ Low"
                confidence = 50
            elif comp_name == "Basic Events" and count < 20:
                status = "⚠ Low"
                confidence = 50
            else:
                status = "✓ Good"
                confidence = 100
            
            # Add to table
            table.add_row(comp_name, str(count), status)
            
            # Store component results
            quality_results["components"][comp_name] = {
                "count": count,
                "status": status,
                "confidence": confidence
            }
            
            confidence_scores.append(confidence)
        
        # Calculate overall confidence
        if confidence_scores:
            quality_results["confidence"] = int(sum(confidence_scores) / len(confidence_scores))
        
        # Display the table
        console.print(table)
        
        # Add issues based on component analysis
        if counts["fault_trees"] == 0:
            quality_results["issues"].append("No fault trees found.")
        
        if counts["event_trees"] == 0:
            quality_results["issues"].append("No event trees found.")
        
        if counts["basic_events"] == 0:
            quality_results["issues"].append("No basic events found.")
        
        # Display issues if any
        if quality_results["issues"]:
            console.print("\n[bold yellow]Issues Found:[/bold yellow]")
            for issue in quality_results["issues"]:
                console.print(f"- {issue}")
        
        # Show overall confidence
        confidence_color = "green" if quality_results["confidence"] >= 80 else \
                          "yellow" if quality_results["confidence"] >= 50 else "red"
        
        console.print(f"\n[bold]Overall Data Quality Confidence:[/bold] [{confidence_color}]{quality_results['confidence']}%[/{confidence_color}]")
        
        return True, quality_results

def visualize_schema(job_id):
    """
    Visualize the schema for easy consumption.
    
    This implements step 6 of the workflow - visualization.
    """
    # Check if the visualize command is being run in an environment with a display
    try:
        # First check if we can run the visualization command
        success, _, _ = run_command(
            ["vyom", "view", job_id, "--no-browser"], 
            "Creating visualization",
            show_output=False
        )
        
        if success:
            console.print("[green]✓[/green] Schema visualization created successfully")
            console.print(f"To view in browser, run: vyom view {job_id}")
        else:
            console.print("[yellow]Could not create browser visualization - falling back to text view[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Cannot create browser visualization: {str(e)}[/yellow]")
        console.print("[yellow]Falling back to text-based visualization[/yellow]")
    
    # Provide a simpler text-based visualization
    if DIRECT_API:
        try:
            job_data = db.get_job_data(job_id)
            if not job_data or "saphire_data" not in job_data:
                console.print("[yellow]No SAPHIRE data available for text visualization[/yellow]")
                return
            
            saphire_data = job_data["saphire_data"]
            
            # Show project information
            project = saphire_data.get("project", {})
            if project:
                project_table = Table(title="Project Information")
                project_table.add_column("Property", style="cyan")
                project_table.add_column("Value", style="green")
                
                for key, value in project.items():
                    if key != "description":
                        project_table.add_row(key, str(value))
                
                console.print(project_table)
                
                if "description" in project:
                    console.print("[bold]Project Description:[/bold]")
                    console.print(project["description"])
            
            # Show fault tree summary
            fault_trees = saphire_data.get("fault_trees", [])
            if fault_trees:
                console.print("\n[bold]Fault Trees Summary:[/bold]")
                ft_table = Table()
                ft_table.add_column("ID", style="cyan")
                ft_table.add_column("Name", style="green")
                ft_table.add_column("Gates", style="yellow")
                ft_table.add_column("Basic Events", style="magenta")
                
                for i, ft in enumerate(fault_trees[:5]):  # Show top 5
                    ft_table.add_row(
                        ft.get("id", "Unknown"),
                        ft.get("name", "Unnamed"),
                        str(len(ft.get("gates", []))),
                        str(len(ft.get("basic_events", [])))
                    )
                
                console.print(ft_table)
                if len(fault_trees) > 5:
                    console.print(f"\n[italic]... and {len(fault_trees) - 5} more fault trees[/italic]")
            else:
                console.print("[yellow]No fault trees found to visualize[/yellow]")
            
            # Show event tree summary
            event_trees = saphire_data.get("event_trees", [])
            if event_trees:
                console.print("\n[bold]Event Trees Summary:[/bold]")
                et_table = Table()
                et_table.add_column("ID", style="cyan")
                et_table.add_column("Name", style="green")
                et_table.add_column("Init Event", style="yellow")
                et_table.add_column("Sequences", style="magenta")
                
                for i, et in enumerate(event_trees[:5]):  # Show top 5
                    et_table.add_row(
                        et.get("id", "Unknown"),
                        et.get("name", "Unnamed"),
                        et.get("initiating_event", "Unknown"),
                        str(len(et.get("sequences", [])))
                    )
                
                console.print(et_table)
                if len(event_trees) > 5:
                    console.print(f"\n[italic]... and {len(event_trees) - 5} more event trees[/italic]")
            else:
                console.print("[yellow]No event trees found to visualize[/yellow]")
            
            # Show basic events summary
            basic_events = saphire_data.get("basic_events", [])
            if basic_events:
                console.print("\n[bold]Basic Events Summary:[/bold]")
                be_table = Table()
                be_table.add_column("ID", style="cyan")
                be_table.add_column("Name", style="green")
                be_table.add_column("Probability", style="yellow")
                
                for i, be in enumerate(basic_events[:5]):  # Show top 5
                    be_table.add_row(
                        be.get("id", "Unknown"),
                        be.get("name", "Unnamed"),
                        str(be.get("probability", "N/A"))
                    )
                
                console.print(be_table)
                if len(basic_events) > 5:
                    console.print(f"\n[italic]... and {len(basic_events) - 5} more basic events[/italic]")
            else:
                console.print("[yellow]No basic events found to visualize[/yellow]")
        except Exception as e:
            console.print(f"[red]Error visualizing basic events: {str(e)}[/red]")
    else:
        console.print("[yellow]No basic events data available for visualization[/yellow]")
    
    console.print("\n[bold]Visualization Complete[/bold]")
    console.print("For more detailed exploration, use the following commands:")
    console.print(f"  vyom explore {job_id}")
    console.print(f"  vyom explore {job_id} --query '$.saphire_data.event_trees'")

def main():
    """Main function implementing the 6-step workflow."""
    console.print(Panel(
        "[bold]HTGR PRA 6-Step Workflow Test[/bold]\n\n"
        "Testing specific workflow as requested:\n"
        "1. Import ZIP file\n"
        "2. Get extraction status\n"
        "3. Create SAPHIRE schema\n" 
        "4. Get schema generation status\n"
        "5. Assess data completeness\n"
        "6. Visualize schema",
        title="Workflow Test", 
        border_style="blue"
    ))
    
    # Step 1: Check if input file exists and process it
    console.print("\n[bold]Step 1: Importing ZIP file[/bold]")
    if not os.path.exists(input_file):
        console.print(f"[bold red]Error:[/bold red] Input file not found: {input_file}")
        console.print(f"Please ensure the file exists at: {input_file}")
        return False
    
    console.print(f"[green]✓[/green] Found input file: {input_description}")
    
    # Import the ZIP file
    success, output, _ = run_command(
        ["vyom", "import", input_file], 
        "Importing SAPHIRE ZIP file"
    )
    
    if not success:
        console.print("[bold red]Failed to import ZIP file[/bold red]")
        return False
    
    # Extract job ID from output
    job_id = get_job_id_from_output(output)
    if not job_id:
        console.print("[bold red]Could not determine job ID from output[/bold red]")
        return False
    
    console.print(f"[green]✓[/green] Job ID: {job_id}")
    
    # Step 2: Get extraction status
    console.print("\n[bold]Step 2: Getting extraction status[/bold]")
    success, output, _ = run_command(
        ["vyom", "show", job_id], 
        "Checking extraction status"
    )
    
    if not success:
        console.print("[bold red]Failed to get extraction status[/bold red]")
        return False
    
    # Steps 3-5: Assess schema generation, status, and completeness
    console.print("\n[bold]Steps 3-5: Assessing schema generation, status, and completeness[/bold]")
    success, quality_results = assess_data_quality(job_id)
    
    # Step 6: Visualize the schema
    console.print("\n[bold]Step 6: Visualizing schema[/bold]")
    visualize_schema(job_id)
    
    # Final summary
    console.print(Panel(
        "[bold]Workflow Test Summary[/bold]\n"
        f"• Job ID: {job_id}\n"
        f"• ZIP file successfully imported: {'✓' if success else '✗'}\n"
        f"• Schema quality: {quality_results.get('confidence', 'N/A')}% complete\n\n"
        f"[bold]Next Steps:[/bold]\n"
        f"• To view raw data: vyom explore {job_id}\n"
        f"• To convert to OpenPRA: vyom convert {job_id}\n"
        f"• To export data: vyom export {job_id}",
        title="Test Complete", 
        border_style="green"
    ))
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        console.print(f"[bold red]Error in workflow test: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1) 
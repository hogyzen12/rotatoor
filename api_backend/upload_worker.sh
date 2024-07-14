#!/bin/bash

# Set the directory where the script and plotter.py are located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to run the plotter and update graphs
update_graphs() {
    echo "Starting graph update at $(date)"

    # Activate the Python virtual environment if you're using one
    # source /path/to/your/venv/bin/activate

    # Run the Python plotter script
    python3 "$SCRIPT_DIR/plotter.py"

    # Check if the plotter script ran successfully
    if [ $? -eq 0 ]; then
        echo "Plotter script completed successfully"

        # Update each graph file on the cloud
        for file in "$SCRIPT_DIR/graphs"/*.png; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                echo "Updating $filename on the cloud..."
                shdw-drive edit-file -r https://radial-tame-snow.solana-mainnet.quiknode.pro/f02bf8d532bcad89e4758a5e5540fb988debdcd2/ -kp /Users/hogyzen12/.config/solana/6tBou5MHL5aWpDy6cgf3wiwGGK2mR8qs68ujtpaoWrf2.json -f "$file" -u "https://shdw-drive.genesysgo.net/3UgjUKQ1CAeaecg5CWk88q9jGHg8LJg9MAybp4pevtFz/$filename"
                
                # Check if the update was successful
                if [ $? -eq 0 ]; then
                    echo "$filename updated successfully"
                else
                    echo "Error updating $filename"
                fi
            fi
        done
    else
        echo "Error: Plotter script failed"
    fi

    echo "Graph update completed at $(date)"
    echo "-----------------------------------"
}

# Main loop
while true; do
    update_graphs

    # Sleep for 15 minutes (900 seconds)
    sleep 900
done
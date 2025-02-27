"""
Map silicon probe channels and visualize the probe geometry.

Inputs:
- headstage_source: 'Intan' (default) or other sources
- save_path: Path to save the probe mapping and visualization. Default is 
    'data/silicon_probe'.

Outputs:
- Probe mapping CSV file (probe_mapping.csv)
- Visualization plot saved as PNG file (probe_visualization.png)
- Additional data saved in NumPy format (probewiring.npy and locations.npy)

Usage:
# required arguments only
python map_silicon_probe_channels.py

# with optional arguments
python map_silicon_probe_channels.py --headstage_source Intan
--save_path data/silicon_probe/probe_info

"""

# imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import argparse


def probe_128AN_bottom(headstage_source, save_path):
    """
    Maps the 128AN_bottom probe channels and creates visualization.
    
    Parameters:
    -----------
    headstage_source : str, default='Intan'
        Source of the headstage. If 'Intan', channels are zero-indexed
    save_path : Path, optional
        Path to save the probe mapping CSV file. The default is 
        'data/silicon_probe/probe_info'.
        
    Returns:
    --------
    Dict : Contains probe geometry organized by shafts and visualization data
    """
    # Define probe parameters
    tipelectrode = 30  # nearest tip-electrode vertical distance in microns
    
    # Create probe wiring matrix
    probewiring = np.array([
        [1, 0, 0, 700, 2], [2, 0, 0, 650, 2], [3, 0, 0, 600, 2],
        [4, 0, 0, 550, 2], [5, 0, 0, 500, 2], [6, 0, 0, 450, 2],
        [7, 0, 0, 400, 2], [8, 0, 0, 350, 2], [9, 0, 0, 300, 2],
        [10, 0, 0, 250, 2], [11, 0, 0, 200, 2], [12, 0, 0, 150, 2],
        [13, 0, 0, 100, 2], [14, 0, 0, 50, 2], [15, 0, 0, 0, 2],
        [16, 0, 0, 750, 2], [17, 0, 0, 800, 2], [18, 0, 0, 850, 2],
        [19, 0, 0, 900, 2], [20, 0, 0, 950, 2], [21, 4, 0, 1000, 2],
        [22, 20, 0, 1050, 2], [23, 20, 0, 975, 2], [24, 20, 0, 875, 2],
        [25, 20, 0, 775, 2], [26, 20, 0, 675, 2], [27, 20, 0, 575, 2],
        [28, 20, 0, 475, 2], [29, 20, 0, 375, 2], [30, 20, 0, 275, 2],
        [31, 20, 0, 175, 2], [32, 20, 0, 75, 2], [33, 20, 0, 25, 2],
        [34, 20, 0, 125, 2], [35, 20, 0, 225, 2], [36, 20, 0, 325, 2],
        [37, 20, 0, 425, 2], [38, 20, 0, 525, 2], [39, 20, 0, 625, 2],
        [40, 20, 0, 725, 2], [41, 20, 0, 825, 2], [42, 20, 0, 925, 2],
        [43, 20, 0, 1025, 2], [44, 36, 0, 1000, 2], [45, 40, 0, 950, 2],
        [46, 40, 0, 900, 2], [47, 40, 0, 850, 2], [48, 40, 0, 800, 2],
        [49, 40, 0, 0, 2], [50, 40, 0, 50, 2], [51, 40, 0, 100, 2],
        [52, 40, 0, 150, 2], [53, 40, 0, 200, 2], [54, 40, 0, 250, 2],
        [55, 40, 0, 300, 2], [56, 40, 0, 350, 2], [57, 40, 0, 400, 2],
        [58, 40, 0, 450, 2], [59, 40, 0, 500, 2], [60, 40, 0, 550, 2],
        [61, 40, 0, 600, 2], [62, 40, 0, 650, 2], [63, 40, 0, 700, 2],
        [64, 40, 0, 750, 2],
        [65, 200, 0, 700, 1], [66, 200, 0, 650, 1], [67, 200, 0, 600, 1],
        [68, 200, 0, 550, 1], [69, 200, 0, 500, 1], [70, 200, 0, 450, 1],
        [71, 200, 0, 400, 1], [72, 200, 0, 350, 1], [73, 200, 0, 300, 1],
        [74, 200, 0, 250, 1], [75, 200, 0, 200, 1], [76, 200, 0, 150, 1],
        [77, 200, 0, 100, 1], [78, 200, 0, 50, 1], [79, 200, 0, 0, 1],
        [80, 200, 0, 750, 1], [81, 200, 0, 800, 1], [82, 200, 0, 850, 1],
        [83, 200, 0, 900, 1], [84, 200, 0, 950, 1], [85, 204, 0, 1000, 1],
        [86, 220, 0, 1050, 1], [87, 220, 0, 975, 1], [88, 220, 0, 875, 1],
        [89, 220, 0, 775, 1], [90, 220, 0, 675, 1], [91, 220, 0, 575, 1],
        [92, 220, 0, 475, 1], [93, 220, 0, 375, 1], [94, 220, 0, 275, 1],
        [95, 220, 0, 175, 1], [96, 220, 0, 75, 1], [97, 220, 0, 25, 1],
        [98, 220, 0, 125, 1], [99, 220, 0, 225, 1], [100, 220, 0, 325, 1],
        [101, 220, 0, 425, 1], [102, 220, 0, 525, 1], [103, 220, 0, 625, 1],
        [104, 220, 0, 725, 1], [105, 220, 0, 825, 1], [106, 220, 0, 925, 1],
        [107, 220, 0, 1025, 1], [108, 236, 0, 1000, 1], [109, 240, 0, 950, 1],
        [110, 240, 0, 900, 1], [111, 240, 0, 850, 1], [112, 240, 0, 800, 1],
        [113, 240, 0, 0, 1], [114, 240, 0, 50, 1], [115, 240, 0, 100, 1],
        [116, 240, 0, 150, 1], [117, 240, 0, 200, 1], [118, 240, 0, 250, 1],
        [119, 240, 0, 300, 1], [120, 240, 0, 350, 1], [121, 240, 0, 400, 1],
        [122, 240, 0, 450, 1], [123, 240, 0, 500, 1], [124, 240, 0, 550, 1],
        [125, 240, 0, 600, 1], [126, 240, 0, 650, 1], [127, 240, 0, 700, 1],
        [128, 240, 0, 750, 1]
    ])

    # Process data for each shaft
    shaft1_mask = probewiring[:, 4] == 1
    shaft2_mask = probewiring[:, 4] == 2
    
    shaft1_channels = probewiring[shaft1_mask]
    shaft2_channels = probewiring[shaft2_mask]
    
    # Sort by z-coordinate (depth)
    shaft1_channels = shaft1_channels[shaft1_channels[:, 3].argsort()]
    shaft2_channels = shaft2_channels[shaft2_channels[:, 3].argsort()]
    
    # Create geometry dictionary
    probe_map = {
        'geometry': {
            'shaft1': {
                'channels': shaft1_channels[:, 0].astype(int),
                'x_coords': shaft1_channels[:, 1],
                'y_coords': shaft1_channels[:, 2],
                'z_coords': shaft1_channels[:, 3]
            },
            'shaft2': {
                'channels': shaft2_channels[:, 0].astype(int),
                'x_coords': shaft2_channels[:, 1],
                'y_coords': shaft2_channels[:, 2],
                'z_coords': shaft2_channels[:, 3]
            }
        },
        'spacing': 50.0,
        'n_shafts': 2,
        'orientation': 'vertical',
        'tipelectrode': tipelectrode
    }
    
    # Create visualization data structure
    vis_data = {
        'channels': probewiring[:, 0],
        'x': probewiring[:, 1],
        'y': probewiring[:, 2],
        'z': probewiring[:, 3] - np.min(probewiring[:, 3]),  # Adjust z coordinates
        'shaft': probewiring[:, 4]
    }
    
    # Adjust channel numbers for Intan
    if headstage_source == 'Intan':
        vis_data['channels'] = vis_data['channels'] - 1
    
    # Create visualization
    _create_probe_visualization(vis_data, save_path)
    
    # Save data if path provided
    if save_path is not None:
        df.to_csv(f'{save_path}/probe_mapping.csv', index=False)
        df = pd.DataFrame(probewiring, columns=['channel', 'x', 'y', 'z', 'shaft'])
        
        # Save additional formats
        np.save(f'{save_path}/probewiring.npy', probewiring)
        np.save(f'{save_path}/locations.npy', vis_data)
    
    return probe_map


def _create_probe_visualization(vis_data, save_path: Optional[Path] = None):
    """Create probe visualization plot."""
    vis_data['z'] = -vis_data['z']
    plt.figure(figsize=(10, 10))
    plt.plot(vis_data['x'], vis_data['z'], 's', markersize=11)
    
    # Add channel labels
    for i in range(len(vis_data['channels'])):
        plt.text(vis_data['x'][i]-10, vis_data['z'][i]-8,
                str(int(vis_data['channels'][i])), fontsize=9)
    
    # Set axis limits and properties
    x_min, x_max = np.min(vis_data['x']), np.max(vis_data['x'])
    z_min, z_max = np.min(vis_data['z']), np.max(vis_data['z'])
    plt.xlim([x_min-50, x_max+50])
    plt.ylim([z_min-50, z_max+50])
    plt.gca().set_aspect('equal')
    plt.gca().tick_params(direction='out', labelsize=10)

    # add axis labels
    plt.xlabel('X (microns)', fontsize=12)
    plt.ylabel('Z (microns)', fontsize=12)

    # add "top/bottom" labels
    plt.text(x_max+55, z_max, 'Top', fontsize=12)
    plt.text(x_max+55, z_min, 'Tip', fontsize=12)

    # save and show plot
    if save_path is not None:
        plt.savefig(f'{save_path}/probe_visualization.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Map silicon probe channels and visualize.")
    parser.add_argument('--headstage_source', type=str, default='Intan',
                        help="Source of the headstage (default: 'Intan')")
    parser.add_argument('--save_path', type=str, default='data/silicon_probe',
                        help="Path to save the probe mapping and visualization (default: 'data/silicon_probe/probe_info')")
    args = parser.parse_args()

    # Create save path if it doesn't exist
    save_path = Path(args.save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    # Run the probe mapping and visualization
    probe_128AN_bottom(args.headstage_source, save_path)
    print(f"Probe mapping and visualization saved to {save_path}")
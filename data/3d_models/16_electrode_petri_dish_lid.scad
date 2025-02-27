// Petri dish lid with holes for needle electrodes
// Electrodes are arranged in pairs, in a radial pattern

// Parameters
diameter = 90;          // Total outer diameter of the lid
top_height = 5;         // Thickness of the top cover

rim_height = 5;         // Height of the rim extending below the lid
rim_thickness = 0.5;    // Thickness of the rim/sidewalls
rim_offset = 1;         // Extra clearance for snug fit over the dish

num_pairs = 8;          // Number of hole pairs (8 pairs = 16 holes)
pair_separation = 10;   // Separation distance between holes in a pair
placement_radius = 20;  // Distance from the center for hole placement
hole_radius_min = 0.8;  // Inner radius of the tapered electrode hole
hole_radius_max = 1.0;  // Outer radius of the tapered electrode hole


// Create the lid with a rim
module lid() {
    total_height = top_height + rim_height;
    difference() {
        // Main body of the lid
        cylinder(d=diameter, h=total_height, center=false);

        // Hollow out the lid (separate top and sidewall thickness)
        translate([0, 0, top_height])
            difference() {
                // Hollow out the full height of the lid
                cylinder(d=diameter - 2 * rim_thickness, h=total_height, center=false);

                // Remove extra material at the top for thinner sidewalls
                translate([0, 0, -top_height])
                    cylinder(d=diameter - 2 * rim_thickness, h=top_height, center=false);
            }

        // Add a rim for secure fit
        translate([0, 0, -rim_height])
            difference() {
                cylinder(d=diameter + rim_offset, h=rim_height, center=false);
                translate([0, 0, rim_thickness])
                    cylinder(d=diameter - rim_thickness, h=rim_height, center=false);
            }

        // Create holes for electrodes
        electrode_holes();
    }
}

// Create holes for electrodes, placed in the top only
module electrode_holes() {
    for (i = [0:num_pairs-1]) {
        angle = i * 360 / num_pairs;

        for (offset = [-pair_separation / 2, pair_separation / 2]) {
            // Calculate hole positions
            x = (placement_radius + offset) * cos(angle);
            y = (placement_radius + offset) * sin(angle);

            // Create tapered cone
            translate([x, y, 0])
                rotate([0, 0, angle])
                    cylinder(r1=hole_radius_max, r2=hole_radius_min, h=top_height, center=false);
        }
    }
}

// Export the lid with rim
lid();

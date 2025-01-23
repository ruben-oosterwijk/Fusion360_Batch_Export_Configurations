import itertools
import csv
import math

def calculate_max_shelf_count(height, threshold, corpus_thickness):
    # Extract numeric value from thickness string
    thickness = int(corpus_thickness.split()[0])
    
    # Calculate usable height (subtract top and bottom panel)
    usable_height = height - (2 * thickness)
    
    # Calculate minimum number of sections needed
    # n sections require (n-1) shelves
    min_sections = math.ceil(usable_height / threshold)
    max_shelves = max(0, min_sections - 1)  # Allow 0 as minimum
    
    return max_shelves

def generate_cabinet_configurations():
    # Define the ranges
    heights = range(2500, 2501, 400)   # 400 to 2900 step 300
    widths = range(400, 1201, 200)    # 400 to 1200 step 200
    depths = range(400, 801, 200)     # 200 to 800 step 200
    divider_counts = range(0, 2)       # 0 to 1 divider
    threshold = 350                    # Maximum space between shelves/dividers
    
    # Standard thicknesses
    corpus_thickness = "18 mm"
    front_thickness = "20 mm"
    back_thickness = "10 mm"
    
    # Create CSV header
    header = ['Filename', 'Height', 'Width', 'Depth', 'Shelf_Amount', 'Divider_Amount', 
             'Thickness_Corpus', 'Thickness_Front', 'Thickness_Back']
    
    rows = []
    example_configs = []  # Store some examples for display
    
    # Generate configurations
    for h, w, d, div in itertools.product(heights, widths, depths, divider_counts):
        # Calculate maximum number of shelves for this height
        max_shelves = calculate_max_shelf_count(h, threshold, corpus_thickness)
        
        # Generate configurations for all possible shelf counts from 0 to max_shelves
        for shelf_count in range(max_shelves + 1):
            # Create logical filename
            filename = f"CSC_Bottom_Plinth_H{h}_W{w}_D{d}_S{shelf_count}_Div{div}"
            
            # Create row with measurements in mm
            row = [
                filename,
                f"{h} mm",   # Height
                f"{w} mm",   # Width
                f"{d} mm",   # Depth
                str(shelf_count),  # Current shelf amount
                str(div),    # Divider amount
                corpus_thickness,
                front_thickness,
                back_thickness
            ]
            rows.append(row)
            
            # Store example configurations for different heights
            if w == 600 and d == 400 and div == 1:
                example_configs.append((h, shelf_count, max_shelves))
    
    # Write to CSV
    with open('cabinet_library.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    
    print(f"\nGenerated {len(rows)} cabinet configurations")
    print("\nExample configurations (for width=600mm, depth=400mm, with divider):")
    print("Height (mm) | Shelf Count | Max Shelves | Usable Space")
    print("-" * 65)
    for height, shelf_count, max_shelves in sorted(set(example_configs)):
        usable_height = height - (2 * int(corpus_thickness.split()[0]))
        space_between = usable_height / (shelf_count + 1) if shelf_count > 0 else usable_height
        if shelf_count == 0:  # Only print once for each height
            print(f"{height:^11} | 0 to {max_shelves:^2}   | {max_shelves:^11} | {usable_height:.1f}mm usable height")

if __name__ == "__main__":
    generate_cabinet_configurations()
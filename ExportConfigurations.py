import adsk.core, adsk.fusion, traceback
import os
from typing import Dict, Optional, List
import csv

class DesignConfiguration:
    def __init__(self, design):
        self.design = design
        self.root = design.rootComponent
        self.cache: Dict[str, adsk.fusion.Occurrence] = {}
        
    def find_occurrence(self, path: str) -> Optional[adsk.fusion.Occurrence]:
        """Cached component lookup using path notation (e.g., 'Corpus:1/Outside:1')"""
        if path in self.cache:
            return self.cache[path]
            
        parts = path.split('/')
        current = self.root.occurrences
        
        for part in parts:
            found = None
            for occ in current:
                if occ.name == part:
                    found = occ
                    break
            if not found:
                return None
            current = found.childOccurrences
            
        self.cache[path] = found
        return found

    def update_visibility(self, path: str, visible: bool) -> None:
        """Update component visibility with caching"""
        component = self.find_occurrence(path)
        if component:
            component.isLightBulbOn = visible

    def update_entry_type(self, entry_type: str) -> None:
        valid_types = {"Cabinet", "Round Part", "Half Round Part", "Square Part"}
        if entry_type not in valid_types:
            app = adsk.core.Application.get()
            app.userInterface.messageBox(f'Warning: Invalid entry type "{entry_type}"')
            return

        components_to_hide = [
            "Corpus:1",
            "Parts:1/Half_Round_Part:1",
            "Parts:1/Round_Part:1",
            "Parts:1/Square_Part:1"
        ]

        for path in components_to_hide:
            self.update_visibility(path, False)

        # Show only required components
        if entry_type == "Cabinet":
            self.update_visibility("Corpus:1", True)
        elif entry_type == "Round Part":
            self.update_visibility("Parts:1", True)
            self.update_visibility("Parts:1/Round_Part:1", True)
        elif entry_type == "Half Round Part":
            self.update_visibility("Parts:1", True)
            self.update_visibility("Parts:1/Half_Round_Part:1", True)
        elif entry_type == "Square Part":
            self.update_visibility("Parts:1", True)
            self.update_visibility("Parts:1/Square_Part:1", True)
            
    def update_front_type(self, front_type: str) -> None:
        """Optimized front type updates using cached lookups"""
        # Hide all front components initially
        components_to_hide = [
            "Corpus:1/Outside:1/Front:1/Fixed Front:1",
            "Corpus:1/Outside:1/Front:1/Single Door:1",
            "Corpus:1/Outside:1/Front:1/Double Door:1",
            "Corpus:1/Outside:1/Front:1/Drawer:1",
            "Corpus:1/Outside:1/Front:1/Single Door with Drawer:1",
            "Corpus:1/Outside:1/Front:1/Double Door with Drawer:1",
            "Corpus:1/Outside:1/Front:1/Single Door with Fixed Front:1",
            "Corpus:1/Outside:1/Front:1/Double Door with Fixed Front:1",
            "Corpus:1/Hardware:1/Door Handle:1",
            "Corpus:1/Hardware:1/Hinges:1",
            "Corpus:1/Hardware:1/Door Handle(Mirror):1",
            "Corpus:1/Hardware:1/Hinges(Mirror):1",
            "Corpus:1/Hardware:1/Drawer Handle:1"
        ]
        
        for path in components_to_hide:
            self.update_visibility(path, False)

        # Show only required components
        if front_type == "One door":
            self.update_visibility("Corpus:1/Outside:1/Front:1/Single Door:1", True)
            self.update_visibility("Corpus:1/Hardware:1/Door Handle:1", True)
            self.update_visibility("Corpus:1/Hardware:1/Hinges:1", True)
        elif front_type == "Two doors":
            components_to_show = [
                "Corpus:1/Outside:1/Front:1/Double Door:1",
                "Corpus:1/Hardware:1/Door Handle:1",
                "Corpus:1/Hardware:1/Hinges:1",
                "Corpus:1/Hardware:1/Door Handle(Mirror):1",
                "Corpus:1/Hardware:1/Hinges(Mirror):1"
            ]
            for path in components_to_show:
                self.update_visibility(path, True)
        elif front_type == "Fixed front":
            self.update_visibility("Corpus:1/Outside:1/Front:1/Fixed Front:1", True)
        elif front_type == "One door + One drawer":
            self.update_visibility("Corpus:1/Outside:1/Front:1/Single Door with Drawer:1", True)
            self.update_visibility("Corpus:1/Hardware:1/Door Handle:1", True)
            self.update_visibility("Corpus:1/Hardware:1/Hinges:1", True)
        elif front_type == "Two doors + Two drawers":
            components_to_show = [
                "Corpus:1/Outside:1/Front:1/Double Door with Drawer:1",
                "Corpus:1/Hardware:1/Door Handle:1",
                "Corpus:1/Hardware:1/Hinges:1",
                "Corpus:1/Hardware:1/Door Handle(Mirror):1",
                "Corpus:1/Hardware:1/Hinges(Mirror):1"
            ]
            for path in components_to_show:
                self.update_visibility(path, True)
        elif front_type == "One door + Fixed front":
            self.update_visibility("Corpus:1/Outside:1/Front:1/Single Door with Fixed Front:1", True)
            self.update_visibility("Corpus:1/Hardware:1/Door Handle:1", True)
            self.update_visibility("Corpus:1/Hardware:1/Hinges:1", True)
        elif front_type == "Two doors + Fixed front":
            components_to_show = [
                "Corpus:1/Outside:1/Front:1/Double Door with Fixed Front:1",
                "Corpus:1/Hardware:1/Door Handle:1",
                "Corpus:1/Hardware:1/Hinges:1",
                "Corpus:1/Hardware:1/Door Handle(Mirror):1",
                "Corpus:1/Hardware:1/Hinges(Mirror):1"
            ]
            for path in components_to_show:
                self.update_visibility(path, True)
        elif "drawers" in front_type:
            self.update_visibility("Corpus:1/Outside:1/Front:1/Drawer:1", True)
            self.update_visibility("Corpus:1/Hardware:1/Drawer Handle:1", True)

    def update_plinth_type(self, plinth_setting: str) -> None:
        """Optimized plinth updates using cached lookups"""
        plinth_components = {
            "bottom": "Corpus:1/Outside:1/Plinth_Bottom:1",
            "left": "Corpus:1/Outside:1/Plinth_Left:1",
            "right": "Corpus:1/Outside:1/Plinth_Right:1"
        }
        
        # Hide all initially
        for path in plinth_components.values():
            self.update_visibility(path, False)
            
        # Show based on setting
        if "Bottom" in plinth_setting:
            self.update_visibility(plinth_components["bottom"], True)
        if "Left" in plinth_setting:
            self.update_visibility(plinth_components["left"], True)
        if "Right" in plinth_setting:
            self.update_visibility(plinth_components["right"], True)

    def update_panel_type(self, panel_setting: str) -> None:
        """Optimized panel updates using cached lookups"""
        panel_components = {
            "right": "Corpus:1/Outside:1/Extra_Side_Panel_Right:1",
            "left": "Corpus:1/Outside:1/Extra_Side_Panel_Left:1"
        }
        
        # Hide all initially
        for path in panel_components.values():
            self.update_visibility(path, False)
            
        # Show based on setting
        if panel_setting in ["Right", "Both"]:
            self.update_visibility(panel_components["right"], True)
        if panel_setting in ["Left", "Both"]:
            self.update_visibility(panel_components["left"], True)

    def update_shelves_and_dividers(self, shelf_amount: int, divider_amount: int) -> None:
        self.update_visibility("Corpus:1/Inside:1/Shelving:1", shelf_amount > 0)
        self.update_visibility("Corpus:1/Inside:1/Dividers:1", divider_amount > 0)

    def update_feet(self, feet_toggle) -> None:
        """Update feet visibility based on input value (1 or empty)"""
        feet_visible = feet_toggle == "1"
        self.update_visibility("Corpus:1/Hardware:1/Feet:1", feet_visible)

    def update_clothing_rods(self, clothing_rods_amount: int) -> None:
        self.update_visibility("Corpus:1/Hardware:1/Clothing Rods:1", clothing_rods_amount > 0)

    def update_parameters(self, params: dict) -> None:
        """Batch update parameters"""
        user_params = self.design.userParameters
        for name, value in params.items():
            param = user_params.itemByName(name)
            if param:
                param.expression = str(value)

    
    def update_appearance_color(self, appearance_name: str, r: int, g: int, b: int) -> None:
        """Update the color of an existing appearance"""
        try:
            # Convert RGB values to 0-1 range
            color = adsk.core.Color.create(r, g, b, 255)
            
            appearances = self.design.appearances
            appearance = appearances.itemByName(appearance_name)
            if appearance:
                color_property = appearance.appearanceProperties.itemByName('Color')
                if color_property:
                    color_property.value = color
        except Exception as e:
            app = adsk.core.Application.get()
            app.userInterface.messageBox(f'Failed to update appearance color for {appearance_name}:\n{str(e)}')

    def update_all_appearances(self, row: dict) -> None:
        try:
            for appearance_type in ['Front', 'Corpus', 'Panel', 'Plinth']:
                try:
                    r = int(row[f'{appearance_type}_Color_R'])
                    g = int(row[f'{appearance_type}_Color_G'])
                    b = int(row[f'{appearance_type}_Color_B'])
                    self.update_appearance_color(f'Placeholder_{appearance_type}s', r, g, b)
                except (ValueError, KeyError) as e:
                    app = adsk.core.Application.get()
                    app.userInterface.messageBox(f'Warning: Could not update {appearance_type} color: {str(e)}')
                    continue
        except Exception as e:
            app = adsk.core.Application.get()
            app.userInterface.messageBox(f'Failed to update appearances:\n{str(e)}')


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # File selection
        csv_file = ui.createFileDialog()
        csv_file.title = "Select CSV Configuration File"
        csv_file.filter = "CSV files (*.csv);;All files (*.*)"
        if csv_file.showOpen() != adsk.core.DialogResults.DialogOK:
            return
            
        folder_dialog = ui.createFolderDialog()
        folder_dialog.title = "Select Output Folder"
        if folder_dialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
            
        base_dir = folder_dialog.folder
        
        ui.messageBox('Starting export process. This might take a while...')
        app.userInterface.suppressDialogs = True
        
        # Initialize configuration manager
        design = app.activeProduct
        config_manager = DesignConfiguration(design)
        export_mgr = design.exportManager
        
        # Process CSV file
        with open(csv_file.filename, 'r') as file:
            reader = csv.DictReader(file)
            total_processed = 0
            
            for row in reader:
                # Create parent directory if needed
                # Create parent directory if needed
                parent_dir = os.path.join(base_dir, row['Parent_file'])
                os.makedirs(parent_dir, exist_ok=True)
                
                # Add this new line here
                config_manager.update_all_appearances(row)
                # Update design configuration
                config_manager.update_entry_type(row['Entry_Type'])
                config_manager.update_front_type(row['Front_Type'])
                config_manager.update_plinth_type(row['Plinth_Setting'])
                config_manager.update_panel_type(row['Extra_Side_Panel_Setting'])
                config_manager.update_shelves_and_dividers(
                    int(row['Shelf_Amount']), 
                    int(row['Divider_Amount'])
                )
                
                config_manager.update_clothing_rods(int(row['Clothing_Rod_Amount']))
                config_manager.update_feet(row['Feet'])
                
                # Batch update parameters
                params = {
                    'Height': row['Height'],
                    'Width': row['Width'],
                    'Depth': row['Depth'],
                    'Thickness_Corpus': row['Thickness_Corpus'],
                    'Thickness_Front': row['Thickness_Front'],
                    'Thickness_Back': row['Thickness_Back'],
                    'Shelf_Amount': row['Shelf_Amount'],
                    'Divider_Amount': row['Divider_Amount'],
                    'Side_Panel_Left_Thickness': row['Thickness_Extra_Panel'],
                    'Side_Panel_Right_Thickness': row['Thickness_Extra_Panel'],
                    'Plinth_Bottom_Thickness': row['Thickness_Plinth'],
                    'Plinth_Thickness_Left': row['Thickness_Plinth'],
                    'Plinth_Thickness_Right': row['Thickness_Plinth'],
                    'Clothing_Rod_Amount': row['Clothing_Rod_Amount']
                }
                
                if "drawers" in row['Front_Type'].lower():
                    try:
                        num_drawers = int(row['Front_Type'].split()[0])
                        params['Drawer_Amount'] = str(num_drawers)
                    except ValueError:
                        pass
                # params['Quantity'] = row['Quantity']
                config_manager.update_parameters(params)
                
                # Force design update
                design.rootComponent.parentDesign.designType = adsk.fusion.DesignTypes.ParametricDesignType
                design.rootComponent.parentDesign.activeComponent.isParametric = True
                adsk.doEvents()
                
                # Generate filename and export
                filename = f"{row['Parent_file']}_{row['Element_Name']}_{row['Entry_Type']}_{row['Quantity']}x"
                step_path = os.path.join(parent_dir, f"{filename}.stp")
                step_options = export_mgr.createSTEPExportOptions(step_path)
                export_mgr.execute(step_options)
                
                total_processed += 1
                if total_processed % 10 == 0:
                    print(f'Processed {total_processed} files... Current: {row["Element_Name"]} ({row["Entry_Type"]})')


        
        app.userInterface.suppressDialogs = False
        ui.messageBox(f'Export complete! Processed {total_processed} configurations.')
        
    except:
        if ui:
            app.userInterface.suppressDialogs = False
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    finally:
        if app:
            app.userInterface.suppressDialogs = False

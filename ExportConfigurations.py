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

    def update_front_type(self, front_type: str) -> None:
        """Optimized front type updates using cached lookups"""
        # Hide all front components initially
        components_to_hide = [
            "Corpus:1/Outside:1/Front:1/Single Door:1",
            "Corpus:1/Outside:1/Front:1/Double Door:1",
            "Corpus:1/Outside:1/Front:1/Drawer:1",
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
                "Corpus:1/Outside:1/Front:1/Single Door:1",
                "Corpus:1/Hardware:1/Door Handle:1",
                "Corpus:1/Hardware:1/Hinges:1",
                "Corpus:1/Outside:1/Front:1/Double Door:1",
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
        """Optimized shelf and divider updates"""
        self.update_visibility("Corpus:1/Inside:1/Shelving:1", shelf_amount > 0)
        self.update_visibility("Corpus:1/Inside:1/Dividers:1", divider_amount > 0)

    def update_feet(self, shelf_amount: int, divider_amount: int) -> None:
        """Optimized shelf and divider updates"""
        self.update_visibility("Corpus:1/Inside:1/Shelving:1", shelf_amount > 0)
        self.update_visibility("Corpus:1/Inside:1/Dividers:1", divider_amount > 0)

    def update_parameters(self, params: dict) -> None:
        """Batch update parameters"""
        user_params = self.design.userParameters
        for name, value in params.items():
            param = user_params.itemByName(name)
            if param:
                param.expression = str(value)

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
                parent_dir = os.path.join(base_dir, row['Parent_file'])
                os.makedirs(parent_dir, exist_ok=True)
                
                # Update design configuration
                config_manager.update_front_type(row['Front_Type'])
                config_manager.update_plinth_type(row['Plinth_Setting'])
                config_manager.update_panel_type(row['Panel_Setting'])
                config_manager.update_shelves_and_dividers(
                    int(row['Shelf_Amount']), 
                    int(row['Divider_Amount'])
                )
                
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
                    'Quantity': row['Quantity'],
                    'Side_Panel_Left_Thickness': row['Thickness_Extra_Panel'],
                    'Side_Panel_Right_Thickness': row['Thickness_Extra_Panel'],
                    'Plinth_Bottom_Thickness': row['Thickness_Plinth'],
                    'Plinth_Thickness_Left': row['Thickness_Plinth'],
                    'Plinth_Thickness_Right': row['Thickness_Plinth']
                }
                
                if "drawers" in row['Front_Type'].lower():
                    try:
                        num_drawers = int(row['Front_Type'].split()[0])
                        params['Drawer_Amount'] = str(num_drawers)
                    except ValueError:
                        pass
                
                config_manager.update_parameters(params)
                
                # Force design update
                design.rootComponent.parentDesign.designType = adsk.fusion.DesignTypes.ParametricDesignType
                design.rootComponent.parentDesign.activeComponent.isParametric = True
                adsk.doEvents()
                
                # Generate filename and export
                filename = f"{row['Parent_file']}_{row['Element_Name']}_{row['Quantity']}x_FM-{row['Front_material']}_CM-{row['Corpus_material']}_PM-{row['Plinth_material']}"
                step_path = os.path.join(parent_dir, f"{filename}.stp")
                step_options = export_mgr.createSTEPExportOptions(step_path)
                export_mgr.execute(step_options)
                
                total_processed += 1
                if total_processed % 10 == 0:
                    print(f'Processed {total_processed} files...')
        
        app.userInterface.suppressDialogs = False
        ui.messageBox(f'Export complete! Processed {total_processed} configurations.')
        
    except:
        if ui:
            app.userInterface.suppressDialogs = False
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    finally:
        if app:
            app.userInterface.suppressDialogs = False

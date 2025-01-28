import adsk.core, adsk.fusion, traceback
import os

def get_component_mass(design, component_name):
    try:
        root = design.rootComponent
        corpus = root.occurrences.itemByName('Corpus:1')
        if not corpus:
            return 0
            
        target_component = None
        for occ in corpus.childOccurrences:
            if occ.name == component_name:
                target_component = occ
                break
                
        if target_component:
            # Force update of the model
            target_component.component.name = target_component.component.name
            physicalProperties = target_component.physicalProperties
            mass = physicalProperties.mass
            return round(mass, 3)  # Round to 3 decimal places (kg)
        else:
            return 0
    except:
        return 0
    
def find_occurrence_by_name(parent_occurrences, name):
    """
    Recursively searches for an occurrence by name within the hierarchy.
    """
    for occurrence in parent_occurrences:
        if occurrence.name == name:
            return occurrence
        # Recursively check children
        found = find_occurrence_by_name(occurrence.childOccurrences, name)
        if found:
            return found
    return None

def update_front_type(design, front_type):
    try:
        root = design.rootComponent
        # Traverse the hierarchy
        corpus_occurrence = find_occurrence_by_name(root.occurrences, "Corpus:1")
        if not corpus_occurrence:
            raise ValueError("Corpus component not found!")

        outside_occurrence = find_occurrence_by_name(corpus_occurrence.childOccurrences, "Outside:1")
        if not outside_occurrence:
            raise ValueError("Outside component not found!")

        door_occurrence = find_occurrence_by_name(outside_occurrence.childOccurrences, "Door:1")
        drawer_occurrence = find_occurrence_by_name(outside_occurrence.childOccurrences, "Drawer:1")


        # Hide all doors and drawers initially
        if door_occurrence:
            door_occurrence.isLightBulbOn = False

        if drawer_occurrence:
                drawer_occurrence.isLightBulbOn = False

        # Handle the `Front_Type` input
        if front_type == "One door":
            door_occurrence.isLightBulbOn = True
        elif front_type == "Two doors":
            door_occurrence.isLightBulbOn = True
        elif front_type == "No Front (Default)":
            # Keep all components hidden
            drawer_occurrence.isLightBulbOn = False
            door_occurrence.isLightBulbOn = False
        elif "drawers" in front_type:
            drawer_occurrence.isLightBulbOn = True
    except Exception as e:
        app = adsk.core.Application.get()
        app.userInterface.messageBox(f"Error updating Front_Type:\n{traceback.format_exc()}")
        
def update_plinth_type(design, plinth_setting):
    try:
        root = design.rootComponent
        # Traverse the hierarchy
        corpus_occurrence = find_occurrence_by_name(root.occurrences, "Corpus:1")
        if not corpus_occurrence:
            raise ValueError("Corpus component not found!")

        outside_occurrence = find_occurrence_by_name(corpus_occurrence.childOccurrences, "Outside:1")
        if not outside_occurrence:
            raise ValueError("Outside component not found!")

        # Find all plinth components
        plinth_bottom = find_occurrence_by_name(outside_occurrence.childOccurrences, "Plinth_Bottom:1")
        plinth_left = find_occurrence_by_name(outside_occurrence.childOccurrences, "Plinth_Left:1")
        plinth_right = find_occurrence_by_name(outside_occurrence.childOccurrences, "Plinth_Right:1")
        
        # Hide all plinth components initially
        if plinth_bottom:
            plinth_bottom.isLightBulbOn = False
            
        if plinth_left:
            plinth_left.isLightBulbOn = False
            
        if plinth_right:
            plinth_right.isLightBulbOn = False

        # Handle the plinth_setting input
        if plinth_setting == "Bottom":
            plinth_bottom.isLightBulbOn = True
        elif plinth_setting == "Left":
            plinth_left.isLightBulbOn = True
        elif plinth_setting == "Right":
            plinth_right.isLightBulbOn = True
        elif plinth_setting == "Left + Bottom":
            plinth_left.isLightBulbOn = True
            plinth_bottom.isLightBulbOn = True
        elif plinth_setting == "Right + Bottom":
            plinth_right.isLightBulbOn = True
            plinth_bottom.isLightBulbOn = True
        elif plinth_setting == "Left + Right + Bottom":
            plinth_left.isLightBulbOn = True
            plinth_right.isLightBulbOn = True
            plinth_bottom.isLightBulbOn = True
        elif plinth_setting == "None (Default)":
            # Keep all components hidden
            plinth_bottom.isLightBulbOn = False
            plinth_left.isLightBulbOn = False
            plinth_right.isLightBulbOn = False
            
    except Exception as e:
        app = adsk.core.Application.get()
        app.userInterface.messageBox(f"Error updating Plinth_Setting:\n{traceback.format_exc()}")

def update_panel_type(design, panel_setting):
    try:
        root = design.rootComponent
        # Traverse the hierarchy
        corpus_occurrence = find_occurrence_by_name(root.occurrences, "Corpus:1")
        if not corpus_occurrence:
            raise ValueError("Corpus component not found!")

        outside_occurrence = find_occurrence_by_name(corpus_occurrence.childOccurrences, "Outside:1")
        if not outside_occurrence:
            raise ValueError("Outside component not found!")

        # Find all panel components
        extra_panel_right = find_occurrence_by_name(outside_occurrence.childOccurrences, "Extra_Side_Panel_Right:1")
        extra_panel_left = find_occurrence_by_name(outside_occurrence.childOccurrences, "Extra_Side_Panel_Left:1")

        # Hide all panel components initially
        if extra_panel_right:
            extra_panel_right.isLightBulbOn = False
        if extra_panel_left:
            extra_panel_left.isLightBulbOn = False

        # Handle the panel_setting input
        if panel_setting == "Right":
            if extra_panel_right:
                extra_panel_right.isLightBulbOn = True
        elif panel_setting == "Left":
            if extra_panel_left:
                extra_panel_left.isLightBulbOn = True
        elif panel_setting == "Both":
            extra_panel_left.isLightBulbOn = True
            extra_panel_right.isLightBulbOn = True
        elif panel_setting == "None (Default)":
            # Keep all components hidden
            if extra_panel_right:
                extra_panel_right.isLightBulbOn = False
            if extra_panel_left:
                extra_panel_left.isLightBulbOn = False

    except Exception as e:
        app = adsk.core.Application.get()
        app.userInterface.messageBox(f"Error updating Panel_Setting:\n{traceback.format_exc()}")
        
def update_shelves(design, shelf_amount):
    try:
        root = design.rootComponent
        # Traverse the hierarchy
        corpus_occurrence = find_occurrence_by_name(root.occurrences, "Corpus:1")
        if not corpus_occurrence:
            raise ValueError("Corpus component not found!")

        outside_occurrence = find_occurrence_by_name(corpus_occurrence.childOccurrences, "Inside:1")
        if not outside_occurrence:
            raise ValueError("Outside component not found!")

        # Find all dividers components
        shelving = find_occurrence_by_name(outside_occurrence.childOccurrences, "Shelving:1")
        
        # Hide all shelving components initially
        if shelving:
            shelving.isLightBulbOn = False

        if shelf_amount > 0:
            shelving.isLightBulbOn = True

    except Exception as e:
        app = adsk.core.Application.get()
        app.userInterface.messageBox(f"Error updating Shelving_Setting:\n{traceback.format_exc()}")
        
def update_dividers(design, divider_amount):
    try:
        root = design.rootComponent
        # Traverse the hierarchy
        corpus_occurrence = find_occurrence_by_name(root.occurrences, "Corpus:1")
        if not corpus_occurrence:
            raise ValueError("Corpus component not found!")

        outside_occurrence = find_occurrence_by_name(corpus_occurrence.childOccurrences, "Inside:1")
        if not outside_occurrence:
            raise ValueError("Outside component not found!")

        # Find all panel components
        dividers = find_occurrence_by_name(outside_occurrence.childOccurrences, "Dividers:1")

        # Hide all shelving components initially
        if dividers:
            dividers.isLightBulbOn = False

        if divider_amount > 0:
            dividers.isLightBulbOn = True

    except Exception as e:
        app = adsk.core.Application.get()
        app.userInterface.messageBox(f"Error updating Divider_Setting:\n{traceback.format_exc()}")
        
        
def select_file(ui):
    try:
        fileDialog = ui.createFileDialog()
        fileDialog.title = "Select CSV Configuration File"
        fileDialog.filter = "CSV files (*.csv);;All files (*.*)"
        fileDialog.filterIndex = 0
        
        if fileDialog.showOpen() != adsk.core.DialogResults.DialogOK:
            return None
            
        return fileDialog.filename
    except:
        return None

def select_folder(ui):
    try:
        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Select Output Folder"
        
        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return None
            
        return folderDialog.folder
    except:
        return None


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        csv_file = select_file(ui)
        if not csv_file:
            ui.messageBox('Operation cancelled - No CSV file selected')
            return

        base_dir = select_folder(ui)
        if not base_dir:
            ui.messageBox('Operation cancelled - No output folder selected')
            return

        ui.messageBox('Starting export process. This might take a while...')
        app.userInterface.suppressDialogs = True

        design = app.activeProduct

        file = open(csv_file)
        next(file)

        total_processed = 0

        for line in file:
            pieces = line.strip().split(',')
            pieces = [p.strip('"') for p in pieces]
            parent_filename = pieces[0]
            element_name = pieces[1]
            quantity = pieces[2]
            height = pieces[3]
            width = pieces[4]
            depth = pieces[5]
            front_type = pieces[6]
            shelf_amount = int(pieces[7])
            divider_amount = int(pieces[8])
            plinth_setting = pieces[9]
            panel_setting = pieces[10]
            front_material = pieces[11]
            corpus_material = pieces[12]
            plinth_material = pieces[13]
            extra_panel_material = pieces[14]
            front_thickness = pieces[15]
            corpus_thickness = pieces[16]
            back_thickness = pieces[17]
            plinth_thickness = pieces[18]
            extra_panel_thickness = pieces[19]
            
            # Create only parent folder
            parent_dir = os.path.join(base_dir, parent_filename)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            params = design.userParameters
            
            # Update the Front_Type configuration
            update_front_type(design, front_type)
            update_dividers(design, divider_amount)
            update_shelves(design, shelf_amount)
            

            # Set all parameters
            params.itemByName('Height').expression = height
            params.itemByName('Width').expression = width
            params.itemByName('Depth').expression = depth
            params.itemByName('Thickness_Corpus').expression = corpus_thickness
            params.itemByName('Thickness_Front').expression = front_thickness
            params.itemByName('Thickness_Back').expression = back_thickness
            params.itemByName('Shelf_Amount').expression = str(shelf_amount)
            params.itemByName('Divider_Amount').expression = str(divider_amount)
            params.itemByName('Quantity').expression = quantity
            
            
            params.itemByName('Side_Panel_Left_Thickness').expression = extra_panel_thickness
            params.itemByName('Side_Panel_Right_Thickness').expression = extra_panel_thickness
            
            params.itemByName('Plinth_Bottom_Thickness').expression = plinth_thickness
            params.itemByName('Plinth_Thickness_Left').expression = plinth_thickness
            params.itemByName('Plinth_Thickness_Right').expression = plinth_thickness
            
            # Update the Front_Type configuration
            update_plinth_type(design, plinth_setting)
            # Update the Front_Type configuration        
            update_panel_type(design, panel_setting)
            
            # Handle drawer amount
            if "drawers" in front_type.lower():
                try:
                    num_drawers = int(front_type.split(" ")[0])
                    params.itemByName('Drawer_Amount').expression = str(num_drawers)
                except:
                    ui.messageBox(f'Warning: Could not set drawer amount from "{front_type}"')

            # Force a full update of the design
            design.rootComponent.parentDesign.designType = adsk.fusion.DesignTypes.ParametricDesignType
            design.rootComponent.parentDesign.activeComponent.isParametric = True

            # Add a small delay to ensure update completes
            adsk.doEvents()

            # Calculate masses of Inside and Outside components
            m_inside = get_component_mass(design, "Inside:1")
            m_outside = get_component_mass(design, "Outside:1")
            m_total = m_inside + m_outside

            filename_with_properties = (f"{parent_filename}_{element_name}_{quantity}x_FM-{front_material}_"
                                     f"CM-{corpus_material}_PM-{plinth_material}_Totalmass-{m_total:.3f}")

            exportMgr = design.exportManager
            step_path = os.path.join(parent_dir, filename_with_properties + '.stp')
            stepOptions = exportMgr.createSTEPExportOptions(step_path)
            exportMgr.execute(stepOptions)

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

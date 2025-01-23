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
            
            filename = pieces[0]
            height = pieces[1]
            width = pieces[2]
            depth = pieces[3]
            shelf_amount = pieces[4]
            divider_amount = pieces[5]
            corpus_thickness = pieces[6]
            front_thickness = pieces[7]
            back_thickness = pieces[8]
            
            dir_path = os.path.join(base_dir, f"Div{divider_amount}", f"Shelf{shelf_amount}")
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            params = design.userParameters
            
            # Set all parameters
            params.itemByName('Height').expression = height
            params.itemByName('Width').expression = width
            params.itemByName('Depth').expression = depth
            params.itemByName('Shelf_Amount').expression = shelf_amount
            params.itemByName('Divider_Amount').expression = divider_amount
            params.itemByName('Thickness_Corpus').expression = corpus_thickness
            params.itemByName('Thickness_Front').expression = front_thickness
            params.itemByName('Thickness_Back').expression = back_thickness
            
            # Force a full update of the design
            design.rootComponent.parentDesign.designType = adsk.fusion.DesignTypes.ParametricDesignType
            design.rootComponent.parentDesign.activeComponent.isParametric = True
            
            # Add a small delay to ensure update completes
            adsk.doEvents()
            
            # Calculate masses of Inside and Outside components
            m_inside = get_component_mass(design, "Inside:1")
            m_outside = get_component_mass(design, "Outside:1")
            m_total = m_inside + m_outside
            
            filename_with_properties = (f"{filename}_massTotal{m_total:.3f}")
            
            exportMgr = design.exportManager
            step_path = os.path.join(dir_path, filename_with_properties + '.stp')
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
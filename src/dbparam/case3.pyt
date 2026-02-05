import json
import os

import arcpy


class Toolbox(object):

    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "Test with absolute paths"

        # List of tool classes associated with this toolbox
        self.tools = [ToolA]


class ToolA(object):
    DEFAULT_CONFIG = {
        "db-sde": "C:\\PRJ\\GP-Tool-Problems\\data\\sql-cases.sde",
        "db-gdb": "C:\\PRJ\\GP-Tool-Problems\\data\\cases.gdb"
    }

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Case 3"
        self.description = "Test with absolute paths"
        self.canRunInBackground = False

        config = self._read_configfile()
        self.config = dict(self.DEFAULT_CONFIG)
        self.config.update(config)  # does not work with arcmap

    @staticmethod
    def _read_configfile():
        try:
            configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'case2.json')
            with open(configfile, 'r') as f:
                return json.loads(f.read())
        except Exception as e:
            arcpy.AddError('Failed reading config file. {0}'.format(e))
            return e

    def getParameterInfo(self):
        """Define parameter definitions
        handles the parameters from the Toolboxwindow

        :keyword: https://desktop.arcgis.com/en/arcmap/10.7/analyze/creating-tools/defining-parameters-in-a-python-toolbox.htm

        """
        params = []
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        arcpy.AddMessage(f"Workspace: {arcpy.env.workspace}")
        arcpy.AddMessage(f"packageWorkspace: {arcpy.env.packageWorkspace}")

        # Workaround: Immer relativ zu packageWorkspace aufbauen, auch nach Rewrite
        pkg_ws = arcpy.env.packageWorkspace
        script_dir = os.path.dirname(os.path.abspath(__file__))
        arcpy.AddMessage(f"Package Workspace: {pkg_ws}")
        arcpy.AddMessage(f"Script Dir: {script_dir}")

        # Config-Pfade (wie in DEFAULTCONFIG: 'db-sde': '../sql-cases.sde', etc.)
        config_paths = self.config  # {'db-sde': '../sql-cases.sde', 'db-gdb': '../test.gdb'}

        for key, rel_path in config_paths.items():
            # Relativ zu packageWorkspace joinen (Server-kompatibel)
            ws_path = os.path.normpath(os.path.join(pkg_ws, rel_path))
            arcpy.AddMessage(f"Setting {key}: {ws_path} (rel: {rel_path})")

            try:
                # Test Existenz und setze workspace
                if arcpy.Exists(ws_path):
                    arcpy.env.workspace = ws_path
                    arcpy.AddMessage(f"✓ Workspace set to {arcpy.env.workspace}")
                else:
                    abs_fallback = os.path.normpath(os.path.join(script_dir, rel_path))
                    if arcpy.Exists(abs_fallback):
                        arcpy.env.workspace = abs_fallback
                        arcpy.AddMessage(f"✓ Fallback to abs: {arcpy.env.workspace}")
                    else:
                        arcpy.AddError(f"✗ Workspace '{ws_path}' or fallback not found")
                        raise Exception(f"DB path invalid: {rel_path}")
            except Exception as e:
                arcpy.AddError(f"Failed for {key}: {str(e)}")

        # Deine weitere Tool-Logik hier
        arcpy.AddMessage("Tool executed successfully with relative workspaces.")
        return


if __name__ == '__main__':
    tb = Toolbox()
    a = ToolA()
    a.execute(None, None)

# DCS UV Map Converter Tool

This Blender Add-on converts UV maps generated on ModelViewer 2 to an image format.

## Installation

### Prerequisites

DCS 2.7, older versions can't generate the UV map.

Download and install Blender 2.92.0 from https://www.blender.org/download/

Download the latest release of the Add-on from https://github.com/Ettenmure/dcs-uv-converter/releases

### Activating the Add-on in Blender

In Blender, on the top left of the screen go to Edit > Preferences.

Open the Add-ons menu and click "Install", locate the previously downloaded "DCSUVConverter.zip" and click "Install Add-on".

Next, click on the checkbox to the left of the Add-on name to active it. Exit Blender.

## Usage

### Exporting the UV map in Model Viewer

On the Model Viewer, load the model of your choosing.

On the textures panel, expand the texture that you want to generate a UV map for.

Click "UV to file", save the generated .csv file on your hard drive. This file contains the UV map data and will used in the next step.

![Readme0](./images/ReadmeImage0.PNG)

### Converting the UV map to an image in Blender

Open a new Blender file. Don't use an existing one, the conversion process will delete every object on the scene.

On the Properties editor, at the right of the screen, change to the "Scene" tab.

![Readme1](./images/ReadmeImage1.PNG)

Here you should see an entry called "DCS UV Converter", expand it to reveal the "Convert .csv" button.

Click the grey "Convert .csv" button. A new window will open asking you to locate on your hard drive the .csv file that you previously created.
Select it and press the blue "Convert .csv" button.

![Readme2](./images/ReadmeImage2.PNG)

The conversion process has now begun, this can last from seconds to minutes depending on the complexity of the UV map and your computer hardware. 
Do not exit blender while it's running.

Once it finishes you will be notified in two forms. First, a small message saying "UV Conversion finished." will briefly appear at the status bar on the bottom of the screen. 
Second, on the outliner editor at the top right of the screen a new collection called "Conversion finished" will appear.

![Readme3](./images/ReadmeImage3.PNG)

The conversion process has now finished, exit Blender.

The generated UV map is an image in .png format that will be located at the same folder as the .csv. Its name is the same as that of the .csv but with "_UV" added at the end.

## Troubleshooting

**There is no "DCS UV Converter" at the scene tab**

- The Add-on has either not been installed or is installed but not activated. Please review the documentation for Blender Add-ons:
https://docs.blender.org/manual/en/latest/editors/preferences/addons.html


## Planned features

These have not been implemented yet but are planned for later releases:

- Batch conversion
- UV maps two and four times the size of the original texture
- Additional image export options

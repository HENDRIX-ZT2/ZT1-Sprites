# ZT1-Sprites
A plugin to automize sprite rendering for Zoo Tycoon 1.

Automatic ZT1 Sprite Rendering for blender 2.78+

Be careful when downloading files, you should unzip and then rezip it without the parent folder.
In blender, select the re-zipped file by clicking "File > User Preferences > Addons > Install from File..."
Confirm with "Install from File..."
Tick the box at the right to enable the script.
Click "Save User Settings" at the bottom.
Then the new ZT1 Rendering panel will appear in the Render tab.

How to use:

Both static objects and animated animals etc. are supported. So you can ignore the parts that refer to animations if you just want still objects.

First, you must install and activate the provided script. If you want to import from ZT2, also install my BFB and edited NIF scripts.

0) Make sure to turn on the Blender Console so you can trace progress on the slower operations.

1) Import / create a model. If you import a BFB file, make sure to turn the mirror option OFF.

2) Import / create animations. Rename them to match what the ANI file expects, make any edits required to make them match.

3) Scale the armature, not the model (that would distort it). 1 blender grid square corresponds to 1 meter ingame.

4) Only for water animals: There are 4 different special cases: surface (hide the underside), undersurface (hide the upperside), underwater (hide surface and shadow), shadow (hide the model itself). The scripts use a boolean modifier and other things to set everything up. All you have to do is label the animation names with + (for surface), - (for undersurface), * (for underwater) and # (for shadow). Land actions are not prefaced.

5) Then you only need the "Render" Tab.
Locate the "Output" field. Specify where the files should be created. ZT Studio expects "temp/output" as its default root folder. On top of that, add the path of your animations root. Usually, this will be ../output/animals/CODENAME/m for male animals, and .../output/animals/CODENAME/y for babies.

6) In most cases, you will have to adjust the frame rate of the animation. Blender runs at 24fps by default, ZT1 tends to use 8-12fps. Locate the "Dimensions" Tab. Enter the old frame rate (eg. 24) into the left part of the "Time Remapping" field, and the desired ZT1 frame rate (eg. 10) into the right part. Locate the "ZT1 Sprite Rendering" Tab and click "Remap Action Time" to apply the new frame rate.

7) For ZT2 imports: Try each of the _muting buttons_ in the "ZT1 Sprite Rendering" Tab and see when walk or run animations become stationary. That means they no longer move forwards and walk on a treadmill. You could also do this manually in the Action editor, and of course this step is not needed if you made your own anims to begin with. The channel muting is a little intelligent. It will not mute anything if Bip01 is in roughly the same position at the first and last frame. This prevents sliding in such cases if Bip01 was animated.

8) Once you have done that, click "Render all Sprites". Alternatively, you can also render out only the current anim. This is especially useful if you have effects on some anims but not on others (like ripples and splashes), or if you've changed something and don't want to render everything again.

9) Now you have to create the color palette for your animations. First select an animation (in the action editor) that contains all colours you will need, including those for effects (splashes, dust, etc) and such. Then make sure you set your output file path in blender correctly. This is relevant for palette generation. If you select .../output/animals/CODENAME, you will get a shared palette for all life stages (sourced from m). If you specify .../output/animals/CODENAME/m, you only process the male files and they receive their own palette. You can then process the other life stages individually. Click _Generate Color Palette_ for each new palette. This will produce a png file in the folder you specified in output, with the name of the parent folder. Open this palette png file and move the bright green pixel into the top left corner. Swap the pixel there with the one where the green one was. This is required to make the conversion work flawlessly.

10) Once your palettes are all edited, click the "Convert Sprites to ZT1" button. This will first run FFMPEG to apply this palette to all files. Lastly, it will run a batch processing operation in ZT Studio to convert all PNGs to ZT1 graphics, which you can then add to your projects.




Fallback workflow, if you are running into problems with the automatic conversion workflow.

1-8) as above

9) Process the images as described here: https://github.com/jbostoen/ZTStudio/wiki/How-to-create-a-color-palette-to-share-with-several-graphics-(views,-animations)-using-GIMP If you don't do this, ZT Studio will raise an error because every image has too many colors.

10) Open ZT Studio. Make sure you have the files in "C:/temp/output" now. Change ZT Studio's settings like this: Conversions > Batch Conversions > Start Numbering at Frame 0; Writing PNG Files > Crop to relevant pixels of this frame (might not be needed). Run the Batch Conversion feature and you should get ZT1 animations and palettes.

# C_of_G - Center of Gravity Addon
   
V2.0.0 Blender 2.8 Version

Addon Download : [C_of_G.py](https://github.com/nerk987/C_of_G/releases/download/v2.0.0/C_of_G.py) 

## Introduction
It's important when animating to have a sense of the 'weight' of the character, otherwise the action will not look realistic. 

This addon continuously animates an empty to the approximate center of gravity of a Blender armature to assist this process. A second empty is kept level with the root bone of the armature underneath the center of gravity.

In order to calculate the center of gravity, the addon requires a mass value for each bone that contributes to the mass of the character. The C_of_G addon can automatically allocate a default mass. Most rigs include fairly standard names for bones using terms such as 'head', 'arm', 'spine', 'upper' etc. The 'Add Mass' button uses these terms to allocate an appropriate mass to bones selected for deformation. The length of the bone is also taken into account. This works quite well for Rigify and MakeHuman rigs for example. 

The values of mass that are assigned can be adjusted in the Tool Panel if required, or you can directly add modify or add the values in the Custom Parameter section of the bone tabs.

## Installation

Install the addon in the usual way.

## Usage

Select your amature in either object mode or pose mode. 

Find the 'C_of_G' panel in the 'Tools' tab of the tool shelf. The name field displays the selected armature.

Click on the 'Add mass for C_of_G' control. A custom field will be added to each bone with deformation selected.If the name of the bone contains a term like 'head', or 'foot', then the add-on will have guessed a mass to insert in the custom field. Otherwise, the field will be set to zero. You can see custom fields down the bottom of the 'Bone' tab in the properties panel.

If you aren't happy with the default mass allocation, adjust it the way you want. You can select one or more bones and then change the setting in the 'C_of_G' panel, or you can go directly to the custom fields and change the mass.

Then, click on the 'Track C_of_G' button. An upsidedown cone empty shows the position of the character's centre of gravity, and a cone empty shows the location directly under the centre of gravity level with the rot bone of the character.

##More Details

If there is no bone named 'root' in your character, then the lower C_of_G marker will not be shown. If you want it to appear, rename a suitable bone, or add a bone called 'root' and hit the 'Track C_of_G' button again.

If you only want one of the two empties to appear, just delete the one you don't want. The addon will keep tracking with the other.

IF you don't like the shape of the empties, you can change this in the usual way, and the addon will continue to track.

If you save your work, and reload it later, the empties and the mass allocation will also be saved. As long as the 'C_of_G' addon is loaded, the empties will continue tracking.

The addon uses a small amount of CPU time to do the tracking. If you delete both empties, the background task will be removed. If you wish to go back to tracking, just hit the 'Track C_of_G' button again and the empties will be re-added.(They will go back to being cones though if you had changed this...)









 
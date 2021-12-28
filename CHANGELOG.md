# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.3.0-alpha] - 2021-12-28
### Added
- Console output with the time it took to finish and the filepath for the generated file.

### Changed
- The UV map is now exported as .svg instead of .png, which is faster.
- The generated file no longer has the original texture file extension on its filename.
- Parts of DUCMesh are now on a loop.
- Double vertices are now removed using bmesh.
- Changed the bpy.ops.object.delete to bpy.data.objects.remove at DUCExport, cleans the console.
- Leftover meshes are now removed at the end.

### Removed
- Checkbox for double resolution, since it's no longer a raster image.
- README.md, removed planned features section.

## [0.2.0-alpha] - 2021-04-27
### Added
- Checkbox for double resolution UV map.

### Changed
- \_\_init\_\_.py, the conversion process has been moved from one single class into multiple ones.
- README.md, added sections for updating from an older version and manually installing the Add-on.

## [0.1.0-alpha] - 2021-04-21
### Added
- DCSUVConverter, contains the Blender Add-on.
- images, contains screenshots for README.md.
- CHANGELOG.md
- LICENSE
- README.md

[0.3.0-alpha]: https://github.com/Ettenmure/dcs-uv-converter/releases/tag/0.3.0-alpha
[0.2.0-alpha]: https://github.com/Ettenmure/dcs-uv-converter/releases/tag/0.2.0-alpha
[0.1.0-alpha]: https://github.com/Ettenmure/dcs-uv-converter/releases/tag/0.1.0-alpha

# ExoMeshOptimizer
 Unreal Engine 5 Mesh Optimizer

---

# Disable Nanite & Setup LODs (Legacy Script)

This repository provides a Python script that bulk-edits Static Meshes in Unreal Engine to:

1. Disable Nanite.  
2. Enforce a specific number of LOD levels.  
3. Set reduction percentages for each LOD.  
4. (Optionally) enable auto-compute LOD distances.

## Why “Legacy”?

Because certain Unreal Engine versions (especially early UE5 builds and some custom distributions) **do not** support newer Python API calls like `set_lod_count()` in the `StaticMeshEditorSubsystem`. Instead, this script manipulates the `source_models` property directly, which is more “legacy” but works on many builds that lack modern APIs.

## Usage

1. **Copy the Script**  
   Place the file (e.g., `init_optimizer.py`) in a location accessible to your UE Editor Python environment (such as `YourProject/Content/Python` or your local desktop).

2. **Open Unreal Engine & Enable Python**  
   - Make sure the **Editor Scripting Utilities** and **Python Editor Script Plugin** are enabled in **Edit > Plugins**.  
   - Restart the editor if needed.

3. **Run the Script**  
   - Open **Window > Developer Tools > Output Log** (UE5) or **Python Console**.  
   - Type:
     ```python
     import sys
     script_path = r"C:/Users/realc/Desktop/init_optimizer.py"  # Example path to your script
     if script_path not in sys.path:
         sys.path.append(script_path)
     exec(open(script_path).read())
     ```
   - The script will execute immediately if it ends with a call to `disable_nanite_and_setup_lods_legacy()`.

4. **Check Logs**  
   - Inspect the **Output Log** or **Python Console** for messages.  
   - The script will list or note any issues (e.g., assets that could not be modified).

5. **Reload Assets**  
   - If you have the Static Mesh Editor already open for certain assets, **close and reopen** those assets to see updated LODs and Nanite disabled status.  
   - Alternatively, right-click the mesh in the Content Browser ? “Reload”.

## Example Script Snippet

```python
import unreal

def disable_nanite_and_setup_lods_legacy(
    folder_path="/Game/Gameplay/Environments/Assets/Kitbash/Future_Warfare",
    recursive=True,
    num_lods=4,
    lod_reduction_percents=[1.0, 0.75, 0.5, 0.25],
    auto_compute_lod_distances=True
):
    asset_paths = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=recursive)

    for asset_path in asset_paths:
        asset = unreal.load_asset(asset_path)
        if not isinstance(asset, unreal.StaticMesh):
            continue

        # 1. Disable Nanite
        nanite_settings = asset.get_editor_property("nanite_settings")
        if nanite_settings and nanite_settings.get_editor_property("enabled"):
            nanite_settings.set_editor_property("enabled", False)
            asset.set_editor_property("nanite_settings", nanite_settings)

        # 2. Retrieve source_models
        try:
            source_models = asset.get_editor_property("source_models")
        except Exception as e:
            unreal.log_warning(f"Could not access source_models on {asset_path}. Error: {e}")
            continue
        
        if source_models is None:
            unreal.log_warning(f"{asset_path} has no source_models property accessible.")
            continue

        # 3. Adjust number of LODs
        current_count = len(source_models)
        if current_count < num_lods:
            for _ in range(current_count, num_lods):
                source_models.append(unreal.StaticMeshSourceModel())
        elif current_count > num_lods:
            source_models = source_models[:num_lods]
        
        # 4. Optional: auto-compute distances
        try:
            asset.set_editor_property("auto_compute_lod_distances", auto_compute_lod_distances)
        except:
            pass

        # 5. Set each LOD’s reduction percent
        for lod_index in range(num_lods):
            if lod_index >= len(source_models):
                break
            lod_model = source_models[lod_index]
            build_settings = lod_model.get_editor_property("build_settings")
            reduction_settings = build_settings.get_editor_property("reduction_settings")

            if lod_index < len(lod_reduction_percents):
                reduction_settings.set_editor_property("percent_triangles", lod_reduction_percents[lod_index])
            
            build_settings.set_editor_property("reduction_settings", reduction_settings)
            lod_model.set_editor_property("build_settings", build_settings)

        # 6. Reassign updated source_models
        asset.set_editor_property("source_models", source_models)

        # 7. Build & mark dirty
        asset.build()
        asset.mark_package_dirty()

    # 8. Save changes
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Run the script
disable_nanite_and_setup_lods_legacy()
```

## Known Limitations

- **Older Engine Builds**: If your build also hides `source_models`, or if you get errors like “Failed to find property ‘source_models’,” you may have no direct Python reflection path to manage LODs.  
- **Editor UI Refresh**: Unreal sometimes needs you to reopen or reload assets to reflect changes.  
- **Map/Thumbnail Loading**: UE may load or reference certain maps/thumbnails if your assets are used in those maps, which is normal.

## Contributing

1. **Fork** this repository.  
2. **Create** a new branch with your feature or fix.  
3. **Submit** a Pull Request describing what changed and why.

## License

This script is provided “as is” without warranty of any kind. You are free to use and modify it in your projects. Refer to the [LICENSE](LICENSE) file (if any) for details.

---

Happy Optimizing!
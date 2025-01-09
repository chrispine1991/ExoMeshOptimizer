import unreal

def disable_nanite_enable_lod_for_all_static_meshes():
    # 1. Retrieve all assets under '/Game' (recursive=True means all subfolders)
    all_assets = unreal.EditorAssetLibrary.list_assets("/Game", recursive=True)
    
    for asset_path in all_assets:
        # 2. Load each asset
        asset = unreal.load_asset(asset_path)
        
        # 3. Check if it is a Static Mesh
        if isinstance(asset, unreal.StaticMesh):
            
            # ---- Disable Nanite ----
            nanite_settings = asset.get_editor_property("nanite_settings")
            if nanite_settings is not None:
                nanite_settings.set_editor_property("enabled", False)
                asset.set_editor_property("nanite_settings", nanite_settings)
            
            # ---- Enable LOD ----
            # Example: Set 4 LODs; can adjust number as desired.
            asset.set_editor_property("num_lods", 4)
            asset.set_editor_property("auto_compute_lod_distances", True)
            
            # Rebuild the mesh with the new settings
            asset.build()
            
            # Mark the package dirty so it can be saved
            asset.mark_package_dirty()
    
    # 4. Save all updated assets
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Run the function
disable_nanite_enable_lod_for_all_static_meshes()

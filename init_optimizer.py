import unreal

def disable_nanite_and_setup_lods(
        folder_path="/Game/Gameplay/Environments/Assets/Kitbash/Future_Warfare",
        recursive=True,
        num_lods=4,
        lod_reduction_percents=[1.0, 0.5, 0.25, 0.125],
        lod_screen_sizes=[1.0, 0.8, 0.5, 0.3]
    ):
    
    # Get all assets in the specified folder (and subfolders if recursive=True).
    all_assets = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=recursive)
    
    for asset_path in all_assets:
        asset = unreal.load_asset(asset_path)
        
        if isinstance(asset, unreal.StaticMesh):
            # Disable Nanite
            nanite_settings = asset.get_editor_property("nanite_settings")
            if nanite_settings is not None:
                nanite_settings.set_editor_property("enabled", False)
                asset.set_editor_property("nanite_settings", nanite_settings)
            
            # Ensure the mesh has the correct number of LODs
            asset.set_editor_property("num_lods", num_lods)

            # Apply custom LOD settings for each LOD level
            # Note: LOD0 is the base mesh (often no reduction). 
            #       Adjust array values or skip LOD0 reduction if desired.
            for lod_index in range(num_lods):
                # Get the LOD struct (each element in asset.lods)
                lod = asset.get_editor_property("lods")[lod_index]
                
                # Build settings (where we can tweak reduction and more)
                build_settings = lod.get_editor_property("build_settings")
                reduction_settings = build_settings.get_editor_property("reduction_settings")
                
                # Safeguard in case your arrays are shorter than num_lods
                reduction_percent = lod_reduction_percents[lod_index] if lod_index < len(lod_reduction_percents) else 1.0
                screen_size = lod_screen_sizes[lod_index] if lod_index < len(lod_screen_sizes) else 1.0
                
                # ReductionSettings.percent_triangles (1.0 = 100%, 0.5 = 50%, etc.)
                reduction_settings.set_editor_property("percent_triangles", reduction_percent)
                build_settings.set_editor_property("reduction_settings", reduction_settings)
                
                # Apply the build settings back to the LOD
                lod.set_editor_property("build_settings", build_settings)
                
                # Screen size (how large on screen before switching LODs)
                lod.set_editor_property("screen_size", screen_size)

            # Build with new LOD settings
            asset.build()
            
            # Mark the asset package as dirty so changes can be saved
            asset.mark_package_dirty()
    
    # Save all updated assets
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Call the function:
#  - folder_path: Where your target meshes are located.
#  - recursive: Whether to include subfolders.
#  - num_lods: How many LODs to generate.
#  - lod_reduction_percents: The fraction of triangles to keep per LOD index.
#  - lod_screen_sizes: The screen size threshold for each LOD index.

disable_nanite_and_setup_lods(
    folder_path="/Game/Gameplay/Environments/Assets/Kitbash/Future_Warfare",
    recursive=True,
    num_lods=4,
    lod_reduction_percents=[1.0, 0.5, 0.25, 0.125],
    lod_screen_sizes=[1.0, 0.8, 0.5, 0.3]
)

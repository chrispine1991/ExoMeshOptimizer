import unreal

def disable_nanite_and_setup_lods(
        folder_path="/Game/Gameplay/Environments/Assets/Kitbash/Future_Warfare",
        recursive=True,
        num_lods=4,
        lod_reduction_percents=[1.0, 0.5, 0.25, 0.125],
        lod_screen_sizes=[1.0, 0.8, 0.5, 0.3]
    ):
    all_assets = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=recursive)
    
    for asset_path in all_assets:
        # Print the path to confirm which assets we are dealing with
        print(asset_path)

        asset = unreal.load_asset(asset_path)
        
        if isinstance(asset, unreal.StaticMesh):
            # Disable Nanite
            nanite_settings = asset.get_editor_property("nanite_settings")
            if nanite_settings is not None:
                nanite_settings.set_editor_property("enabled", False)
                asset.set_editor_property("nanite_settings", nanite_settings)
            
            # Ensure the mesh has the correct number of LODs
            asset.set_editor_property("num_lods", num_lods)

            # Apply custom LOD settings
            for lod_index in range(num_lods):
                lod = asset.get_editor_property("lods")[lod_index]
                build_settings = lod.get_editor_property("build_settings")
                reduction_settings = build_settings.get_editor_property("reduction_settings")
                
                reduction_percent = (
                    lod_reduction_percents[lod_index]
                    if lod_index < len(lod_reduction_percents) else 1.0
                )
                screen_size = (
                    lod_screen_sizes[lod_index]
                    if lod_index < len(lod_screen_sizes) else 1.0
                )
                
                reduction_settings.set_editor_property("percent_triangles", reduction_percent)
                build_settings.set_editor_property("reduction_settings", reduction_settings)
                lod.set_editor_property("build_settings", build_settings)
                
                lod.set_editor_property("screen_size", screen_size)

            asset.build()
            asset.mark_package_dirty()
    
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Run the function
disable_nanite_and_setup_lods()

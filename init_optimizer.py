import unreal

def disable_nanite_and_setup_lods(
    folder_path="/Game/Gameplay/Environments/Assets/Kitbash/Future_Warfare",
    recursive=True,
    num_lods=4,
    lod_reduction_percents=[1.0, 0.75, 0.5, 0.25],
    lod_screen_sizes=[1.0, 0.8, 0.5, 0.3]
):
    # Gather all assets in the specified folder (plus subfolders if recursive=True).
    all_assets = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=recursive)

    for asset_path in all_assets:
        asset = unreal.load_asset(asset_path)
        
        # Only operate on Static Meshes
        if isinstance(asset, unreal.StaticMesh):
            # 1. Disable Nanite
            nanite_settings = asset.get_editor_property("nanite_settings")
            if nanite_settings and nanite_settings.get_editor_property("enabled") is True:
                nanite_settings.set_editor_property("enabled", False)
                asset.set_editor_property("nanite_settings", nanite_settings)

            # 2. Get the SourceModels array (each element is one LOD)
            source_models = asset.get_editor_property("source_models")
            current_count = len(source_models)

            # If we have fewer SourceModels than desired, append new ones
            if current_count < num_lods:
                for _ in range(current_count, num_lods):
                    source_models.append(unreal.StaticMeshSourceModel())
            
            # If we have more SourceModels than desired, truncate the list
            elif current_count > num_lods:
                source_models = source_models[:num_lods]
            
            # 3. Apply LOD reduction and screen size settings
            for lod_index in range(num_lods):
                lod_model = source_models[lod_index]
                
                build_settings = lod_model.get_editor_property("build_settings")
                reduction_settings = build_settings.get_editor_property("reduction_settings")

                # Safely pick a reduction % for this LOD index
                if lod_index < len(lod_reduction_percents):
                    reduction_settings.set_editor_property("percent_triangles", lod_reduction_percents[lod_index])

                # Assign screen size to define when UE uses this LOD
                if lod_index < len(lod_screen_sizes):
                    lod_model.set_editor_property("screen_size", lod_screen_sizes[lod_index])
                
                # Reassign the updated reduction settings
                build_settings.set_editor_property("reduction_settings", reduction_settings)
                lod_model.set_editor_property("build_settings", build_settings)

            # Update the static mesh with the new SourceModels array
            asset.set_editor_property("source_models", source_models)
            
            # (Optional) Let Unreal auto-compute the distances between LODs
            # asset.set_editor_property("auto_compute_lod_distances", True)

            # 4. Build the mesh with new settings and mark it dirty
            asset.build()
            asset.mark_package_dirty()

    # Finally, save all changed packages
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)


# Run the function
disable_nanite_and_setup_lods()

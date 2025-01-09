import unreal

def disable_nanite_and_setup_lods_legacy(
    folder_path="/Game/<Path To Folder>",
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

        # 2. Attempt to retrieve source_models
        try:
            source_models = asset.get_editor_property("source_models")
        except Exception as e:
            print(f"Could not access source_models on {asset_path}. Error: {e}")
            continue
        
        if source_models is None:
            print(f"{asset_path} has no source_models property accessible.")
            continue

        # 3. Adjust number of LODs in source_models
        current_count = len(source_models)
        if current_count < num_lods:
            # Add new LODs
            for _ in range(current_count, num_lods):
                source_models.append(unreal.StaticMeshSourceModel())
        elif current_count > num_lods:
            # Remove extra LODs
            source_models = source_models[:num_lods]
        
        # 4. Optionally set auto_compute_lod_distances
        #    Note: Some older builds might not have this property either
        try:
            asset.set_editor_property("auto_compute_lod_distances", auto_compute_lod_distances)
        except:
            pass  # If not available, ignore

        # 5. Loop and set each LOD’s reduction percent
        for lod_index in range(num_lods):
            if lod_index >= len(source_models):
                break
            lod_model = source_models[lod_index]
            
            # Build settings
            build_settings = lod_model.get_editor_property("build_settings")
            reduction_settings = build_settings.get_editor_property("reduction_settings")
            
            # If we have a reduction percent for this LOD index, set it
            if lod_index < len(lod_reduction_percents):
                reduction_settings.set_editor_property("percent_triangles", lod_reduction_percents[lod_index])
            
            build_settings.set_editor_property("reduction_settings", reduction_settings)
            lod_model.set_editor_property("build_settings", build_settings)
        
        # 6. Reassign updated source_models
        asset.set_editor_property("source_models", source_models)

        # 7. Build & mark dirty
        asset.build()
        asset.mark_package_dirty()

    # 8. Save all dirty packages
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Run
disable_nanite_and_setup_lods_legacy()

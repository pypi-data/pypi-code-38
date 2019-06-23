from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(build_policy="missing")
    only_export = True
    
    if not only_export:
        builder.add()
        # builder.add_common_builds() #uncomment to allow more builds
        builder.run()
    else:
        if not builder.skip_check_credentials:
            builder.remotes_manager.add_remotes_to_conan()
            builder.auth_manager.login(builder.remotes_manager.upload_remote_name)
        name, version, user, channel, _ = builder.reference
        builder.conan_api.export(".", name, version, user, channel)
        builder.uploader.upload_recipe(builder.reference, True)

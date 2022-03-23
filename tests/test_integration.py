import os
import subprocess
from unittest import TestCase
from unittest.mock import Mock, patch

from ruamel.yaml import YAML

from conda_vendor.cli import (
    ironbank_from_meta_manifest,
    local_channels_from_meta_manifest,
    meta_manifest_from_env_yml,
    yaml_from_manifest,
)
from conda_vendor.custom_manifest import IBManifest

from conda_lock.src_parser import VersionedDependency, Selectors

# TODO: update for Dependency/VersionedDependency
def test_meta_manifest_from_env_yml(tmp_path, minimal_conda_forge_environment):

    test_manifest_filename = "test_metamanifest.yaml"
    expected_manifest_path = tmp_path / test_manifest_filename
    expected_packages = ["python=3.9.5", "conda-mirror=0.8.2"]

    # TODO: update for new Channel and Dependency objs
    def test_get_packages_from_manifest(meta_manifest, expected_packages):
        """
        Just a helper to make sure we got the packages we asked for
        """
        
        i_bank_pkg_list = []
        # add dependencies from main
        # WIP TODO: refactoring for updated yaml manifest output format
        for platform_main in meta_manifest["main"]:
            for entry_main in meta_manifest["main"][platform_main]["entries"]:
                name = entry_main["name"]
                version = entry_main["version"]
                dep_entry = f"{name}={version}"
                #print(f"DEP_ENTRY:{dep_entry}")
                if dep_entry == "python=3.9.5" or dep_entry == "conda-mirror=0.8.2":
                    i_bank_pkg_list.append(dep_entry)
        # add dependencies from conda-forge
        for platform_conda_forge in meta_manifest["conda-forge"]:
            for entry_conda_forge in meta_manifest["conda-forge"][platform_conda_forge]["entries"]:
                name = entry_conda_forge["name"]
                version = entry_conda_forge["version"]
                dep_entry = f"{name}={version}"
                #print(f"DEP_ENTRY:{dep_entry}")
                if dep_entry == "python=3.9.5" or dep_entry == "conda-mirror=0.8.2":
                    i_bank_pkg_list.append(dep_entry)
        
        #print(i_bank_pkg_list)    
        return i_bank_pkg_list

    meta_manifest_from_env_yml(
        minimal_conda_forge_environment, tmp_path, test_manifest_filename
    )
    with open(expected_manifest_path) as f:
        actual_manifest = YAML(typ="safe").load(
            f,
        )

    ## Ensure main and conda-forge channels are present in keys
    assert "main" in actual_manifest.keys()
    assert "conda-forge" in actual_manifest.keys()
    result_packages = test_get_packages_from_manifest(
        actual_manifest, expected_packages
    )
    TestCase().assertIn(result_packages, expected_packages)
    
    

# TODO: update for Dependency/VersionedDependency
#def test_local_channels_from_meta_manifest(tmp_path, minimal_conda_forge_environment):
#    test_env_name = "the_test_env"
#    test_manifest_filename = "test_metamanifest.yaml"
#    channel_root = tmp_path
#    test_manifest_path = tmp_path / test_manifest_filename
#    path_to_env_yaml = tmp_path / f"local_{test_env_name}.yaml"
#
#    meta_manifest_from_env_yml(
#        minimal_conda_forge_environment, tmp_path, test_manifest_filename
#    )
#
#    yaml_from_manifest(
#        channel_root=tmp_path,
#        meta_manifest_path=test_manifest_path,
#        env_name=test_env_name,
#    )
#
#    local_channels_from_meta_manifest(
#        channel_root=tmp_path, meta_manifest_path=test_manifest_path
#    )
#
#    try:
#        cmd_str_clean = f"conda clean --all -y"
#
#        process_out_clean = subprocess.check_output(
#            cmd_str_clean, stderr=subprocess.STDOUT, shell=True
#        ).decode("utf-8")
#    except:
#        pass
#
#    cmd_str_create_env = f"conda env create -f {path_to_env_yaml} --offline"
#    cmd_str_check_env = "conda env list "
#    cmd_str_list_explicit = f"conda list -n {test_env_name} --explicit"
#    cmd_rm_env = f"conda env remove -n {test_env_name}"
#
#    new_env = os.environ.copy()
#    new_env["CONDA_ADD_PIP_AS_PYTHON_DEPENDENCY"] = "False"
#
#    process_out_create_env = subprocess.check_output(
#        cmd_str_create_env, stderr=subprocess.STDOUT, env=new_env, shell=True
#    ).decode("utf-8")
#
#    process_out_env_list = subprocess.check_output(
#        cmd_str_check_env, stderr=subprocess.STDOUT, shell=True
#    ).decode("utf-8")
#
#    assert test_env_name in process_out_env_list
#
#    process_out_list_explicit = subprocess.check_output(
#        cmd_str_list_explicit, stderr=subprocess.STDOUT, shell=True
#    ).decode("utf-8")
#    assert "https" not in process_out_list_explicit
#
#    process_out_rm_env = subprocess.check_output(
#        cmd_rm_env, stderr=subprocess.STDOUT, shell=True
#    ).decode("utf-8")
#
#    assert "Remove all packages in environment" in process_out_rm_env
#    assert test_env_name in process_out_rm_env


@patch("conda_vendor.custom_manifest.IBManifest.__init__")
@patch("conda_vendor.custom_manifest.IBManifest.write_custom_manifest")
def test_ironbank_from_meta_manifest(
    mock_c, mock_i, tmp_path, get_path_location_for_manifest_fixture
):
    mock_i.return_value = None
    meta_manifest_path = get_path_location_for_manifest_fixture
    output_manifest_dir = tmp_path

    ironbank_from_meta_manifest(meta_manifest_path, output_manifest_dir)
    mock_c.assert_called_once_with(output_manifest_dir)
    mock_i.assert_called_once_with(meta_manifest_path)


@patch("conda_vendor.env_yaml_from_manifest.YamlFromManifest.__init__")
@patch("conda_vendor.env_yaml_from_manifest.YamlFromManifest.create_yaml")
def test_yaml_from_manifest(
    mock_c, mock_i, tmp_path, get_path_location_for_manifest_fixture
):
    mock_i.return_value = None

    meta_manifest_path = get_path_location_for_manifest_fixture
    channel_root = tmp_path

    env_name = "forgin-georgin"
    yaml_from_manifest(channel_root, meta_manifest_path, env_name)

    mock_c.assert_called_once_with(channel_root, env_name)
    mock_i.assert_called_once_with(channel_root, meta_manifest_path=meta_manifest_path)

# TODO: update for Dependency/VersionedDependency
#def test_smoke_cli(tmp_path, minimal_environment):
#    test_environment_str = str(minimal_environment)
#    test_output_metamanifest_root = str(tmp_path)
#    test_metamanifest_path = str(tmp_path / "meta_manifest.yaml")
#    test_output_channel_root = str(tmp_path / "local_channel")
#
#    cmd_str_clean = f"conda vendor meta-manifest --environment-yaml {test_environment_str} --manifest-root {test_output_metamanifest_root}"
#    subprocess.check_output(cmd_str_clean, stderr=subprocess.STDOUT, shell=True).decode(
#        "utf-8"
#    )
#    cmd_str_clean = f"conda vendor channels --channel-root {test_output_channel_root} --meta-manifest-path {test_metamanifest_path} -v"
#
#    subprocess.check_output(cmd_str_clean, stderr=subprocess.STDOUT, shell=True).decode(
#        "utf-8"
#    )

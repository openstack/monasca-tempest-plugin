# install_monasca_tempest_plugin
function install_monasca_tempest_plugin {
    setup_dev_lib "monasca-tempest-plugin"
}

if [[ "$1" == "stack" ]]; then
    case "$2" in
        install)
            echo_summary "Installing monasca-tempest-plugin"
            install_monasca_tempest_plugin
            ;;
    esac
fi

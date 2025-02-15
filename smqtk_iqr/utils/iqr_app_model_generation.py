"""
Train and generate models for the SMQTK IQR Application.

This application takes the same configuration file as the IqrService REST
service.  To generate a default configuration, please refer to the
``runApplication`` tool for the ``IqrService`` application:

    runApplication -a IqrService -g config.IqrService.json
"""
import argparse
import glob
import logging
import os.path as osp

from smqtk_dataprovider import DataSet
from smqtk_dataprovider.impls.data_element.file import DataFileElement
from smqtk_descriptors.descriptor_element_factory import DescriptorElementFactory
from smqtk_descriptors import DescriptorGenerator
from smqtk_indexing import NearestNeighborsIndex
from smqtk_iqr.utils import cli
from smqtk_core.configuration import (
    from_config_dict,
)


__author__ = 'paul.tunison@kitware.com'


def cli_parser():
    # Forgoing the ``cli.basic_cli_parser`` due to our use of dual
    # configuration files for this utility.
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('-v', '--verbose',
                        default=False, action='store_true',
                        help='Output additional debug logging.')
    parser.add_argument('-c', '--config',
                        metavar="PATH", nargs=2, required=True,
                        help='Path to the JSON configuration files. The first '
                             'file provided should be the configuration file '
                             'for the ``IqrSearchDispatcher`` web-application '
                             'and the second should be the configuration file '
                             'for the ``IqrService`` web-application.')

    parser.add_argument("-t", "--tab",
                        default=None, required=True,
                        help="The configuration \"tab\" of the "
                             "``IqrSearchDispatcher`` configuration to use. "
                             "This informs what dataset to add the input data "
                             "files to.")
    parser.add_argument("input_files",
                        metavar='GLOB', nargs="+",
                        help="Shell glob to files to add to the configured "
                             "data set.")

    return parser


def main():
    args = cli_parser().parse_args()

    ui_config_filepath, iqr_config_filepath = args.config
    llevel = logging.DEBUG if args.verbose else logging.INFO
    tab = args.tab
    input_files_globs = args.input_files

    # Not using `cli.utility_main_helper`` due to deviating from single-
    # config-with-default usage.
    cli.initialize_logging(logging.getLogger('smqtk'), llevel)
    cli.initialize_logging(logging.getLogger('__main__'), llevel)
    log = logging.getLogger(__name__)

    log.info("Loading UI config: '{}'".format(ui_config_filepath))
    ui_config, ui_config_loaded = cli.load_config(ui_config_filepath)
    log.info("Loading IQR config: '{}'".format(iqr_config_filepath))
    iqr_config, iqr_config_loaded = cli.load_config(iqr_config_filepath)
    if not (ui_config_loaded and iqr_config_loaded):
        raise RuntimeError("One or both configuration files failed to load.")

    # Ensure the given "tab" exists in UI configuration.
    if tab is None:
        log.error("No configuration tab provided to drive model generation.")
        exit(1)
    if tab not in ui_config["iqr_tabs"]:
        log.error("Invalid tab provided: '{}'. Available tags: {}"
                  .format(tab, list(ui_config["iqr_tabs"])))
        exit(1)

    #
    # Gather Configurations
    #
    log.info("Extracting plugin configurations")

    ui_tab_config = ui_config["iqr_tabs"][tab]
    iqr_plugins_config = iqr_config['iqr_service']['plugins']

    # Configure DataSet implementation and parameters
    data_set_config = ui_tab_config['data_set']

    # Configure DescriptorElementFactory instance, which defines what
    # implementation of DescriptorElement to use for storing generated
    # descriptor vectors below.
    descriptor_elem_factory_config = iqr_plugins_config['descriptor_factory']

    # Configure DescriptorGenerator algorithm implementation, parameters and
    # persistent model component locations (if implementation has any).
    descriptor_generator_config = iqr_plugins_config['descriptor_generator']

    # Configure NearestNeighborIndex algorithm implementation, parameters and
    # persistent model component locations (if implementation has any).
    nn_index_config = iqr_plugins_config['neighbor_index']

    #
    # Initialize data/algorithms
    #
    # Constructing appropriate data structures and algorithms, needed for the
    # IQR demo application, in preparation for model training.
    #
    log.info("Instantiating plugins")
    #: :type: representation.DataSet
    data_set = \
        from_config_dict(data_set_config, DataSet.get_impls())
    descriptor_elem_factory = DescriptorElementFactory \
        .from_config(descriptor_elem_factory_config)
    #: :type: algorithms.DescriptorGenerator
    descriptor_generator = \
        from_config_dict(descriptor_generator_config,
                         DescriptorGenerator.get_impls())

    #: :type: algorithms.NearestNeighborsIndex
    nn_index = \
        from_config_dict(nn_index_config,
                         NearestNeighborsIndex.get_impls())

    #
    # Build models
    #
    log.info("Adding files to dataset '{}'".format(data_set))
    for g in input_files_globs:
        g = osp.expanduser(g)
        if osp.isfile(g):
            data_set.add_data(DataFileElement(g, readonly=True))
        else:
            log.debug("Expanding glob: %s" % g)
            for fp in glob.iglob(g):
                data_set.add_data(DataFileElement(fp, readonly=True))

    # Generate a model if the generator defines a known generation method.
    try:
        log.debug("descriptor generator as model to generate?")
        descriptor_generator.generate_model(data_set)  # type: ignore
    except AttributeError as ex:
        log.debug("descriptor generator as model to generate - Nope: {}"
                  .format(str(ex)))

    # Generate descriptors of data for building NN index.
    log.info("Computing descriptors for data set with {}"
             .format(descriptor_generator))
    descr_list = list(descriptor_generator.generate_elements(
        data_set, descr_factory=descriptor_elem_factory
    ))

    # Possible additional support steps before building NNIndex
    try:
        # Fit the LSH index functor
        log.debug("Has LSH Functor to fit?")
        nn_index.lsh_functor.fit(descr_list)  # type: ignore
    except AttributeError as ex:
        log.debug("Has LSH Functor to fit - Nope: {}".format(str(ex)))

    log.info("Building nearest neighbors index {}".format(nn_index))
    nn_index.build_index(descr_list)


if __name__ == "__main__":
    main()

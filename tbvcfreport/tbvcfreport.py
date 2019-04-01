"""
Interface to CLI
"""
import logging
import os
import sys

import click
from snpit import snpit

try:
    from .report import generate_report
    from .vcfproc import VCFProc
except (ImportError, ValueError):
    from report import generate_report
    from vcfproc import VCFProc

log = logging.getLogger(__name__)


def check_vcf(vcf_file):
    """
    Check vcf file for emptiness
    :param vcf_file:
    :return:
    """
    _file = False
    if os.stat(vcf_file).st_size > 0:
        _file = True
    else:
        sys.stderr.write(
            '{vcf_file} is empty!\n'.format(vcf_file=vcf_file))
    return _file


@click.group()
def cli():
    """
    tbvcfreport is a command line tool that generates an HTML-based VCF report.
    :return:
    """
    pass


@cli.command()
@click.argument('vcf_dir', type=click.Path(exists=True))
def generate(vcf_dir):
    """
    Generate report from VCF files in VCF_DIR.
    :param vcf_dir:
    :return:
    """
    if os.path.isdir(vcf_dir):
        for root, dirs, files in os.walk(vcf_dir):
            if len(os.listdir(vcf_dir)) == 0:
                log.error(
                    '{vcf_dir} is empty!\n'.format(vcf_dir=vcf_dir))
            for vcf_file in files:
                vcf_file = '/'.join(
                    [os.path.abspath(vcf_dir), vcf_file]
                )
                if check_vcf(vcf_file):
                    file_name = vcf_file.split('/')[-1].split('.')[0]
                    lineage_parser = snpit(input_file=vcf_file)
                    (species, lineage, sublineage, percent_agreement) = lineage_parser.determine_lineage()
                    percent_agreement = round(percent_agreement)
                    vcf_file = VCFProc(vcf_file=vcf_file)
                    variants = vcf_file.parse()
                    generate_report(file_name=file_name, data={'variants': variants,
                                                               'lineage': {
                                                                    'species': species,
                                                                    'lineage': lineage,
                                                                    'sublineage': sublineage,
                                                                    'percent_agreement': percent_agreement
                                                               }})
    elif os.path.isfile(vcf_dir):
        vcf_file = os.path.abspath(vcf_dir)
        if check_vcf(vcf_file):
            file_name = vcf_file.split('/')[-1].split('.')[0]
            vcf_file = VCFProc(vcf_file=vcf_file)
            variants = vcf_file.parse()
            generate_report(file_name=file_name, data=variants)
            # webbrowser.open('file://' + os.path.realpath(report))
    else:
        log.error("Can't generate report for {}!".format(vcf_dir))


if __name__ == '__main__':
    generate()

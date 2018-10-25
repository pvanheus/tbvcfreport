"""
Interface to handle VCF files
"""
import sys
import vcf
import logging
from tqdm import tqdm

try:
    from .dbconn import get_gene_data
except (ImportError, ValueError):
    from dbconn import get_gene_data

log = logging.getLogger(__name__)


class VCFProc(object):
    """
    Process VCF File
    """

    def __init__(self, vcf_file):
        self.vcf_file = vcf_file

    def parse(self):
        variants, rv_tags, known_variant = [], [], False
        if self.vcf_file.endswith(".vcf"):
            log.info("Processing: {}...\n".format(self.vcf_file))
            with open(self.vcf_file) as _vcf:
                vcf_reader = vcf.Reader(_vcf)
                for record in tqdm(vcf_reader):
                    if record.var_type == 'snp':
                        record.affected_start += 1
                    affected_region = "..".join(
                        [str(record.affected_start), str(record.affected_end)])
                    # Usually there is more than one annotation reported in
                    # each ANN. A variant can affect multiple genes
                    if record.INFO.get('ANN'):
                        annotations = self.get_variant_ann(record=record)
                        for annotation in annotations:
                            gene_identifier = annotation[4]
                            # TODO: It is much faster to issue 1 query
                            rv_tags.append(gene_identifier)
                            gene_db_data = get_gene_data(gene_identifier)
                            if annotation[10] is not '':
                                # Check if variant in known (in db)
                                known_variant = self.is_variant_known(
                                    record.POS, annotation, gene_db_data['variant'])
                            annotation.extend(
                                [record.CHROM, record.POS, record.REF,
                                 record.var_type, affected_region,
                                 gene_db_data, known_variant])
                            variants.append(annotation)
        else:
            sys.stderr.write("Can't parse {vcf_file}".format(
                vcf_file=self.vcf_file))
        return variants

    @staticmethod
    def get_variant_ann(record):
        """
        Get Annotation from ANN
        :param record:
        :return:
        """
        annotations = []
        if record.INFO.get('ANN'):
            annotations = [ann.split("|") for ann in record.INFO['ANN']]
        return annotations

    @staticmethod
    def is_variant_known(pos, rec_annotation, db_variants):
        known = False
        if len(db_variants) is 0:
            return known
        else:
            for variant in db_variants:
                if rec_annotation[10].strip('p.') == variant['consequence'] and pos == variant['pos']:
                    known = True
                    log.info("Found known variant for {gene}: {variant}"
                             .format(gene=rec_annotation[3],
                                     variant=variant['consequence']))
        return known

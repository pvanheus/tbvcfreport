import pytest

from tbvcfreport.vcfproc import VCFProc
from test_cli import TEST_VCF


@pytest.fixture(scope="module")
def vcf_proc():
    vcf = VCFProc(vcf_file=TEST_VCF)
    return vcf


# @pytest.mark.skip(reason="no way of currently testing this")
def test_parse(vcf_proc):
    result = vcf_proc.parse()
    assert isinstance(result, list) is True
